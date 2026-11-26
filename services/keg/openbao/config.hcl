ui             = true
disable_mlock  = true

api_addr       = "https://openbao.keg.house"
cluster_addr   = "https://openbao:8201"

storage "raft" {
  path    = "/openbao/data"
  node_id = "raft_node_1"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}

audit "file" "to-stdout" {
  description = "Write audit information to standard output."
  options {
    file_path = "stdout"
    log_raw = "true"
  }
}

