set positional-arguments

default:
  @just --list

local:
  pyinfra @local deploy.py -y

deploy: local
  pyinfra hosts.py deploy.py -y

dryrun: local
  pyinfra hosts.py deploy.py --diff --dry
