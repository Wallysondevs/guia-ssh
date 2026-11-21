# -*- coding: utf-8 -*-
"""Nível 1 · Base: o que é SSH, o laboratório, a primeira conexão e comandos remotos."""
from lib_guia import *
from respostas import *

def aula(**k):
    return k

# ---------------------------------------------------------------- introdução
def intro_corpo():
    return f"""
<h2>A ideia: um terminal em outro computador</h2>
<p>O <strong>SSH</strong> (<em>Secure Shell</em>, “casca segura”) é o jeito padrão de usar o terminal de <strong>outro computador</strong> pela rede. Você digita no seu teclado, e os comandos rodam lá, no servidor. Tudo o que vai e volta é <strong>criptografado</strong>: quem estiver no meio do caminho (o Wi-Fi do café, o provedor) não consegue ler as senhas nem os arquivos.</p>
<p>É com SSH que se administra quase todo servidor Linux do mundo, que se envia código para o GitHub e que se copiam arquivos entre máquinas. Uma provinha: do notebook da Ana, um comando que roda no servidor e devolve a resposta:</p>
{T("intro-prova", "ssh lab@servidor hostname", "ssh lab@servidor 'whoami; pwd'", notas={"servidor": "quem respondeu foi o servidor", "/home/lab": "a pasta do usuário lab, lá no servidor"})}
<hr>
<h2>Cliente e servidor</h2>
<p>Toda conexão SSH tem dois lados:</p>
<div class="table-wrap"><table class="ref">
<tr><th>Lado</th><th>Programa</th><th>Neste guia</th></tr>
<tr><td><strong>Cliente</strong>: de onde você se conecta</td><td><code>ssh</code> (e <code>scp</code>, <code>sftp</code>, <code>ssh-keygen</code>…)</td><td>o <code>notebook</code>, com a usuária <code>ana</code></td></tr>
<tr><td><strong>Servidor</strong>: onde os comandos rodam</td><td><code>sshd</code>, o “daemon” que fica esperando conexões na <strong>porta 22</strong></td><td>o <code>servidor</code>, com o usuário <code>lab</code></td></tr>
</table></div>
<p>Os dois programas vêm do projeto <strong>OpenSSH</strong>, o mesmo no Linux, no macOS e no Windows 10/11. Veja a versão do seu cliente:</p>
{T("intro-versao", "ssh -V", notas={"OpenSSH_10.0p2": "a versão usada em todo o guia"})}
{ANAT(("ssh", "o cliente SSH."), ("-V", "maiúsculo: mostra a versão e sai (o <code>-v</code> minúsculo é outra coisa, “verboso”, e aparece no Nível 5)."))}
<p>No servidor, o <code>sshd</code> fica rodando o tempo todo. No laboratório, o usuário <code>lab</code> pode conferir que ele está lá, ouvindo a porta 22:</p>
{T("intro-sshd", "ps -C sshd -o pid,cmd", quem="servidor")}
<hr>
<h2>O formato do comando</h2>
<pre class="cmd">
ssh usuario@computador comando
</pre>
<ul>
<li><code>usuario</code>: a conta <strong>no servidor</strong> (pode ser diferente do seu usuário no notebook).</li>
<li><code>computador</code>: o nome ou o IP do servidor (<code>servidor</code>, <code>192.168.0.20</code>…).</li>
<li><code>comando</code> (opcional): se você passar um comando, ele roda lá e o ssh volta. Sem comando, você entra numa sessão no servidor, como na <a href="primeira-conexao.html">próxima aula</a>.</li>
</ul>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Nome errado", "Se o nome do computador estiver errado, o ssh nem chega a tentar conectar. Na coleta, digitamos “servidr”:", T("intro-erro", "ssh lab@servidr hostname"), "“Could not resolve hostname” quer dizer: não sei que computador é esse. Confira o nome ou use o IP.")}
"""

def intro_ex():
    return (EX(1, "O cliente", "Qual programa você roda no seu computador para se conectar?", "", "ssh") +
            EX(2, "A versão", "Complete para ver a versão do cliente:", "ssh ", "-V") +
            MC(3, "Em <code>ssh lab@servidor hostname</code>, quem é <code>lab</code>?", ["O nome do servidor", "A conta de usuário no servidor", "A senha", "O comando"], 2) +
            MC(4, "Por padrão, o <code>sshd</code> espera conexões na porta:", ["80", "443", "22", "2222"], 3))

