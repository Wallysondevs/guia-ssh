# -*- coding: utf-8 -*-
"""Nível 2 · Chaves: entrar sem senha com chaves SSH, agente e permissões."""
from lib_guia import *
from respostas import *

def aula(**k):
    return k

FRASE_LAB = "frase do lab"
COM_FRASE = ["notebook", "ana", "ssh-keygen -q -p -f ~/.ssh/id_ed25519 -P '' -N '%s'" % FRASE_LAB]
SEM_SENHA = [["servidor", "root", "echo 'PasswordAuthentication no' > /etc/ssh/sshd_config.d/10-sem-senha.conf && kill -HUP $(cat /run/sshd.pid) && sleep 0.5"]]

# ---------------------------------------------------------------- senha x chave
CC_V = "ssh -v lab@servidor true 2>&1 | grep -E 'Authentications that|Offering|accepts key|Authenticated to'"
def cc_corpo():
    return f"""
<h2>A ideia: um cadeado e uma chave</h2>
<p>Até aqui a Ana entrou com <strong>senha</strong>. Funciona, mas tem problemas: dá para adivinhar senha fraca, e digitar a toda hora cansa (e atrapalha scripts). O SSH tem um jeito melhor: um <strong>par de chaves</strong>.</p>
<ul>
<li>A <strong>chave privada</strong> (<code>~/.ssh/id_ed25519</code>) fica só no notebook. É o segredo: <strong>nunca</strong> mande para ninguém.</li>
<li>A <strong>chave pública</strong> (<code>~/.ssh/id_ed25519.pub</code>) pode ser copiada para quantos servidores você quiser. Ela é como um cadeado que só a sua chave privada abre.</li>
</ul>
<p>No servidor, a chave pública fica no arquivo <code>~/.ssh/authorized_keys</code> do usuário. Na conexão, o servidor manda um desafio que só quem tem a chave privada consegue responder. A chave privada nunca sai do notebook.</p>
<hr>
<h2>1. Com senha</h2>
{T("cc-senha", "ssh lab@servidor hostname", estado="conhecido", resp=[SENHA], notas={"password:": "sem chave, o servidor pede a senha"})}
<hr>
<h2>2. Com chave</h2>
<p>Depois de criar e instalar a chave (as próximas duas aulas mostram como), o notebook ficou assim:</p>
{T("cc-chave", "ls -l ~/.ssh", "cat ~/.ssh/id_ed25519.pub", "ssh lab@servidor hostname", notas={"-rw------- 1 ana ana 399": "a privada: só a ana lê", "id_ed25519.pub": "a pública: pode ser lida por todos", "ssh-ed25519 AAAA": "a chave pública inteira cabe numa linha"})}
<p>E no servidor, a mesma linha da chave pública está no <code>authorized_keys</code> do <code>lab</code>:</p>
{T("cc-servidor", "cat ~/.ssh/authorized_keys", quem="servidor")}
<div class="warning"><strong>Nunca mostre a chave privada</strong><p>O arquivo <code>id_ed25519</code> (sem <code>.pub</code>) começa com uma linha de traços que avisa que ali há uma chave privada (<code>-----BEGIN OPENSSH PRIV…</code>) e continua com várias linhas de letras. Não cole esse conteúdo em lugar nenhum: chat, e-mail, GitHub, fórum. Quem tem esse arquivo entra nos seus servidores. O guia nunca mostra uma chave privada.</p></div>
<hr>
<h2>3. Vendo a conversa com <code>-v</code></h2>
<p>O <code>-v</code> (“verboso”) mostra o que o ssh está fazendo. Filtrando as linhas da autenticação:</p>
{T("cc-v", CC_V, notas={"can continue": "o servidor aceita chave ou senha", "Offering": "o ssh oferece a chave pública", "accepts key": "o servidor reconheceu a chave", "using \"publickey\"": "entrou com a chave, sem senha"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A chave sumiu do servidor", "Se alguém apagar o <code>authorized_keys</code> no servidor, a chave deixa de valer e o ssh volta a pedir a senha. Na coleta, apagamos o arquivo antes:", T("cc-erro", "ssh lab@servidor hostname", resp=[SENHA], prep=[["servidor", "root", "rm /home/lab/.ssh/authorized_keys"]]), "Se o ssh pedir senha quando você esperava a chave, confira o <code>~/.ssh/authorized_keys</code> no servidor.")}
"""

def cc_ex():
    return (EX(1, "A pública", "Qual arquivo pode ser copiado para os servidores?", "~/.ssh/", "id_ed25519.pub") +
            EX(2, "No servidor", "Em que arquivo do servidor fica a chave pública?", "~/.ssh/", "authorized_keys") +
            MC(3, "A chave privada pode ser enviada:", ["por e-mail, se for para você mesmo", "para o servidor", "para ninguém: ela não sai do seu computador", "para o GitHub"], 3) +
            MC(4, "Na conexão com chave, o que viaja até o servidor?", ["a chave privada", "a resposta a um desafio, feita com a chave privada", "a senha", "o arquivo known_hosts"], 2))

def cc_miss():
    return (M("cc-m1", "liste os arquivos da sua pasta <code>~/.ssh</code>.", "ls ~/.ssh", r"src:^ls\b;;src:\.ssh;;outre:(^|\s)id_ed25519\.pub(\s|$)") +
            M("cc-m2", "mostre com <code>-v</code> que você entrou com a chave.", "ssh -v lab@servidor true 2>&1 | grep 'Authenticated to'", r"src:ssh -v;;src:grep;;outre:^Authenticated to \S+ .*using \"publickey\""))

