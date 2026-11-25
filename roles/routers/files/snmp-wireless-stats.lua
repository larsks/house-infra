#!/opt/bin/lua

-- net-snmp pass_persist script publishing per-client wifi RSSI and
-- per-radio noise floor, for both the 2.4GHz and 5GHz radios, read
-- from the broadcom `wl` tool. Register it in snmpd.conf with:
--
--   pass_persist .1.3.6.1.4.1.8072.9999 /jffs/scripts/snmp-wireless-stats.lua
--
-- 1.3.6.1.4.1.8072.9999 is NET-SNMP-MIB::netSnmpPlaypen, the subtree
-- net-snmp reserves for exactly this kind of unregistered, local use.
--
--   .1.<ifidx>              -- noise floor (dBm) for interface ifidx
--   .2.<ifidx>.<clientidx>  -- RSSI (dBm) for a client, keyed by its
--                              position in that interface's (sorted,
--                              stable) assoclist
--   .3.<ifidx>              -- the interface name itself (string),
--                              so ifidx is self-describing
--   .4.<ifidx>.<clientidx>  -- the client's MAC address (string), so
--                              clientidx is self-describing too
--
-- ifidx is the 1-based position of the interface in WL_IFACES, which
-- defaults to "eth1 eth2" -- this board's 2.4GHz and 5GHz radios --
-- but varies by board, so override it if needed. clientidx is a
-- client's 1-based position within that interface's sorted assoclist;
-- it can shift between polls as clients associate/disassociate, same
-- as ifIndex-style tables generally.
--
-- pass_persist scripts must not block snmpd, but `wl` is slow enough
-- (tens of ms per association/rssi call, times two radios) that
-- running it inline on every get/getnext would. So this forks: the
-- child polls `wl` on a timer and writes the result table to a state
-- file; the parent only ever reads that file and talks the
-- pass_persist protocol on stdio, so it never blocks on the radios.

local posix = require("posix")

-- luaposix's getpid/getppid shape has changed across versions: some
-- take a selector argument ("pid"/"ppid") and return a number, some
-- take no arguments and return a number directly, and some take no
-- arguments and return a table of {pid=, ppid=, uid=, ...}. Probe
-- for whichever this build supports rather than assuming one.
local function get_pid()
  local ok, v = pcall(posix.getpid, "pid")
  if ok and type(v) == "number" then
    return v
  end
  ok, v = pcall(posix.getpid)
  if ok and type(v) == "number" then
    return v
  elseif ok and type(v) == "table" then
    return v.pid
  end
  error("snmp-wireless-stats: could not determine own pid")
end

local function get_ppid()
  local ok, v = pcall(posix.getpid, "ppid")
  if ok and type(v) == "number" then
    return v
  end
  if posix.getppid then
    ok, v = pcall(posix.getppid)
    if ok and type(v) == "number" then
      return v
    end
  end
  ok, v = pcall(posix.getpid)
  if ok and type(v) == "table" then
    return v.ppid
  end
  error("snmp-wireless-stats: could not determine parent pid")
end

local STATE_FILE = os.getenv("WL_METRICS_STATE_FILE") or "/tmp/snmp-wireless-stats.state"
local POLL_INTERVAL = tonumber(os.getenv("WL_METRICS_POLL_INTERVAL")) or 5

