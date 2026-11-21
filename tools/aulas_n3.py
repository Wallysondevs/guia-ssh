# -*- coding: utf-8 -*-
"""Nível 3 · Config e arquivos: ~/.ssh/config, conexões reaproveitadas, scp, sftp, rsync e pipes."""
from lib_guia import *
from respostas import *

def aula(**k):
    return k

CF_SRV = "printf 'Host srv\\n    HostName 192.168.0.20\\n    User lab\\n' >> ~/.ssh/config"
CF_G = "ssh -G srv | grep -E '^(hostname|user|port|identityfile) '"
# ---------------------------------------------------------------- ssh config
def cf_corpo():
    return f"""
<h2>A ideia: apelidos para os seus servidores</h2>
<p>Digitar <code>ssh -i ~/.ssh/chave -p 2222 lab@192.168.0.20</code> toda vez cansa e dá erro. O arquivo <code>~/.ssh/config</code> guarda essas opções com um <strong>apelido</strong>: depois, basta <code>ssh srv</code>. Vale também para <code>scp</code>, <code>sftp</code> e <code>rsync</code>.</p>
<pre class="cmd">
Host srv
    HostName 192.168.0.20
    User lab
    Port 22
    IdentityFile ~/.ssh/id_ed25519
</pre>
<ul>
<li><code>Host srv</code>: o apelido. As linhas recuadas abaixo valem para ele.</li>
<li><code>HostName</code>: o endereço de verdade (nome ou IP).</li>
<li><code>User</code>, <code>Port</code>, <code>IdentityFile</code>: o usuário, a porta e a chave, como <code>lab@</code>, <code>-p</code> e <code>-i</code>.</li>
</ul>
<hr>
<h2>1. Criar o arquivo</h2>
<p>Você pode editar com <code>nano ~/.ssh/config</code>. Na coleta, a Ana criou o bloco com <code>printf</code> e deixou o arquivo com permissão <code>600</code>:</p>
{T("cf-criar", CF_SRV, "chmod 600 ~/.ssh/config", "cat ~/.ssh/config", "ssh srv hostname")}
<hr>
<h2>2. Ver o que o ssh vai usar: <code>ssh -G</code></h2>
<p>O <code>-G</code> não conecta: mostra a configuração final que o ssh usaria para aquele apelido. É o melhor jeito de conferir o arquivo:</p>
{T("cf-G", CF_G, prep=[["notebook", "ana", CF_SRV]], notas={"hostname 192.168.0.20": "veio do HostName", "user lab": "veio do User", "port 22": "o padrão, já que não foi dito"})}
<hr>
<h2>3. O apelido vale para tudo</h2>
{T("cf-scp", "scp notas.txt srv:", "ssh srv ls", prep=[["notebook", "ana", CF_SRV]])}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Opção com erro de digitação", "Uma opção escrita errado (aqui, <code>HostNme</code>) faz o ssh parar, avisando a linha:", T("cf-erro", "printf 'Host srv\\n    HostNme 192.168.0.20\\n' > ~/.ssh/config", "ssh srv hostname"), "Corrija a linha indicada. O <code>ssh -G apelido</code> acusa o mesmo erro sem tentar conectar.")}
"""

def cf_ex():
    return (EX(1, "O apelido", "Que palavra abre um bloco no ~/.ssh/config?", "", "Host", " srv", rotulo="palavra") +
            EX(2, "O endereço", "Que opção diz o endereço de verdade?", "    ", "HostName", " 192.168.0.20", rotulo="opção") +
            MC(3, "<code>ssh -G srv</code>:", ["conecta no srv", "mostra a configuração final, sem conectar", "apaga o apelido", "gera uma chave"], 2) +
            MC(4, "O apelido do config funciona com:", ["só o ssh", "ssh, scp, sftp e rsync", "só o scp", "só no servidor"], 2))

def cf_miss():
    return (M("cf-m1", "mostre que usuário o ssh vai usar para o apelido <code>servidor</code> do seu config.", "ssh -G servidor | grep '^user '", r"src:ssh -G;;outre:^user \S+$", estado="config") +
            M("cf-m2", "rode um comando no servidor usando só o apelido.", "ssh servidor 'echo alias funcionando'", r"src:^ssh servidor\b;;outre:^alias funcionando$", estado="config"))

