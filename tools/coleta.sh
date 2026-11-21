#!/usr/bin/env bash
# coleta.sh — monta o laboratório, colhe as saídas de todas as caixas e desmonta tudo.
#
#   sudo bash tools/coleta.sh            (todas as caixas)
#   sudo bash tools/coleta.sh tunel-     (só as caixas cujo id começa com o prefixo)
#
# Precisa de root (namespaces de rede), openssh-client, openssh-server, rsync, rsyslog,
# fail2ban, curl e do locale pt_BR.UTF-8. O laboratório fica em /srv/guia-ssh-lab e é
# apagado no fim, com os usuários de teste que ele criou.
set -eu
cd "$(dirname "$0")/.."
trap 'bash tools/lab.sh descer' EXIT
bash tools/lab.sh subir
python3 tools/coleta.py "${1:-}"
