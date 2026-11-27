resource "vault_mount" "kvv2" {
  path        = "house"
  type        = "kv"
  options     = { version = "2" }
  description = "House secrets"
}

resource "vault_policy" "house_secret_reader" {
  name   = "house_secret_reader"
  policy = <<-EOT
    path "house/data/*" {
      capabilities = ["read", "list"]
    }

    path "house/metadata/*" {
      capabilities = ["read", "list"]
    }
  EOT
}