# ---------------------------------------------------------------- config avançado
CA_ORDEM1 = "printf 'Host srv\\n    User lab\\nHost *\\n    User ana\\n' > certo.conf"
CA_ORDEM2 = "printf 'Host *\\n    User ana\\nHost srv\\n    User lab\\n' > errado.conf"
CA_INC = "mkdir -p ~/.ssh/config.d && printf 'Host wiki\\n    HostName 192.168.0.130\\n    User lab\\n' > ~/.ssh/config.d/trabalho.conf && sed -i '1i Include config.d/*.conf' ~/.ssh/config"
def ca_corpo():
    return f"""
<h2>A ideia: regras para muitos servidores</h2>
<p>O config fica mais poderoso com três recursos: <strong>curingas</strong> (<code>Host *</code>), a regra de <strong>“o primeiro valor vence”</strong> e o <code>Include</code>, que junta vários arquivos.</p>
<hr>
<h2>1. Curingas e vários nomes</h2>
<p><code>Host *</code> vale para todos os servidores; <code>Host srv servidor</code> dá dois nomes ao mesmo bloco. O <code>ServerAliveInterval 60</code> manda um “sinal de vida” a cada 60 segundos, o que evita a queda de conexões paradas:</p>
{T("ca-curinga", "printf 'Host srv servidor\\n    HostName 192.168.0.20\\n    User lab\\n\\nHost *\\n    ServerAliveInterval 60\\n' > ~/.ssh/config", "ssh -G srv | grep -E '^(user|serveraliveinterval) '", "ssh -G servidor | grep -E '^(user|serveraliveinterval) '")}
<hr>
<h2>2. O primeiro valor vence</h2>
<p>O ssh lê o arquivo de cima para baixo e fica com o <strong>primeiro</strong> valor de cada opção. Por isso o <code>Host *</code> vai <strong>no fim</strong>, como padrão. O <code>-F</code> lê outro arquivo no lugar do config:</p>
{T("ca-ordem", CA_ORDEM1, CA_ORDEM2, "ssh -F certo.conf -G srv | grep '^user '", "ssh -F errado.conf -G srv | grep '^user '", notas={"user lab": "o bloco srv veio antes", "user ana": "o Host * veio antes e ganhou"})}
<hr>
<h2>3. Separar em arquivos: <code>Include</code></h2>
<p>Com muitos servidores, separe: um arquivo para o trabalho, outro para casa. O <code>Include</code> precisa ficar no <strong>começo</strong> do config:</p>
{T("ca-include", CA_INC, "head -3 ~/.ssh/config", "ssh -G wiki | grep -E '^(hostname|user) '", estado="config")}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Permissão do config", "O config também precisa ser só seu. Com escrita para outros, o ssh se recusa a ler:", T("ca-erro", "chmod 666 ~/.ssh/config", "ssh servidor hostname", estado="config"), "Corrija com <code>chmod 600 ~/.ssh/config</code>.")}
"""

def ca_ex():
    return (EX(1, "Para todos", "Complete o bloco que vale para todos os servidores:", "Host ", "*") +
            EX(2, "Sinal de vida", "Que opção manda um sinal de vida a cada N segundos?", "    ", "ServerAliveInterval", " 60", rotulo="opção") +
            MC(3, "Onde deve ficar o <code>Host *</code>?", ["No começo do arquivo", "No fim, como padrão", "Em qualquer lugar, dá no mesmo", "Só no servidor"], 2) +
            MC(4, "Duas linhas <code>User</code> valem para o mesmo servidor. Qual ganha?", ["A última", "A primeira", "As duas", "Nenhuma"], 2))

def ca_miss():
    return (M("ca-m1", "mostre o valor do <code>ServerAliveInterval</code> que o ssh usaria para o servidor.", "ssh -G servidor | grep -i '^serveraliveinterval'", r"src:ssh -G;;outre:^serveraliveinterval \d+$", estado="config") +
            M("ca-m2", "mude o <code>ServerAliveInterval</code> só nesta conexão (com <code>-o</code>) e confira com <code>-G</code>.", "ssh -o ServerAliveInterval=30 -G servidor | grep -i '^serveraliveinterval'", r"src:-o ServerAliveInterval=30;;outre:^serveraliveinterval 30$", estado="config"))

