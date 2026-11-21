# -*- coding: utf-8 -*-
"""Ajudantes das aulas do Guia SSH (caixas de terminal, missões, exercícios). Usado por tools/gerar.py."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODO = "paginas"  # o gerar.py troca
BLOCOS = {}   # id -> lista de comandos (ordem de registro)
ORDEM = []

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def registra(bid, cmds, op):
    item = {"cmds": list(cmds), "op": op}
    if bid in BLOCOS:
        if BLOCOS[bid] != item:
            raise SystemExit("bloco repetido com comandos diferentes: " + bid)
        return
    BLOCOS[bid] = item; ORDEM.append(bid)

def opcoes(estado="chave", quem="notebook", resp=None, prep=None, tempo=None):
    op = {"estado": estado, "quem": quem}
    if resp: op["resp"] = [list(x) for x in resp]
    if prep: op["prep"] = [list(x) for x in prep]
    if tempo: op["tempo"] = tempo
    return op

def coleta(bid):
    f = ROOT / "_saidas-anon" / (bid + ".json")
    if not f.exists():
        raise SystemExit("falta a coleta de " + bid + " (rode sudo python3 tools/coleta.py " + bid + ")")
    d = json.loads(f.read_text(encoding="utf-8"))
    if [x["cmd"] for x in d] != BLOCOS[bid]["cmds"]:
        raise SystemExit("coleta desatualizada para " + bid + " (rode sudo python3 tools/coleta.py " + bid + ")")
    return d

def saida_txt(o):
    o = o.rstrip("\n")
    return o

PROIBIDO_INICIO = re.compile(r"^(\$|#>)( |$)|^[A-Z]:\\|^PS ")
CHAVE_PRIVADA = re.compile(r"-----(BEGIN|END) [A-Z ]*PRIVATE KEY|PRIVATE KEY-----")

def confere_linhas(bid, linhas):
    for k, l in enumerate(linhas):
        if ("/tmp/" in l and "/tmp/ssh-" not in l) or "guia-ssh-lab" in l or "/srv/" in l:
            raise SystemExit("saída de %s mostra caminho da máquina de coleta: %r" % (bid, l))
        if CHAVE_PRIVADA.search(l):
            raise SystemExit("saída de %s mostra o começo de uma chave privada: %r" % (bid, l))
        if PROIBIDO_INICIO.search(l) or "«" in l:
            raise SystemExit("saída de %s tem linha que o desenhista do terminal confundiria: %r" % (bid, l))
        if k == 0 and re.match(r"^> ?", l):
            raise SystemExit("saída de %s começa com '>' (seria lida como continuação): %r" % (bid, l))

QUEM = {"notebook": ("ana", "notebook"), "servidor": ("lab", "servidor"), "interno": ("lab", "interno")}

def T(bid, *cmds, notas=None, titulo=None, estado="chave", quem="notebook", resp=None, prep=None, tempo=None):
    """Caixa de terminal com comandos e saídas reais. notas = {trecho_da_linha: etiqueta}."""
    registra(bid, cmds, opcoes(estado, quem, resp, prep, tempo))
    if MODO != "paginas":
        return ""
    d = coleta(bid)
    notas = dict(notas or {})
    linhas = []
    for x in d:
        linhas.append("$ " + x["cmd"])
        out = saida_txt(x["out"])
        if out != "":
            ols = out.split("\n")
            confere_linhas(bid, ols)
            for l in ols:
                for trecho in list(notas):
                    if trecho in l:
                        l = l + "   « " + notas.pop(trecho)
                        break
                linhas.append(l)
    if notas:
        raise SystemExit("nota sem linha em %s: %r" % (bid, list(notas)))
    linhas.append("$")
    tit = ' data-title="%s"' % esc(titulo) if titulo else ""
    u, h = QUEM[quem]
    ext = "" if quem == "notebook" else ' data-user="%s" data-host="%s"' % (u, h)
    return '<pre class="term" data-cwd="~"%s%s>%s</pre>' % (ext, tit, esc("\n".join(linhas)))

def saida_de(bid):
    d = coleta(bid)
    return "\n".join(saida_txt(x["out"]) for x in d if saida_txt(x["out"]) != "")

def M(bid, tarefa, cmds, goal, script="", estado="chave", quem="notebook", resp=None, prep=None, tempo=None):
    """Missão 'cole a saída'. goal: metas separadas por ;; (src:, out:, outre:, erro:, semerro)."""
    if isinstance(cmds, str):
        cmds = [cmds]
    registra(bid, cmds, opcoes(estado, quem, resp, prep, tempo))
    if MODO != "paginas":
        return ""
    goal = ";;".join((m.replace('\\"', '"') if m.split(":", 1)[0] in ("out", "erro") else m) for m in goal.split(";;"))
    saida = saida_de(bid)
    confere_linhas(bid, saida.split("\n"))
    sol = "\n".join(cmds)
    for meta in goal.split(";;"):
        tipo, _, val = meta.partition(":")
        if tipo in ("out", "erro") and val not in saida:
            raise SystemExit("missão %s: a saída real não tem %r\n---\n%s" % (bid, val, saida))
        if tipo in ("out", "erro") and val in sol:
            raise SystemExit("missão %s: a meta %r também aparece no próprio comando (falso positivo)" % (bid, val))
        if tipo == "outre" and ("\\A" in val or "\\Z" in val):
            raise SystemExit("missão %s: \\A e \\Z não existem na regex do JavaScript" % bid)
        if tipo == "outre" and not re.search(val, saida, re.M):
            raise SystemExit("missão %s: a saída real não casa com %r\n---\n%s" % (bid, val, saida))
        if tipo == "outre" and re.search(val, sol, re.M):
            raise SystemExit("missão %s: a meta %r casa com o próprio comando (falso positivo)" % (bid, val))
        if tipo == "src" and not re.search(val, sol, re.M):
            raise SystemExit("missão %s: a solução não cumpre src %r" % (bid, val))
    if not re.search(r"(^|;;)(out|outre|erro):", goal):
        raise SystemExit("missão %s precisa de meta out/outre/erro" % bid)
    if saida.strip() == "":
        raise SystemExit("missão %s sem saída real" % bid)
    u, h = QUEM[quem]
    onde = "" if quem == "notebook" else ' <span class="onde">(rode no <strong>%s</strong>, como <code>%s</code>)</span>' % (h, u)
    return "\n".join([
        '<div class="trycmd" data-goal="%s">' % esc(goal),
        '<p class="try-task"><strong>Missão:</strong> %s%s</p>' % (tarefa, onde),
        '<pre class="script" data-file="comandos.sh">\n%s\n</pre>' % esc(script),
        '<pre class="solucao" data-file="comandos.sh">\n%s\n</pre>' % esc(sol),
        '<pre class="saida-ok" data-file="comandos.sh" hidden>\n%s\n</pre>' % esc(saida),
        "</div>"])

def ANAT(*pares):
    return '<dl class="anatomy">' + "".join("<dt>%s</dt><dd>%s</dd>" % (esc(a), b) for a, b in pares) + "</dl>"

def REF(linhas, cab=("Você digita", "O que faz")):
    h = '<div class="table-wrap"><table class="ref">\n<tr><th>%s</th><th>%s</th></tr>\n' % cab
    for a, b in linhas:
        h += "<tr><td><code>%s</code></td><td>%s</td></tr>\n" % (esc(a), b)
    return h + "</table></div>"

def EX(n, titulo, texto, antes, resposta, depois="", rotulo="resposta"):
    resp = "|".join(r.replace("|", "\\|") for r in ([resposta] if isinstance(resposta, str) else resposta))
    return ('<div class="exercise"><h3>%d. %s</h3><p>%s</p><div class="ex-code">%s<input data-answer="%s" aria-label="%s">%s</div></div>'
            % (n, titulo, texto, esc(antes), esc(resp), esc(rotulo), esc(depois)))

_mc = [0]
def MC(n, pergunta, opcoes, certa):
    _mc[0] += 1
    nome = "q%d" % n
    h = '<div class="mc" data-answer="%d"><p class="mc-q">%d. %s</p>\n' % (certa, n, pergunta)
    h += "\n".join('<label><input type="radio" name="%s"> %s</label>' % (nome, o) for o in opcoes)
    return h + "</div>"

def caixa(cls, titulo, corpo):
    return '<div class="%s"><strong>%s</strong>\n%s</div>' % (cls, titulo, corpo)

def CEN(titulo, texto, term, depois=""):
    return '<div class="cenario"><strong>%s</strong>\n<p>%s</p>\n%s\n%s</div>' % (titulo, texto, term, ("<p>%s</p>" % depois) if depois else "")

OPENSSH = "OpenSSH 10.0p2"
PASTA = ('<p class="pasta-teste">Todas as saídas desta aula foram colhidas de verdade com o <strong>' + OPENSSH + ' no Linux</strong> '
         '(Debian 13, Bash 5.2, <code>pt_BR.UTF-8</code>), no <a href="preparando.html">laboratório do guia</a>: o <code>notebook</code> '
         '(usuária <code>ana</code>, 192.168.0.10), o <code>servidor</code> (usuário <code>lab</code>, 192.168.0.20) e o <code>interno</code> '
         '(192.168.0.130, que só o servidor alcança). Antes de cada caixa o laboratório volta a um estado conhecido. As chaves e as '
         'impressões digitais que aparecem são de teste e já foram destruídas.</p>')

HEAD = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
<script>try{{var t=localStorage.getItem("tema");if(t)document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
</head>
<body>
<div class="layout">
<nav class="sidebar" id="sidebar" aria-label="Tópicos"></nav>
<main class="main">
<div class="content">

<div class="pager"></div>

'''
FOOT = '''

<div class="pager"></div>

</div>
</main>
</div>
<script src="assets/site.js"></script>
</body>
</html>
'''

def pagina_aula(a):
    corpo = []
    corpo.append("<h1>%s</h1>" % a["h1"])
    corpo.append('<p class="intro">%s</p>' % a["intro"])
    corpo.append('<div class="note"><strong>Você vai aprender</strong><ul>\n%s\n</ul></div>' % "\n".join("<li>%s</li>" % x for x in a["aprender"]))
    if a.get("pasta", True):
        corpo.append(PASTA)
    corpo.append("<hr>")
    corpo.append(a["corpo"]())
    if a.get("ref"):
        corpo.append("<hr>\n<h2>Referência rápida</h2>\n" + REF(a["ref"]))
    corpo.append("<hr>\n<h2>Exercícios</h2>\n" + a["exercicios"]())
    corpo.append("<hr>\n<h2>Missões</h2>\n<p>Rode no seu laboratório (o seu notebook e o seu servidor de teste) e cole o que o terminal respondeu. O botão <strong>Conferir</strong> compara com o que a saída real precisa ter.</p>\n" + a["missoes"]())
    corpo.append("<hr>\n<h2>Resumo</h2>\n<ul>\n%s\n</ul>" % "\n".join("<li>%s</li>" % x for x in a["resumo"]))
    return HEAD.format(title=esc(a["title"] + " | Guia SSH"), desc=esc(a["desc"])) + "\n\n".join(corpo) + FOOT

