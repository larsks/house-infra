set positional-arguments

default:
  @just --list

local:
  uv run pyinfra --chdir local @local deploy.py -y

deploy *args: local
  uv run pyinfra hosts.py deploy.py --diff -y "$@"

dryrun *args: local
  uv run pyinfra hosts.py deploy.py --diff --dry "$@"

run *args:
  uv run pyinfra hosts.py "$@"
