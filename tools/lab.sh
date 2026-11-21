#!/usr/bin/env bash
# lab.sh — o laboratório de três computadores do Guia SSH, todo dentro de UMA máquina Linux.
#
#   sudo bash tools/lab.sh subir      cria usuários, redes e modelos
#   sudo bash tools/lab.sh estado X   volta o laboratório ao estado X (zero, conhecido, chave, config)
#   sudo bash tools/lab.sh descer     para tudo e apaga o laboratório (usuários, redes, arquivos)
#
# Cada "computador" é um namespace de rede + UTS (nome de host) + montagem:
#   notebook  192.168.0.10   (cliente; usuária ana)
#   servidor  192.168.0.20 e 192.168.0.129   (sshd na porta 22; usuário lab)
#   interno   192.168.0.130  (sshd; só o servidor alcança)
# Nada escuta fora dos namespaces: a máquina de verdade não ganha porta aberta.
# /home, /root, /etc/ssh, /tmp, /run, /var/log, /etc/hosts e /etc/motd de cada
# computador são pastas do laboratório montadas por cima: as chaves de host e os
# arquivos da máquina de verdade nunca aparecem.
set -eu
LAB=${LAB:-/srv/guia-ssh-lab}
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
SENHA_LAB=${SENHA_LAB:-lab123}
NS="notebook servidor interno"

usuario_de() { case "$1" in notebook) echo ana;; *) echo lab;; esac; }
ip_de() { case "$1" in notebook) echo 192.168.0.10;; servidor) echo 192.168.0.20;; interno) echo 192.168.0.130;; esac; }

# Cada computador tem um processo "init" (python3) dono dos namespaces dele (rede, nome, montagens,
# processos). "entra" roda um comando como root lá dentro, com nsenter.
# o "init" de cada computador: só espera e recolhe os processos que terminam
# o "init" de cada computador: só espera e recolhe os processos que terminam
INIT='import os, signal
signal.signal(signal.SIGCHLD, lambda *a: None)
while True:
    try:
        os.waitpid(-1, 0)
    except ChildProcessError:
        signal.pause()'
liga() { # ns
  local ns="$1" r="$LAB/rt/$1"
  ( ip netns exec "$ns" unshare --pid --fork --mount-proc --uts --mount --propagation private sh -c "
    hostname $ns
    for d in home root etc/ssh etc/fail2ban tmp run var/log etc/update-motd.d; do mount --bind $r/\$(echo \$d | tr / _) /\$d; done
    mount --bind $r/hosts /etc/hosts; mount --bind $r/motd /etc/motd; mount --bind $r/sudoers.d /etc/sudoers.d
    exec python3 -c \"$INIT\"" </dev/null >/dev/null 2>&1 &
    echo $! >"$LAB/rt/$ns.pai" )
  local pai filho=""; pai=$(cat "$LAB/rt/$ns.pai"); rm -f "$LAB/rt/$ns.pai"
  for _ in $(seq 100); do filho=$(pgrep -P "$pai" || true); [ -n "$filho" ] && break; sleep 0.02; done
  [ -n "$filho" ] || { echo "não consegui ligar $ns" >&2; exit 1; }
  echo "$filho" >"$LAB/rt/$ns.pid"
}
desliga() { # ns
  local f="$LAB/rt/$1.pid"
  if [ -f "$f" ]; then kill -9 "$(cat "$f")" 2>/dev/null || true; rm -f "$f"; fi
  local p; p=$(ip netns pids "$1" 2>/dev/null || true); [ -n "$p" ] && kill -9 $p 2>/dev/null || true
  return 0
}
entra() {
  nsenter -t "$(cat "$LAB/rt/$1.pid")" -m -u -n -p -i --wd=/ sh -c "$2"
}