# ---------------------------------------------------------------- ssh-keygen
def kg_corpo():
    return f"""
<h2>A ideia: criar o seu par de chaves</h2>
<p>O <code>ssh-keygen</code> cria o par. Use o tipo <strong>ed25519</strong>: é moderno, rápido e tem chaves curtas. O <code>-C</code> põe um comentário (costuma ser <code>usuario@computador</code>) para você saber, lá no servidor, de quem é cada chave.</p>
<hr>
<h2>1. Gerar a chave</h2>
<p>A Ana gerou a primeira chave dela. O ssh-keygen fez três perguntas: onde salvar (Enter aceita o padrão), e a <strong>frase secreta</strong> (<em>passphrase</em>) duas vezes. A frase protege a chave privada: se alguém copiar o arquivo, ainda precisa dela. Como a senha, ela não aparece enquanto você digita.</p>
{T("kg-gerar", "ssh-keygen -t ed25519 -C \"ana@notebook\"", estado="zero", resp=[["save the key", "\n"], FRASE(FRASE_LAB, "Enter passphrase"), FRASE(FRASE_LAB, "Enter same passphrase")],
   notas={"Created directory": "a pasta ~/.ssh foi criada", "identification has been saved": "a chave privada", "public key has been saved": "a chave pública", "The key fingerprint is": "a impressão digital da chave"})}
{ANAT(("-t ed25519", "o tipo da chave."), ("-C \"ana@notebook\"", "o comentário que vai no fim da chave pública."))}
<p>O desenho (<em>randomart</em>) é outra forma de ver o fingerprint: duas chaves diferentes dão desenhos diferentes.</p>
<hr>
<h2>2. O que foi criado</h2>
{T("kg-ver", "ls -l ~/.ssh", "cat ~/.ssh/id_ed25519.pub", "ssh-keygen -lf ~/.ssh/id_ed25519.pub", "file ~/.ssh/id_ed25519", estado="chavelocal",
   notas={"-rw------- 1 ana ana": "privada: permissão 600", "OpenSSH private key": "o file diz o que é, sem mostrar o conteúdo"})}
<p>Para saber o que é um arquivo de chave sem abrir, use <code>file</code> ou <code>ssh-keygen -l</code>. Abrir a privada com <code>cat</code> mostraria o segredo na tela.</p>
<hr>
<h2>3. Escolher o nome e não perguntar nada</h2>
<p>Em scripts, ou para ter uma chave por servidor, passe tudo na linha: <code>-f</code> (arquivo), <code>-N</code> (frase; <code>''</code> = sem frase) e <code>-q</code> (quieto):</p>
{T("kg-nome", "ssh-keygen -t ed25519 -f ~/.ssh/servidor_lab -N '' -C 'chave do lab' -q", "ls ~/.ssh", "ssh-keygen -t rsa -b 4096 -f ~/.ssh/antiga_rsa -N '' -q", "ssh-keygen -lf ~/.ssh/antiga_rsa.pub", estado="chavelocal",
   notas={"(RSA)": "RSA de 4096 bits: o tipo antigo"})}
<div class="tip"><strong>ed25519 ou RSA?</strong><p>Prefira <strong>ed25519</strong>. Use RSA (com <code>-b 4096</code>) só se um sistema antigo não aceitar ed25519.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A chave já existe", "Rodar o ssh-keygen de novo com o mesmo nome pergunta se pode <strong>sobrescrever</strong>. Responda <code>n</code>: trocar a chave quebra o acesso a todos os servidores onde a antiga está instalada.", T("kg-erro", "ssh-keygen -t ed25519", estado="chavelocal", resp=[["save the key", "\n"], ["Overwrite \\(y/n\\)\\? ", "n\n"]]), "Para uma chave nova, escolha outro nome com <code>-f</code>.")}
"""

def kg_ex():
    return (EX(1, "O tipo", "Complete para gerar uma chave do tipo recomendado:", "ssh-keygen -t ", "ed25519") +
            EX(2, "Sem frase", "Que valor do <code>-N</code> cria a chave sem frase secreta?", "ssh-keygen -N ", ["''", '""']) +
            MC(3, "Para que serve a frase secreta?", ["Para entrar no servidor sem chave", "Para proteger a chave privada se alguém copiar o arquivo", "Para o servidor saber o seu nome", "Para nada"], 2) +
            MC(4, "Como ver a impressão digital de uma chave?", ["<code>cat ~/.ssh/id_ed25519</code>", "<code>ssh-keygen -lf arquivo.pub</code>", "<code>ssh -V</code>", "<code>ls -l</code>"], 2))

def kg_miss():
    return (M("kg-m1", "gere uma chave ed25519 de teste chamada <code>teste_ed25519</code>, sem frase.", "ssh-keygen -t ed25519 -f ~/.ssh/teste_ed25519 -N '' -C teste", r"src:ssh-keygen;;src:-t ed25519;;src:-f\s+\S*teste_ed25519;;out:Your identification has been saved", estado="chavelocal") +
            M("kg-m2", "mostre a impressão digital da sua chave pública.", "ssh-keygen -lf ~/.ssh/id_ed25519.pub", r"src:ssh-keygen -lf;;outre:^256 SHA256:\S+ .*\(ED25519\)$", estado="chavelocal"))

# ---------------------------------------------------------------- ssh-copy-id
def ci_corpo():
    return f"""
<h2>A ideia: instalar a chave pública no servidor</h2>
<p>O <code>ssh-copy-id</code> faz login com a <strong>senha</strong> uma última vez e acrescenta a sua chave pública ao <code>~/.ssh/authorized_keys</code> do servidor, criando a pasta e acertando as permissões. Daí em diante, entra-se com a chave.</p>
<hr>
<h2>1. Copiar a chave</h2>
{T("ci-copiar", "ssh-copy-id lab@servidor", "ssh lab@servidor hostname", estado="chavelocal", resp=[SENHA],
   notas={"Source of key": "qual chave ele vai instalar", "password:": "a última vez que a senha é pedida", "Number of key(s) added: 1": "instalada", "servidor": "entrou sem senha"})}
<p>No servidor, o <code>ssh-copy-id</code> deixou a pasta e o arquivo com as permissões certas (<code>700</code> e <code>600</code>):</p>
{T("ci-servidor", "ls -la ~/.ssh", "cat ~/.ssh/authorized_keys", quem="servidor")}
<hr>
<h2>2. Rodar de novo não duplica</h2>
{T("ci-repetir", "ssh-copy-id lab@servidor", notas={"All keys were skipped": "a chave já estava lá"})}
<hr>
<h2>3. Escolher qual chave instalar: <code>-i</code></h2>
<p>Com várias chaves, o <code>-i</code> diz qual instalar. Como a chave padrão já estava no servidor, nem precisou de senha:</p>
{T("ci-i", "ssh-copy-id -i ~/.ssh/servidor_lab.pub lab@servidor", "ssh -i ~/.ssh/servidor_lab lab@servidor 'tail -1 ~/.ssh/authorized_keys'",
   prep=[["notebook", "ana", "ssh-keygen -q -t ed25519 -f ~/.ssh/servidor_lab -N '' -C 'chave do lab'"]], notas={"chave do lab": "a chave nova, no fim do arquivo"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Ainda não existe chave", "Sem chave em <code>~/.ssh</code>, o ssh-copy-id não tem o que copiar:", T("ci-erro", "ssh-copy-id lab@servidor", estado="conhecido"), "Gere a chave antes, com <code>ssh-keygen -t ed25519</code>.")}
"""