# ---------------------------------------------------------------- multiplexação
MX_CONF = "printf 'Host servidor\\n    ControlMaster auto\\n    ControlPath ~/.ssh/cm-%%r@%%h:%%p\\n    ControlPersist 10m\\n' | cat - ~/.ssh/config > /tmp/config.novo && mv /tmp/config.novo ~/.ssh/config"
MX_M = "ssh -o ControlMaster=auto -o ControlPath='~/.ssh/cm-%r@%h:%p' -o ControlPersist=1m servidor true; ssh -o ControlPath='~/.ssh/cm-%r@%h:%p' -O check servidor"
MX_M2 = "ssh -o ControlMaster=auto -o ControlPath='~/.ssh/cm-%r@%h:%p' -o ControlPersist=1m servidor true; ssh -o ControlPath='~/.ssh/cm-%r@%h:%p' -O exit servidor"
def mx_corpo():
    return f"""
<h2>A ideia: uma conexão, muitas sessões</h2>
<p>Cada <code>ssh</code> faz a negociação de criptografia e a autenticação do zero. Com <strong>ControlMaster</strong>, a primeira conexão vira uma “mestre” que fica aberta, e as próximas passam por dentro dela, sem negociar de novo. Fica bem mais rápido, ótimo para scripts que rodam vários comandos seguidos.</p>
<hr>
<h2>1. Ligar no config</h2>
<pre class="cmd">
Host servidor
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
</pre>
{ANAT(("ControlMaster auto", "usa uma mestre se existir; se não, cria."), ("ControlPath", "onde fica o “soquete” da mestre (<code>%r</code> usuário, <code>%h</code> host, <code>%p</code> porta)."), ("ControlPersist 10m", "mantém a mestre aberta 10 minutos depois da última sessão."))}
<p>Na coleta, a Ana pôs o bloco no começo do config (lembre: o primeiro valor vence) e mediu o tempo de duas conexões:</p>
{T("mx-tempo", MX_CONF, "time ssh servidor true", "time ssh servidor true", estado="config", notas={})}
<p>A segunda foi mais rápida: já havia uma mestre aberta. Os números exatos variam; numa rede de verdade, com o servidor longe, a diferença é bem maior.</p>
<hr>
<h2>2. Controlar a mestre: <code>-O</code></h2>
{T("mx-o", MX_CONF, "ssh servidor true", "ls ~/.ssh", "ssh -O check servidor", "ssh -O exit servidor", "ssh -O check servidor", estado="config",
   notas={"cm-lab@192.168.0.20:22": "o soquete da mestre", "Master running": "a mestre está aberta", "Exit request sent": "pedido para fechar"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Pasta do ControlPath não existe", "Se o ControlPath apontar para uma pasta que não existe, a mestre não consegue criar o soquete:", T("mx-erro", "ssh -o ControlMaster=auto -o ControlPath='~/.ssh/naoexiste/cm-%r@%h:%p' servidor true", estado="config"), "Crie a pasta antes (<code>mkdir -p ~/.ssh/naoexiste</code>) ou use um caminho que exista.")}
"""

def mx_ex():
    return (EX(1, "Ligar", "Que opção do config cria e usa conexões mestre?", "    ", "ControlMaster", " auto", rotulo="opção") +
            EX(2, "Conferir", "Complete para ver se há uma mestre aberta:", "ssh -O ", "check", " servidor", rotulo="comando") +
            MC(3, "O ganho do ControlMaster é:", ["criptografia mais forte", "conexões seguintes sem negociar de novo, mais rápidas", "não precisar de chave", "abrir portas"], 2) +
            MC(4, "<code>ControlPersist 10m</code> quer dizer:", ["a conexão cai em 10 minutos", "a mestre fica aberta 10 minutos depois da última sessão", "tenta conectar por 10 minutos", "nada"], 2))

def mx_miss():
    return (M("mx-m1", "abra uma conexão mestre e confira se ela está rodando.", MX_M, r"src:ControlMaster=auto;;src:-O check;;outre:^Master running \(pid=\d+\)$", estado="config") +
            M("mx-m2", "abra uma conexão mestre e feche-a com <code>-O exit</code>.", MX_M2, r"src:-O exit;;out:Exit request sent.", estado="config"))