def intro_miss():
    return (M("intro-m1", "mostre a versão do seu cliente SSH.", "ssh -V", r"src:\bssh -V\b;;outre:^OpenSSH_\d+\.\d+") +
            M("intro-m2", "rode no servidor um <code>echo</code> que mostre o nome dele.", "ssh lab@servidor 'echo conectado em $(hostname)'", r"src:^ssh\b;;src:hostname;;outre:^conectado em \S+$"))

# ---------------------------------------------------------------- preparando
def prep_corpo():
    return f"""
<h2>A ideia: um laboratório só seu</h2>
<p>Para aprender SSH você precisa de <strong>dois computadores</strong>: um cliente e um servidor. Não precisa comprar nada nem alugar servidor na internet. Qualquer uma destas opções serve:</p>
<ul>
<li><strong>Dois computadores em casa</strong> (um notebook e um PC velho, um Raspberry Pi…), na mesma rede.</li>
<li><strong>Uma máquina virtual</strong> (VirtualBox, GNOME Boxes) com Debian ou Ubuntu, fazendo o papel de servidor.</li>
<li><strong>Um computador só</strong>: o servidor SSH roda no próprio Linux, e você se conecta em <code>localhost</code>. Tudo funciona igual, só que os dois lados são a mesma máquina.</li>
</ul>
<p>Os exemplos do guia usam três computadores fictícios, todos numa rede de teste:</p>
<div class="table-wrap"><table class="ref">
<tr><th>Computador</th><th>IP</th><th>Usuário</th><th>Papel</th></tr>
<tr><td><code>notebook</code></td><td>192.168.0.10</td><td><code>ana</code></td><td>o cliente: de onde a Ana se conecta</td></tr>
<tr><td><code>servidor</code></td><td>192.168.0.20</td><td><code>lab</code></td><td>o servidor SSH principal</td></tr>
<tr><td><code>interno</code></td><td>192.168.0.130</td><td><code>lab</code></td><td>uma máquina que só o servidor alcança (aparece no Nível 4)</td></tr>
</table></div>
<hr>
<h2>1. No servidor: instalar o sshd e criar o usuário lab</h2>
<p>No computador que vai ser o servidor (Debian ou Ubuntu), instale o servidor SSH e crie o usuário de teste <code>lab</code>, com uma senha que você vai lembrar e permissão de usar <code>sudo</code>:</p>
<pre class="cmd">
sudo apt install openssh-server
sudo adduser lab
sudo adduser lab sudo
</pre>
<p>Depois, entre como <code>lab</code> (<code>sudo -iu lab</code>) e crie os arquivos de exemplo com o script <a href="arquivos/preparar-servidor.sh"><code>preparar-servidor.sh</code></a>: <code>bash preparar-servidor.sh</code>. Ele cria o <code>relatorio.txt</code> e uma página em <code>site/</code>.</p>
<p>Descubra o IP do servidor com <code>ip -br addr</code>. No laboratório, o servidor tem duas placas de rede, uma para cada rede de teste:</p>
{T("prep-ip-servidor", "hostname", "ip -br addr", quem="servidor", notas={"192.168.0.20/25": "o IP que o notebook usa"})}
<hr>
<h2>2. No notebook: dar um nome ao servidor</h2>
<p>Para escrever <code>servidor</code> em vez do IP, acrescente uma linha ao <code>/etc/hosts</code> do notebook, <strong>com o IP do seu servidor</strong> (se for o mesmo computador, use <code>127.0.0.1</code>):</p>
<pre class="cmd">
echo "192.168.0.20 servidor" | sudo tee -a /etc/hosts
</pre>
<p>E crie os arquivos de exemplo do lado do cliente com o <a href="arquivos/preparar-notebook.sh"><code>preparar-notebook.sh</code></a>: <code>bash preparar-notebook.sh</code>, na sua pasta pessoal. No laboratório, o notebook ficou assim:</p>
{T("prep-notebook", "hostname", "getent hosts servidor", "ping -c 2 servidor", "ls", estado="zero")}
{ANAT(("getent hosts servidor", "mostra que IP o nome <code>servidor</code> tem para este computador."), ("ping -c 2", "manda dois “pings”: se voltarem, a rede até o servidor funciona."))}
<div class="tip"><strong>O cliente já vem instalado</strong><p>O <code>ssh</code> (pacote <code>openssh-client</code>) vem em quase todo Linux, no macOS e no Windows 10/11. Só o servidor precisa do <code>openssh-server</code>.</p></div>
<hr>
<h2>3. O resto do laboratório</h2>
<p>Algumas aulas de túneis usam duas páginas de teste. Quando chegar lá, deixe-as rodando num terminal à parte:</p>
<pre class="cmd">
cd ~/site && python3 -m http.server -b 127.0.0.1 8080     # no servidor, como lab
cd ~/site && python3 -m http.server -b 127.0.0.1 3000     # no notebook, como você
</pre>
<p>A máquina <code>interno</code> é opcional. Sem ela, as aulas mostram como fazer o mesmo com o próprio servidor.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("O servidor SSH não está rodando", "Se o <code>openssh-server</code> não estiver instalado, ou o serviço estiver parado, a conexão é recusada na hora. Na coleta, paramos o sshd de propósito:", T("prep-erro", "ssh lab@servidor", prep=[["servidor", "root", "kill $(cat /run/sshd.pid)"]]), "“Connection refused”: o computador existe e respondeu, mas ninguém atende na porta 22. No servidor, confira com <code>sudo systemctl status ssh</code>.")}
"""