def ci_ex():
    return (EX(1, "Instalar", "Complete para instalar a sua chave no servidor:", "", "ssh-copy-id", " lab@servidor", rotulo="comando") +
            EX(2, "Outra chave", "Complete para instalar a chave <code>servidor_lab.pub</code>:", "ssh-copy-id ", "-i", " ~/.ssh/servidor_lab.pub lab@servidor", rotulo="opção") +
            MC(3, "O ssh-copy-id pede a senha porque:", ["a chave está errada", "precisa entrar uma vez para instalar a chave", "sempre vai pedir", "o servidor caiu"], 2) +
            MC(4, "Rodar o ssh-copy-id duas vezes:", ["duplica a chave", "apaga a chave", "não duplica: ele avisa que a chave já existe", "trava o servidor"], 3))

def ci_miss():
    return (M("ci-m1", "instale a sua chave pública no servidor.", "ssh-copy-id lab@servidor", r"src:^ssh-copy-id\b;;out:Number of key(s) added: 1", estado="chavelocal", resp=[SENHA]) +
            M("ci-m2", "prove que entra sem senha: proíba a senha só nesta conexão.", "ssh -o PasswordAuthentication=no lab@servidor 'echo entrei sem senha'", r"src:PasswordAuthentication=no;;outre:^entrei sem senha$"))

# ---------------------------------------------------------------- authorized_keys
AK_MANUAL = "cat ~/.ssh/id_ed25519.pub | ssh lab@servidor 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
AK_RESTRITA = ["servidor", "root", "sed -i 's/^/command=\"cat relatorio.txt\",restrict /' /home/lab/.ssh/authorized_keys"]
AK_FROM = ["servidor", "root", "sed -i 's/^/from=\"192.168.0.99\" /' /home/lab/.ssh/authorized_keys"]
def ak_corpo():
    return f"""
<h2>A ideia: o authorized_keys é só um arquivo de texto</h2>
<p>Cada linha do <code>~/.ssh/authorized_keys</code> é uma chave pública que pode entrar como aquele usuário. Onde não há <code>ssh-copy-id</code> (alguns sistemas, o Windows), dá para fazer o mesmo à mão. E dá para pôr <strong>regras</strong> no começo da linha.</p>
<hr>
<h2>1. Instalar à mão</h2>
<p>O <code>cat</code> manda a chave pública pelo cano; no servidor, o <code>cat &gt;&gt;</code> acrescenta no fim do arquivo:</p>
{T("ak-manual", AK_MANUAL, "ssh lab@servidor 'wc -l ~/.ssh/authorized_keys'", estado="chavelocal", resp=[SENHA])}
<div class="warning"><strong>&gt;&gt; e não &gt;</strong><p>Use <code>&gt;&gt;</code> (acrescentar). Um <code>&gt;</code> apagaria as outras chaves do arquivo e trancaria quem entrava com elas.</p></div>
<hr>
<h2>2. Regras na frente da chave</h2>
<p>Antes da chave, opções separadas por vírgula limitam o que ela pode fazer. Com <code>command="…"</code>, a chave <strong>só</strong> roda aquele comando, peça o que pedir. O <code>restrict</code> desliga terminal, túneis e encaminhamentos. É o jeito certo de dar a um script uma chave que só faz uma coisa:</p>
<p>No servidor, a linha da chave da Ana ganhou uma regra na frente (aqui cortada em 70 letras):</p>
{T("ak-linha", "cut -c1-70 ~/.ssh/authorized_keys", quem="servidor", prep=[AK_RESTRITA], notas={"command=": "a regra na frente da chave"})}
<p>Agora, do notebook, peça o que pedir:</p>
{T("ak-opcoes", "ssh lab@servidor hostname", "ssh lab@servidor 'rm -rf ~'", "ssh lab@servidor", prep=[AK_RESTRITA],
   notas={"PTY allocation": "restrict: sem terminal"})}
<p>Nem o <code>hostname</code> nem o <code>rm -rf ~</code> rodaram: no lugar dele, o servidor rodou o comando da regra e mostrou o relatório.</p>
<div class="table-wrap"><table class="ref">
<tr><th>Opção</th><th>O que faz</th></tr>
<tr><td><code>command="cmd"</code></td><td>a chave só roda <code>cmd</code></td></tr>
<tr><td><code>from="192.168.0.0/24"</code></td><td>só aceita a chave vindo desses IPs</td></tr>
<tr><td><code>restrict</code></td><td>sem terminal, sem túneis, sem encaminhamento de agente</td></tr>
<tr><td><code>no-port-forwarding</code></td><td>só proíbe os túneis</td></tr>
</table></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A regra from= não bate", "Com <code>from=\"192.168.0.99\"</code>, a chave só vale vindo desse IP. O notebook é o 192.168.0.10, então o servidor ignora a chave. Com <code>BatchMode=yes</code> o ssh não pergunta a senha e desiste:", T("ak-erro", "ssh -o BatchMode=yes lab@servidor hostname", prep=[AK_FROM]), "Se uma chave “parou de funcionar”, olhe se há regras no começo da linha dela no <code>authorized_keys</code>.")}
"""

