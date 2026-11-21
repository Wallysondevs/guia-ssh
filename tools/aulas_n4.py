# -*- coding: utf-8 -*-
"""Nível 4 · Túneis e saltos: -L, -R, -D, ProxyJump e túneis no config."""
from lib_guia import *
from respostas import *

def aula(**k):
    return k

SEGUNDO_PLANO = '<div class="note"><strong>-f e -N</strong><p><code>-N</code>: não roda comando nenhum, só mantém o túnel. <code>-f</code>: vai para o segundo plano depois de conectar, devolvendo o terminal. Para fechar, use <code>pkill -f "ssh -f -N"</code> (ou o <code>kill</code> com o número do processo).</p></div>'

# ---------------------------------------------------------------- túnel local
def tl_corpo():
    return f"""
<h2>A ideia: trazer uma porta do servidor para o notebook</h2>
<p>O servidor tem um painel web que só escuta em <code>127.0.0.1:8080</code>, ou seja, só abre <strong>de dentro</strong> do próprio servidor. É assim, de propósito, com muitos painéis e bancos de dados. Um <strong>túnel local</strong> (<code>-L</code>) abre uma porta no notebook e leva tudo o que chega nela, por dentro do SSH, até o servidor.</p>
<pre class="cmd">
ssh -L porta_no_notebook:destino:porta_do_destino usuario@servidor
</pre>
<p>O <code>destino</code> é visto <strong>a partir do servidor</strong>: <code>localhost</code> ali quer dizer “o próprio servidor”.</p>
<hr>
<h2>1. Antes do túnel</h2>
{T("tl-antes", "curl -sS http://localhost:8080/", "ssh lab@servidor 'curl -s http://localhost:8080/'", notas={"Could not connect": "no notebook, nada na porta 8080", "Painel do servidor": "no servidor, o painel responde"})}
<hr>
<h2>2. Abrindo o túnel</h2>
{T("tl-abrir", "ssh -f -N -L 8080:localhost:8080 lab@servidor", "curl -s http://localhost:8080/", "ss -ltn | grep 8080", notas={"Painel do servidor": "o painel, aberto no notebook", "127.0.0.1:8080": "a porta do túnel, só no notebook"})}
{SEGUNDO_PLANO}
<p>No navegador do notebook, <code>http://localhost:8080</code> abre o painel. A porta local não precisa ser igual à remota:</p>
{T("tl-porta", "ssh -f -N -L 9000:localhost:8080 lab@servidor", "curl -s http://localhost:9000/")}
<div class="tip"><strong>Só no notebook</strong><p>Por padrão, a porta do túnel escuta só em <code>127.0.0.1</code>: outras máquinas da sua rede não a enxergam. Mais seguro assim.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A porta já está em uso", "Abrir o mesmo túnel duas vezes (ou numa porta que outro programa usa) não funciona. O ssh avisa, mas a conexão continua, sem túnel:", T("tl-erro", "ssh -f -N -L 8080:localhost:8080 lab@servidor", "ssh -f -N -L 8080:localhost:8080 lab@servidor"), "Escolha outra porta local, ou feche o túnel antigo. Em scripts, use <code>-o ExitOnForwardFailure=yes</code>, que faz o ssh desistir (aula <a href='tuneis-config.html'>Túneis no config</a>).")}
"""

def tl_ex():
    return (EX(1, "Túnel local", "Que opção abre um túnel local?", "ssh ", "-L", " 8080:localhost:8080 lab@servidor", rotulo="opção") +
            EX(2, "Só o túnel", "Que opção diz “não rode comando, só mantenha o túnel”?", "ssh -f ", "-N", " -L 8080:localhost:8080 lab@servidor", rotulo="opção") +
            MC(3, "Em <code>-L 8080:localhost:8080</code>, o segundo <code>localhost</code> é:", ["o notebook", "o servidor (visto de lá)", "a internet", "o roteador"], 2) +
            MC(4, "A porta do túnel local, por padrão, escuta em:", ["todas as placas de rede", "só 127.0.0.1 do notebook", "no servidor", "na internet"], 2))