def prep_ex():
    return (EX(1, "O pacote do servidor", "Complete o comando que instala o servidor SSH:", "sudo apt install ", "openssh-server") +
            EX(2, "Usuário de teste", "Complete para criar o usuário <code>lab</code> no servidor:", "sudo adduser ", "lab") +
            MC(3, "Em que arquivo do notebook se dá um nome a um IP?", ["<code>~/.bashrc</code>", "<code>/etc/hosts</code>", "<code>/etc/ssh/sshd_config</code>", "<code>~/notas.txt</code>"], 2) +
            MC(4, "Dá para aprender SSH com um computador só?", ["Não, precisa de dois", "Sim, conectando em <code>localhost</code>", "Só no Windows", "Só com internet"], 2))

def prep_miss():
    return (M("prep-m1", "veja que IP o nome <code>servidor</code> tem no seu notebook.", "getent hosts servidor", r"src:\bgetent hosts\b;;outre:^\d+\.\d+\.\d+\.\d+\s+servidor$") +
            M("prep-m2", "no servidor, mostre o processo do <code>sshd</code> que espera conexões.", "ps -C sshd -o cmd", r"src:\bps\b;;src:sshd;;outre:^sshd: \S+ \[listener\]", quem="servidor"))

# ---------------------------------------------------------------- primeira conexão
def pc_corpo():
    return f"""
<h2>A ideia: entrar no servidor</h2>
<p>Sem comando no fim, o <code>ssh</code> abre uma <strong>sessão</strong>: o prompt muda para o do servidor, e tudo o que você digita roda lá, até sair com <code>exit</code>.</p>
<hr>
<h2>1. A primeira vez: a pergunta do “fingerprint”</h2>
<p>Na primeira conexão com um servidor, o ssh ainda não conhece a <strong>chave do servidor</strong> (a “identidade” dele) e pergunta se você confia. Foi assim no notebook da Ana, que ainda nunca tinha se conectado:</p>
{T("pc-primeira", "ssh lab@servidor", estado="zero", resp=[SIM, SENHA, NO("servidor", "hostname"), NO("servidor", "whoami"), NO("servidor", "exit")],
   notas={"key fingerprint": "a impressão digital da chave do servidor", "(yes/no": "a Ana digitou yes", "Permanently added": "guardado em ~/.ssh/known_hosts", "password:": "a senha não aparece enquanto você digita", "lab@servidor:~$ hostname": "agora o prompt é do servidor", "closed": "de volta ao notebook"})}
<p>Passo a passo:</p>
<ol class="passo">
<li><strong>“The authenticity of host … can't be established”</strong>: o ssh nunca viu este servidor. Ele mostra a <strong>impressão digital</strong> (<em>fingerprint</em>) da chave dele, um resumo como <code>SHA256:…</code>.</li>
<li>Você responde <code>yes</code> (por extenso). O ssh guarda a chave em <code>~/.ssh/known_hosts</code> e não pergunta de novo.</li>
<li>Vem a <strong>senha</strong> do usuário <code>lab</code> no servidor. Nada aparece enquanto você digita: nem bolinhas. É normal.</li>
<li>Pronto: o prompt agora é <code>lab@servidor</code>. O <code>exit</code> fecha a sessão (o Bash do servidor, em português, responde “sair”).</li>
</ol>
<div class="warning"><strong>Confira a impressão digital</strong><p>O certo é comparar o fingerprint com o do servidor antes de digitar <code>yes</code>. A aula <a href="known-hosts.html">known_hosts</a> mostra como ver o fingerprint no próprio servidor.</p></div>
<hr>
<h2>2. Da segunda vez em diante</h2>
<p>Com a chave do servidor guardada, o ssh vai direto para a senha:</p>
{T("pc-segunda", "ssh lab@servidor", estado="conhecido", resp=[SENHA, NO("servidor", "exit")])}
<hr>
<h2>3. E se eu não disser o usuário?</h2>
<p>Sem o <code>usuario@</code>, o ssh usa o <strong>seu nome no notebook</strong>. Aqui, a Ana digitou só <code>ssh servidor</code>: o ssh pediu a senha de <code>ana</code>, uma conta que não é dela no servidor, e as tentativas falharam:</p>
{T("pc-sem-usuario", "ssh -o NumberOfPasswordPrompts=2 servidor", estado="conhecido", resp=[ERRADA(1), ERRADA(2)], notas={"ana@servidor's password": "o ssh supôs o usuário ana"})}
<p>O <code>-o NumberOfPasswordPrompts=2</code> só encurtou a demonstração (o normal são 3 tentativas). A solução é dizer o usuário certo: <code>ssh lab@servidor</code>. A aula <a href="ssh-config.html">~/.ssh/config</a> mostra como não precisar repetir isso.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Responder “no” à pergunta", "Se você responder <code>no</code> (ou só apertar Enter), o ssh desiste, e nada é guardado:", T("pc-erro", "ssh lab@servidor", estado="zero", resp=[NAO]), "“Host key verification failed.” aqui só quer dizer “você não confirmou”. Rode de novo e responda <code>yes</code> por extenso.")}
"""