def ak_ex():
    return (EX(1, "Acrescentar", "Que redirecionamento acrescenta no fim do arquivo, sem apagar?", "cat >", ">", " ~/.ssh/authorized_keys", rotulo="símbolo") +
            EX(2, "Só um comando", "Complete a regra que faz a chave rodar só o <code>uptime</code>:", "", 'command="uptime"', " ssh-ed25519 AAAA…", rotulo="regra") +
            MC(3, "Cada linha do authorized_keys é:", ["uma senha", "uma chave pública que pode entrar", "um servidor conhecido", "um comando"], 2) +
            MC(4, "O <code>restrict</code> numa chave:", ["apaga a chave", "desliga terminal, túneis e encaminhamentos", "obriga a senha", "muda a porta"], 2))

def ak_miss():
    return (M("ak-m1", "no servidor, conte quantas chaves ed25519 o seu <code>authorized_keys</code> tem.", "grep -c ssh-ed25519 ~/.ssh/authorized_keys", r"src:grep -c;;src:authorized_keys;;outre:^\d+$", quem="servidor") +
            M("ak-m2", "do notebook, mostre o tipo e o comentário das chaves instaladas no servidor.", "ssh lab@servidor 'cut -d\" \" -f1,3 ~/.ssh/authorized_keys'", r"src:^ssh\b;;src:cut;;outre:^ssh-ed25519 \S+@\S+$"))

# ---------------------------------------------------------------- passphrase
def pp_corpo():
    return f"""
<h2>A ideia: uma senha para a chave</h2>
<p>A frase secreta (<em>passphrase</em>) <strong>criptografa a chave privada</strong> no disco. Se o notebook for roubado, ou alguém copiar o arquivo, a chave não serve sem a frase. Ela nunca vai para o servidor: é conferida no próprio notebook.</p>
<hr>
<h2>1. Entrar com uma chave que tem frase</h2>
<p>Com frase, o ssh pede a frase da <strong>chave</strong> (repare na pergunta: não é a senha do servidor):</p>
{T("pp-pedir", "ssh lab@servidor hostname", prep=[COM_FRASE], resp=[FRASE(FRASE_LAB, "Enter passphrase for key")], notas={"Enter passphrase for key": "a frase da chave, conferida no notebook"})}
<p>Digitar a frase a cada conexão cansa. A solução é o <a href="ssh-agent.html">ssh-agent</a>, na próxima aula.</p>
<hr>
<h2>2. Pôr, trocar ou tirar a frase: <code>ssh-keygen -p</code></h2>
<p>O <code>-p</code> pede a frase antiga e a nova (duas vezes). A chave continua a mesma, então nada muda nos servidores:</p>
{T("pp-trocar", "ssh-keygen -p -f ~/.ssh/id_ed25519", "ssh-keygen -lf ~/.ssh/id_ed25519.pub", prep=[COM_FRASE],
   resp=[FRASE(FRASE_LAB, "Enter old passphrase"), FRASE("frase nova e longa", "Enter new passphrase"), FRASE("frase nova e longa", "Enter same passphrase")],
   notas={"with the new passphrase": "trocada", "SHA256:": "a impressão digital não mudou"})}
<hr>
<h2>3. Perdi o .pub: <code>ssh-keygen -y</code></h2>
<p>A chave pública sai da privada. Se o <code>.pub</code> sumiu, o <code>-y</code> recria (pedindo a frase):</p>
{T("pp-y", "ssh-keygen -y -f ~/.ssh/id_ed25519", prep=[COM_FRASE], resp=[FRASE(FRASE_LAB, "Enter passphrase")])}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Frase errada", "Errou a frase? O ssh-keygen avisa que não conseguiu abrir a chave:", T("pp-erro", "ssh-keygen -y -f ~/.ssh/id_ed25519", prep=[COM_FRASE], resp=[FRASE("frase errada", "Enter passphrase")]), "Esqueceu a frase de vez? Não há como recuperar: gere uma chave nova e instale nos servidores.")}
"""

def pp_ex():
    return (EX(1, "Trocar a frase", "Complete para trocar a frase da chave:", "ssh-keygen ", "-p", " -f ~/.ssh/id_ed25519", rotulo="opção") +
            EX(2, "Recriar a pública", "Complete para mostrar a chave pública a partir da privada:", "ssh-keygen ", "-y", " -f ~/.ssh/id_ed25519", rotulo="opção") +
            MC(3, "A frase secreta da chave é conferida:", ["no servidor", "no notebook", "no GitHub", "no known_hosts"], 2) +
            MC(4, "Trocar a frase com <code>ssh-keygen -p</code>:", ["exige reinstalar a chave nos servidores", "mantém a mesma chave (nada muda nos servidores)", "apaga a chave pública", "muda o fingerprint"], 2))

def pp_miss():
    return (M("pp-m1", "ponha a frase <code>nova frase</code> na chave de teste <code>teste_ed25519</code> (que não tem frase).", "ssh-keygen -p -f ~/.ssh/teste_ed25519 -P '' -N 'nova frase'", r"src:ssh-keygen -p;;src:teste_ed25519;;out:saved with the new passphrase",
              estado="chavelocal", prep=[["notebook", "ana", "ssh-keygen -q -t ed25519 -f ~/.ssh/teste_ed25519 -N '' -C teste"]]) +
            M("pp-m2", "mostre a chave pública da <code>teste_ed25519</code> a partir da privada, informando a frase.", "ssh-keygen -y -f ~/.ssh/teste_ed25519 -P 'nova frase'", r"src:ssh-keygen -y;;outre:^ssh-ed25519 AAAA\S+",
              estado="chavelocal", prep=[["notebook", "ana", "ssh-keygen -q -t ed25519 -f ~/.ssh/teste_ed25519 -N 'nova frase' -C teste"]]))