def tl_miss():
    return (M("tl-m1", "abra um túnel até o painel do servidor e baixe a página pelo túnel.", "ssh -f -N -L 8080:localhost:8080 lab@servidor && curl -s http://localhost:8080/", r"src:-L 8080:localhost:8080;;out:Painel do servidor") +
            M("tl-m2", "abra o túnel e mostre a porta 8080 escutando no notebook.", "ssh -f -N -L 8080:localhost:8080 lab@servidor && ss -ltn | grep ':8080 '", r"src:-L;;src:ss -ltn;;outre:^LISTEN\s.*127\.0\.0\.1:8080\s"))

# ---------------------------------------------------------------- túnel para outra máquina
def tr_corpo():
    return f"""
<h2>A ideia: o servidor como ponte</h2>
<p>O destino do <code>-L</code> não precisa ser o próprio servidor: pode ser <strong>qualquer máquina que o servidor alcance</strong>. No laboratório, a máquina <code>interno</code> (192.168.0.130) tem uma wiki na porta 80, mas fica numa rede que o notebook não enxerga. O servidor enxerga.</p>
<hr>
<h2>1. O notebook não chega lá</h2>
{T("tr-direto", "curl -sS --max-time 3 http://192.168.0.130/", "ssh lab@servidor 'curl -s http://192.168.0.130/'", notas={"Wiki interna": "do servidor, abre"})}
<hr>
<h2>2. Pelo túnel</h2>
{T("tr-tunel", "ssh -f -N -L 8081:192.168.0.130:80 lab@servidor", "curl -s http://localhost:8081/", notas={"Wiki interna": "do notebook, pelo servidor"})}
<p>O caminho: notebook (porta 8081) → SSH criptografado até o servidor → o servidor abre uma conexão comum até 192.168.0.130:80. Esse último trecho, dentro da rede do servidor, <strong>não</strong> é criptografado pelo SSH.</p>
<hr>
<h2>3. Um túnel até o próprio SSH</h2>
<p>O destino pode ser até outro servidor SSH. Aqui, a porta 2200 do notebook leva à porta 22 do <code>interno</code>, e o ssh entra por ela:</p>
{T("tr-ssh", "ssh -f -N -L 2200:192.168.0.130:22 lab@servidor", "ssh -p 2200 -o HostKeyAlias=interno lab@localhost hostname", notas={"interno": "entrou no interno pelo túnel"})}
<p>O <code>HostKeyAlias=interno</code> diz ao ssh para conferir a chave como sendo a do <code>interno</code>, e não a de “localhost”. Para isso existe um jeito bem mais simples, o <a href="proxyjump.html">ProxyJump</a>.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("O servidor também não alcança", "Se nem o servidor chega ao destino, o túnel abre, mas cada conexão falha lá na ponta. O ssh avisa no terminal em que o túnel foi aberto:", T("tr-erro", "ssh -f -N -L 8082:192.168.0.140:80 lab@servidor", "curl -sS --max-time 5 http://localhost:8082/"), "“connect failed” vem do servidor: confira, nele, se o destino responde (<code>ssh lab@servidor 'curl -s http://destino/'</code>).")}
"""

def tr_ex():
    return (EX(1, "Outra máquina", "Complete para levar a porta 8081 do notebook à porta 80 do 192.168.0.130:", "ssh -f -N -L 8081:", "192.168.0.130:80", " lab@servidor", rotulo="destino") +
            EX(2, "Porta do ssh", "Que opção do ssh escolhe a porta (para entrar pelo túnel)?", "ssh ", "-p", " 2200 lab@localhost", rotulo="opção") +
            MC(3, "No <code>-L</code>, o destino precisa ser alcançável:", ["pelo notebook", "pelo servidor", "pela internet", "por todos"], 2) +
            MC(4, "O trecho entre o servidor e o destino:", ["é criptografado pelo SSH", "não é criptografado pelo SSH", "não existe", "passa pelo notebook"], 2))