def pc_ex():
    return (EX(1, "A resposta", "O que digitar na pergunta da primeira conexão para aceitar?", "", "yes") +
            EX(2, "Sair", "Que comando fecha a sessão no servidor?", "", ["exit", "logout"]) +
            MC(3, "Onde o ssh guarda a chave dos servidores que você aceitou?", ["<code>~/.ssh/known_hosts</code>", "<code>/etc/hosts</code>", "<code>~/.bashrc</code>", "<code>/etc/passwd</code>"], 1) +
            MC(4, "Por que nada aparece quando você digita a senha?", ["O teclado travou", "É proposital: a senha não é mostrada", "Precisa apertar Ctrl", "O servidor caiu"], 2))

def pc_miss():
    return (M("pc-m1", "conecte pela primeira vez e rode <code>hostname</code> no servidor (aceite a chave com <code>yes</code> e digite a senha).", "ssh lab@servidor hostname",
              r"src:^ssh\b;;out:Permanently added", estado="zero", resp=[SIM, SENHA]) +
            M("pc-m2", "rode no servidor um <code>echo</code> com o nome dele.", "ssh lab@servidor 'echo Olá do $(hostname)'", r"src:^ssh\b;;outre:^Olá do \S+", estado="conhecido", resp=[SENHA]))

# ---------------------------------------------------------------- known_hosts
KH_LF = "ssh-keyscan -t ed25519 servidor 2>/dev/null | ssh-keygen -lf -"
def kh_corpo():
    return f"""
<h2>A ideia: a agenda de servidores conhecidos</h2>
<p>Cada servidor SSH tem um <strong>par de chaves de host</strong>, criado quando o <code>openssh-server</code> é instalado. Quando você aceita a chave na primeira conexão, o ssh anota no arquivo <code>~/.ssh/known_hosts</code>: “este nome tem esta chave”. Nas próximas vezes, ele confere. Se a chave mudar, o ssh <strong>se recusa a conectar</strong>, porque alguém pode estar fingindo ser o seu servidor (o ataque “homem do meio”).</p>
<hr>
<h2>1. O arquivo known_hosts</h2>
{T("kh-arquivo", "ls -l ~/.ssh", "cat ~/.ssh/known_hosts", estado="conhecido", notas={"|1|": "o nome vem embaralhado (HashKnownHosts)"})}
<p>No Debian e no Ubuntu os nomes ficam <strong>embaralhados</strong> (<code>|1|…</code>), para que ninguém descubra, lendo o arquivo, em que servidores você entra. Para procurar um servidor, use o <code>ssh-keygen -F</code>:</p>
{T("kh-procurar", "ssh-keygen -F servidor", estado="conhecido", notas={"found: line 1": "achou: linha 1 do arquivo"})}
<hr>
<h2>2. Conferir a impressão digital no servidor</h2>
<p>Antes de digitar <code>yes</code>, compare o fingerprint com o do servidor. Quem tem acesso ao servidor (pelo console, por exemplo) vê assim:</p>
{T("kh-servidor", "ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub", quem="servidor", notas={"SHA256:": "tem de ser igual ao da pergunta"})}
{ANAT(("ssh-keygen -l", "mostra o fingerprint de uma chave."), ("-f arquivo", "qual chave."), ("ssh_host_ed25519_key.pub", "a parte pública da chave de host do tipo ED25519."))}
<p>Do lado do cliente, o <code>ssh-keyscan</code> pergunta a chave ao servidor sem fazer login. Junto com o <code>ssh-keygen -lf -</code>, mostra o mesmo fingerprint:</p>
{T("kh-keyscan", "ssh-keyscan -t ed25519 servidor", KH_LF, estado="zero")}
<p>As duas impressões digitais batem com a da pergunta da primeira conexão. Só confie se forem iguais.</p>
<hr>
<h2>3. Esquecer um servidor: <code>ssh-keygen -R</code></h2>
<p>Se o servidor foi reinstalado (e por isso ganhou chaves novas), apague a entrada antiga:</p>
{T("kh-remover", "ssh-keygen -R servidor", estado="conhecido", notas={"retained as": "ele guarda uma cópia do arquivo antigo"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Conferência rígida", "Com <code>StrictHostKeyChecking=yes</code> (comum em scripts), o ssh não pergunta nada: se não conhece o servidor, recusa:", T("kh-erro", "ssh -o StrictHostKeyChecking=yes lab@servidor hostname", estado="zero"), "Em scripts, prefira guardar a chave antes (com <code>ssh-keyscan</code>, conferindo o fingerprint) a desligar a conferência.")}
"""

