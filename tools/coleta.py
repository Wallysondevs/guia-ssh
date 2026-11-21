#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""coleta.py — roda de verdade, no laboratório (tools/lab.sh), os comandos de todas as caixas.

  sudo python3 tools/coleta.py            (todas as caixas de tools/comandos.txt)
  sudo python3 tools/coleta.py tunel-     (só as caixas cujo id começa com o prefixo)

Para cada caixa ("### id" em tools/comandos.txt, com a linha "#@ {...}" de opções):
  1. volta o laboratório ao estado pedido (zero, conhecido, chave, config) e roda
     os preparos escondidos ("prep");
  2. abre um Bash interativo num terminal de verdade (pty), no computador pedido
     (notebook como ana; servidor ou interno como lab), e digita um comando por vez,
     respondendo às perguntas do ssh (yes/no, senha) quando elas aparecem ("resp");
  3. grava o que o terminal mostrou em _saidas/<id>.json e a cópia conferida em
     _saidas-anon/<id>.json (nenhuma das duas vai para o git).
"""
import json, os, pty, re, select, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB = ["bash", str(ROOT / "tools" / "lab.sh")]
USU = {"notebook": "ana", "servidor": "lab", "interno": "lab"}
SENT = re.compile(rb"\x1e(\d+)\x1e\r?\n")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|\x1b[=>]")
FILTRO = sys.argv[1] if len(sys.argv) > 1 else ""

def proibidos():
    p = []
    lista = Path(os.environ.get("PROIBIDO", str(ROOT.parent / "lista.txt")))
    if lista.exists():
        for l in lista.read_text(encoding="utf-8").splitlines():
            if l and not l.startswith("#"):
                p.append(l)
    p += ["BEGIN OPENSSH " + "PRIVATE KEY", "/srv/guia-ssh-lab", os.uname().nodename]
    return p
PROIB = proibidos()

def confere(bid, txt):
    for pad in PROIB:
        if pad.startswith("re:"):
            if re.search(pad[3:], txt, re.I):
                raise SystemExit("caixa %s: saída tem %r\n%s" % (bid, pad, txt))
        elif pad.lower() in txt.lower():
            raise SystemExit("caixa %s: saída tem %r\n%s" % (bid, pad, txt))

def limpa(b):
    t = b.decode("utf-8", "replace")
    t = ANSI.sub("", t).replace("\x07", "")
    linhas = []
    for l in t.replace("\r\n", "\n").split("\n"):
        if "\r" in l:
            partes = [x for x in l.split("\r") if x != ""]
            l = partes[-1] if partes else ""
        linhas.append(l)
    return "\n".join(linhas)

class Sessao:
    def __init__(self, ns):
        u = USU[ns]
        inner = ("cd /home/%s && exec setpriv --reuid %s --regid %s --init-groups env -i HOME=/home/%s USER=%s LOGNAME=%s "
                 "SHELL=/bin/bash PATH=/usr/local/bin:/usr/bin:/bin LANG=pt_BR.UTF-8 TERM=dumb "
                 "bash --norc --noprofile --noediting -i" % (u, u, u, u, u, u))
        pid, fd = pty.fork()
        if pid == 0:
            os.execvp(LAB[0], LAB + ["entra", ns, inner])
        self.pid, self.fd = pid, fd
        import fcntl, termios, struct
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 100, 0, 0))
        self.buf = b""
        self.escreve("stty cols 100 rows 40; PS1=''; PS2=''; PROMPT_COMMAND='printf \"\\036%d\\036\\n\" $?'\n")
        self.espera(None, [], 15)

    def escreve(self, s):
        os.write(self.fd, s.encode("utf-8"))

    def espera(self, bid, resp, limite):
        fim = time.time() + limite
        visto = 0
        while True:
            m = SENT.search(self.buf)
            if m:
                out = self.buf[:m.start()]; self.buf = self.buf[m.end():]
                return out, int(m.group(1))
            if resp:
                alvo, texto = resp[0]
                mm = re.search(alvo.encode("utf-8"), self.buf[visto:])
                if mm:
                    visto += mm.end()
                    time.sleep(0.15)
                    self.escreve(texto)
                    resp.pop(0)
                    continue
            r, _, _ = select.select([self.fd], [], [], 0.2)
            if r:
                try:
                    d = os.read(self.fd, 65536)
                except OSError:
                    d = b""
                if not d:
                    raise SystemExit("caixa %s: o terminal fechou\n%s" % (bid, limpa(self.buf)))
                self.buf += d
            if time.time() > fim:
                raise SystemExit("caixa %s: tempo esgotado esperando %r\n%s" % (bid, resp[:1], limpa(self.buf)))

    def fecha(self):
        try:
            self.escreve("exit\n"); time.sleep(0.1)
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass

def roda_caixa(bid, op, cmds):
    if op.get("estado", "chave") != "continua":
        subprocess.run(LAB + ["estado", op.get("estado", "chave")], check=True, stdout=subprocess.DEVNULL)
    for ns, quem, c in op.get("prep", []):
        if quem != "root":
            c = "cd ~ && " + c
            c = "setpriv --reuid %s --regid %s --init-groups env HOME=/home/%s LANG=pt_BR.UTF-8 bash -c %s" % (quem, quem, quem, json.dumps(c))
        r = subprocess.run(LAB + ["entra", ns, c], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode:
            raise SystemExit("caixa %s: prep falhou: %s\n%s" % (bid, c, r.stdout.decode()))
    s = Sessao(op.get("quem", "notebook"))
    resp = [list(x) for x in op.get("resp", [])]
    res = []
    try:
        for c in cmds:
            s.escreve(c + "\n")
            out, cod = s.espera(bid, resp, op.get("tempo", 30))
            t = limpa(out)
            if t.startswith(c + "\n"):
                t = t[len(c) + 1:]
            else:
                raise SystemExit("caixa %s: eco inesperado do comando %r\n%s" % (bid, c, t))
            confere(bid, t)
            res.append({"cmd": c, "out": t, "status": cod})
    finally:
        s.fecha()
    if resp:
        raise SystemExit("caixa %s: respostas não usadas: %r" % (bid, resp))
    for pasta in ("_saidas", "_saidas-anon"):
        (ROOT / pasta).mkdir(exist_ok=True)
        (ROOT / pasta / (bid + ".json")).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("coletada: %s (%d comando(s))" % (bid, len(cmds)), flush=True)

def main():
    caixas, bid, op, cmds = [], None, {}, []
    for l in (ROOT / "tools" / "comandos.txt").read_text(encoding="utf-8").splitlines():
        if l.startswith("### "):
            if bid: caixas.append((bid, op, cmds))
            bid, op, cmds = l[4:], {}, []
        elif l.startswith("#@ "):
            op = json.loads(l[3:])
        elif l.strip() and not l.startswith("# ") and bid:
            cmds.append(l)
    if bid: caixas.append((bid, op, cmds))
    for bid, op, cmds in caixas:
        if FILTRO and not bid.startswith(FILTRO):
            continue
        roda_caixa(bid, op, cmds)
    u = os.environ.get("SUDO_UID"); g = os.environ.get("SUDO_GID")
    if u:
        subprocess.run(["chown", "-R", "%s:%s" % (u, g), str(ROOT / "_saidas"), str(ROOT / "_saidas-anon")])

if __name__ == "__main__":
    main()
