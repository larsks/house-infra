set positional-arguments

default:
  @just --list

local:
  pyinfra @local deploy.py -y

deploy *args: local
  pyinfra hosts.py deploy.py --diff -y "$@"

dryrun *args: local
  pyinfra hosts.py deploy.py --diff --dry "$@"