# ---------------------------------------------------------------- ssh-agent
AG_FWD = "ssh -A lab@servidor 'ssh-add -l; ssh -o StrictHostKeyChecking=accept-new lab@interno hostname'"
def ag_corpo():
    return f"""
<h2>A ideia: digitar a frase uma vez só</h2>
<p>O <code>ssh-agent</code> é um programa que fica rodando e <strong>guarda a chave já destravada na memória</strong>. Você digita a frase uma vez, no <code>ssh-add</code>, e o ssh pede a chave ao agente nas próximas conexões. Muitos desktops (GNOME, KDE, macOS) já iniciam um agente sozinhos.</p>
<hr>
<h2>1. Iniciar o agente e pôr a chave</h2>
{T("ag-iniciar", "eval \"$(ssh-agent -s)\"", "ssh-add", "ssh-add -l", "ssh lab@servidor hostname", "ssh lab@servidor 'echo de novo, sem frase'", prep=[COM_FRASE], resp=[FRASE(FRASE_LAB, "Enter passphrase")],
   notas={"Agent pid": "o agente está rodando", "Identity added": "a chave destravada está no agente", "(ED25519)": "as chaves que o agente guarda"})}
{ANAT(("ssh-agent -s", "inicia o agente e imprime as variáveis que dizem onde ele está."), ("eval \"$(…)\"", "aplica essas variáveis no terminal atual."), ("ssh-add", "põe as chaves padrão no agente (pede a frase)."), ("ssh-add -l", "lista as chaves do agente."))}
<hr>
<h2>2. Tirar as chaves e parar o agente</h2>
{T("ag-parar", "eval \"$(ssh-agent -s)\"", "ssh-add -q", "ssh-add -t 3600 -q ~/.ssh/id_ed25519", "ssh-add -D", "ssh-add -l", "eval \"$(ssh-agent -k)\"",
   notas={"All identities removed": "o agente esqueceu as chaves", "has no identities": "vazio", "killed": "agente encerrado"})}
<p>O <code>-t 3600</code> põe a chave com prazo: depois de uma hora o agente a esquece sozinho. Bom para computadores compartilhados.</p>
<hr>
<h2>3. Levar o agente junto: <code>-A</code> (com cuidado)</h2>
<p>Com <code>-A</code> (<em>agent forwarding</em>), o servidor pode usar o agente do notebook para entrar em outra máquina, sem a chave privada sair do notebook:</p>
{T("ag-fwd", "eval \"$(ssh-agent -s)\"", "ssh-add -q", AG_FWD, notas={"ana@notebook (ED25519)": "a chave do notebook, vista do servidor", "interno": "o servidor entrou no interno com a chave da Ana"})}
<div class="warning"><strong>Só em servidor de confiança</strong><p>Enquanto a conexão com <code>-A</code> estiver aberta, o administrador do servidor (o root de lá) pode usar o seu agente para entrar onde a sua chave entra. Para pular de máquina em máquina, prefira o <a href="proxyjump.html">ProxyJump (<code>-J</code>)</a>, que não expõe o agente.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Não há agente", "Num terminal sem agente (um servidor, uma sessão de texto), o ssh-add não tem com quem falar:", T("ag-erro", "ssh-add -l"), "Inicie um com <code>eval \"$(ssh-agent -s)\"</code> e rode o <code>ssh-add</code> de novo.")}
"""

def ag_ex():
    return (EX(1, "Pôr a chave", "Que comando põe as suas chaves no agente?", "", "ssh-add") +
            EX(2, "Listar", "Complete para listar as chaves do agente:", "ssh-add ", "-l", rotulo="opção") +
            MC(3, "O ssh-agent guarda:", ["a senha do servidor", "as chaves privadas já destravadas, na memória", "o known_hosts", "os arquivos copiados"], 2) +
            MC(4, "O <code>ssh -A</code> é arriscado porque:", ["deixa a conexão lenta", "o root do servidor pode usar o seu agente enquanto você está conectado", "apaga a chave", "manda a chave privada para o servidor"], 2))

def ag_miss():
    return (M("ag-m1", "inicie um agente, ponha a sua chave nele e liste as chaves.", "eval \"$(ssh-agent -s)\" && ssh-add ~/.ssh/id_ed25519 && ssh-add -l", r"src:ssh-agent;;src:ssh-add -l;;outre:^256 SHA256:\S+ .*\(ED25519\)$", estado="chavelocal") +
            M("ag-m2", "inicie um agente novo e mostre que ele começa vazio.", "eval \"$(ssh-agent -s)\" && ssh-add -l", r"src:ssh-agent;;src:ssh-add -l;;out:The agent has no identities", estado="chavelocal"))