# ---------------------------------------------------------------- scp
def sc_corpo():
    return f"""
<h2>A ideia: cp entre computadores</h2>
<p>O <code>scp</code> copia arquivos pelo SSH, com a mesma cara do <code>cp</code>: <code>scp origem destino</code>. O lado remoto se escreve <code>usuario@computador:caminho</code>. Os <strong>dois-pontos</strong> são o que diz “é no outro computador”; caminho vazio depois deles é a pasta pessoal.</p>
<hr>
<h2>1. Enviar do notebook para o servidor</h2>
{T("sc-enviar", "scp notas.txt lab@servidor:", "scp notas.txt lab@servidor:/tmp/notas-da-ana.txt", "ssh lab@servidor 'ls; ls /tmp'", notas={"100%": "nome, progresso, tamanho, velocidade e tempo"})}
<hr>
<h2>2. Trazer do servidor</h2>
{T("sc-baixar", "scp lab@servidor:relatorio.txt .", "cat relatorio.txt")}
<p>O <code>.</code> no fim é “aqui, na pasta atual”.</p>
<hr>
<h2>3. Pastas inteiras: <code>-r</code></h2>
{T("sc-r", "scp -r projeto lab@servidor:", "ssh lab@servidor 'ls -R projeto'")}
<div class="table-wrap"><table class="ref">
<tr><th>Opção</th><th>O que faz</th></tr>
<tr><td><code>-r</code></td><td>copia pastas, com tudo dentro</td></tr>
<tr><td><code>-P 2222</code></td><td>porta (<strong>P maiúsculo</strong> no scp; no ssh é <code>-p</code> minúsculo)</td></tr>
<tr><td><code>-p</code></td><td>mantém datas e permissões</td></tr>
<tr><td><code>-i chave</code></td><td>escolhe a chave</td></tr>
</table></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Esqueci os dois-pontos", "Sem os <code>:</code>, o scp entende <code>lab@servidor</code> como um <strong>nome de arquivo local</strong>. Ele não reclama: só copia dentro do próprio notebook.", T("sc-erro", "scp notas.txt lab@servidor", "ls"), "Viu um arquivo chamado <code>lab@servidor</code> aparecer? Apague-o e rode de novo com os dois-pontos: <code>lab@servidor:</code>.")}
"""

def sc_ex():
    return (EX(1, "O lado remoto", "Complete para enviar à pasta pessoal do lab:", "scp notas.txt lab@servidor", ":", rotulo="símbolo") +
            EX(2, "Pasta inteira", "Que opção do scp copia uma pasta?", "scp ", "-r", " projeto lab@servidor:", rotulo="opção") +
            MC(3, "No scp, a porta se escolhe com:", ["<code>-p</code>", "<code>-P</code>", "<code>--port</code>", "<code>:22</code>"], 2) +
            MC(4, "<code>scp lab@servidor:relatorio.txt .</code>:", ["envia o relatório", "traz o relatório para a pasta atual", "apaga o relatório", "dá erro"], 2))

def sc_miss():
    return (M("sc-m1", "traga o <code>relatorio.txt</code> do servidor e mostre as vendas.", "scp lab@servidor:relatorio.txt . && grep vendas relatorio.txt", r"src:^scp\b;;src:lab@servidor:relatorio\.txt;;outre:^vendas: \d+$") +
            M("sc-m2", "envie o <code>notas.txt</code> e mostre a primeira linha dele, lá no servidor.", "scp notas.txt lab@servidor: && ssh lab@servidor 'head -1 notas.txt'", r"src:^scp\b;;src:head -1;;outre:^Anotações da Ana$"))

# ---------------------------------------------------------------- sftp
def sf_corpo():
    return f"""
<h2>A ideia: um “explorador de arquivos” no terminal</h2>
<p>O <code>sftp</code> abre uma sessão só para arquivos: você navega no servidor com <code>ls</code> e <code>cd</code> e transfere com <code>get</code> (baixar) e <code>put</code> (enviar). Os comandos com <code>l</code> na frente (<code>lls</code>, <code>lcd</code>, <code>lpwd</code>) valem para o lado local, o notebook. Programas gráficos como o FileZilla usam o mesmo protocolo.</p>
<hr>
<h2>1. Uma sessão</h2>
{T("sf-sessao", "sftp lab@servidor", resp=[SFTP("pwd"), SFTP("ls"), SFTP("get relatorio.txt"), SFTP("put notas.txt"), SFTP("ls -l"), SFTP("lls"), SFTP("bye")],
   notas={"Remote working directory": "pwd: a pasta no servidor", "Fetching": "get: baixando", "Uploading": "put: enviando"})}
<div class="table-wrap"><table class="ref">
<tr><th>No servidor</th><th>No notebook</th><th>Transferir</th></tr>
<tr><td><code>ls</code>, <code>cd</code>, <code>pwd</code>, <code>mkdir</code>, <code>rm</code></td><td><code>lls</code>, <code>lcd</code>, <code>lpwd</code>, <code>lmkdir</code></td><td><code>get arq</code>, <code>put arq</code>, <code>get -r pasta</code>, <code>put -r pasta</code></td></tr>
</table></div>
<hr>
<h2>2. Em lote: <code>sftp -b</code></h2>
<p>Num script, ponha os comandos num arquivo e rode com <code>-b</code>. O sftp mostra cada comando com <code>sftp&gt;</code> na frente:</p>
{T("sf-lote", "printf 'cd site\\nls\\nget index.html\\n' > lote.sftp", "sftp -b lote.sftp lab@servidor", "cat index.html")}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Arquivo que não existe, em lote", "Em modo lote, o primeiro erro <strong>para tudo</strong> (o que vem depois não roda). Útil em scripts: nada acontece pela metade sem você saber.", T("sf-erro", "printf 'get naoexiste.txt\\nget relatorio.txt\\n' > lote.sftp", "sftp -b lote.sftp lab@servidor", "ls"), "Para seguir mesmo com erro, ponha um <code>-</code> na frente do comando no arquivo: <code>-get naoexiste.txt</code>.")}
"""