def kh_ex():
    return (EX(1, "Procurar", "Complete para procurar o servidor no known_hosts:", "ssh-keygen ", "-F", " servidor", rotulo="opção") +
            EX(2, "Apagar", "Complete para apagar a entrada do servidor:", "ssh-keygen ", "-R", " servidor", rotulo="opção") +
            MC(3, "Por que o ssh guarda a chave do servidor?", ["Para ir mais rápido", "Para perceber se outro computador fingir ser o servidor", "Para guardar a senha", "Para economizar internet"], 2) +
            MC(4, "Os nomes no known_hosts aparecem como <code>|1|…</code> porque:", ["o arquivo está corrompido", "estão embaralhados de propósito (HashKnownHosts)", "são senhas", "o ssh é antigo"], 2))

def kh_miss():
    return (M("kh-m1", "procure o <code>servidor</code> no seu known_hosts.", "ssh-keygen -F servidor", r"src:ssh-keygen -F;;out:# Host servidor found", estado="conhecido") +
            M("kh-m2", "mostre o fingerprint da chave ED25519 do servidor sem fazer login.", KH_LF, r"src:ssh-keyscan;;src:ssh-keygen -lf;;outre:^256 SHA256:\S+ .*\(ED25519\)$", estado="zero"))

# ---------------------------------------------------------------- comando remoto
CR_PIPE = "ssh lab@servidor 'cat relatorio.txt' | grep vendas"
def cr_corpo():
    return f"""
<h2>A ideia: um comando, sem entrar</h2>
<p>Muitas vezes você só quer <strong>uma resposta</strong> do servidor. Ponha o comando depois do endereço: o ssh conecta, roda, mostra a saída e volta. Daqui em diante, o notebook da Ana já tem <a href="ssh-keygen.html">chave SSH</a> instalada no servidor, então não aparece a pergunta da senha.</p>
{T("cr-simples", "ssh lab@servidor hostname", "ssh lab@servidor ls", "ssh lab@servidor cat relatorio.txt")}
<hr>
<h2>1. As aspas: quem expande o quê</h2>
<p>O Bash do <strong>notebook</strong> lê o comando antes do ssh. Sem aspas simples, ele troca <code>$HOSTNAME</code> pelo nome do notebook antes de mandar. Com aspas simples, o texto vai intacto e quem expande é o Bash do servidor:</p>
{T("cr-aspas", "ssh lab@servidor echo $HOSTNAME", "ssh lab@servidor 'echo $HOSTNAME'", notas={"notebook": "expandido no notebook!", "servidor": "expandido no servidor"})}
<div class="tip"><strong>Regra prática</strong><p>Ponha o comando remoto entre <strong>aspas simples</strong>. Assim ele chega ao servidor exatamente como você escreveu.</p></div>
<hr>
<h2>2. Pipes dos dois lados</h2>
<p>Um <code>|</code> fora das aspas roda <strong>no notebook</strong>, com a saída que veio do servidor. Dentro das aspas, roda <strong>no servidor</strong>. O resultado é o mesmo; muda onde o trabalho acontece:</p>
{T("cr-pipe", CR_PIPE, "ssh lab@servidor 'grep vendas relatorio.txt'", "ssh lab@servidor 'cat relatorio.txt' > copia.txt", "cat copia.txt")}
<p>O <code>&gt; copia.txt</code> fora das aspas gravou a saída do servidor num arquivo <strong>do notebook</strong>: um jeito simples de trazer um arquivo de texto.</p>
<hr>
<h2>3. O código de saída e o terminal</h2>
<p>O ssh devolve o código de saída do comando remoto, então dá para usar em scripts com <code>&amp;&amp;</code> e <code>if</code>:</p>
{T("cr-status", "ssh lab@servidor 'ls naoexiste'; echo \"código: $?\"")}
<p>Um comando remoto não ganha um terminal de verdade (um “tty”). Programas de tela cheia, como <code>top</code> ou <code>nano</code>, precisam de um: peça com <code>-t</code>.</p>
{T("cr-tty", "ssh lab@servidor tty", "ssh -t lab@servidor tty", notas={"não é um tty": "sem -t, não há terminal", "/dev/pts/": "com -t, há"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Esqueci as aspas no &&", "Sem aspas, o <code>&amp;&amp;</code> é do Bash do notebook: só o <code>cd</code> foi para o servidor, e o <code>pwd</code> rodou no notebook:", T("cr-erro", "ssh lab@servidor cd /etc && pwd"), "Com aspas, <code>ssh lab@servidor 'cd /etc &amp;&amp; pwd'</code> roda os dois no servidor e mostra <code>/etc</code>.")}
"""