local WL_IFACES = {}
for iface in (os.getenv("WL_IFACES") or "eth1 eth2"):gmatch("%S+") do
  WL_IFACES[#WL_IFACES + 1] = iface
end

local BASE = ".1.3.6.1.4.1.8072.9999"
local NOISE_BASE = BASE .. ".1"
local RSSI_BASE = BASE .. ".2"
local IFNAME_BASE = BASE .. ".3"
local MAC_BASE = BASE .. ".4"

-- ---------------------------------------------------------------------
-- shared helpers
-- ---------------------------------------------------------------------

local function last_field(line)
  local last
  for word in line:gmatch("%S+") do
    last = word
  end
  return last
end

-- Run a command, returning the last whitespace-separated field of its
-- last non-empty output line (that's the shape of `wl`'s output,
-- whether it prints just the value or "label value").
local function run_last_field(cmd)
  local fh = io.popen(cmd .. " 2>/dev/null")
  if not fh then
    return nil
  end
  local value
  for line in fh:lines() do
    if line:match("%S") then
      value = last_field(line)
    end
  end
  fh:close()
  return value
end

local function mac_to_octets(mac)
  local octets = {}
  for hex in mac:gmatch("[^:]+") do
    octets[#octets + 1] = tonumber(hex, 16)
  end
  return octets
end

-- Split an OID like ".1.3.6.1...N" into a table of numbers.
local function oid_parts(oid)
  local parts = {}
  for n in oid:gmatch("%d+") do
    parts[#parts + 1] = tonumber(n)
  end
  return parts
end

-- Numeric OID comparison: a strict prefix sorts before any of its own
-- extensions, otherwise compare sub-identifiers left to right.
-- Returns -1, 0 or 1.
local function oid_cmp(a, b)
  local pa, pb = oid_parts(a), oid_parts(b)
  local n = math.min(#pa, #pb)
  for i = 1, n do
    if pa[i] < pb[i] then
      return -1
    elseif pa[i] > pb[i] then
      return 1
    end
  end
  if #pa < #pb then
    return -1
  elseif #pa > #pb then
    return 1
  end
  return 0
end

-- ---------------------------------------------------------------------
-- child: polls `wl` and writes the state file
-- ---------------------------------------------------------------------

-- Builds the four OID branches independently, in ifidx order (and,
-- within the rssi/mac branches, clientidx order) -- that's already
-- overall ascending OID order (branch 1 < 2 < 3 < 4), so no final
-- cross-branch sort is needed and a sequential getnext scan works.
local function build_entries()
  local noise_entries, rssi_entries, ifname_entries, mac_entries = {}, {}, {}, {}

  for idx, iface in ipairs(WL_IFACES) do
    ifname_entries[#ifname_entries + 1] =
      { oid = IFNAME_BASE .. "." .. idx, type = "string", value = iface }

    local noise = run_last_field(string.format("wl -i %s noise", iface))
    if noise then
      noise_entries[#noise_entries + 1] =
        { oid = NOISE_BASE .. "." .. idx, type = "integer", value = noise }
    end

    local fh = io.popen(string.format("wl -i %s assoclist 2>/dev/null", iface))
    local macs = {}
    if fh then
      for line in fh:lines() do
        local mac = last_field(line)
        if mac then
          macs[#macs + 1] = mac
        end
      end
      fh:close()
    end

    -- Sort so clientidx assignment (and so the table's OID order) is
    -- stable across polls rather than following `wl`'s own ordering.
    table.sort(macs, function(a, b)
      local oa, ob = mac_to_octets(a), mac_to_octets(b)
      for i = 1, 6 do
        if oa[i] ~= ob[i] then
          return oa[i] < ob[i]
        end
      end
      return false
    end)

    local clientidx = 0
    for _, mac in ipairs(macs) do
      local rssi = run_last_field(string.format("wl -i %s rssi %s", iface, mac))
      if rssi then
        clientidx = clientidx + 1
        rssi_entries[#rssi_entries + 1] =
          { oid = RSSI_BASE .. "." .. idx .. "." .. clientidx, type = "integer", value = rssi }
        mac_entries[#mac_entries + 1] =
          { oid = MAC_BASE .. "." .. idx .. "." .. clientidx, type = "string", value = mac }
      end
    end
  end

  local entries = {}
  for _, e in ipairs(noise_entries) do
    entries[#entries + 1] = e
  end
  for _, e in ipairs(rssi_entries) do
    entries[#entries + 1] = e
  end
  for _, e in ipairs(ifname_entries) do
    entries[#entries + 1] = e
  end
  for _, e in ipairs(mac_entries) do
    entries[#entries + 1] = e
  end
  return entries
end

local function write_state(entries)
  local tmp = string.format("%s.tmp.%d", STATE_FILE, get_pid())
  local fh, err = io.open(tmp, "w")
  if not fh then
    return nil, err
  end
  for _, e in ipairs(entries) do
    fh:write(e.oid, "\t", e.type, "\t", e.value, "\n")
  end
  fh:close()
  -- rename(2) is atomic, so the parent never sees a half-written file.
  return os.rename(tmp, STATE_FILE)
end

local function child_loop(parent_pid)
  while true do
    write_state(build_entries())

    -- If we've been reparented, the parent is gone; stop polling
    -- rather than running forever as an orphan.
    if get_ppid() ~= parent_pid then
      os.exit(0)
    end

    posix.sleep(POLL_INTERVAL)
  end
end

-- ---------------------------------------------------------------------
-- parent: speaks the pass_persist protocol on stdio
-- ---------------------------------------------------------------------

local function read_state()
  local entries = {}
  local fh = io.open(STATE_FILE, "r")
  if not fh then
    return entries
  end
  for line in fh:lines() do
    local oid, typ, value = line:match("^(.-)\t(.-)\t(.*)$")
    if oid then
      entries[#entries + 1] = { oid = oid, type = typ, value = value }
    end
  end
  fh:close()
  return entries
end

local function do_get(oid)
  for _, e in ipairs(read_state()) do
    if e.oid == oid then
      return e
    end
  end
  return nil
end

local function do_getnext(oid)
  -- Entries are stored in ascending OID order, so the first one
  -- greater than the request is the answer.
  for _, e in ipairs(read_state()) do
    if oid_cmp(oid, e.oid) < 0 then
      return e
    end
  end
  return nil
end

local function respond_entry(e)
  if e then
    print(e.oid)
    print(e.type)
    print(e.value)
  else
    print("NONE")
  end
  io.stdout:flush()
end

local function parent_loop(child_pid)
  io.stdout:setvbuf("line")
  while true do
    local cmd = io.read("*l")
    if cmd == nil then
      break
    elseif cmd == "PING" then
      print("PONG")
      io.stdout:flush()
    elseif cmd == "get" then
      respond_entry(do_get(io.read("*l")))
    elseif cmd == "getnext" then
      respond_entry(do_getnext(io.read("*l")))
    elseif cmd == "set" then
      io.read("*l") -- type
      io.read("*l") -- value
      print("not-writable")
      io.stdout:flush()
    end
  end

  posix.kill(child_pid, posix.SIGTERM)
  posix.wait(child_pid)
end

-- ---------------------------------------------------------------------

local parent_pid = get_pid()
local pid = posix.fork()

if pid == 0 then
  child_loop(parent_pid)
elseif pid then
  parent_loop(pid)
else
  io.stderr:write("snmp-wireless-stats: fork failed\n")
  os.exit(1)
end
