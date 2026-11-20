set positional-arguments

default:
  @just --list

deploy:
  pyinfra @local deploy.py -y
  pyinfra hosts.py deploy.py -y

dryrun:
  pyinfra hosts.py deploy.py --diff --dry