modelos() {
  local t="$LAB/tpl"
  rm -rf "$t"; mkdir -p "$t"
  for ns in $NS; do
    local b="$t/$ns"; mkdir -p "$b"/{home,root,etc_ssh,etc_fail2ban,tmp,run/sshd,var_log,etc_update-motd.d,sudoers.d}
    chmod 1777 "$b/tmp"; chmod 755 "$b/run/sshd"; chmod 750 "$b/sudoers.d"
    cp -a /etc/ssh/ssh_config /etc/ssh/ssh_config.d /etc/ssh/moduli "$b/etc_ssh/"
    printf '127.0.0.1\tlocalhost\n127.0.1.1\t%s\n' "$ns" >"$b/hosts"
    : >"$b/motd"
  done
  printf '192.168.0.20\tservidor\n' >>"$t/notebook/hosts"
  printf '192.168.0.130\tinterno\n' >>"$t/servidor/hosts"
  printf '\nServidor de laboratório do Guia SSH. Tudo aqui é de teste.\n\n' >"$t/servidor/motd"
  printf '\nMáquina interna (só acessível pelo servidor).\n\n' >"$t/interno/motd"
  # servidores: sshd_config de fábrica do Debian e chaves de host novas, só do laboratório
  for ns in servidor interno; do
    local b="$t/$ns"
    cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.d "$b/etc_ssh/"
    find "$b/etc_ssh/sshd_config.d" -type f -delete
    for k in ed25519 ecdsa rsa; do ssh-keygen -q -t $k -N '' -C "root@$ns" -f "$b/etc_ssh/ssh_host_${k}_key"; done
    printf 'module(load="imuxsock" SysSock.Name="/run/systemd/journal/dev-log")\n$FileOwner root\n$FileGroup adm\n$FileCreateMode 0640\nauth,authpriv.*\t/var/log/auth.log\n' >"$b/etc_ssh/.rsyslog-lab.conf"
    cp -a /etc/fail2ban/. "$b/etc_fail2ban/"
    printf '[DEFAULT]\ndbfile = :memory:\n' >"$b/etc_fail2ban/fail2ban.local"
    printf '[sshd]\nenabled = true\nbackend = polling\nlogpath = /var/log/auth.log\nmaxretry = 3\nfindtime = 10m\nbantime = 10m\n' >"$b/etc_fail2ban/jail.local"
    printf 'lab ALL=(ALL) NOPASSWD: ALL\n' >"$b/sudoers.d/lab"; chmod 440 "$b/sudoers.d/lab"
    mkdir -p "$b/home/lab"
    printf "PS1='\\\\u@\\\\h:\\\\w\\\\\$ '\nexport LANG=pt_BR.UTF-8\n" >"$b/home/lab/.bashrc"
    printf '[ -f ~/.bashrc ] && . ~/.bashrc\n' >"$b/home/lab/.profile"
    printf 'set enable-bracketed-paste off\n' >"$b/home/lab/.inputrc"
    cp "$b/home/lab/.inputrc" "$b/root/.inputrc"
    printf "PS1='\\\\u@\\\\h:\\\\w\\\\\$ '\n" >"$b/root/.bashrc"
    chown -R lab:lab "$b/home/lab"
  done
  ( cd "$t/servidor/home/lab" && bash "$RAIZ/arquivos/preparar-servidor.sh" . >/dev/null )
  mkdir -p "$t/interno/home/lab/wiki"
  echo '<h1>Wiki interna</h1><p>Só a rede interna enxerga esta página.</p>' >"$t/interno/home/lab/wiki/index.html"
  chown -R lab:lab "$t/servidor/home/lab" "$t/interno/home/lab"
  # notebook: a pasta da ana com os arquivos de exemplo
  local h="$t/notebook/home/ana"; mkdir -p "$h"
  printf "PS1='\\\\u@\\\\h:\\\\w\\\\\$ '\n" >"$h/.bashrc"
  ( cd "$h" && bash "$RAIZ/arquivos/preparar-notebook.sh" . >/dev/null )
  chown -R ana:ana "$h"
  # chave da ana e known_hosts prontos (estados chave/config), gerados dentro do notebook
  mkdir -p "$LAB/rt"; desliga notebook; rm -rf "$LAB/rt/notebook"; cp -a "$t/notebook" "$LAB/rt/notebook"; liga notebook
  entra notebook "setpriv --reuid ana --regid ana --init-groups env HOME=/home/ana ssh-keygen -q -t ed25519 -N '' -f /home/ana/.ssh/id_ed25519 </dev/null >/dev/null"
  mkdir -p "$t/chave"; cp -a "$LAB/rt/notebook/home/ana/.ssh/id_ed25519" "$LAB/rt/notebook/home/ana/.ssh/id_ed25519.pub" "$t/chave/"
  { printf 'servidor '; cut -d' ' -f1,2 "$t/servidor/etc_ssh/ssh_host_ed25519_key.pub"; printf '192.168.0.20 '; cut -d' ' -f1,2 "$t/servidor/etc_ssh/ssh_host_ed25519_key.pub"; printf '192.168.0.130 '; cat "$t/interno/etc_ssh/ssh_host_ed25519_key.pub" | cut -d' ' -f1,2; printf 'interno '; cat "$t/interno/etc_ssh/ssh_host_ed25519_key.pub" | cut -d' ' -f1,2; } >"$t/chave/known_hosts.claro"
}

rede() {
  for ns in $NS; do ip netns del "$ns" 2>/dev/null || true; ip netns add "$ns"; ip -n "$ns" link set lo up
    ip netns exec "$ns" sysctl -q -w net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1 net.ipv4.ping_group_range="0 2147483647" net.ipv6.conf.lo.disable_ipv6=0; done
  ip link add nb0 netns notebook type veth peer name sv0 netns servidor
  ip link add sv1 netns servidor type veth peer name in0 netns interno
  ip -n notebook link set nb0 address 02:00:00:00:00:10; ip -n servidor link set sv0 address 02:00:00:00:00:20
  ip -n servidor link set sv1 address 02:00:00:00:00:21; ip -n interno link set in0 address 02:00:00:00:00:30
  ip -n notebook addr add 192.168.0.10/25 dev nb0; ip -n servidor addr add 192.168.0.20/25 dev sv0
  ip -n servidor addr add 192.168.0.129/25 dev sv1; ip -n interno addr add 192.168.0.130/25 dev in0
  ip -n notebook link set nb0 up; ip -n servidor link set sv0 up; ip -n servidor link set sv1 up; ip -n interno link set in0 up
}