def sf_ex():
    return (EX(1, "Baixar", "Que comando do sftp baixa um arquivo?", "sftp> ", "get", " relatorio.txt", rotulo="comando") +
            EX(2, "Enviar", "Que comando do sftp envia um arquivo?", "sftp> ", "put", " notas.txt", rotulo="comando") +
            MC(3, "No sftp, <code>lls</code> lista:", ["o servidor", "o notebook (local)", "as chaves", "os logs"], 2) +
            MC(4, "Em <code>sftp -b</code>, um comando que falha:", ["é ignorado", "para o lote", "repete", "apaga o arquivo"], 2))

def sf_miss():
    return (M("sf-m1", "mostre a pasta de trabalho do servidor com o sftp, sem abrir sessão (mande o comando pelo cano).", "echo pwd | sftp -q lab@servidor", r"src:\|\s*sftp\b;;outre:^Remote working directory: /\S+$") +
            M("sf-m2", "crie um lote que baixa o <code>relatorio.txt</code> e rode com <code>sftp -b</code>.", "printf 'get relatorio.txt\\n' > lote.sftp && sftp -b lote.sftp lab@servidor", r"src:sftp -b;;outre:^sftp> get relatorio\.txt$"))

# ---------------------------------------------------------------- rsync
RS_DRY = [["notebook", "ana", "rsync -a projeto/ lab@servidor:projeto/ && rm projeto/estilo.css"]]
def rs_corpo():
    return f"""
<h2>A ideia: copiar só o que mudou</h2>
<p>O <code>rsync</code> sincroniza pastas: na primeira vez copia tudo; nas seguintes, só o que mudou. Por isso é o preferido para backups e para mandar um site para o servidor. Ele usa o SSH como transporte (e precisa estar instalado nos dois lados: <code>sudo apt install rsync</code>).</p>
<hr>
<h2>1. A primeira cópia e a segunda</h2>
{T("rs-primeira", "rsync -av projeto/ lab@servidor:projeto/", "rsync -av projeto/ lab@servidor:projeto/", notas={"img/logo.png": "a primeira vez: tudo", "sent 2": "a segunda: nada a copiar"})}
{ANAT(("-a", "“arquivo”: copia pastas, mantém datas e permissões."), ("-v", "mostra o que está copiando."), ("projeto/", "com barra no fim: o <strong>conteúdo</strong> da pasta."), ("lab@servidor:projeto/", "o destino, no formato do scp."))}
<hr>
<h2>2. Só o que mudou</h2>
{T("rs-mudanca", "rsync -a projeto/ lab@servidor:projeto/", "echo 'p { margin: 0; }' >> projeto/estilo.css", "rsync -av projeto/ lab@servidor:projeto/", notas={"estilo.css": "só o arquivo alterado"})}
<hr>
<h2>3. Ensaiar antes: <code>--dry-run</code> e <code>--delete</code></h2>
<p>O <code>--delete</code> apaga no destino o que não existe mais na origem: o destino fica <strong>igual</strong>. É poderoso e perigoso. Ensaie com <code>--dry-run</code> (ou <code>-n</code>), que só mostra o que faria. Aqui, a Ana apagou o <code>estilo.css</code> do notebook depois de uma cópia:</p>
{T("rs-dry", "rsync -av --delete --dry-run projeto/ lab@servidor:projeto/", "ssh lab@servidor 'ls projeto'", "rsync -av --delete projeto/ lab@servidor:projeto/", "ssh lab@servidor 'ls projeto'", prep=RS_DRY,
   notas={"deleting estilo.css": "o que o --delete apaga", "(DRY RUN)": "ensaio: nada foi apagado ainda"})}
<div class="tip"><strong>-e: escolher como conectar</strong><p>O <code>-e</code> passa opções ao ssh, como a porta ou a chave: <code>rsync -av -e 'ssh -p 2222 -i ~/.ssh/servidor_lab' projeto/ lab@servidor:projeto/</code>. Com o <a href="ssh-config.html">config</a>, nem precisa: o apelido já traz tudo.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("A barra no fim muda tudo", "<code>projeto</code> (sem barra) copia a <strong>pasta</strong>; <code>projeto/</code> (com barra) copia o <strong>conteúdo</strong>. Errar isso cria uma pasta dentro da outra:", T("rs-erro", "rsync -a projeto lab@servidor:copia1/", "rsync -a projeto/ lab@servidor:copia2/", "ssh lab@servidor 'ls copia1 copia2'"), "Na dúvida, use barra nos dois lados (<code>origem/ destino/</code>) e ensaie com <code>-n</code>.")}
"""

