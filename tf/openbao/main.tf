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

resource "vault_auth_backend" "keg_containers" {
  type = "approle"
  path = "keg"
}

resource "vault_approle_auth_backend_role" "keg_containers" {
  backend        = vault_auth_backend.keg_containers.path
  role_name      = "house_secret_reader"
  token_policies = [vault_policy.house_secret_reader.name]
}
