set positional-arguments

default:
  @just --list

local:
  pyinfra @local deploy.py -y

deploy *args: local
  pyinfra hosts.py deploy.py -y "$@"

dryrun *args: local
  pyinfra hosts.py deploy.py --diff --dry "$@"