def rs_ex():
    return (EX(1, "Ensaiar", "Que opção do rsync só mostra o que faria?", "rsync -av ", "--dry-run", " projeto/ lab@servidor:projeto/", rotulo="opção") +
            EX(2, "Espelhar", "Que opção apaga no destino o que sumiu da origem?", "rsync -av ", "--delete", " projeto/ lab@servidor:projeto/", rotulo="opção") +
            MC(3, "Na segunda vez, o rsync copia:", ["tudo de novo", "só o que mudou", "nada, nunca", "só as pastas"], 2) +
            MC(4, "<code>rsync -a projeto/ srv:destino/</code> copia:", ["a pasta projeto para dentro de destino", "o conteúdo de projeto para dentro de destino", "só os arquivos .txt", "nada"], 2))

def rs_miss():
    return (M("rs-m1", "sincronize a pasta <code>projeto</code> com o servidor, mostrando o que foi copiado.", "rsync -av projeto/ lab@servidor:projeto/", r"src:^rsync -a;;out:sending incremental file list") +
            M("rs-m2", "ensaie um espelhamento com <code>--delete</code>, sem mudar nada.", "rsync -av --dry-run --delete projeto/ lab@servidor:projeto/", r"src:--dry-run|-n\b;;src:--delete;;out:(DRY RUN)"))

# ---------------------------------------------------------------- pipes remotos
PR_TAR = "tar czf - projeto | ssh lab@servidor 'mkdir -p backup && tar xzf - -C backup'"
PR_DIFF = "diff <(ssh lab@servidor cat relatorio.txt) relatorio-local.txt"
def pr_corpo():
    return f"""
<h2>A ideia: o cano atravessa a rede</h2>
<p>O ssh liga a entrada e a saída do comando remoto às do notebook. Então dá para usar o <code>|</code> através da rede: o que um programa escreve no notebook chega como entrada de outro programa no servidor, e vice-versa. Sem arquivo temporário.</p>
<hr>
<h2>1. Enviar uma pasta compactada</h2>
<p>O <code>tar czf -</code> compacta a pasta e escreve no cano (o <code>-</code> é a saída padrão). No servidor, o <code>tar xzf -</code> lê do cano e extrai:</p>
{T("pr-tar", PR_TAR, "ssh lab@servidor 'ls -R backup'")}
<hr>
<h2>2. Trazer um backup do servidor</h2>
{T("pr-baixar", "ssh lab@servidor 'tar czf - site relatorio.txt' > backup-servidor.tar.gz", "tar tzf backup-servidor.tar.gz", "ls -l backup-servidor.tar.gz")}
<hr>
<h2>3. Comparar um arquivo local com o remoto</h2>
<p>O <code>&lt;(…)</code> do Bash faz a saída de um comando parecer um arquivo. Com ele, o <code>diff</code> compara o relatório do servidor com uma cópia local alterada:</p>
{T("pr-diff", PR_DIFF, prep=[["notebook", "ana", "printf 'Relatório mensal\\nvendas: 45\\nclientes novos: 7\\n' > relatorio-local.txt"]], notas={"< vendas: 42": "no servidor", "> vendas: 45": "no notebook"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Faltou o “-” do tar", "Sem o <code>-</code>, o <code>tar czf projeto</code> entende <code>projeto</code> como o nome do arquivo a <strong>criar</strong>, e não tem nada para pôr nele:", T("pr-erro", "tar czf projeto | ssh lab@servidor 'tar tzf -'"), "O <code>f -</code> é o que manda o tar escrever no cano: <code>tar czf - projeto</code>.")}
"""

def pr_ex():
    return (EX(1, "O cano", "No <code>tar czf - projeto</code>, o que manda o tar escrever na saída?", "tar czf ", "-", " projeto", rotulo="símbolo") +
            EX(2, "Extrair lá", "Complete o lado do servidor:", "ssh lab@servidor 'tar ", "xzf", " -'", rotulo="opções") +
            MC(3, "Em <code>ssh srv 'tar czf - site' &gt; b.tar.gz</code>, o arquivo b.tar.gz fica:", ["no servidor", "no notebook", "nos dois", "em lugar nenhum"], 2) +
            MC(4, "Por que usar tar pelo cano em vez de scp -r?", ["É obrigatório", "Compacta e manda tudo num fluxo só, sem arquivo temporário", "É mais seguro", "Não usa SSH"], 2))

