#!/usr/bin/env bash
# Varre páginas, arquivos de exemplo e histórico do git atrás de strings proibidas.
# A lista real (nome da máquina, usuário, pastas, IPs e impressões digitais
# da máquina da coleta) fica FORA do repo:  PROIBIDO=../lista.txt
# Além dela, entram padrões embutidos genéricos: IPv4 (menos os ilustrativos
# 192.168.0.*, 203.0.113.*, 127.* e 255.*), MAC (menos os inventados
# 02:00:00:00:00:*), GUID, /home/<nome> que não seja ana nem lab, o começo
# de uma chave privada e o servidor e o provedor reais do autor.
# "re:" = expressão regular (grep -P), sem diferenciar maiúsculas.
set -u
cd "$(dirname "$0")/.."
LISTA="${PROIBIDO:-../lista.txt}"

padroes=()
# IPv4: libera 192.168.0.* (a rede do laboratório), 203.0.113.* (reservada para exemplos), 127.* e 255.*
padroes+=("re:(?<![\\d.])(?!192\\.168\\.0\\.|203\\.0\\.113\\.|127\\.|255\\.)(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]\\d?)\\.(\\d{1,3}\\.){2}\\d{1,3}(?![\\d.])")
# MAC (menos os inventados 02:00:00:00:00:*) e GUID
padroes+=("re:\\b(?!02:00:00:00:00:)([0-9a-f]{2}[:-]){5}[0-9a-f]{2}\\b")
padroes+=("re:\\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\b")
# /home/<nome> que não seja ana nem lab (o <nome> do exemplo do guia não conta)
padroes+=("re:/home/(?!(ana|lab)\\b)[a-z_][a-z0-9_-]*")
# o começo de uma chave privada (os colchetes evitam casar com este arquivo)
padroes+=("re:BEGIN [A-Z ]*PRIVAT[E] KEY")

if [ -f "$LISTA" ]; then
  echo "Usando lista $LISTA (além dos padrões embutidos)."
  while IFS= read -r linha || [ -n "$linha" ]; do
    [[ -z "$linha" || "$linha" == \#* ]] && continue
    padroes+=("$linha")
  done < "$LISTA"
else
  echo "Lista $LISTA não encontrada; usando só os padrões embutidos."
fi

falhou=0
for pad0 in "${padroes[@]}"; do
  if [[ "$pad0" == re:* ]]; then pad="${pad0#re:}"; opt=(-P -i); else pad="$pad0"; opt=(-F -i); fi
  achou=$(grep -rn "${opt[@]}" --exclude-dir=.git --exclude-dir=_saidas --exclude-dir=_saidas-anon --exclude-dir=node_modules --exclude-dir=__pycache__ -I -e "$pad" . | head -5)
  hist=$(git log --all -p 2>/dev/null | grep -c "${opt[@]}" -e "$pad")
  if [ -n "$achou" ] || [ "$hist" != "0" ]; then
    falhou=1; echo "FALHA: $pad (histórico: $hist)"; [ -n "$achou" ] && echo "$achou"
  fi
done
[ $falhou = 0 ] && echo "OK: nenhuma string proibida nas páginas nem no histórico."
exit $falhou