# ---------------------------------------------------------------- permissões
PM_STAT = "stat -c '%a %U %n' ~/.ssh ~/.ssh/*"
PM_RUIM = [["notebook", "root", "chmod 644 /home/ana/.ssh/id_ed25519"]]
PM_HOME = [["servidor", "root", "chmod 777 /home/lab"], ["notebook", "ana", "ssh -o BatchMode=yes lab@servidor true || true"]]
def pm_corpo():
    return f"""
<h2>A ideia: o ssh confere quem pode ler e escrever</h2>
<p>O SSH é desconfiado de propósito. Se a sua chave privada puder ser lida por outros usuários, ou se o <code>authorized_keys</code> do servidor puder ser alterado por outros, ele <strong>ignora</strong> o arquivo. As permissões certas:</p>
<div class="table-wrap"><table class="ref">
<tr><th>Arquivo</th><th>Permissão</th><th>Por quê</th></tr>
<tr><td><code>~/.ssh</code></td><td><code>700</code> (<code>drwx------</code>)</td><td>só você entra na pasta</td></tr>
<tr><td><code>~/.ssh/id_ed25519</code> (privada)</td><td><code>600</code> (<code>-rw-------</code>)</td><td>só você lê o segredo</td></tr>
<tr><td><code>~/.ssh/id_ed25519.pub</code></td><td><code>644</code></td><td>a pública pode ser lida</td></tr>
<tr><td><code>~/.ssh/authorized_keys</code>, <code>config</code></td><td><code>600</code></td><td>ninguém mais altera</td></tr>
<tr><td>a pasta pessoal (<code>~</code>) no servidor</td><td>sem escrita para os outros (<code>755</code> ou <code>700</code>)</td><td>senão, outro usuário poderia trocar o <code>.ssh</code></td></tr>
</table></div>
<hr>
<h2>1. Conferir</h2>
{T("pm-ver", "ls -ld ~/.ssh", PM_STAT)}
<hr>
<h2>2. Chave privada aberta demais</h2>
<p>Alguém (ou um <code>cp</code> descuidado) deixou a chave com <code>644</code>. O ssh se recusa a usá-la e cai para a senha:</p>
{T("pm-aberta", "ls -l ~/.ssh/id_ed25519", "ssh lab@servidor hostname", "chmod 600 ~/.ssh/id_ed25519", "ssh lab@servidor hostname", prep=PM_RUIM, resp=[SENHA],
   notas={"UNPROTECTED PRIVATE KEY FILE": "chave legível por outros", "bad permissions": "o ssh ignorou a chave", "password:": "e caiu para a senha"})}
<hr>
<h2>3. Do lado do servidor: StrictModes</h2>
<p>No servidor, o sshd faz a mesma conferência (opção <code>StrictModes</code>, ligada por padrão). Aqui, a pasta <code>/home/lab</code> ficou com escrita para todos (<code>777</code>). O cliente só vê a chave ser recusada; o motivo aparece no log do servidor. (O Debian e o Ubuntu toleram escrita para o <em>grupo</em> quando o grupo só tem o próprio usuário; escrita para todos, nunca.)</p>
{T("pm-servidor", "ls -ld /home/lab", "sudo grep 'bad ownershi[p]' /var/log/auth.log", quem="servidor", prep=PM_HOME, notas={"drwxrwxrwx": "qualquer um pode escrever: perigoso", "bad ownership or modes": "o sshd recusou o authorized_keys"})}
<p>O <code>[p]</code> no fim do padrão é um truque: assim o <code>grep</code> não acha a linha que o próprio <code>sudo</code> grava no log com o comando. A correção é <code>chmod 755 /home/lab</code> (ou <code>700</code>) no servidor.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Arrumar tudo de uma vez", "Na dúvida, estes três comandos deixam a pasta do notebook como o ssh gosta:", T("pm-arrumar", "chmod 700 ~/.ssh", "chmod 600 ~/.ssh/id_ed25519 ~/.ssh/known_hosts", "chmod 644 ~/.ssh/id_ed25519.pub", PM_STAT, prep=[["notebook", "root", "chmod 777 /home/ana/.ssh; chmod 666 /home/ana/.ssh/*"]]), "Do lado do servidor, o equivalente é <code>chmod 700 ~/.ssh</code> e <code>chmod 600 ~/.ssh/authorized_keys</code>.")}
"""

def pm_ex():
    return (EX(1, "A privada", "Complete a permissão da chave privada:", "chmod ", "600", " ~/.ssh/id_ed25519", rotulo="permissão") +
            EX(2, "A pasta", "Complete a permissão da pasta ~/.ssh:", "chmod ", "700", " ~/.ssh", rotulo="permissão") +
            MC(3, "“UNPROTECTED PRIVATE KEY FILE” quer dizer:", ["a chave tem frase", "outros usuários podem ler a sua chave privada", "a chave é antiga", "o servidor recusou"], 2) +
            MC(4, "No servidor, a pasta pessoal com escrita para todos faz o sshd:", ["pedir a senha duas vezes", "recusar o authorized_keys", "mudar de porta", "apagar a chave"], 2))

def pm_miss():
    return (M("pm-m1", "mostre as permissões da pasta <code>~/.ssh</code> e da sua chave privada em números.", "stat -c '%a %n' ~/.ssh ~/.ssh/id_ed25519", r"src:stat;;outre:^700 \S*\.ssh$;;outre:^600 \S*id_ed25519$") +
            M("pm-m2", "deixe a chave aberta demais de propósito, veja o aviso e conserte.", "chmod 644 ~/.ssh/id_ed25519; ssh -o BatchMode=yes lab@servidor true; chmod 600 ~/.ssh/id_ed25519", r"src:chmod 644;;src:chmod 600;;out:UNPROTECTED PRIVATE KEY FILE"))

# ---------------------------------------------------------------- várias chaves
VC_SO_LAB = [["notebook", "ana", "ssh-keygen -q -t ed25519 -f ~/.ssh/servidor_lab -N '' -C 'chave do lab'"], ["servidor", "root", "cp /srv/guia-ssh-lab/rt/notebook/home/ana/.ssh/servidor_lab.pub /home/lab/.ssh/authorized_keys"]]
VC_V = "ssh -v -i ~/.ssh/servidor_lab lab@servidor true 2>&1 | grep -E 'Will attempt key|Server accepts key'"
VC_CHAVES = "for i in 1 2 3 4 5 6; do ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/k$i; done"
def vc_corpo():
    return f"""
<h2>A ideia: uma chave para cada lugar</h2>
<p>Muita gente tem várias chaves: uma do trabalho, uma do GitHub, uma do servidor de casa. O ssh tenta, em ordem, as chaves do agente e as chaves padrão (<code>id_ed25519</code>, <code>id_rsa</code>…). Para uma chave com outro nome, diga qual com <code>-i</code>.</p>
<hr>
<h2>1. Escolher a chave: <code>-i</code></h2>
<p>No servidor, desta vez, só a chave <code>servidor_lab</code> está instalada. A padrão não entra; com <code>-i</code>, entra:</p>
{T("vc-i", "ssh -o BatchMode=yes lab@servidor hostname", "ssh -i ~/.ssh/servidor_lab lab@servidor hostname", prep=VC_SO_LAB,
   notas={"Permission denied": "a chave padrão não está no servidor"})}
<p>(Na coleta, a cópia da chave para o servidor foi feita antes, por fora.)</p>
{T("vc-ordem", VC_V, prep=VC_SO_LAB, notas={"explicit": "a do -i vem primeiro", "accepts key": "o servidor aceitou esta"})}
<hr>
<h2>2. Chaves demais: “Too many authentication failures”</h2>
<p>O servidor aceita poucas tentativas por conexão (<code>MaxAuthTries</code>, 6 por padrão). Com muitas chaves no agente, o ssh oferece uma por uma e pode ser expulso antes de chegar à certa:</p>
{T("vc-muitas", VC_CHAVES, "eval \"$(ssh-agent -s)\" >/dev/null && ssh-add -q ~/.ssh/k1 ~/.ssh/k2 ~/.ssh/k3 ~/.ssh/k4 ~/.ssh/k5 ~/.ssh/k6", "ssh lab@servidor hostname", "ssh -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 lab@servidor hostname",
   notas={"Too many authentication failures": "esgotou as tentativas", "servidor": "com IdentitiesOnly, só a chave certa"})}
{ANAT(("-o IdentitiesOnly=yes", "usa só as chaves indicadas com <code>-i</code> (ou no config), não todas as do agente."))}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("-i com a chave pública", "O <code>-i</code> recebe a chave <strong>privada</strong> (sem <code>.pub</code>). Com o <code>.pub</code>, o ssh tenta usá-lo como chave privada, reclama das permissões (um <code>.pub</code> é <code>644</code>) e o ignora:", T("vc-erro", "ssh -o BatchMode=yes -i ~/.ssh/servidor_lab.pub lab@servidor hostname", prep=VC_SO_LAB), "Passe o arquivo sem <code>.pub</code>: <code>-i ~/.ssh/servidor_lab</code>.")}
"""