def cr_ex():
    return (EX(1, "Aspas", "Que tipo de aspas manda o comando intacto para o servidor?", "", ["simples", "aspas simples", "'"]) +
            EX(2, "Terminal", "Complete para pedir um terminal para o comando remoto:", "ssh ", "-t", " lab@servidor top", rotulo="opção") +
            MC(3, "Em <code>ssh lab@servidor 'cat relatorio.txt' | grep vendas</code>, o <code>grep</code> roda:", ["no servidor", "no notebook", "nos dois", "em nenhum"], 2) +
            MC(4, "<code>ssh lab@servidor echo $HOSTNAME</code> mostra:", ["o nome do servidor", "o nome do notebook", "um erro", "nada"], 2))

def cr_miss():
    return (M("cr-m1", "faça o servidor dizer o próprio nome, com a variável <code>$HOSTNAME</code> expandida lá.", "ssh lab@servidor 'echo \"remoto: $HOSTNAME\"'", r"src:^ssh\b;;src:'[^']*\$HOSTNAME[^']*';;outre:^remoto: [^$\s]+$") +
            M("cr-m2", "rode um <code>ls</code> de um arquivo que não existe no servidor e mostre o código de saída que o ssh devolveu.", "ssh lab@servidor 'ls naoexiste'; echo \"código: $?\"", r"src:^ssh\b;;src:\$\?;;outre:^código: 2$"))

# ---------------------------------------------------------------- sessão remota
def sr_corpo():
    return f"""
<h2>A ideia: trabalhar lá dentro</h2>
<p>Numa sessão SSH, o prompt avisa onde você está: <code>ana@notebook</code> é o seu computador; <code>lab@servidor</code> é o servidor. Parece óbvio, mas apagar arquivos no computador errado é o erro mais comum de quem começa. <strong>Olhe o prompt antes de cada comando importante.</strong></p>
<hr>
<h2>1. Uma sessão de trabalho</h2>
{T("sr-sessao", "ssh lab@servidor", resp=[NO("servidor", "pwd"), NO("servidor", "ls -l"), NO("servidor", "cat relatorio.txt"), NO("servidor", "sudo whoami"), NO("servidor", "exit")],
   notas={"sudo whoami": "o sudo no servidor vale para o servidor"})}
<p>Comandos de administração, como <code>sudo apt update</code>, funcionam igual: rodam no servidor, com os privilégios do usuário <code>lab</code> de lá.</p>
<hr>
<h2>2. As teclas de escape do ssh: <code>~?</code> e <code>~.</code></h2>
<p>O cliente ssh tem atalhos próprios, que começam com <code>~</code> logo depois de um Enter. O <code>~?</code> mostra a lista:</p>
{T("sr-escape", "ssh lab@servidor", resp=[NO("servidor", ""), ["lab@servidor:~\\$ ", "~?"], ["~\\.", "exit\n"]], notas={"~.": "derruba a conexão na hora"})}
<p>O mais útil é o <code>~.</code>: quando a rede cai e a sessão congela, ele <strong>fecha a conexão travada</strong> sem você ter de fechar o terminal:</p>
{T("sr-matar", "ssh lab@servidor", resp=[NO("servidor", ""), ["lab@servidor:~\\$ ", "~."]], notas={"closed": "o ssh fechou a conexão"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("O programa não existe no servidor", "Cada computador tem os seus programas. O <code>htop</code> existe no notebook? Não importa: o comando roda no servidor, e lá ele não foi instalado:", T("sr-erro", "ssh lab@servidor htop"), "A mensagem vem do Bash do <strong>servidor</strong> (“linha 1” é a do comando que o ssh mandou). Instale lá com <code>sudo apt install htop</code>, ou use outro comando.")}
"""