def tr_miss():
    return (M("tr-m1", "leve a porta 8082 do notebook até o painel do servidor (127.0.0.1:8080, visto de lá) e baixe a página.", "ssh -f -N -L 8082:127.0.0.1:8080 lab@servidor && curl -s http://localhost:8082/", r"src:-L 8082:127\.0\.0\.1:8080;;out:Painel do servidor") +
            M("tr-m2", "abra um túnel da porta 2201 até a porta 22 do servidor e entre por ele.", "ssh -f -N -L 2201:localhost:22 lab@servidor && ssh -p 2201 -o HostKeyAlias=servidor lab@localhost 'echo \"pelo túnel: $(hostname)\"'", r"src:-L 2201:localhost:22;;src:-p 2201;;outre:^pelo túnel: \S+$"))

# ---------------------------------------------------------------- túnel remoto
def rr_corpo():
    return f"""
<h2>A ideia: o contrário do -L</h2>
<p>O <strong>túnel remoto</strong> (<code>-R</code>) abre uma porta <strong>no servidor</strong> que leva até o notebook. Serve para mostrar algo que roda no seu computador (um site em desenvolvimento, por exemplo) a partir do servidor, sem abrir nada no seu roteador.</p>
<pre class="cmd">
ssh -R porta_no_servidor:destino:porta_do_destino usuario@servidor
</pre>
<p>Agora o <code>destino</code> é visto <strong>a partir do notebook</strong>. No laboratório, a Ana tem um site rodando no notebook, em <code>127.0.0.1:3000</code>.</p>
<hr>
<h2>1. Abrindo o túnel remoto</h2>
{T("rr-abrir", "curl -s http://localhost:3000/", "ssh -f -N -R 9000:localhost:3000 lab@servidor", "ssh lab@servidor 'curl -s http://localhost:9000/'", notas={"Site da Ana": "no notebook"})}
<p>A última linha rodou <strong>no servidor</strong> e trouxe a página do notebook.</p>
<hr>
<h2>2. Quem enxerga a porta</h2>
<p>No servidor, a porta 9000 escuta só em <code>127.0.0.1</code>: só quem já está dentro do servidor a usa. Para abrir para a rede do servidor, o administrador teria de ligar <code>GatewayPorts</code> no <code>sshd_config</code> (raramente uma boa ideia).</p>
{T("rr-porta", "ssh -f -N -R 9000:localhost:3000 lab@servidor", "ssh lab@servidor 'ss -ltn | grep 9000'", notas={"127.0.0.1:9000": "só dentro do servidor"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A porta do servidor está ocupada", "Se a porta já estiver em uso no servidor (aqui, por um túnel aberto antes), o servidor recusa e o ssh só avisa:", T("rr-erro", "ssh -f -N -R 9000:localhost:3000 lab@servidor", "ssh -f -N -R 9000:localhost:3000 lab@servidor"), "Use outra porta no servidor. Lá, <code>ss -ltn</code> mostra o que já está ocupado.")}
"""

def rr_ex():
    return (EX(1, "Túnel remoto", "Que opção abre uma porta no servidor que leva ao notebook?", "ssh -f -N ", "-R", " 9000:localhost:3000 lab@servidor", rotulo="opção") +
            EX(2, "No servidor", "Complete para baixar, no servidor, a página que veio pelo túnel:", "ssh lab@servidor 'curl -s http://localhost:", "9000", "/'", rotulo="porta") +
            MC(3, "No <code>-R 9000:localhost:3000</code>, o <code>localhost</code> é:", ["o servidor", "o notebook", "a internet", "o interno"], 2) +
            MC(4, "Por padrão, a porta de um <code>-R</code> no servidor escuta:", ["para toda a internet", "só em 127.0.0.1 do servidor", "no notebook", "em lugar nenhum"], 2))