para_tudo() {
  for ns in $NS; do desliga "$ns"; done
  sleep 0.1
}

espera_porta() { # ns porta
  for _ in $(seq 100); do ip netns exec "$1" ss -ltnH "sport = :$2" | grep -q . && return 0; sleep 0.05; done
  echo "porta $2 não abriu em $1" >&2; return 1
}

sobe_servicos() {
  for ns in servidor interno; do
    # o rsyslog do laboratório recebe o log do sshd no /dev/log do computador e grava /var/log/auth.log
    entra "$ns" "mkdir -p /run/systemd/journal && rsyslogd -f /etc/ssh/.rsyslog-lab.conf -i /run/rsyslogd.pid && for i in \$(seq 50); do [ -S /run/systemd/journal/dev-log ] && break; sleep 0.05; done && /usr/sbin/sshd"
    espera_porta "$ns" 22
  done
  entra servidor "cd /home/lab/site && setsid setpriv --reuid lab --regid lab --init-groups python3 -m http.server -b 127.0.0.1 8080 >/dev/null 2>&1 </dev/null &"
  entra interno "cd /home/lab/wiki && setsid python3 -m http.server -b 0.0.0.0 80 >/dev/null 2>&1 </dev/null &"
  entra notebook "cd /home/ana/site && setsid setpriv --reuid ana --regid ana --init-groups python3 -m http.server -b 127.0.0.1 3000 >/dev/null 2>&1 </dev/null &"
  espera_porta servidor 8080; espera_porta interno 80; espera_porta notebook 3000
}

estado() { # zero | conhecido | chavelocal | chave | config  (cada um inclui o anterior)
  local e="$1" t="$LAB/tpl"
  para_tudo
  for ns in $NS; do rm -rf "$LAB/rt/$ns"; cp -a "$t/$ns" "$LAB/rt/$ns"; liga "$ns"; done
  local s="$LAB/rt/notebook/home/ana/.ssh"
  case "$e" in zero) ;; conhecido|chavelocal|chave|config)
    install -d -o ana -g ana -m 700 "$s"
    install -o ana -g ana -m 600 "$t/chave/known_hosts.claro" "$s/known_hosts"
    entra notebook "setpriv --reuid ana --regid ana --init-groups env HOME=/home/ana ssh-keygen -q -H -f /home/ana/.ssh/known_hosts >/dev/null 2>&1; rm -f /home/ana/.ssh/known_hosts.old"
    ;; *) echo "estado desconhecido: $e" >&2; exit 2;; esac
  case "$e" in chavelocal|chave|config)
    install -o ana -g ana -m 600 "$t/chave/id_ed25519" "$s/id_ed25519"
    install -o ana -g ana -m 644 "$t/chave/id_ed25519.pub" "$s/id_ed25519.pub";; esac
  case "$e" in chave|config)
    for ns in servidor interno; do local d="$LAB/rt/$ns/home/lab/.ssh"
      install -d -o lab -g lab -m 700 "$d"; install -o lab -g lab -m 600 "$t/chave/id_ed25519.pub" "$d/authorized_keys"; done
    ;; esac
  if [ "$e" = config ]; then
    printf 'Host servidor\n    HostName 192.168.0.20\n    User lab\n\nHost interno\n    HostName 192.168.0.130\n    User lab\n    ProxyJump servidor\n' >"$s/config"
    chown ana:ana "$s/config"; chmod 600 "$s/config"
  fi
  sobe_servicos
}

subir() {
  id ana >/dev/null 2>&1 || { useradd -M -d /home/ana -s /bin/bash ana; echo ana >>"$LAB.criados"; }
  id lab >/dev/null 2>&1 || { useradd -M -d /home/lab -s /bin/bash lab; echo lab >>"$LAB.criados"; }
  echo "lab:$SENHA_LAB" | chpasswd
  mkdir -p "$LAB"; chmod 700 "$LAB"
  mkdir -p "$LAB/rt"; para_tudo; rede; modelos; estado zero
  echo "laboratório no ar"
}

descer() {
  para_tudo
  for ns in $NS; do ip netns del "$ns" 2>/dev/null || true; done
  if [ -f "$LAB.criados" ]; then
    while read -r u; do
      # espera os processos do usuário terminarem (o userdel recusa usuário em uso)
      for _ in $(seq 50); do pgrep -u "$u" >/dev/null || break; sleep 0.1; done
      userdel "$u" || echo "não consegui apagar o usuário $u" >&2
    done <"$LAB.criados"
    rm -f "$LAB.criados"
  fi
  rm -rf "$LAB"
  echo "laboratório desmontado"
}

case "${1:-}" in
  subir) subir;; descer) descer;; estado) estado "${2:?estado}";; entra) entra "$2" "$3";;
  *) echo "uso: sudo bash tools/lab.sh subir|estado NOME|descer" >&2; exit 2;;
esac