def pr_miss():
    return (M("pr-m1", "traga o <code>relatorio.txt</code> do servidor por um tar no cano e extraia no notebook mostrando o nome.", "ssh lab@servidor 'tar czf - relatorio.txt' | tar xzvf -", r"src:tar czf -;;src:tar xzvf -;;outre:^relatorio\.txt$") +
            M("pr-m2", "conte as linhas do relatório do servidor com o <code>wc</code> rodando no notebook.", "ssh lab@servidor 'cat relatorio.txt' | wc -l", r"src:\|\s*wc -l;;outre:^3$"))

NIVEL = {"id": "n3", "nome": "Nível 3 · Config e arquivos", "curto": "Arquivos", "desc": "O ~/.ssh/config e a cópia de arquivos: scp, sftp, rsync e pipes", "grupos": [
    {"grupo": "O arquivo config", "aulas": [
        aula(slug="ssh-config", menu="Apelidos no ~/.ssh/config", title="~/.ssh/config: apelidos com Host, HostName, User e Port", h1='Apelidos no <span class="hl">~/.ssh/config</span>',
             desc="Criar apelidos de servidores no ~/.ssh/config com Host, HostName, User, Port e IdentityFile, e conferir com ssh -G.",
             intro="O config guarda o usuário, a porta e a chave de cada servidor com um apelido curto.",
             aprender=["Escrever um bloco <code>Host</code>.", "Conferir a configuração com <code>ssh -G</code>.", "Usar o apelido no scp e no rsync."],
             corpo=cf_corpo, exercicios=cf_ex, missoes=cf_miss,
             ref=[("Host apelido", "abre um bloco."), ("HostName / User / Port", "endereço, usuário, porta."), ("IdentityFile ~/.ssh/chave", "a chave."), ("ssh -G apelido", "mostra o resultado.")],
             resumo=["Um bloco <code>Host</code> por servidor.", "<code>ssh -G</code> confere sem conectar.", "O apelido vale para scp, sftp e rsync."]),
        aula(slug="ssh-config-avancado", menu="Config: curingas, ordem e Include", title="~/.ssh/config avançado: Host *, ordem das regras e Include", h1='Config: curingas, ordem e <span class="hl">Include</span>',
             desc="Regras do ~/.ssh/config: Host * e vários nomes, o primeiro valor vence, ServerAliveInterval e Include de arquivos separados.",
             intro="Com vários servidores, o config precisa de regras gerais. Esta aula mostra os curingas, a ordem e o Include.",
             aprender=["Usar <code>Host *</code> e vários nomes num bloco.", "Entender que o primeiro valor vence.", "Separar o config com <code>Include</code>."],
             corpo=ca_corpo, exercicios=ca_ex, missoes=ca_miss,
             ref=[("Host *", "todos os servidores (no fim)."), ("Host a b", "dois nomes."), ("ServerAliveInterval 60", "sinal de vida."), ("Include config.d/*.conf", "outros arquivos (no começo).")],
             resumo=["O primeiro valor vence.", "<code>Host *</code> no fim, <code>Include</code> no começo.", "O config precisa de permissão 600."]),
        aula(slug="multiplex", menu="Conexões reaproveitadas (ControlMaster)", title="ControlMaster: reaproveitando a conexão SSH", h1='Conexões <span class="hl">reaproveitadas</span>',
             desc="Usar ControlMaster, ControlPath e ControlPersist para reaproveitar uma conexão SSH, e controlar a mestre com ssh -O check e -O exit.",
             intro="Uma conexão mestre aberta deixa as próximas conexões instantâneas. Esta aula mostra como ligar e controlar.",
             aprender=["Ligar o ControlMaster no config.", "Ver a diferença de tempo.", "Conferir e fechar a mestre com <code>-O</code>."],
             corpo=mx_corpo, exercicios=mx_ex, missoes=mx_miss,
             ref=[("ControlMaster auto", "liga."), ("ControlPath ~/.ssh/cm-%r@%h:%p", "o soquete."), ("ControlPersist 10m", "tempo aberta."), ("ssh -O check / exit srv", "confere / fecha.")],
             resumo=["A mestre evita negociar de novo.", "O ControlPath precisa de uma pasta que exista.", "<code>-O exit</code> fecha a mestre."]),
    ]},
    {"grupo": "Copiando arquivos", "aulas": [
        aula(slug="scp", menu="Copiando com scp", title="scp: copiando arquivos e pastas pelo SSH", h1='Copiando com <span class="hl">scp</span>',
             desc="Enviar e baixar arquivos com scp: o formato usuario@computador:caminho, -r para pastas, -P para porta e o erro dos dois-pontos.",
             intro="O scp é o cp entre computadores. Esta aula mostra os dois sentidos e o erro mais comum.",
             aprender=["Enviar e trazer arquivos.", "Copiar pastas com <code>-r</code>.", "Não esquecer os dois-pontos."],
             corpo=sc_corpo, exercicios=sc_ex, missoes=sc_miss,
             ref=[("scp arq lab@srv:", "envia."), ("scp lab@srv:arq .", "traz."), ("scp -r pasta lab@srv:", "pasta."), ("scp -P 2222 …", "porta.")],
             resumo=["Os <code>:</code> indicam o outro computador.", "<code>-r</code> para pastas.", "No scp a porta é <code>-P</code>."]),
        aula(slug="sftp", menu="Sessão de arquivos com sftp", title="sftp: navegando e transferindo arquivos pelo SSH", h1='Sessão de arquivos: <span class="hl">sftp</span>',
             desc="Usar o sftp: ls, cd, get, put, lls e lcd numa sessão, e o modo lote com sftp -b para scripts.",
             intro="O sftp é uma sessão só para arquivos, com comandos para os dois lados. Também roda em lote, em scripts.",
             aprender=["Navegar e transferir com <code>get</code> e <code>put</code>.", "Usar os comandos locais (<code>lls</code>, <code>lcd</code>).", "Rodar em lote com <code>-b</code>."],
             corpo=sf_corpo, exercicios=sf_ex, missoes=sf_miss,
             ref=[("sftp lab@srv", "abre a sessão."), ("get / put", "baixa / envia."), ("lls / lcd", "lado local."), ("sftp -b lote lab@srv", "em lote.")],
             resumo=["<code>get</code> baixa, <code>put</code> envia.", "Com <code>l</code> na frente, é o notebook.", "Em lote, o primeiro erro para tudo."]),
        aula(slug="rsync", menu="Sincronizando com rsync", title="rsync pelo SSH: -av, --dry-run, --delete e a barra no fim", h1='Sincronizando com <span class="hl">rsync</span>',
             desc="Sincronizar pastas com rsync pelo SSH: -av, cópia só do que mudou, --dry-run, --delete, -e e a diferença da barra no fim.",
             intro="O rsync copia só o que mudou. É a ferramenta de backup e de publicação mais usada com SSH.",
             aprender=["Sincronizar com <code>rsync -av</code>.", "Ensaiar com <code>--dry-run</code> antes do <code>--delete</code>.", "Entender a barra no fim da origem."],
             corpo=rs_corpo, exercicios=rs_ex, missoes=rs_miss,
             ref=[("rsync -av orig/ srv:dest/", "sincroniza."), ("-n / --dry-run", "ensaio."), ("--delete", "espelha (apaga no destino)."), ("-e 'ssh -p 2222'", "opções do ssh.")],
             resumo=["Só o que mudou vai pela rede.", "Ensaie o <code>--delete</code>.", "<code>orig/</code> copia o conteúdo; <code>orig</code>, a pasta."]),
        aula(slug="pipes-remotos", menu="Pipes pela rede (tar e diff)", title="Pipes pelo SSH: tar pelo cano, backups e diff remoto", h1='Pipes pela <span class="hl">rede</span>',
             desc="Usar pipes através do SSH: enviar e trazer pastas com tar pelo cano, backups sem arquivo temporário e diff entre arquivo local e remoto.",
             intro="O cano do Bash atravessa a rede com o ssh. Esta aula mostra receitas clássicas com tar e diff.",
             aprender=["Enviar uma pasta com <code>tar | ssh</code>.", "Trazer um backup com <code>ssh … &gt;</code>.", "Comparar arquivos com <code>diff &lt;(ssh …)</code>."],
             corpo=pr_corpo, exercicios=pr_ex, missoes=pr_miss,
             ref=[("tar czf - pasta | ssh srv 'tar xzf -'", "envia."), ("ssh srv 'tar czf - pasta' > b.tgz", "traz."), ("diff <(ssh srv cat a) b", "compara.")],
             resumo=["O <code>-</code> do tar é o cano.", "O <code>&gt;</code> fora das aspas grava no notebook.", "<code>&lt;(…)</code> vira um arquivo para o diff."]),
    ]},
]}