def rr_miss():
    return (M("rr-m1", "com o seu site rodando na porta 3000, mostre-o a partir do servidor por um túnel remoto.", "ssh -f -N -R 9000:localhost:3000 lab@servidor && ssh lab@servidor 'curl -s http://localhost:9000/'", r"src:-R 9000:localhost:3000;;out:Site da Ana") +
            M("rr-m2", "abra um túnel remoto na porta 9001 e mostre, no servidor, que ela está escutando.", "ssh -f -N -R 9001:localhost:3000 lab@servidor && ssh lab@servidor \"ss -ltn | grep ':9001 '\"", r"src:-R 9001;;src:ss -ltn;;outre:^LISTEN\s.*127\.0\.0\.1:9001\s"))

# ---------------------------------------------------------------- túnel dinâmico
def td_corpo():
    return f"""
<h2>A ideia: um proxy para tudo</h2>
<p>O <code>-L</code> leva <strong>uma</strong> porta a <strong>um</strong> destino. O <strong>túnel dinâmico</strong> (<code>-D</code>) abre no notebook um <strong>proxy SOCKS</strong>: cada programa que usar o proxy diz aonde quer ir, e o servidor faz a conexão. É como se o notebook navegasse “de dentro” do servidor.</p>
<hr>
<h2>1. Abrir o proxy</h2>
{T("td-socks", "ssh -f -N -D 1080 lab@servidor", "curl -s --socks5-hostname localhost:1080 http://192.168.0.130/", "curl -s --socks5-hostname localhost:1080 http://localhost:8080/", "curl -s --socks5-hostname localhost:1080 http://interno/",
   notas={"Wiki interna": "a wiki, alcançada pelo servidor", "Painel do servidor": "localhost aqui é o servidor"})}
{ANAT(("-D 1080", "abre o proxy SOCKS na porta 1080 do notebook."), ("--socks5-hostname", "manda o curl usar o proxy e deixar o <strong>servidor</strong> traduzir os nomes."))}
<p>Repare na última linha: o nome <code>interno</code> só existe para o servidor, e funcionou porque o curl deixou o servidor resolver o nome.</p>
<div class="tip"><strong>No navegador</strong><p>No Firefox: Configurações → Rede → Configurar conexão → <em>SOCKS v5</em>, host <code>localhost</code>, porta <code>1080</code>, e marque “Proxy DNS ao usar SOCKS v5”. Enquanto o túnel estiver aberto, o navegador vê o que o servidor vê.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("O nome resolvido no lugar errado", "Com <code>--socks5</code> (sem <code>-hostname</code>), quem traduz o nome é o <strong>notebook</strong>, que não conhece <code>interno</code>:", T("td-erro", "ssh -f -N -D 1080 lab@servidor", "curl -sS --socks5 localhost:1080 http://interno/"), "Use <code>--socks5-hostname</code> no curl (ou “Proxy DNS” no navegador) para o servidor resolver os nomes. (A mensagem do curl fala em “proxy”, mas o nome que ele não conseguiu traduzir foi <code>interno</code>.)")}
"""

def td_ex():
    return (EX(1, "Túnel dinâmico", "Que opção abre um proxy SOCKS no notebook?", "ssh -f -N ", "-D", " 1080 lab@servidor", rotulo="opção") +
            EX(2, "No curl", "Complete para o servidor resolver os nomes:", "curl -s ", "--socks5-hostname", " localhost:1080 http://interno/", rotulo="opção") +
            MC(3, "A diferença entre <code>-L</code> e <code>-D</code>:", ["nenhuma", "<code>-L</code> é um destino fixo; <code>-D</code> é um proxy para qualquer destino", "<code>-D</code> é mais lento", "<code>-L</code> não usa SSH"], 2) +
            MC(4, "Com o túnel <code>-D</code>, os sites veem a conexão vindo:", ["do notebook", "do servidor", "de lugar nenhum", "do roteador"], 2))