def vc_ex():
    return (EX(1, "Qual chave", "Complete para usar a chave <code>servidor_lab</code>:", "ssh ", "-i", " ~/.ssh/servidor_lab lab@servidor", rotulo="opção") +
            EX(2, "Só a indicada", "Complete a opção que faz o ssh usar só as chaves indicadas:", "ssh -o ", "IdentitiesOnly=yes", " -i ~/.ssh/id_ed25519 lab@servidor") +
            MC(3, "O <code>-i</code> recebe:", ["a chave pública (.pub)", "a chave privada", "o known_hosts", "a senha"], 2) +
            MC(4, "“Too many authentication failures” costuma acontecer quando:", ["a senha está errada", "o agente tem chaves demais e a certa não chega a ser tentada", "o servidor está desligado", "a porta está errada"], 2))

def vc_miss():
    return (M("vc-m1", "entre no servidor indicando a chave com <code>-i</code>.", "ssh -i ~/.ssh/id_ed25519 lab@servidor 'echo usei a chave certa'", r"src:\s-i\s;;outre:^usei a chave certa$") +
            M("vc-m2", "mostre com <code>-v</code> qual chave o servidor aceitou.", "ssh -v -i ~/.ssh/id_ed25519 lab@servidor true 2>&1 | grep 'Server accepts key'", r"src:ssh -v;;src:grep;;outre:^debug1: Server accepts key: "))

