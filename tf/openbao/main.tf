resource "vault_mount" "kvv2" {
  path        = "house"
  type        = "kv"
  options     = { version = "2" }
  description = "House secrets"
}