def td_miss():
    return (M("td-m1", "abra um proxy SOCKS e baixe o painel do servidor por ele.", "ssh -f -N -D 1080 lab@servidor && curl -s --socks5-hostname localhost:1080 http://localhost:8080/", r"src:-D 1080;;src:--socks5-hostname;;out:Painel do servidor") +
            M("td-m2", "tente usar um proxy numa porta sem túnel (1089) e veja o erro do curl.", "curl -sS --socks5-hostname localhost:1089 http://localhost:8080/", r"src:--socks5-hostname localhost:1089;;outre:^curl: \(7\) Failed to connect"))

# ---------------------------------------------------------------- ProxyJump
PJ_SEM_KH = [["notebook", "ana", "ssh-keygen -R 192.168.0.130 >/dev/null 2>&1; rm -f ~/.ssh/known_hosts.old"]]
def pj_corpo():
    return f"""
<h2>A ideia: pular de máquina em máquina</h2>
<p>Em muitas empresas, os servidores internos não aceitam conexão de fora: primeiro se entra num servidor de entrada (o “bastion”) e, dele, nos outros. O <strong>ProxyJump</strong> (<code>-J</code>) faz os dois saltos num comando só, e a autenticação no destino é feita <strong>pelo notebook</strong>, com a chave do notebook. Nada fica guardado no servidor do meio, e o agente não é exposto (ao contrário do <code>-A</code>).</p>
<hr>
<h2>1. Sem o salto, não chega</h2>
{T("pj-sem", "ssh lab@interno hostname", "ssh -o ConnectTimeout=3 lab@192.168.0.130 hostname")}
<hr>
<h2>2. Com <code>-J</code></h2>
{T("pj-j", "ssh -J lab@servidor lab@192.168.0.130 hostname", "ssh -J lab@servidor lab@192.168.0.130 'ip -br addr'", notas={"interno": "chegou ao interno, passando pelo servidor"})}
{ANAT(("-J lab@servidor", "o salto: primeiro conecta aqui."), ("lab@192.168.0.130", "o destino final, visto pelo servidor."))}
<p>Dá para encadear saltos com vírgula: <code>-J lab@a,lab@b destino</code>.</p>
<hr>
<h2>3. No config: <code>ProxyJump</code></h2>
{T("pj-config", "cat ~/.ssh/config", "ssh interno hostname", "ssh -G interno | grep -i '^proxyjump'", "scp notas.txt interno:", "ssh interno ls", estado="config", notas={"ProxyJump servidor": "o salto, guardado no config"})}
<p>Com o bloco no config, <code>ssh</code>, <code>scp</code>, <code>sftp</code> e <code>rsync</code> pulam sozinhos.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A pergunta do fingerprint, para o destino", "Cada máquina tem a sua chave de host. Na primeira vez no <code>interno</code>, o notebook pergunta por ela (o “no hostip for proxy command” é normal: quem conectou foi o servidor do meio):", T("pj-erro", "ssh -J lab@servidor lab@192.168.0.130 hostname", prep=PJ_SEM_KH, resp=[SIM]), "Confira o fingerprint no próprio interno (<code>ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub</code>) e responda <code>yes</code>.")}
"""

def pj_ex():
    return (EX(1, "O salto", "Que opção do ssh faz o salto?", "ssh ", "-J", " lab@servidor lab@192.168.0.130", rotulo="opção") +
            EX(2, "No config", "Que opção do config guarda o salto?", "    ", "ProxyJump", " servidor", rotulo="opção") +
            MC(3, "Com <code>-J</code>, a chave privada usada no destino fica:", ["no servidor do meio", "no notebook", "no destino", "no agente do servidor"], 2) +
            MC(4, "Por que preferir <code>-J</code> a <code>-A</code>?", ["É mais rápido", "Não expõe o seu agente ao servidor do meio", "Não precisa de chave", "Abre mais portas"], 2))