def sr_ex():
    return (EX(1, "Onde estou?", "No prompt <code>lab@servidor:~$</code>, qual é o computador?", "", "servidor") +
            EX(2, "Conexão travada", "Que escape do ssh derruba uma conexão congelada (depois de um Enter)?", "", "~.") +
            MC(3, "Na sessão, <code>sudo apt update</code> atualiza:", ["o notebook", "o servidor", "os dois", "nenhum"], 2) +
            MC(4, "O <code>~?</code> só funciona:", ["no começo de uma linha (logo depois de um Enter)", "no fim da linha", "dentro do nano", "com sudo"], 1))

def sr_miss():
    return (M("sr-m1", "entre no servidor, rode <code>pwd</code> e saia com <code>exit</code>. Cole a sessão inteira.", "ssh lab@servidor", r"src:^ssh\b;;outre:^\S+@\S+:~\$ pwd$;;outre:^Connection to \S+ closed\.$",
              resp=[NO("servidor", "pwd"), NO("servidor", "exit")]) +
            M("sr-m2", "rode <code>sudo whoami</code> no servidor sem abrir uma sessão.", "ssh -t lab@servidor 'sudo whoami'", r"src:^ssh\b;;src:sudo whoami;;outre:^root$"))

NIVEL = {"id": "n1", "nome": "Nível 1 · Base", "curto": "Base", "desc": "O que é SSH, o laboratório, a primeira conexão e comandos remotos", "grupos": [
    {"grupo": "Começando", "aulas": [
        aula(slug="introducao", menu="O que é SSH", title="O que é SSH: cliente, servidor e porta 22", h1='O que é <span class="hl">SSH</span>',
             desc="Introdução ao Guia SSH: para que serve o SSH, a diferença entre cliente (ssh) e servidor (sshd), a porta 22 e o formato do comando.",
             intro="O SSH abre um terminal seguro em outro computador. Esta aula mostra o que ele faz, quem é cliente e quem é servidor, e o formato do comando.",
             aprender=["O que é SSH e por que ele é seguro.", "A diferença entre o cliente <code>ssh</code> e o servidor <code>sshd</code>.", "O formato <code>ssh usuario@computador comando</code>."],
             corpo=intro_corpo, exercicios=intro_ex, missoes=intro_miss,
             ref=[("ssh -V", "versão do cliente."), ("ssh usuario@computador", "abre uma sessão."), ("ssh usuario@computador comando", "roda um comando e volta.")],
             resumo=["SSH = terminal seguro em outro computador.", "Cliente <code>ssh</code>, servidor <code>sshd</code>, porta 22.", "<code>usuario</code> é a conta no servidor."]),
        aula(slug="preparando", menu="O laboratório: notebook e servidor", title="Montando o laboratório de SSH: notebook e servidor", h1='O <span class="hl">laboratório</span>: notebook e servidor',
             desc="Como montar um laboratório de SSH em casa: instalar o openssh-server, criar o usuário lab, dar nome ao servidor no /etc/hosts e criar os arquivos de exemplo.",
             intro="Para praticar você precisa de um cliente e de um servidor. Pode ser dois computadores, uma máquina virtual ou um computador só.",
             aprender=["Instalar o servidor SSH e criar o usuário de teste.", "Dar um nome ao servidor no <code>/etc/hosts</code>.", "Conferir a rede com <code>getent</code> e <code>ping</code>."],
             corpo=prep_corpo, exercicios=prep_ex, missoes=prep_miss,
             ref=[("sudo apt install openssh-server", "instala o servidor."), ("sudo adduser lab", "cria o usuário de teste."), ("ip -br addr", "mostra os IPs."), ("getent hosts servidor", "que IP tem o nome.")],
             resumo=["O servidor precisa do <code>openssh-server</code>; o cliente já vem instalado.", "Dê um nome ao IP no <code>/etc/hosts</code>.", "“Connection refused”: ninguém atende na porta 22."]),
    ]},
    {"grupo": "Primeiros passos", "aulas": [
        aula(slug="primeira-conexao", menu="A primeira conexão", title="A primeira conexão SSH: fingerprint, yes e senha", h1='A primeira <span class="hl">conexão</span>',
             desc="A primeira conexão com ssh: a pergunta do fingerprint, o yes, a senha que não aparece, o prompt do servidor e o exit.",
             intro="Na primeira vez, o ssh pergunta se você confia no servidor. Esta aula mostra a conversa inteira, de verdade.",
             aprender=["Entender a pergunta “authenticity of host”.", "Entrar com senha e sair com <code>exit</code>.", "Por que dizer o usuário no <code>usuario@</code>."],
             corpo=pc_corpo, exercicios=pc_ex, missoes=pc_miss,
             ref=[("ssh lab@servidor", "entra no servidor."), ("yes", "aceita a chave do servidor."), ("exit", "sai da sessão.")],
             resumo=["A primeira conexão pergunta pelo fingerprint: responda <code>yes</code> por extenso.", "A senha não aparece enquanto você digita.", "Sem <code>usuario@</code>, o ssh usa o seu nome local."]),
        aula(slug="known-hosts", menu="known_hosts e fingerprints", title="known_hosts, fingerprint e ssh-keyscan", h1='<span class="hl">known_hosts</span> e fingerprints',
             desc="Como o ssh guarda e confere a chave dos servidores no ~/.ssh/known_hosts: ssh-keygen -F, -R, -lf e ssh-keyscan.",
             intro="O known_hosts é a agenda de servidores em que você já confiou. Esta aula mostra como ler, conferir e limpar essa agenda.",
             aprender=["Procurar e apagar entradas com <code>ssh-keygen -F</code> e <code>-R</code>.", "Conferir o fingerprint no servidor.", "Ler a chave de um servidor com <code>ssh-keyscan</code>."],
             corpo=kh_corpo, exercicios=kh_ex, missoes=kh_miss,
             ref=[("ssh-keygen -F servidor", "procura no known_hosts."), ("ssh-keygen -R servidor", "apaga do known_hosts."), ("ssh-keygen -lf arquivo.pub", "fingerprint de uma chave."), ("ssh-keyscan servidor", "pergunta a chave do servidor.")],
             resumo=["O known_hosts protege contra servidor falso.", "Confira o fingerprint antes do <code>yes</code>.", "Servidor reinstalado: <code>ssh-keygen -R</code>."]),
        aula(slug="comando-remoto", menu="Comandos remotos", title="Rodando comandos remotos com ssh: aspas, pipes e -t", h1='Comandos <span class="hl">remotos</span>',
             desc="Rodar um comando no servidor sem abrir sessão: aspas simples, pipes no notebook e no servidor, código de saída e o -t.",
             intro="Um comando depois do endereço roda no servidor e volta. O segredo está nas aspas: elas decidem quem expande o quê.",
             aprender=["Rodar um comando remoto e trazer a saída.", "Usar aspas para o comando chegar intacto.", "Pipes, redirecionamento e o <code>-t</code>."],
             corpo=cr_corpo, exercicios=cr_ex, missoes=cr_miss,
             ref=[("ssh lab@servidor 'comando'", "roda no servidor."), ("ssh lab@servidor 'cmd' | grep x", "grep no notebook."), ("ssh lab@servidor 'cmd' > arq", "grava no notebook."), ("ssh -t lab@servidor top", "com terminal.")],
             resumo=["Aspas simples: o comando chega intacto.", "Fora das aspas, pipes e <code>&gt;</code> são do notebook.", "<code>-t</code> para programas de tela cheia."]),
        aula(slug="sessao-remota", menu="Trabalhando no servidor", title="Trabalhando numa sessão SSH: prompt, sudo e escapes (~. e ~?)", h1='Trabalhando no <span class="hl">servidor</span>',
             desc="Como trabalhar numa sessão SSH: ler o prompt, usar sudo no servidor e as teclas de escape do ssh, como ~. para derrubar uma conexão travada.",
             intro="Dentro da sessão, tudo roda no servidor. Esta aula ensina a não se perder e a sair de uma conexão travada.",
             aprender=["Ler o prompt para saber onde está.", "Usar <code>sudo</code> no servidor.", "Os escapes <code>~?</code> e <code>~.</code>."],
             corpo=sr_corpo, exercicios=sr_ex, missoes=sr_miss,
             ref=[("Enter ~.", "derruba a conexão."), ("Enter ~?", "lista os escapes."), ("exit", "sai normalmente.")],
             resumo=["Olhe o prompt antes de cada comando importante.", "<code>~.</code> fecha uma conexão congelada.", "Cada computador tem os seus programas."]),
    ]},
]}
