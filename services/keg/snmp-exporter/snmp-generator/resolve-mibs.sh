#!/usr/bin/env bash
#
# Recursively resolve and download missing MIB dependencies for a directory
# of flat, unextensioned ASN.1 MIB files (the layout snmp-generator's
# MIBDIRS expects).
#
# Usage: ./resolve-mibs.sh <mibs-dir>
#
# Repeatedly runs smilint over every MIB file in the directory to find
# unresolved `IMPORTS ... FROM <module>` references, downloads each missing
# module from a public ASN.1 MIB mirror, and repeats until smilint reports
# no more missing imports (or until a module can't be found anywhere, in
# which case it's reported and left for manual handling).
set -euo pipefail

MIB_SOURCES=(
    "https://mibs.pysnmp.com/asn1/%s"
    "https://raw.githubusercontent.com/pysnmp/mibs/main/asn1/%s"
)

dir="${1:?usage: $0 <mibs-dir>}"
[[ -d "$dir" ]] || { echo "error: not a directory: $dir" >&2; exit 1; }
dir="$(cd "$dir" && pwd)"

command -v smilint >/dev/null || { echo "error: smilint not found (install libsmi)" >&2; exit 1; }

declare -A failed_modules=()

find_missing_modules() {
    local args=()
    local f
    for f in "$dir"/*; do
        [[ -f "$f" ]] && args+=(-p "$f")
    done
    SMIPATH="$dir" smilint -s -l 6 "${args[@]}" 2>&1 \
        | grep -o "failed to locate MIB module \`[^']*'" \
        | sed -E "s/failed to locate MIB module \`([^']*)'/\1/" \
        | sort -u
}

fetch_module() {
    local module="$1" url dest
    dest="$dir/$module"
    for url_tmpl in "${MIB_SOURCES[@]}"; do
        # shellcheck disable=SC2059
        url="$(printf "$url_tmpl" "$module")"
        if curl -fsS -o "$dest" "$url" 2>/dev/null; then
            echo "  fetched $module from $url"
            return 0
        fi
        rm -f "$dest"
    done
    return 1
}

echo "Resolving MIB dependencies in: $dir"

iteration=0
while true; do
    iteration=$((iteration + 1))
    mapfile -t missing < <(find_missing_modules)

    # Drop modules we've already tried and failed to fetch, so we don't
    # loop forever on something that genuinely isn't in the mirrors.
    todo=()
    for m in "${missing[@]}"; do
        [[ -n "${failed_modules[$m]:-}" ]] || todo+=("$m")
    done

    if [[ "${#todo[@]}" -eq 0 ]]; then
        if [[ "${#missing[@]}" -eq 0 ]]; then
            echo "Done after $((iteration - 1)) fetch round(s): no unresolved imports."
        else
            echo "Stopped: ${#missing[@]} import(s) remain unresolved and could not be fetched:"
            printf '  %s\n' "${missing[@]}"
            exit 1
        fi
        break
    fi

    echo "Round $iteration: ${#todo[@]} missing module(s): ${todo[*]}"
    for m in "${todo[@]}"; do
        if ! fetch_module "$m"; then
            echo "  could not find $m in any configured mirror"
            failed_modules["$m"]=1
        fi
    done
done