def pj_miss():
    return (M("pj-m1", "pule pelo servidor até o IP dele mesmo (dá para treinar o <code>-J</code> com uma máquina só; troque pelo IP do seu servidor).", "ssh -J lab@servidor lab@192.168.0.20 'echo salto ok'", r"src:-J lab@servidor;;outre:^salto ok$") +
            M("pj-m2", "depois de criar o bloco <code>Host interno</code> com <code>ProxyJump</code>, confira com <code>ssh -G</code>.", "ssh -G interno | grep -i '^proxyjump'", r"src:ssh -G interno;;outre:^proxyjump \S+$", estado="config"))

# ---------------------------------------------------------------- túneis no config
TC_CONF = "printf 'Host painel\\n    HostName 192.168.0.20\\n    User lab\\n    LocalForward 8080 localhost:8080\\n    ExitOnForwardFailure yes\\n' >> ~/.ssh/config"
def tc_corpo():
    return f"""
<h2>A ideia: túneis com nome</h2>
<p>Túnel que você usa todo dia merece um bloco no config. As opções equivalentes: <code>LocalForward</code> (<code>-L</code>), <code>RemoteForward</code> (<code>-R</code>) e <code>DynamicForward</code> (<code>-D</code>). E o <code>ExitOnForwardFailure yes</code> faz o ssh <strong>desistir</strong> se não conseguir abrir o túnel, em vez de ficar conectado sem ele.</p>
<pre class="cmd">
Host painel
    HostName 192.168.0.20
    User lab
    LocalForward 8080 localhost:8080
    ExitOnForwardFailure yes
</pre>
<hr>
<h2>1. Abrir pelo apelido</h2>
{T("tc-abrir", TC_CONF, "ssh -f -N painel", "curl -s http://localhost:8080/", "pgrep -a ssh", estado="config", notas={"ssh -f -N painel": "o processo do túnel"})}
<hr>
<h2>2. Fechar</h2>
{T("tc-fechar", TC_CONF, "ssh -f -N painel", "pkill -f 'ssh -f -N painel'", "pgrep -a ssh", "curl -sS http://localhost:8080/", estado="config")}
<hr>
<h2>3. O ExitOnForwardFailure em ação</h2>
<p>Com a porta 8080 já ocupada por um túnel, o segundo ssh desiste e devolve erro (código 255), em vez de fingir que deu certo:</p>
{T("tc-falha", TC_CONF, "ssh -f -N painel", "ssh -f -N painel; echo \"código: $?\"", estado="config", notas={"código: 255": "desistiu: nada de conexão sem túnel"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Túnel aberto e esquecido", "Túneis com <code>-f</code> ficam abertos até você fechar, mesmo fechando o terminal. Antes de abrir de novo, veja o que já existe:", T("tc-erro", "ssh -f -N -L 8080:localhost:8080 lab@servidor", "ssh -f -N -D 1080 lab@servidor", "pgrep -a ssh"), "Feche o que não usa com <code>kill</code> e o número do processo, ou <code>pkill -f</code> com um pedaço do comando.")}
"""

def tc_ex():
    return (EX(1, "No config", "Que opção do config equivale ao <code>-L</code>?", "    ", "LocalForward", " 8080 localhost:8080", rotulo="opção") +
            EX(2, "Desistir", "Que opção faz o ssh desistir se o túnel falhar?", "    ", "ExitOnForwardFailure", " yes", rotulo="opção") +
            MC(3, "<code>pgrep -a ssh</code> serve para:", ["abrir túneis", "ver os processos ssh abertos, com o comando", "apagar chaves", "testar a senha"], 2) +
            MC(4, "Sem <code>ExitOnForwardFailure</code>, se a porta estiver ocupada:", ["o ssh desiste", "o ssh conecta mesmo sem o túnel", "o ssh troca a porta", "o servidor cai"], 2))