NIVEL = {"id": "n2", "nome": "Nível 2 · Chaves", "curto": "Chaves", "desc": "Entrar sem senha: chaves, ssh-copy-id, agente e permissões", "grupos": [
    {"grupo": "Chaves SSH", "aulas": [
        aula(slug="chaves-conceito", menu="Senha ou chave?", title="Senha ou chave SSH? Chave pública, privada e authorized_keys", h1='Senha ou <span class="hl">chave</span>?',
             desc="Como funciona o login com chave SSH: chave privada e pública, o authorized_keys do servidor e o que o ssh -v mostra.",
             intro="Chaves SSH são mais seguras e mais práticas que senhas. Esta aula explica o par de chaves antes de criar o seu.",
             aprender=["A diferença entre chave privada e pública.", "Onde fica cada uma (notebook e servidor).", "Ler a autenticação com <code>ssh -v</code>."],
             corpo=cc_corpo, exercicios=cc_ex, missoes=cc_miss,
             ref=[("~/.ssh/id_ed25519", "chave privada (segredo)."), ("~/.ssh/id_ed25519.pub", "chave pública."), ("~/.ssh/authorized_keys", "no servidor: quem pode entrar."), ("ssh -v", "mostra a conversa.")],
             resumo=["A privada nunca sai do notebook.", "A pública vai para o <code>authorized_keys</code> do servidor.", "O <code>-v</code> mostra qual chave foi aceita."]),
        aula(slug="ssh-keygen", menu="Criando a chave (ssh-keygen)", title="ssh-keygen: criando uma chave SSH ed25519", h1='Criando a chave: <span class="hl">ssh-keygen</span>',
             desc="Gerar um par de chaves ed25519 com ssh-keygen: frase secreta, -C, -f, -N, fingerprint, randomart e RSA 4096.",
             intro="Um comando cria o seu par de chaves. Esta aula mostra as perguntas do ssh-keygen e o que ele grava.",
             aprender=["Gerar uma chave ed25519 com frase.", "Ver o que foi criado sem abrir a privada.", "Gerar sem perguntas, com <code>-f</code> e <code>-N</code>."],
             corpo=kg_corpo, exercicios=kg_ex, missoes=kg_miss,
             ref=[("ssh-keygen -t ed25519 -C \"eu@pc\"", "gera a chave."), ("-f ~/.ssh/nome", "outro nome de arquivo."), ("-N ''", "sem frase."), ("ssh-keygen -lf chave.pub", "impressão digital.")],
             resumo=["Use ed25519.", "Ponha frase na chave do dia a dia.", "Não sobrescreva uma chave em uso."]),
        aula(slug="ssh-copy-id", menu="Instalando a chave (ssh-copy-id)", title="ssh-copy-id: instalando a chave pública no servidor", h1='Instalando a chave: <span class="hl">ssh-copy-id</span>',
             desc="Copiar a chave pública para o authorized_keys do servidor com ssh-copy-id, com -i, e conferir o login sem senha.",
             intro="Com a chave criada, falta levar a parte pública ao servidor. O ssh-copy-id faz isso com uma última senha.",
             aprender=["Instalar a chave com <code>ssh-copy-id</code>.", "Ver o resultado no servidor.", "Escolher a chave com <code>-i</code>."],
             corpo=ci_corpo, exercicios=ci_ex, missoes=ci_miss,
             ref=[("ssh-copy-id lab@servidor", "instala a chave padrão."), ("ssh-copy-id -i arq.pub lab@servidor", "instala outra chave."), ("ssh -o PasswordAuthentication=no …", "prova que entra sem senha.")],
             resumo=["O ssh-copy-id pede a senha uma última vez.", "Ele acerta as permissões no servidor.", "Rodar de novo não duplica."]),
        aula(slug="authorized-keys", menu="authorized_keys à mão e regras", title="authorized_keys: instalando a chave à mão e limitando o que ela faz", h1='O <span class="hl">authorized_keys</span>',
             desc="Instalar uma chave pública sem ssh-copy-id e limitar o que ela pode fazer com command=, from= e restrict no authorized_keys.",
             intro="O authorized_keys é um arquivo de texto comum. Entendê-lo permite instalar chaves em qualquer lugar e dar a cada uma só o acesso necessário.",
             aprender=["Instalar a chave com <code>cat … | ssh … 'cat &gt;&gt;'</code>.", "Limitar uma chave com <code>command=</code> e <code>restrict</code>.", "Entender por que uma chave com <code>from=</code> é recusada."],
             corpo=ak_corpo, exercicios=ak_ex, missoes=ak_miss,
             ref=[("cat chave.pub | ssh srv 'cat >> ~/.ssh/authorized_keys'", "instala à mão."), ('command="cmd",restrict ssh-ed25519 …', "chave de um comando só."), ('from="IP" ssh-ed25519 …', "só desse IP.")],
             resumo=["Uma linha = uma chave que pode entrar.", "Use <code>&gt;&gt;</code>, nunca <code>&gt;</code>.", "Regras na frente da chave limitam o que ela faz."]),
    ]},
    {"grupo": "No dia a dia", "aulas": [
        aula(slug="passphrase", menu="A frase secreta da chave", title="Passphrase: a frase secreta da chave SSH (ssh-keygen -p e -y)", h1='A <span class="hl">frase secreta</span> da chave',
             desc="Para que serve a passphrase da chave SSH, como trocá-la com ssh-keygen -p e como recriar a chave pública com ssh-keygen -y.",
             intro="A frase secreta protege a chave privada no disco. Esta aula mostra como usar, trocar e o que fazer se errar.",
             aprender=["Entrar com uma chave que tem frase.", "Pôr, trocar ou tirar a frase com <code>-p</code>.", "Recriar o <code>.pub</code> com <code>-y</code>."],
             corpo=pp_corpo, exercicios=pp_ex, missoes=pp_miss,
             ref=[("ssh-keygen -p -f chave", "troca a frase."), ("ssh-keygen -y -f chave", "mostra a pública."), ("-P antiga -N nova", "sem perguntas.")],
             resumo=["A frase é conferida no notebook.", "Trocar a frase não muda a chave.", "Frase esquecida não se recupera."]),
        aula(slug="ssh-agent", menu="O agente (ssh-agent e ssh-add)", title="ssh-agent e ssh-add: digitar a frase uma vez só", h1='O agente: <span class="hl">ssh-agent</span>',
             desc="Usar o ssh-agent para guardar a chave destravada: eval ssh-agent, ssh-add, -l, -D, -t, -k e os riscos do agent forwarding (-A).",
             intro="O agente guarda a chave destravada na memória para você não digitar a frase a cada conexão.",
             aprender=["Iniciar o agente e pôr a chave com <code>ssh-add</code>.", "Listar, tirar e pôr prazo nas chaves.", "O que o <code>-A</code> faz e por que tomar cuidado."],
             corpo=ag_corpo, exercicios=ag_ex, missoes=ag_miss,
             ref=[('eval "$(ssh-agent -s)"', "inicia o agente."), ("ssh-add", "põe a chave."), ("ssh-add -l", "lista."), ("ssh-add -D", "tira todas."), ("ssh-add -t 3600", "com prazo.")],
             resumo=["A frase vai uma vez, no <code>ssh-add</code>.", "<code>-t</code> põe prazo na chave.", "<code>-A</code> só em servidor de confiança."]),
        aula(slug="permissoes", menu="Permissões do ~/.ssh", title="Permissões do ~/.ssh: 700, 600 e o UNPROTECTED PRIVATE KEY FILE", h1='Permissões do <span class="hl">~/.ssh</span>',
             desc="As permissões que o SSH exige no cliente e no servidor: 700 no ~/.ssh, 600 na chave privada, StrictModes e o aviso UNPROTECTED PRIVATE KEY FILE.",
             intro="O SSH ignora arquivos que outros possam ler ou alterar. Esta aula mostra as permissões certas e o que acontece com as erradas.",
             aprender=["As permissões certas de cada arquivo.", "O aviso <code>UNPROTECTED PRIVATE KEY FILE</code>.", "O StrictModes do servidor e o log dele."],
             corpo=pm_corpo, exercicios=pm_ex, missoes=pm_miss,
             ref=[("chmod 700 ~/.ssh", "a pasta."), ("chmod 600 ~/.ssh/id_ed25519", "a privada."), ("chmod 600 ~/.ssh/authorized_keys", "no servidor."), ("stat -c '%a %n' arq", "permissão em número.")],
             resumo=["Privada com 600, pasta com 700.", "Chave aberta demais é ignorada.", "No servidor, a pasta pessoal não pode ter escrita para os outros."]),
        aula(slug="varias-chaves", menu="Várias chaves (-i, IdentitiesOnly)", title="Várias chaves SSH: -i, IdentitiesOnly e Too many authentication failures", h1='Várias <span class="hl">chaves</span>',
             desc="Usar várias chaves SSH: escolher com -i, ver a ordem com -v e resolver o Too many authentication failures com IdentitiesOnly.",
             intro="Com mais de uma chave, é preciso dizer ao ssh qual usar. Esta aula mostra como, e o erro clássico de quem tem chaves demais.",
             aprender=["Escolher a chave com <code>-i</code>.", "Ver a ordem das tentativas com <code>-v</code>.", "Usar <code>IdentitiesOnly</code>."],
             corpo=vc_corpo, exercicios=vc_ex, missoes=vc_miss,
             ref=[("ssh -i ~/.ssh/chave srv", "usa esta chave."), ("-o IdentitiesOnly=yes", "só as indicadas."), ("ssh -v … | grep 'Will attempt'", "ordem das chaves.")],
             resumo=["<code>-i</code> recebe a privada.", "Chaves demais esgotam as tentativas.", "<code>IdentitiesOnly=yes</code> resolve."]),
    ]},
]}