def tc_miss():
    return (M("tc-m1", "abra um túnel em segundo plano e mostre o processo dele.", "ssh -f -N -L 8080:localhost:8080 lab@servidor && pgrep -a ssh", r"src:ssh -f -N -L;;src:pgrep -a ssh;;outre:^\d+ ssh -f -N -L 8080") +
            M("tc-m2", "tente abrir um túnel na porta 3000 do notebook (já usada pelo seu site) com <code>ExitOnForwardFailure</code>.", "ssh -o ExitOnForwardFailure=yes -f -N -L 3000:localhost:8080 lab@servidor", r"src:ExitOnForwardFailure=yes;;out:Address already in use"))

NIVEL = {"id": "n4", "nome": "Nível 4 · Túneis e saltos", "curto": "Túneis", "desc": "Portas pela rede: -L, -R, -D, ProxyJump e túneis no config", "grupos": [
    {"grupo": "Túneis", "aulas": [
        aula(slug="tunel-local", menu="Túnel local (-L)", title="Túnel SSH local (-L): abrindo no notebook uma porta do servidor", h1='Túnel <span class="hl">local</span> (-L)',
             desc="Túnel SSH local com -L: acessar no notebook um serviço que só escuta em localhost no servidor, com -f e -N.",
             intro="O -L traz para o seu computador uma porta que só existe dentro do servidor.",
             aprender=["Abrir um túnel com <code>-L</code>.", "Usar <code>-f</code> e <code>-N</code>.", "Escolher a porta local."],
             corpo=tl_corpo, exercicios=tl_ex, missoes=tl_miss,
             ref=[("ssh -L 8080:localhost:8080 srv", "túnel local."), ("-f -N", "segundo plano, sem comando."), ("ss -ltn", "portas escutando.")],
             resumo=["<code>-L local:destino:porta</code>.", "O destino é visto pelo servidor.", "A porta local escuta só em 127.0.0.1."]),
        aula(slug="tunel-rede", menu="Túnel até outra máquina", title="Túnel SSH até outra máquina da rede do servidor", h1='Túnel até <span class="hl">outra máquina</span>',
             desc="Usar o servidor como ponte com -L para alcançar uma máquina que só a rede do servidor enxerga, inclusive o SSH dela.",
             intro="O destino do -L pode ser outra máquina, desde que o servidor a alcance.",
             aprender=["Levar uma porta até outra máquina.", "Entender qual trecho é criptografado.", "Entrar por SSH através de um túnel."],
             corpo=tr_corpo, exercicios=tr_ex, missoes=tr_miss,
             ref=[("ssh -L 8081:192.168.0.130:80 srv", "até outra máquina."), ("ssh -p 2200 lab@localhost", "entra pelo túnel."), ("-o HostKeyAlias=nome", "confere a chave certa.")],
             resumo=["O servidor é a ponte.", "Do servidor ao destino não há criptografia do SSH.", "Para SSH em cadeia, prefira <code>-J</code>."]),
        aula(slug="tunel-remoto", menu="Túnel remoto (-R)", title="Túnel SSH remoto (-R): mostrando o notebook a partir do servidor", h1='Túnel <span class="hl">remoto</span> (-R)',
             desc="Túnel SSH remoto com -R: abrir no servidor uma porta que leva a um serviço do notebook, e o GatewayPorts.",
             intro="O -R é o -L ao contrário: uma porta no servidor que leva ao seu computador.",
             aprender=["Abrir um túnel com <code>-R</code>.", "Ver a porta no servidor.", "O que é o <code>GatewayPorts</code>."],
             corpo=rr_corpo, exercicios=rr_ex, missoes=rr_miss,
             ref=[("ssh -R 9000:localhost:3000 srv", "túnel remoto."), ("ss -ltn", "no servidor, a porta."), ("GatewayPorts", "no sshd: abrir para a rede.")],
             resumo=["<code>-R servidor:destino:porta</code>.", "O destino é visto pelo notebook.", "A porta escuta só em 127.0.0.1 do servidor."]),
        aula(slug="tunel-dinamico", menu="Proxy SOCKS (-D)", title="Túnel SSH dinâmico (-D): um proxy SOCKS pelo servidor", h1='Proxy SOCKS: túnel <span class="hl">dinâmico</span> (-D)',
             desc="Túnel SSH dinâmico com -D: um proxy SOCKS5 no notebook, curl com --socks5-hostname e configuração no navegador.",
             intro="Com -D, qualquer programa que saiba usar proxy SOCKS passa a sair pelo servidor.",
             aprender=["Abrir um proxy com <code>-D</code>.", "Usar com <code>curl --socks5-hostname</code>.", "Configurar o navegador."],
             corpo=td_corpo, exercicios=td_ex, missoes=td_miss,
             ref=[("ssh -f -N -D 1080 srv", "proxy SOCKS."), ("curl --socks5-hostname localhost:1080 URL", "pelo proxy."), ("Proxy DNS", "no navegador.")],
             resumo=["<code>-D</code> é um proxy para qualquer destino.", "Deixe o servidor resolver os nomes.", "Os sites veem o servidor."]),
    ]},
    {"grupo": "Saltos e atalhos", "aulas": [
        aula(slug="proxyjump", menu="Saltos com ProxyJump (-J)", title="ProxyJump (-J): entrando num servidor interno passando por outro", h1='Saltos com <span class="hl">ProxyJump</span>',
             desc="Usar ProxyJump (-J) para chegar a um servidor interno passando por um bastion, no comando e no ~/.ssh/config.",
             intro="O -J entra num servidor através de outro, com a sua chave e sem expor o agente.",
             aprender=["Pular com <code>-J</code>.", "Guardar o salto com <code>ProxyJump</code>.", "A pergunta do fingerprint do destino."],
             corpo=pj_corpo, exercicios=pj_ex, missoes=pj_miss,
             ref=[("ssh -J lab@srv lab@destino", "um salto."), ("-J a,b", "dois saltos."), ("ProxyJump srv", "no config.")],
             resumo=["O <code>-J</code> autentica no destino a partir do notebook.", "Funciona com scp, sftp e rsync.", "Prefira <code>-J</code> a <code>-A</code>."]),
        aula(slug="tuneis-config", menu="Túneis no config", title="Túneis no ~/.ssh/config: LocalForward e ExitOnForwardFailure", h1='Túneis no <span class="hl">config</span>',
             desc="Guardar túneis no ~/.ssh/config com LocalForward, RemoteForward e DynamicForward, ExitOnForwardFailure, e ver e fechar túneis em segundo plano.",
             intro="Túnel de todo dia vira um apelido. Esta aula mostra como abrir, listar e fechar.",
             aprender=["Escrever <code>LocalForward</code> no config.", "Ver e fechar túneis com <code>pgrep</code> e <code>pkill</code>.", "Usar <code>ExitOnForwardFailure</code>."],
             corpo=tc_corpo, exercicios=tc_ex, missoes=tc_miss,
             ref=[("LocalForward 8080 localhost:8080", "= -L."), ("RemoteForward / DynamicForward", "= -R / -D."), ("ExitOnForwardFailure yes", "desiste se falhar."), ("pgrep -a ssh", "túneis abertos.")],
             resumo=["Túnel com nome: <code>ssh -f -N apelido</code>.", "<code>ExitOnForwardFailure</code> evita conexão sem túnel.", "Feche o que não usa."]),
    ]},
]}
