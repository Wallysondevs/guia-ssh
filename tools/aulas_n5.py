# -*- coding: utf-8 -*-
"""Nível 5 · Servidor e depuração: sshd_config, endurecimento, logs, fail2ban, ssh -v, erros comuns e projetos."""
from lib_guia import *
from respostas import *

def aula(**k):
    return k

HUP = "sleep 0.5"
def CONF(nome, linhas):
    """Preparo escondido: um arquivo em sshd_config.d e o sshd relendo a configuração."""
    return ["servidor", "root", "printf '%s' > /etc/ssh/sshd_config.d/%s && kill -HUP $(cat /run/sshd.pid) && sleep 0.5" % ("".join(l + "\\n" for l in linhas), nome)]
SEM_SENHA = [CONF("10-sem-senha.conf", ["PasswordAuthentication no"])]
ROOT_CHAVE = ["servidor", "root", "mkdir -p /root/.ssh && cp /home/lab/.ssh/authorized_keys /root/.ssh/ && chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys"]
ENDURECER = ["PasswordAuthentication no", "PermitRootLogin no", "KbdInteractiveAuthentication no", "MaxAuthTries 3", "AllowUsers lab", "X11Forwarding no"]
ENDURECER_CMD = "printf '%s' | sudo tee /etc/ssh/sshd_config.d/50-endurecer.conf" % "".join(l + "\\n" for l in ENDURECER)
RECARREGA = 'sudo sshd -t && sudo kill -HUP "$(cat /run/sshd.pid)"'
F2_LIGA = ["servidor", "root", "fail2ban-client -q start && sleep 2"]
ESPERA = ["notebook", "ana", "sleep 3"]
LOGINS = ["notebook", "ana", "ssh lab@servidor true; ssh -o BatchMode=yes teste@servidor true 2>/dev/null; sleep 1; true"]
NOVA_CHAVE_HOST = ["servidor", "root", "for k in ed25519 ecdsa rsa; do rm -f /etc/ssh/ssh_host_${k}_key /etc/ssh/ssh_host_${k}_key.pub; ssh-keygen -q -t $k -N '' -C root@servidor -f /etc/ssh/ssh_host_${k}_key; done; kill -HUP $(cat /run/sshd.pid); sleep 0.5"]
PARA_SSHD = ["servidor", "root", "kill $(cat /run/sshd.pid); sleep 0.5"]
RELOAD_NOTE = ('<div class="note"><strong>Recarregar sem derrubar ninguém</strong><p>Num servidor comum, depois de mexer na configuração rode '
               '<code>sudo sshd -t</code> (confere o arquivo) e <code>sudo systemctl reload ssh</code>. O laboratório do guia não usa o systemd, '
               'então manda o mesmo aviso direto ao processo: <code>sudo kill -HUP "$(cat /run/sshd.pid)"</code>. As sessões abertas continuam vivas.</p></div>')
SESSAO_ABERTA = ('<div class="warning"><strong>Deixe uma sessão aberta</strong><p>Antes de mexer no sshd de um servidor remoto, deixe um terminal '
                 'conectado e teste a mudança em <strong>outro</strong>. Se a configuração nova trancar você do lado de fora, a sessão antiga '
                 'ainda está lá para desfazer.</p></div>')

# ---------------------------------------------------------------- o sshd
def sd_corpo():
    return f"""
<h2>Quem atende do outro lado</h2>
<p>Até aqui você usou o <strong>cliente</strong> (<code>ssh</code>, <code>scp</code>, <code>sftp</code>). Do outro lado está o <strong>servidor</strong>, o programa <code>sshd</code> (o “d” é de <em>daemon</em>, um programa que fica rodando em segundo plano). No Debian e no Ubuntu ele vem no pacote <code>openssh-server</code> e o serviço se chama <code>ssh</code>.</p>
<pre class="cmd">
sudo apt install openssh-server     # instala o servidor
sudo systemctl status ssh           # está rodando?
</pre>
<hr>
<h2>1. O processo e a porta</h2>
<p>Nesta aula os comandos rodam <strong>no servidor</strong>, como <code>lab</code>:</p>
{T("sd-processo", "ps -C sshd -o pid,cmd", "sudo ss -ltnp | grep sshd", quem="servidor", notas={"[listener]": "o processo que espera conexões", ":22": "a porta padrão do SSH"})}
<hr>
<h2>2. Os arquivos</h2>
{T("sd-arquivos", "ls /etc/ssh", quem="servidor", notas={"sshd_config": "a configuração do servidor", "ssh_config": "a do cliente (sem o d)", "ssh_host_ed25519_key.pub": "a chave do servidor, a do fingerprint"})}
<p>Cuidado com a letra: <code>sshd_config</code> é o <strong>servidor</strong>; <code>ssh_config</code> é o <strong>cliente</strong>. O arquivo principal quase não tem nada ativo; o resto são comentários com os valores padrão:</p>
{T("sd-ativo", "grep -Ev '^(#|$)' /etc/ssh/sshd_config", quem="servidor", notas={"Include": "lê os arquivos da pasta sshd_config.d primeiro"})}
<div class="tip"><strong>A primeira vez vale</strong><p>No <code>sshd_config</code>, para a maioria das opções, vale o <strong>primeiro</strong> valor que o sshd encontra. Como o <code>Include</code> está no topo, um arquivo seu em <code>/etc/ssh/sshd_config.d/</code> ganha do resto. É lá que as próximas aulas mexem, sem tocar no arquivo original.</p></div>
<hr>
<h2>3. O que está valendo de verdade</h2>
<p>O <code>sshd -T</code> mostra a configuração final, já com os padrões e os arquivos incluídos, tudo em minúsculas:</p>
{T("sd-T", "sudo sshd -T | grep -E '^(port|passwordauthentication|pubkeyauthentication|permitrootlogin) '", quem="servidor", notas={"passwordauthentication yes": "senha ainda aceita", "without-password": "root só entra com chave"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Sem sudo", "O programa <code>sshd</code> fica em <code>/usr/sbin</code>, pasta que não está no <code>PATH</code> de um usuário comum no Debian:", T("sd-erro", "sshd -T | head -n 3", quem="servidor"), "Use <code>sudo sshd -T</code>: o sudo procura também em <code>/usr/sbin</code>, e o <code>sshd -T</code> precisa ler as chaves privadas do servidor (<code>ssh_host_*_key</code>, sem <code>.pub</code>), que só o root lê.")}
"""

def sd_ex():
    return (EX(1, "O pacote", "Complete para instalar o servidor SSH:", "sudo apt install ", "openssh-server") +
            EX(2, "A configuração final", "Que opção do sshd mostra a configuração que está valendo?", "sudo sshd ", "-T", rotulo="opção") +
            MC(3, "Qual arquivo configura o <strong>servidor</strong>?", ["<code>/etc/ssh/ssh_config</code>", "<code>/etc/ssh/sshd_config</code>", "<code>~/.ssh/config</code>", "<code>~/.ssh/known_hosts</code>"], 2) +
            MC(4, "Por que criar arquivos em <code>sshd_config.d/</code>?", ["é obrigatório", "eles são lidos primeiro e o primeiro valor vale", "o sshd ignora o arquivo principal", "fica mais rápido"], 2))

def sd_miss():
    return (M("sd-m1", "no servidor, mostre em que porta o sshd escuta, segundo a configuração final.", "sudo sshd -T | grep '^port '", r"src:sshd -T;;outre:^port \d+$", quem="servidor") +
            M("sd-m2", "no servidor, mostre a linha que inclui a pasta <code>sshd_config.d</code>.", "grep '^Include' /etc/ssh/sshd_config", r"src:sshd_config;;outre:^Include /etc/ssh/sshd_config\.d/", quem="servidor"))

# ---------------------------------------------------------------- desligando a senha
def ss_corpo():
    return f"""
<h2>Por que desligar a senha</h2>
<p>Todo servidor ligado na internet recebe, o dia inteiro, robôs tentando senhas como <code>123456</code> e <code>admin</code>. Com a chave funcionando (Nível 2), dá para fechar essa porta: o servidor passa a aceitar <strong>só chave</strong>.</p>
{SESSAO_ABERTA}
<hr>
<h2>1. Confira que a chave funciona</h2>
<p>Antes de tudo, no notebook: se esta linha pedir senha, <strong>pare</strong> e volte para a aula do <a href="ssh-copy-id.html">ssh-copy-id</a>.</p>
{T("ss-antes", "ssh -o PasswordAuthentication=no lab@servidor hostname", notas={"servidor": "entrou só com a chave"})}
<hr>
<h2>2. O arquivo novo, no servidor</h2>
{T("ss-criar", "echo 'PasswordAuthentication no' | sudo tee /etc/ssh/sshd_config.d/10-sem-senha.conf", RECARREGA, "sudo sshd -T | grep '^passwordauthentication'", quem="servidor", notas={"passwordauthentication no": "agora vale"})}
{RELOAD_NOTE}
<hr>
<h2>3. Testando do notebook</h2>
<p>Com <code>-o PubkeyAuthentication=no</code> o cliente finge não ter chave, como um robô faria:</p>
{T("ss-teste", "ssh -o PubkeyAuthentication=no lab@servidor", "ssh lab@servidor hostname", prep=SEM_SENHA, notas={"Permission denied (publickey)": "nem pergunta a senha: só chave", "servidor": "com a chave, tudo igual"})}
<p>Repare que a lista entre parênteses mudou: antes era <code>(publickey,password)</code>, agora é só <code>(publickey)</code>.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Erro de digitação", "Uma letra errada no nome da opção e o sshd recusa o arquivo. Por isso o <code>sshd -t</code> vem antes de recarregar:", T("ss-erro", "echo 'PasswordAuthentcation no' | sudo tee /etc/ssh/sshd_config.d/10-sem-senha.conf", RECARREGA, quem="servidor"), "O <code>&amp;&amp;</code> fez o recarregamento não acontecer: o sshd continua com a configuração antiga, que funciona. Corrija o nome e rode de novo.")}
"""

def ss_ex():
    return (EX(1, "A opção", "Complete a linha que desliga a senha no servidor:", "", "PasswordAuthentication", " no", rotulo="opção") +
            EX(2, "Conferir antes", "Que opção do sshd testa a configuração sem aplicar?", "sudo sshd ", "-t", rotulo="opção") +
            MC(3, "Depois de desligar a senha, quem não tem a chave vê:", ["a pergunta da senha", "<code>Permission denied (publickey)</code>", "<code>Connection refused</code>", "nada"], 2) +
            MC(4, "Antes de recarregar o sshd de um servidor remoto, o mais seguro é:", ["desligar o servidor", "deixar uma sessão aberta e testar em outra", "apagar o known_hosts", "trocar a senha"], 2))

def ss_miss():
    return (M("ss-m1", "no servidor, desligue a senha num arquivo em <code>sshd_config.d</code> e mostre que a configuração final mudou.", "echo 'PasswordAuthentication no' | sudo tee /etc/ssh/sshd_config.d/10-sem-senha.conf && sudo sshd -T | grep '^passwordauthentication'", r"src:PasswordAuthentication no;;src:sshd -T;;outre:^passwordauthentication no$", quem="servidor") +
            M("ss-m2", "com a senha já desligada no servidor, tente entrar sem chave.", "ssh -o PubkeyAuthentication=no lab@servidor", r"src:PubkeyAuthentication=no;;out:Permission denied (publickey)", prep=SEM_SENHA))

# ---------------------------------------------------------------- root
def sr_corpo():
    return f"""
<h2>O root e o SSH</h2>
<p>O <code>root</code> existe em todo Linux, então é o primeiro nome que os robôs tentam. O padrão do OpenSSH é <code>PermitRootLogin prohibit-password</code>: o root pode entrar, mas <strong>só com chave</strong>. O mais comum é ir além e proibir de vez, entrando como um usuário comum e usando <code>sudo</code>.</p>
<hr>
<h2>1. Como está</h2>
{T("rt-ver", "sudo sshd -T | grep '^permitrootlogin'", quem="servidor", notas={"without-password": "o nome antigo de prohibit-password"})}
<p>No laboratório, a chave da ana foi posta também no <code>/root/.ssh/authorized_keys</code> do servidor. Com o padrão, ela entra como root:</p>
{T("rt-entra", "ssh root@servidor 'whoami; hostname'", prep=[ROOT_CHAVE], notas={"root": "entrou como root, com a chave"})}
<hr>
<h2>2. Proibindo</h2>
{T("rt-proibir", "echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/20-sem-root.conf", RECARREGA, "sudo sshd -T | grep '^permitrootlogin'", quem="servidor", notas={"permitrootlogin no": "agora vale"})}
<p>Do notebook, a mesma chave já não serve para o root. O <code>BatchMode=yes</code> faz o ssh desistir em vez de perguntar a senha:</p>
{T("rt-teste", "ssh -o BatchMode=yes root@servidor hostname", "ssh lab@servidor 'sudo whoami'", prep=[ROOT_CHAVE, CONF("20-sem-root.conf", ["PermitRootLogin no"])], notas={"Permission denied": "root barrado", "root": "como lab, o sudo ainda chega no root"})}
<div class="note"><strong>sudo sem senha?</strong><p>No laboratório, o <code>lab</code> usa <code>sudo</code> sem senha para as aulas andarem. Num servidor de verdade o <code>sudo</code> pede a senha do usuário; para ele perguntar por SSH, use <code>ssh -t lab@servidor 'sudo comando'</code> (o <code>-t</code> dá um terminal para a pergunta).</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Trancado do lado de fora", "Se o root era o único jeito de entrar e você proibiu, o servidor recusa até a chave certa:", T("rt-erro", "ssh root@servidor", prep=[ROOT_CHAVE, CONF("20-sem-root.conf", ["PermitRootLogin no"]), CONF("10-sem-senha.conf", ["PasswordAuthentication no"])]), "Por isso: crie antes um usuário comum com <code>sudo</code>, entre com ele numa segunda janela e só então proíba o root. Se trancar mesmo assim, só o console do provedor (ou o teclado do servidor) resolve.")}
"""

def sr_ex():
    return (EX(1, "Proibir o root", "Complete a linha que proíbe o root por SSH:", "PermitRootLogin ", "no") +
            EX(2, "Terminal para o sudo", "Que opção do ssh dá um terminal para o sudo perguntar a senha?", "ssh ", "-t", " lab@servidor 'sudo apt update'", rotulo="opção") +
            MC(3, "O padrão <code>prohibit-password</code> quer dizer:", ["root nunca entra", "root entra só com chave", "root entra só com senha", "qualquer um entra como root"], 2) +
            MC(4, "Antes de proibir o root, você precisa:", ["de um usuário comum com sudo que já entra", "apagar o authorized_keys", "trocar a porta", "desligar o fail2ban"], 1))

def sr_miss():
    return (M("rt-m1", "no servidor, mostre o valor do <code>permitrootlogin</code> que está valendo.", "sudo sshd -T | grep '^permitrootlogin'", r"src:sshd -T;;outre:^permitrootlogin \S+$", quem="servidor") +
            M("rt-m2", "com o root proibido no servidor, tente entrar como root sem perguntar senha.", "ssh -o BatchMode=yes root@servidor hostname", r"src:root@servidor;;out:Permission denied", prep=[ROOT_CHAVE, CONF("20-sem-root.conf", ["PermitRootLogin no"])]))

# ---------------------------------------------------------------- endurecendo
def se_corpo():
    return f"""
<h2>Um arquivo com o essencial</h2>
<p>Juntando o que você viu, mais algumas opções, dá para guardar tudo num arquivo só. Cada linha:</p>
{REF([("PasswordAuthentication no", "só chave."), ("PermitRootLogin no", "nada de root direto."), ("KbdInteractiveAuthentication no", "fecha a outra porta de senha (já vem assim no Debian)."), ("MaxAuthTries 3", "no máximo 3 tentativas por conexão."), ("AllowUsers lab", "só estes usuários entram, mais ninguém."), ("X11Forwarding no", "sem janelas gráficas pelo SSH.")], cab=("Linha", "O que faz"))}
{SESSAO_ABERTA}
<hr>
<h2>1. Escrevendo e recarregando</h2>
{T("se-criar", ENDURECER_CMD, RECARREGA, quem="servidor")}
{T("se-T", "sudo sshd -T | grep -E '^(passwordauthentication|permitrootlogin|maxauthtries|allowusers|x11forwarding) '", quem="servidor", prep=[CONF("50-endurecer.conf", ENDURECER)], notas={"x11forwarding no": "o arquivo principal diz yes, mas o seu veio antes"})}
<hr>
<h2>2. Testando do notebook</h2>
{T("se-teste", "ssh lab@servidor hostname", "ssh -o PubkeyAuthentication=no lab@servidor", "ssh -o BatchMode=yes ana@servidor hostname", prep=[CONF("50-endurecer.conf", ENDURECER)], notas={"servidor": "o lab, com chave, entra", "Permission denied": "sem chave ou fora do AllowUsers, não"})}
<hr>
<h2>3. E trocar a porta?</h2>
<p>Mudar a porta 22 para outra (<code>Port 2222</code>) não deixa o servidor mais seguro de verdade, mas diminui muito o lixo nos logs. Quem conecta precisa do <code>-p</code> (ou do <code>Port</code> no config). A chave do servidor é a mesma, então o ssh não pergunta nada:</p>
{T("se-porta", "ssh -p 2222 lab@servidor hostname", "ssh lab@servidor hostname", prep=[CONF("30-porta.conf", ["Port 2222"])], notas={"servidor": "na porta nova, entra", "port 22: Connection refused": "na 22, já não há ninguém"})}
<div class="warning"><strong>Firewall</strong><p>Se o servidor tiver firewall (<code>ufw</code>, <code>nftables</code>, o painel do provedor), libere a porta nova <strong>antes</strong> de recarregar o sshd.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Usuário fora da lista", "Com <code>AllowUsers lab</code>, até um usuário que existe e tem a senha certa fica de fora. No log do servidor aparece o motivo:", T("se-erro", "sudo grep 'not allowe[d]' /var/log/auth.log", quem="servidor", prep=[CONF("50-endurecer.conf", ENDURECER), ["notebook", "ana", "ssh -o BatchMode=yes ana@servidor true 2>/dev/null; sleep 1; true"]]), "Esqueceu alguém? Acrescente o nome na mesma linha (<code>AllowUsers lab maria</code>) e recarregue.")}
"""

def se_ex():
    return (EX(1, "Tentativas", "Complete para permitir no máximo 3 tentativas por conexão:", "MaxAuthTries ", "3") +
            EX(2, "Lista de usuários", "Que opção deixa entrar só os usuários listados?", "", "AllowUsers", " lab", rotulo="opção") +
            MC(3, "Trocar a porta do SSH:", ["deixa o servidor impossível de invadir", "diminui o lixo nos logs, mas não substitui a chave", "desliga a senha", "é obrigatório"], 2) +
            MC(4, "Depois de <code>Port 2222</code>, o cliente conecta com:", ["<code>ssh lab@servidor:2222</code>", "<code>ssh -p 2222 lab@servidor</code>", "<code>ssh -P 2222 lab@servidor</code>", "<code>ssh lab@servidor 2222</code>"], 2))

def se_miss():
    return (M("se-m1", "no servidor, limite as tentativas a 3 num arquivo em <code>sshd_config.d</code> e confira na configuração final.", "echo 'MaxAuthTries 3' | sudo tee /etc/ssh/sshd_config.d/50-endurecer.conf && sudo sshd -T | grep '^maxauthtries'", r"src:MaxAuthTries 3;;src:sshd -T;;outre:^maxauthtries 3$", quem="servidor") +
            M("se-m2", "com o servidor escutando na porta 2222, conecte nela.", "ssh -p 2222 lab@servidor hostname", r"src:-p 2222;;outre:^servidor$", prep=[CONF("30-porta.conf", ["Port 2222"])]))

# ---------------------------------------------------------------- logs
def sl_corpo():
    return f"""
<h2>Onde o sshd conta o que aconteceu</h2>
<p>Cada conexão, aceita ou recusada, vira uma linha de log no servidor. No Debian e no Ubuntu com systemd, o jeito mais direto é o <code>journalctl</code>; onde existe o arquivo <code>/var/log/auth.log</code>, ele tem as mesmas linhas:</p>
<pre class="cmd">
sudo journalctl -u ssh -n 20        # as últimas 20 linhas do serviço ssh
sudo journalctl -u ssh -f           # acompanha ao vivo (Ctrl+C sai)
</pre>
<p>O laboratório grava em <code>/var/log/auth.log</code>. Antes da caixa, a ana entrou uma vez com a chave e alguém tentou o usuário <code>teste</code>, que não existe:</p>
<hr>
<h2>1. As linhas do sshd</h2>
{T("sl-ver", "sudo grep -E 'Accepte[d]|Invalid use[r]|session opene[d] for user lab' /var/log/auth.log", quem="servidor", prep=[LOGINS], notas={"Accepted publickey for lab": "entrou com chave", "Invalid user teste": "usuário que não existe"})}
<div class="tip"><strong>Por que os colchetes no grep?</strong><p>O próprio <code>sudo</code> também escreve no <code>auth.log</code> o comando que rodou, com o texto do grep. <code>Accepte[d]</code> casa com “Accepted”, mas não com a linha do sudo, que tem o texto <code>Accepte[d]</code> com os colchetes.</p></div>
<hr>
<h2>2. Contando</h2>
{T("sl-contar", "sudo grep -c 'Accepted publicke[y]' /var/log/auth.log", "sudo grep 'Invalid use[r]' /var/log/auth.log | awk '{print $(NF-2)}' | sort | uniq -c", quem="servidor", prep=[LOGINS])}
<p>Num servidor de verdade, essa segunda linha costuma mostrar centenas de IPs desconhecidos por dia. É o motivo do <a href="fail2ban.html">fail2ban</a>.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Sem permissão", "O log de autenticação é só do root e do grupo <code>adm</code>:", T("sl-erro", "tail -n 2 /var/log/auth.log", "ls -l /var/log/auth.log", quem="servidor"), "Use <code>sudo</code>, ou peça para entrar no grupo <code>adm</code>.")}
"""

def sl_ex():
    return (EX(1, "Pelo systemd", "Complete para ver o log do serviço ssh:", "sudo journalctl -u ", "ssh", " -n 20") +
            EX(2, "Ao vivo", "Que opção do <code>journalctl</code> acompanha as linhas novas?", "sudo journalctl -u ssh ", "-f", rotulo="opção") +
            MC(3, "<code>Invalid user teste from 192.168.0.10</code> quer dizer:", ["o usuário teste entrou", "alguém em 192.168.0.10 tentou um usuário que não existe", "o servidor caiu", "a chave expirou"], 2) +
            MC(4, "Em que arquivo, no Debian, ficam os logs de login?", ["<code>/var/log/auth.log</code>", "<code>~/.ssh/known_hosts</code>", "<code>/etc/ssh/sshd_config</code>", "<code>/var/log/ssh.txt</code>"], 1))

def sl_miss():
    return (M("sl-m1", "no servidor, conte quantas vezes alguém entrou com chave.", "sudo grep -c 'Accepted publicke[y]' /var/log/auth.log", r"src:grep -c;;src:auth.log;;outre:^\d+$", quem="servidor", prep=[LOGINS]) +
            M("sl-m2", "no servidor, mostre as tentativas com usuários que não existem.", "sudo grep 'Invalid use[r]' /var/log/auth.log", r"src:auth.log;;out:Invalid user", quem="servidor", prep=[LOGINS]))

# ---------------------------------------------------------------- fail2ban
def f2_corpo():
    return f"""
<h2>Bloqueando quem erra demais</h2>
<p>O <code>fail2ban</code> lê os logs, conta as falhas de cada IP e, passando do limite, bloqueia esse IP no firewall por um tempo. Ele é útil sobretudo enquanto a senha ainda está ligada, mas também limpa o barulho dos robôs.</p>
<pre class="cmd">
sudo apt install fail2ban
sudo systemctl enable --now fail2ban
</pre>
<hr>
<h2>1. A regra do laboratório</h2>
<p>A configuração sua vai em <code>/etc/fail2ban/jail.local</code> (o <code>jail.conf</code> é do pacote e não se mexe). A do laboratório:</p>
{T("f2-conf", "cat /etc/fail2ban/jail.local", quem="servidor", notas={"maxretry = 3": "3 falhas...", "findtime = 10m": "...em 10 minutos...", "bantime = 10m": "...e o IP fica 10 minutos bloqueado"})}
<div class="note"><strong>backend</strong><p>No laboratório o fail2ban lê o arquivo <code>/var/log/auth.log</code> (<code>backend = polling</code>). Num Debian 13 com systemd, o pacote já vem com <code>backend = systemd</code> e lê o journal; aí basta o <code>enabled = true</code>.</p></div>
<hr>
<h2>2. Errando a senha</h2>
<p>Do notebook, sem a chave, três senhas erradas seguidas:</p>
{T("f2-errar", "ssh -o PubkeyAuthentication=no lab@servidor", prep=[F2_LIGA], resp=[ERRADA(1), ERRADA(2), ERRADA(3)], notas={"Permission denied": "terceira falha"})}
<p>Alguns segundos depois, nem a chave certa passa: o notebook está bloqueado.</p>
{T("f2-bloqueado", "ssh lab@servidor hostname", estado="continua", prep=[ESPERA], notas={"Connection refused": "o firewall recusou antes do sshd"})}
<hr>
<h2>3. Vendo e desbloqueando, no servidor</h2>
{T("f2-status", "sudo fail2ban-client status sshd", "sudo fail2ban-client set sshd unbanip 192.168.0.10", quem="servidor", estado="continua", notas={"Banned IP list:": "os IPs bloqueados agora"})}
{T("f2-volta", "ssh lab@servidor hostname", estado="continua", notas={"servidor": "liberado de novo"})}
<div class="tip"><strong>Não bloqueie a si mesmo</strong><p>Em <code>jail.local</code>, a linha <code>ignoreip = 127.0.0.1/8 192.168.0.0/24</code> (na seção <code>[DEFAULT]</code>) faz o fail2ban nunca bloquear esses endereços. Ponha ali o IP de onde você trabalha.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("O fail2ban não está rodando", "Sem o serviço, o <code>fail2ban-client</code> não tem com quem falar:", T("f2-erro", "sudo fail2ban-client status", quem="servidor"), "Ligue o serviço (<code>sudo systemctl enable --now fail2ban</code>) e confira com <code>sudo fail2ban-client status</code>.")}
"""

def f2_ex():
    return (EX(1, "O arquivo seu", "Em que arquivo vai a sua configuração?", "/etc/fail2ban/", "jail.local") +
            EX(2, "Desbloquear", "Complete para desbloquear um IP na jail sshd:", "sudo fail2ban-client set sshd ", "unbanip", " 192.168.0.10", rotulo="ação") +
            MC(3, "Com <code>maxretry = 3</code> e <code>bantime = 10m</code>:", ["3 erros e o IP fica 10 minutos bloqueado", "o servidor desliga em 10 minutos", "o usuário é apagado", "3 usuários por vez"], 1) +
            MC(4, "Bloqueado pelo fail2ban, o ssh mostra:", ["<code>Permission denied (publickey)</code>", "<code>Connection refused</code> (ou espera até desistir)", "<code>Host key verification failed</code>", "nada, entra normal"], 2))

def f2_miss():
    return (M("f2-m1", "no servidor, com o fail2ban ligado, mostre as jails ativas.", "sudo fail2ban-client status", r"src:fail2ban-client status;;out:Jail list", quem="servidor", prep=[F2_LIGA]) +
            M("f2-m2", "no servidor, mostre quantas falhas bloqueiam um IP na jail sshd.", "sudo fail2ban-client get sshd maxretry", r"src:get sshd maxretry;;outre:^\d+$", quem="servidor", prep=[F2_LIGA]))

# ---------------------------------------------------------------- depuração
DP_FILTRO = "grep -E 'Connecting to|Connection established|Authenticating to|is known and matches|Authentications that|Offering|accepts key|Authenticated to'"
def dp_corpo():
    return f"""
<h2>O ssh fala o que está fazendo</h2>
<p>Quando algo dá errado e a mensagem final não ajuda, rode o mesmo comando com <code>-v</code> (de <em>verbose</em>). Cada linha que começa com <code>debug1:</code> é um passo da conexão. <code>-vv</code> e <code>-vvv</code> mostram ainda mais.</p>
<p>A saída completa tem dezenas de linhas, e as mensagens do <code>-v</code> saem pela saída de erro. Por isso o <code>2&gt;&amp;1</code> antes do <code>grep</code>:</p>
<hr>
<h2>1. Uma conexão que deu certo</h2>
{T("dp-ok", "ssh -v lab@servidor true 2>&1 | " + DP_FILTRO, notas={"Connecting to servidor [192.168.0.20] port 22": "1. achou o IP e a porta", "is known and matches": "2. a chave do servidor confere", "Authentications that can continue": "3. o que o servidor aceita", "Offering public key": "4. o notebook oferece a chave", "Authenticated to": "5. entrou"})}
<p>Leia sempre nessa ordem: <strong>rede</strong> (conectou?), <strong>servidor</strong> (a chave dele confere?), <strong>você</strong> (que chaves ofereceu, e qual foi aceita?).</p>
<hr>
<h2>2. Uma conexão que não deu</h2>
<p>Aqui a chave do notebook não está no <code>authorized_keys</code> do servidor:</p>
{T("dp-falha", "ssh -v -o BatchMode=yes lab@servidor true 2>&1 | grep -E 'Authentications that|Offering|Trying private key|Permission denied'", estado="chavelocal", notas={"Offering public key": "a chave foi oferecida...", "Permission denied": "...mas o servidor não a conhece"})}
<p>O servidor recusou a chave oferecida e só sobrou a senha. A conclusão: o problema é o <code>authorized_keys</code> do servidor, não a rede.</p>
<hr>
<h2>3. O que o ssh vai fazer, sem conectar</h2>
<p>O <code>ssh -G</code> (do Nível 3) mostra a configuração calculada: útil quando a dúvida é o <code>~/.ssh/config</code>.</p>
{T("dp-G", "ssh -G interno | grep -E '^(hostname|user|port|proxyjump|identityfile) '", estado="config")}
<div class="note"><strong>Do lado do servidor</strong><p>Quem tem acesso ao servidor pode olhar o log (<a href="sshd-logs.html">aula dos logs</a>), que às vezes diz o motivo exato, como <code>bad ownership or modes</code>. Em último caso, <code>sudo /usr/sbin/sshd -d -p 2222</code> sobe um sshd de teste que atende uma conexão na porta 2222 e explica tudo na tela.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Parou no passo 2", "Num notebook que ainda não conhece o servidor, com <code>BatchMode=yes</code> (sem perguntas), o <code>-v</code> mostra que a conexão nem chegou à sua chave:", T("dp-erro", "ssh -v -o BatchMode=yes lab@servidor true 2>&1 | grep -E 'Connection established|Server host key|host key is known|verification failed'", estado="zero"), "A rede está boa (passo 1), mas a chave do servidor não pôde ser conferida (passo 2). Veja a aula de <a href='erros-host.html'>erros de host</a>. Lembre: sem o <code>2&gt;&amp;1</code>, as linhas do <code>-v</code> passam direto pelo <code>grep</code>.")}
"""

def dp_ex():
    return (EX(1, "Mais detalhes", "Que opção mostra os passos da conexão?", "ssh ", "-v", " lab@servidor", rotulo="opção") +
            EX(2, "Para o grep", "Complete para mandar as mensagens do -v para o grep:", "ssh -v lab@servidor true ", "2>&1", " | grep Offering") +
            MC(3, "Aparece <code>Offering public key</code> e depois <code>Permission denied</code>. O problema provável é:", ["a rede", "a chave não está no authorized_keys do servidor", "o DNS", "o known_hosts"], 2) +
            MC(4, "Para ver a configuração calculada sem conectar:", ["<code>ssh -v</code>", "<code>ssh -G</code>", "<code>ssh -T</code>", "<code>ssh -N</code>"], 2))

def dp_miss():
    return (M("dp-m1", "conecte com <code>-v</code> e mostre só a linha que diz como você entrou.", "ssh -v lab@servidor true 2>&1 | grep 'Authenticated to'", r"src:-v;;src:2>&1;;outre:^Authenticated to .* using .publickey.\.$") +
            M("dp-m2", "conecte com <code>-v</code> e mostre que chave o notebook ofereceu.", "ssh -v lab@servidor true 2>&1 | grep 'Offering public key'", r"src:-v;;outre:^debug1: Offering public key: \S+ ED25519 SHA256:"))

# ---------------------------------------------------------------- erros de chave
PERM_RUIM = [["notebook", "ana", "chmod 644 ~/.ssh/id_ed25519"]]
def ek_corpo():
    return f"""
<h2>Os dois erros de chave mais comuns</h2>
<p>Esta aula junta os erros de autenticação que você mais vai ver, o que cada um quer dizer e como resolver.</p>
<hr>
<h2>1. Permission denied (publickey)</h2>
<p>O servidor só aceita chave (senha desligada) e nenhuma das chaves que o notebook ofereceu está no <code>authorized_keys</code> dele:</p>
{T("ek-negado", "ssh lab@servidor", "ssh -v lab@servidor true 2>&1 | grep -E 'Offering|Permission denied'", estado="chavelocal", prep=SEM_SENHA, notas={"Permission denied (publickey)": "só chave, e nenhuma serviu"})}
{REF([("Ofereceu a chave e não foi aceita", "falta a chave pública no <code>~/.ssh/authorized_keys</code> do servidor, ou o usuário está errado."), ("Não ofereceu chave nenhuma", "o nome do arquivo não é o padrão: use <code>-i</code> ou <code>IdentityFile</code>."), ("O log do servidor fala em <code>bad ownership</code>", "permissões da pasta do usuário no servidor (aula de <a href=\"permissoes.html\">permissões</a>).")], cab=("No ssh -v", "Causa provável"))}
<p>Com a senha desligada, o <code>ssh-copy-id</code> não funciona mais: a chave nova entra por outro caminho que já tem acesso (outra chave, o console do provedor, um colega).</p>
<hr>
<h2>2. UNPROTECTED PRIVATE KEY FILE</h2>
<p>A chave privada ficou legível por outros usuários (aqui, <code>644</code>). O ssh se recusa a usá-la:</p>
{T("ek-perm", "ls -l ~/.ssh/id_ed25519", "ssh -o BatchMode=yes lab@servidor hostname", "chmod 600 ~/.ssh/id_ed25519", "ssh lab@servidor hostname", prep=PERM_RUIM, notas={"UNPROTECTED PRIVATE KEY FILE": "o aviso", "bad permissions": "a chave foi ignorada", "-rw-r--r--": "todo mundo lê: ruim"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Usuário errado", "A chave está certa, mas no usuário errado do servidor. A ana não tem conta lá com essa chave:", T("ek-erro", "ssh -o BatchMode=yes ana@servidor hostname"), "Confira o usuário antes do <code>@</code> (ou o <code>User</code> no config). Sem usuário, o ssh usa o seu nome do notebook.")}
"""

def ek_ex():
    return (EX(1, "Arrumando a chave", "Complete para deixar a chave privada só para você:", "chmod ", "600", " ~/.ssh/id_ed25519") +
            EX(2, "Sem perguntas", "Que opção faz o ssh desistir em vez de pedir senha?", "ssh -o ", "BatchMode=yes", " lab@servidor", rotulo="opção") +
            MC(3, "<code>Permission denied (publickey)</code> quer dizer:", ["o servidor está desligado", "o servidor só aceita chave e nenhuma serviu", "a rede caiu", "a chave do servidor mudou"], 2) +
            MC(4, "<code>UNPROTECTED PRIVATE KEY FILE</code> se resolve com:", ["<code>chmod 600</code> na chave privada", "<code>ssh-keygen -R</code>", "apagando o known_hosts", "reiniciando o servidor"], 1))

def ek_miss():
    return (M("ek-m1", "a sua chave privada ficou com permissões abertas. Arrume e conecte.", "chmod 600 ~/.ssh/id_ed25519 && ssh lab@servidor hostname", r"src:chmod 600;;outre:^servidor$", prep=PERM_RUIM) +
            M("ek-m2", "com uma chave que o servidor não conhece, tente entrar sem perguntar senha.", "ssh -o BatchMode=yes lab@servidor hostname", r"src:BatchMode=yes;;out:Permission denied", estado="chavelocal"))

# ---------------------------------------------------------------- erros de host
def eh_corpo():
    return f"""
<h2>Quando a chave do servidor não bate</h2>
<p>O <code>known_hosts</code> (Nível 1) guarda a chave de cada servidor. Se o servidor responde com uma chave diferente, o ssh <strong>para tudo</strong>: pode ser um ataque (alguém no meio do caminho), ou só um servidor reinstalado.</p>
<hr>
<h2>1. REMOTE HOST IDENTIFICATION HAS CHANGED</h2>
<p>Na coleta, as chaves do servidor foram geradas de novo, como acontece numa reinstalação:</p>
{T("eh-mudou", "ssh lab@servidor hostname", prep=[NOVA_CHAVE_HOST], notas={"REMOTE HOST IDENTIFICATION HAS CHANGED": "a chave mudou", "known_hosts:1": "a linha com a chave antiga", "Host key verification failed": "e o ssh não conecta"})}
<div class="warning"><strong>Antes de apagar</strong><p>Pergunte: o servidor foi reinstalado? Trocou de máquina? Se ninguém sabe por que mudou, <strong>não conecte</strong>. Confira o fingerprint novo direto no servidor (console do provedor): <code>ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub</code>.</p></div>
<hr>
<h2>2. Tirando a chave velha</h2>
<p>Sabendo que a mudança é legítima, o <code>ssh-keygen -R</code> apaga a linha antiga, e a próxima conexão pergunta como se fosse a primeira:</p>
{T("eh-R", "ssh-keygen -R servidor", "ssh lab@servidor hostname", prep=[NOVA_CHAVE_HOST], resp=[SIM], notas={"found: line 1": "achou a linha antiga", "known_hosts.old": "e guardou uma cópia", "(yes/no/[fingerprint])": "a pergunta de novo, com a chave nova"})}
<hr>
<h2>3. Host key verification failed, sem pergunta</h2>
<p>Em scripts (<code>BatchMode=yes</code>) o ssh não pode perguntar. Um servidor ainda desconhecido também dá esse erro:</p>
{T("eh-batch", "ssh -o BatchMode=yes lab@servidor true", estado="zero", notas={"Host key verification failed": "desconhecido e sem poder perguntar"})}
<p>A saída é conectar uma vez à mão (respondendo <code>yes</code> depois de conferir), ou pôr a chave no <code>known_hosts</code> antes, com <code>ssh-keyscan servidor &gt;&gt; ~/.ssh/known_hosts</code>, conferindo o fingerprint.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Apagou o nome, sobrou o IP", "Se você conecta às vezes pelo nome e às vezes pelo IP, o <code>known_hosts</code> tem duas linhas. Tirar só uma não basta:", T("eh-erro", "ssh-keygen -R servidor", "ssh lab@192.168.0.20 hostname", estado="conhecido", prep=[NOVA_CHAVE_HOST]), "Rode o <code>ssh-keygen -R</code> também para o IP: <code>ssh-keygen -R 192.168.0.20</code>.")}
"""

def eh_ex():
    return (EX(1, "Tirar a chave antiga", "Complete para apagar o servidor do known_hosts:", "ssh-keygen ", "-R", " servidor", rotulo="opção") +
            EX(2, "Conferir no servidor", "Complete para ver o fingerprint da chave do servidor, lá dentro:", "ssh-keygen -lf /etc/ssh/", "ssh_host_ed25519_key.pub") +
            MC(3, "A chave do servidor mudou e ninguém sabe por quê. Você:", ["apaga o known_hosts e entra", "não conecta e confere o fingerprint por outro caminho", "usa <code>-v</code>", "desliga o fail2ban"], 2) +
            MC(4, "<code>Host key verification failed</code> aparece quando:", ["a senha está errada", "a chave do servidor não pôde ser confirmada", "a porta está fechada", "falta o authorized_keys"], 2))

def eh_miss():
    return (M("eh-m1", "o servidor foi reinstalado (de verdade). Tire a chave antiga e conecte de novo.", "ssh-keygen -R servidor && ssh lab@servidor hostname", r"src:ssh-keygen -R;;out:known_hosts updated;;outre:^servidor$", prep=[NOVA_CHAVE_HOST], resp=[SIM]) +
            M("eh-m2", "sem conhecer o servidor ainda, tente conectar sem deixar o ssh perguntar.", "ssh -o BatchMode=yes lab@servidor true", r"src:BatchMode=yes;;out:Host key verification failed", estado="zero"))

# ---------------------------------------------------------------- erros de conexão
def ec_corpo():
    return f"""
<h2>Antes da senha e da chave: a rede</h2>
<p>Estes erros acontecem antes de qualquer autenticação. A mensagem diz em que passo parou:</p>
{REF([("Could not resolve hostname", "o nome não virou IP: erro de digitação ou DNS."), ("Connection refused", "o computador respondeu, mas ninguém atende nessa porta."), ("Connection timed out", "ninguém respondeu: IP errado, firewall descartando ou máquina desligada."), ("No route to host / Network is unreachable", "o notebook não tem caminho até esse IP.")], cab=("Mensagem", "Onde parou"))}
<hr>
<h2>1. Nome errado</h2>
{T("ec-nome", "ssh lab@servidr", notas={"Could not resolve hostname servidr": "o nome não existe"})}
<hr>
<h2>2. Porta errada ou sshd parado</h2>
{T("ec-porta", "ssh -p 2222 lab@servidor", notas={"Connection refused": "nada na porta 2222"})}
<p>A mesma mensagem, na porta certa, quando o sshd está parado (na coleta, paramos de propósito):</p>
{T("ec-parado", "ssh lab@servidor", prep=[PARA_SSHD], notas={"port 22: Connection refused": "o servidor está lá, o sshd não"})}
<p>No servidor: <code>sudo systemctl status ssh</code> e <code>sudo systemctl start ssh</code>.</p>
<hr>
<h2>3. Ninguém responde</h2>
<p>Um IP da rede em que não há máquina nenhuma. O <code>ConnectTimeout</code> evita esperar mais de um minuto:</p>
{T("ec-ninguem", "ssh -o ConnectTimeout=5 lab@192.168.0.50", tempo=60)}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Testando só a porta", "Para saber se a porta abre, sem entrar, o <code>-v</code> com <code>true</code> mostra o primeiro passo. Conectou e deu outro erro depois? Então a rede está boa:", T("ec-erro", "ssh -v -o BatchMode=yes lab@servidor true 2>&1 | grep -E 'Connecting to|Connection established|Permission denied'", estado="chavelocal", prep=SEM_SENHA), "Aqui a conexão foi estabelecida: o problema não é a rede, é a chave.")}
"""

def ec_ex():
    return (EX(1, "Sem esperar demais", "Complete para desistir depois de 5 segundos:", "ssh -o ", "ConnectTimeout=5", " lab@servidor", rotulo="opção") +
            EX(2, "Outra porta", "Complete para conectar na porta 2222:", "ssh ", "-p 2222", " lab@servidor") +
            MC(3, "<code>Connection refused</code> quer dizer:", ["senha errada", "o computador respondeu, mas nada escuta na porta", "o nome não existe", "a chave mudou"], 2) +
            MC(4, "<code>Could not resolve hostname</code>: o que conferir primeiro?", ["a digitação do nome", "as permissões da chave", "o authorized_keys", "o fail2ban"], 1))

def ec_miss():
    return (M("ec-m1", "tente conectar numa porta em que nada escuta.", "ssh -p 2222 lab@servidor", r"src:-p 2222;;out:Connection refused") +
            M("ec-m2", "erre o nome do servidor de propósito.", "ssh lab@servidr", r"src:servidr;;out:Could not resolve hostname"))

# ---------------------------------------------------------------- projeto: acesso
PA_CONF = "printf 'Host srv\\n    HostName servidor\\n    User lab\\n' >> ~/.ssh/config"
def pa_corpo():
    return f"""
<h2>O projeto</h2>
<p>Do zero, num servidor novo: criar a chave, levar para o servidor, dar um apelido, desligar a senha e provar que só a chave entra. É o roteiro de todo servidor que você for ganhar. As caixas seguem uma a outra, sem voltar o laboratório ao começo.</p>
<hr>
<h2>1. A chave e o servidor</h2>
{T("pa-1", "ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/id_ed25519", "ssh-copy-id lab@servidor", estado="zero", resp=[SIM, SENHA], notas={"Number of key(s) added: 1": "a chave chegou"})}
<p>Aqui a chave ficou sem frase para a caixa andar sozinha. No seu notebook, ponha uma frase e use o <a href="ssh-agent.html">ssh-agent</a>.</p>
<hr>
<h2>2. O apelido</h2>
{T("pa-2", PA_CONF, "chmod 600 ~/.ssh/config", "ssh srv hostname", estado="continua", notas={"servidor": "pelo apelido, sem senha"})}
<hr>
<h2>3. Fechando a senha, no servidor</h2>
{T("pa-3", "echo 'PasswordAuthentication no' | sudo tee /etc/ssh/sshd_config.d/10-sem-senha.conf", RECARREGA, quem="servidor", estado="continua")}
<hr>
<h2>4. A prova</h2>
{T("pa-4", "ssh -o PubkeyAuthentication=no srv", "ssh srv 'whoami; hostname'", estado="continua", notas={"Permission denied (publickey)": "sem chave, nada", "lab": "com a chave, tudo"})}
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Desligou a senha antes da chave", "Se a ordem se inverte, o servidor tranca você do lado de fora e o <code>ssh-copy-id</code> já não consegue entrar:", T("pa-erro", "ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/id_ed25519", "ssh-copy-id lab@servidor", estado="conhecido", prep=SEM_SENHA), "Sempre: chave primeiro, teste, e só então a senha sai.")}
"""

def pa_ex():
    return (EX(1, "Levando a chave", "Complete para copiar a chave para o servidor:", "", "ssh-copy-id", " lab@servidor", rotulo="comando") +
            MC(2, "A ordem certa é:", ["desligar a senha, depois copiar a chave", "copiar a chave, testar, depois desligar a senha", "trocar a porta primeiro", "tanto faz"], 2) +
            MC(3, "Para provar que a senha está mesmo desligada, use:", ["<code>ssh -o PubkeyAuthentication=no srv</code>", "<code>ssh -v srv</code>", "<code>ssh-keygen -R srv</code>", "<code>ssh -G srv</code>"], 1))

def pa_miss():
    return (M("pa-m1", "num notebook sem chave, crie uma e leve para o servidor.", "ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/id_ed25519 && ssh-copy-id lab@servidor", r"src:ssh-keygen;;src:ssh-copy-id;;out:Number of key(s) added: 1", estado="zero", resp=[SIM, SENHA]) +
            M("pa-m2", "com o apelido pronto, mostre com que usuário e em que máquina você entra.", "ssh servidor 'whoami; hostname'", r"src:whoami;;outre:^lab$;;outre:^servidor$", estado="config"))

# ---------------------------------------------------------------- projeto: backup
PB_SCRIPT = "printf '#!/bin/sh\\nrsync -a --delete ~/projeto/ servidor:backup/ && echo backup ok\\n' > backup.sh"
def pb_corpo():
    return f"""
<h2>O projeto</h2>
<p>Guardar a pasta <code>projeto</code> do notebook no servidor, atualizar só o que mudou, recuperar um arquivo apagado e deixar tudo num script. Usa o apelido <code>servidor</code> do <code>~/.ssh/config</code> e o <a href="rsync.html">rsync</a>.</p>
<hr>
<h2>1. A primeira cópia</h2>
{T("pb-1", "rsync -a projeto/ servidor:backup/", "ssh servidor 'ls -R backup'", estado="config")}
<hr>
<h2>2. Só o que mudou</h2>
{T("pb-2", "echo '<!-- versão 2 -->' >> projeto/index.html", "rsync -av projeto/ servidor:backup/", estado="continua", notas={"index.html": "só este arquivo viajou"})}
<hr>
<h2>3. Recuperando um arquivo</h2>
{T("pb-3", "rm projeto/estilo.css", "rsync -av servidor:backup/estilo.css projeto/", "ls projeto", estado="continua", notas={"estilo.css": "voltou do servidor"})}
<hr>
<h2>4. Um script</h2>
{T("pb-4", PB_SCRIPT, "chmod +x backup.sh", "./backup.sh", "cat backup.sh", estado="continua", notas={"backup ok": "o script rodou"})}
<p>Para rodar sozinho todo dia às 20h, o <code>crontab -e</code> recebe uma linha como <code>0 20 * * * $HOME/backup.sh</code>. Como a chave não pede nada (ou o agente está carregado), o cron consegue conectar.</p>
<div class="warning"><strong>--delete</strong><p>Com <code>--delete</code>, o que você apagar no notebook some também do backup na próxima vez. Para guardar versões, use uma pasta por dia, como <code>backup/$(date +%F)/</code>.</p></div>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Esqueceu a barra", "Sem a barra no fim de <code>projeto/</code>, o rsync cria uma pasta <code>projeto</code> dentro do destino, em vez de copiar o que está nela:", T("pb-erro", "rsync -a projeto servidor:backup/", "ssh servidor 'ls backup'", estado="config"), "Com a barra, vai o <strong>conteúdo</strong> da pasta; sem ela, a pasta inteira. Use sempre <code>--dry-run</code> na dúvida.")}
"""

def pb_ex():
    return (EX(1, "O backup", "Complete para copiar o conteúdo da pasta:", "rsync -a ", "projeto/", " servidor:backup/projeto/") +
            EX(2, "Ensaiar antes", "Que opção do rsync mostra o que faria, sem fazer?", "rsync -av ", "--dry-run", " projeto/ servidor:backup/", rotulo="opção") +
            MC(3, "Na segunda vez, o rsync envia:", ["tudo de novo", "só o que mudou", "nada", "só as pastas"], 2) +
            MC(4, "Para o cron conseguir conectar, a chave:", ["precisa de frase, digitada pelo cron", "não pode pedir frase (ou o agente já está carregado)", "tem de ser RSA", "fica no servidor"], 2))

def pb_miss():
    return (M("pb-m1", "copie a pasta <code>projeto</code> para <code>backup</code> no servidor e liste o que chegou.", "rsync -a projeto/ servidor:backup/ && ssh servidor ls backup", r"src:rsync;;out:index.html", estado="config") +
            M("pb-m2", "ensaie o backup, sem copiar nada.", "rsync -av --dry-run projeto/ servidor:backup/", r"src:--dry-run;;out:(DRY RUN)", estado="config"))

# ---------------------------------------------------------------- projeto: túnel
PT_CONF = "printf 'Host wiki\\n    HostName 192.168.0.130\\n    User lab\\n    ProxyJump servidor\\n    LocalForward 8090 localhost:80\\n    ExitOnForwardFailure yes\\n' >> ~/.ssh/config"
def pt_corpo():
    return f"""
<h2>O projeto</h2>
<p>A wiki da empresa roda na máquina <code>interno</code>, que só a rede do servidor enxerga. O objetivo: abrir a wiki no navegador do notebook com <strong>um comando</strong>, pulando pelo servidor e com um túnel, tudo guardado no config.</p>
<hr>
<h2>1. O ponto de partida</h2>
{T("pt-1", "curl -sS --max-time 3 http://192.168.0.130/", "ssh interno 'curl -s http://localhost/'", estado="config", notas={"Wiki interna": "lá dentro ela existe"})}
<hr>
<h2>2. O bloco no config</h2>
{T("pt-2", PT_CONF, "ssh -G wiki | grep -E '^(hostname|proxyjump|localforward) '", estado="continua")}
<hr>
<h2>3. Abrindo, usando e fechando</h2>
{T("pt-3", "ssh -f -N wiki", "curl -s http://localhost:8090/", "pgrep -a ssh", "pkill -f 'ssh -f -N wiki'", estado="continua", notas={"Wiki interna": "no notebook, pela porta 8090"})}
<p>O segundo processo, <code>ssh -W</code>, é o salto pelo servidor que o <code>ProxyJump</code> abriu sozinho; ele termina junto com o túnel. No navegador, <code>http://localhost:8090</code>. O caminho: notebook → (SSH) → servidor → (SSH) → interno → wiki. Os dois trechos da rede vão criptografados.</p>
<hr>
<h2 id="errado">Quando dá errado</h2>
{CEN("Abriu duas vezes", "Com <code>ExitOnForwardFailure</code>, o segundo túnel na mesma porta desiste em vez de ficar conectado à toa:", T("pt-erro", PT_CONF, "ssh -f -N wiki", "ssh -f -N wiki; echo \"código: $?\"", estado="config"), "Feche o primeiro (<code>pkill -f 'ssh -f -N wiki'</code>) ou use outra porta.")}
"""

def pt_ex():
    return (EX(1, "O salto", "Que linha do config faz passar pelo servidor?", "", "ProxyJump", " servidor", rotulo="opção") +
            EX(2, "O túnel", "Que linha do config abre o túnel local?", "", "LocalForward", " 8090 localhost:80", rotulo="opção") +
            MC(3, "Em <code>LocalForward 8090 localhost:80</code> dentro de <code>Host wiki</code>, o <code>localhost</code> é:", ["o notebook", "o servidor", "a máquina interno", "a internet"], 3))

def pt_miss():
    return (M("pt-m1", "abra um túnel até a wiki da máquina interno e leia a página no notebook.", "ssh -f -N -L 8090:localhost:80 interno && curl -s http://localhost:8090/", r"src:-L 8090;;out:Wiki interna", estado="config") +
            M("pt-m2", "leia a wiki pulando pelo servidor, sem túnel, rodando o curl lá dentro.", "ssh -J servidor lab@192.168.0.130 'curl -s http://localhost/'", r"src:-J servidor;;out:Wiki interna", estado="config"))

NIVEL = {"id": "n5", "nome": "Nível 5 · Servidor e depuração", "curto": "Servidor", "desc": "O sshd, endurecimento, logs, fail2ban, ssh -v, erros comuns e projetos", "grupos": [
    {"grupo": "O servidor", "aulas": [
        aula(slug="sshd-intro", menu="O servidor sshd", title="O servidor sshd: processo, porta, sshd_config e sshd -T", h1='O servidor <span class="hl">sshd</span>',
             desc="Conhecer o servidor SSH: o processo sshd, a porta 22, os arquivos de /etc/ssh, o Include de sshd_config.d e a configuração final com sshd -T.",
             intro="Do outro lado de cada conexão está o sshd. Esta aula mostra onde ele mora e como ler a configuração dele.",
             aprender=["Achar o processo e a porta do sshd.", "Diferenciar <code>sshd_config</code> de <code>ssh_config</code>.", "Ler a configuração final com <code>sshd -T</code>."],
             corpo=sd_corpo, exercicios=sd_ex, missoes=sd_miss,
             ref=[("sudo systemctl status ssh", "o serviço."), ("/etc/ssh/sshd_config", "configuração do servidor."), ("/etc/ssh/sshd_config.d/", "os seus arquivos."), ("sudo sshd -T", "a configuração final.")],
             resumo=["O servidor é o <code>sshd</code>, pacote <code>openssh-server</code>.", "Mexa em <code>sshd_config.d/</code>, que é lido primeiro.", "<code>sshd -T</code> mostra o que vale."]),
        aula(slug="sshd-senha", menu="Desligando a senha", title="Desligar o login por senha no SSH: PasswordAuthentication no", h1='Desligando a <span class="hl">senha</span>',
             desc="Desligar o login por senha no servidor SSH com PasswordAuthentication no, testar com sshd -t, recarregar e provar do cliente.",
             intro="Com a chave funcionando, o servidor pode parar de aceitar senha. Os robôs ficam do lado de fora.",
             aprender=["Criar um arquivo em <code>sshd_config.d</code>.", "Testar com <code>sshd -t</code> e recarregar.", "Provar com <code>PubkeyAuthentication=no</code>."],
             corpo=ss_corpo, exercicios=ss_ex, missoes=ss_miss,
             ref=[("PasswordAuthentication no", "só chave."), ("sudo sshd -t", "confere a configuração."), ("sudo systemctl reload ssh", "aplica."), ("ssh -o PubkeyAuthentication=no", "testa sem chave.")],
             resumo=["Chave primeiro, senha depois.", "<code>sshd -t</code> antes de recarregar.", "Teste numa segunda sessão."]),
        aula(slug="sshd-root", menu="Login do root", title="PermitRootLogin: proibir o login do root por SSH", h1='O login do <span class="hl">root</span>',
             desc="O PermitRootLogin do sshd: o padrão prohibit-password, proibir o root com PermitRootLogin no e usar um usuário com sudo.",
             intro="O root é o primeiro nome que os robôs tentam. O melhor é ele nem entrar por SSH.",
             aprender=["Ler o <code>PermitRootLogin</code>.", "Proibir o root.", "Usar <code>sudo</code> por SSH."],
             corpo=sr_corpo, exercicios=sr_ex, missoes=sr_miss,
             ref=[("PermitRootLogin no", "root não entra."), ("prohibit-password", "o padrão: só com chave."), ("ssh -t srv 'sudo cmd'", "sudo com pergunta.")],
             resumo=["Entre com usuário comum e use sudo.", "Crie o usuário antes de proibir o root.", "<code>without-password</code> é o mesmo que <code>prohibit-password</code>."]),
        aula(slug="sshd-endurecer", menu="Endurecendo o servidor", title="Endurecer o servidor SSH: MaxAuthTries, AllowUsers, Port e mais", h1='Endurecendo o <span class="hl">servidor</span>',
             desc="Um arquivo de endurecimento para o sshd: sem senha, sem root, MaxAuthTries, AllowUsers, X11Forwarding e a troca de porta com Port.",
             intro="Algumas linhas num arquivo só deixam o servidor bem mais fechado.",
             aprender=["Montar um arquivo de endurecimento.", "Conferir com <code>sshd -T</code>.", "Trocar a porta e conectar nela."],
             corpo=se_corpo, exercicios=se_ex, missoes=se_miss,
             ref=[("MaxAuthTries 3", "tentativas por conexão."), ("AllowUsers lab", "só estes."), ("Port 2222", "outra porta."), ("ssh -p 2222", "conecta nela.")],
             resumo=["Um arquivo seu em <code>sshd_config.d</code>.", "Libere o firewall antes de trocar a porta.", "<code>AllowUsers</code> barra até quem tem senha."]),
        aula(slug="sshd-logs", menu="Os logs do servidor", title="Logs do SSH: auth.log, journalctl e quem tentou entrar", h1='Os <span class="hl">logs</span> do servidor',
             desc="Ler os logs do sshd no /var/log/auth.log e no journalctl: logins aceitos, usuários inválidos e de onde vieram.",
             intro="Cada tentativa de login deixa rastro. Esta aula mostra onde e como ler.",
             aprender=["Achar o log do sshd.", "Ler linhas de login aceito e recusado.", "Contar tentativas por IP."],
             corpo=sl_corpo, exercicios=sl_ex, missoes=sl_miss,
             ref=[("sudo journalctl -u ssh", "log pelo systemd."), ("/var/log/auth.log", "o arquivo."), ("Accepted publickey", "entrou com chave."), ("Invalid user", "usuário que não existe.")],
             resumo=["O log é do root (e do grupo adm).", "Os colchetes no grep evitam a linha do sudo.", "Muito <code>Invalid user</code>? fail2ban."]),
        aula(slug="fail2ban", menu="fail2ban", title="fail2ban no SSH: bloquear IPs que erram a senha", h1='<span class="hl">fail2ban</span>: bloqueando quem erra',
             desc="Instalar e configurar o fail2ban para o SSH: jail.local, maxretry, bantime, ver os IPs bloqueados e desbloquear com unbanip.",
             intro="O fail2ban lê o log e bloqueia no firewall quem erra demais. Aqui você é bloqueado de verdade e se desbloqueia.",
             aprender=["Ler um <code>jail.local</code>.", "Ver um bloqueio acontecer.", "Ver e desbloquear IPs."],
             corpo=f2_corpo, exercicios=f2_ex, missoes=f2_miss,
             ref=[("/etc/fail2ban/jail.local", "a sua configuração."), ("fail2ban-client status sshd", "a jail do ssh."), ("set sshd unbanip IP", "desbloqueia."), ("ignoreip", "nunca bloquear.")],
             resumo=["3 falhas em 10 minutos, 10 minutos bloqueado.", "Bloqueado vê <code>Connection refused</code>.", "Ponha o seu IP no <code>ignoreip</code>."]),
    ]},
    {"grupo": "Depuração e erros", "aulas": [
        aula(slug="depuracao", menu="Depurando com -v", title="Depurar o SSH com ssh -v: lendo os passos da conexão", h1='Depurando com <span class="hl">-v</span>',
             desc="Usar ssh -v para ver cada passo da conexão: rede, chave do servidor, chaves oferecidas e autenticação; e ssh -G para a configuração.",
             intro="O -v transforma um erro misterioso numa lista de passos. Esta aula ensina a ler.",
             aprender=["Ler as linhas do <code>ssh -v</code>.", "Filtrar com <code>2&gt;&amp;1 | grep</code>.", "Saber onde a conexão parou."],
             corpo=dp_corpo, exercicios=dp_ex, missoes=dp_miss,
             ref=[("ssh -v / -vv / -vvv", "cada vez mais detalhe."), ("2>&1 | grep", "filtra o -v."), ("ssh -G host", "configuração calculada."), ("sshd -d -p 2222", "servidor de teste.")],
             resumo=["Rede, servidor, você: nessa ordem.", "O -v sai pela saída de erro.", "O log do servidor completa a história."]),
        aula(slug="erros-chave", menu="Erros de chave", title="Permission denied (publickey) e UNPROTECTED PRIVATE KEY FILE no SSH", h1='Erros de <span class="hl">chave</span>',
             desc="Resolver os erros de chave do SSH: Permission denied (publickey) e UNPROTECTED PRIVATE KEY FILE, com ssh -v e chmod 600.",
             intro="Os dois erros de chave mais comuns, com a causa e o conserto.",
             aprender=["Entender <code>Permission denied (publickey)</code>.", "Consertar <code>UNPROTECTED PRIVATE KEY FILE</code>.", "Conferir o usuário."],
             corpo=ek_corpo, exercicios=ek_ex, missoes=ek_miss,
             ref=[("Permission denied (publickey)", "nenhuma chave serviu."), ("UNPROTECTED PRIVATE KEY FILE", "<code>chmod 600</code> na chave."), ("-o BatchMode=yes", "não pergunta senha.")],
             resumo=["Veja com <code>-v</code> que chave foi oferecida.", "Chave privada: <code>600</code>.", "Confira o usuário."]),
        aula(slug="erros-host", menu="Erros de host", title="REMOTE HOST IDENTIFICATION HAS CHANGED e Host key verification failed", h1='Erros de <span class="hl">host</span>',
             desc="Quando a chave do servidor muda: REMOTE HOST IDENTIFICATION HAS CHANGED, Host key verification failed, ssh-keygen -R e ssh-keyscan.",
             intro="Quando a chave do servidor muda, o ssh se recusa a conectar. Às vezes é ataque, quase sempre é reinstalação.",
             aprender=["Ler o aviso de chave mudada.", "Tirar a chave antiga com <code>ssh-keygen -R</code>.", "Entender o erro em scripts."],
             corpo=eh_corpo, exercicios=eh_ex, missoes=eh_miss,
             ref=[("ssh-keygen -R servidor", "tira a chave antiga."), ("ssh-keyscan servidor", "lê a chave do servidor."), ("ssh-keygen -lf chave.pub", "fingerprint.")],
             resumo=["Chave mudou sem explicação: não conecte.", "<code>-R</code> para o nome e para o IP.", "Em scripts, conheça o servidor antes."]),
        aula(slug="erros-conexao", menu="Erros de conexão", title="Connection refused, timed out e Could not resolve hostname no SSH", h1='Erros de <span class="hl">conexão</span>',
             desc="Erros de rede do SSH: Could not resolve hostname, Connection refused, Connection timed out e No route to host, com ConnectTimeout.",
             intro="Antes da chave e da senha, a conexão precisa chegar. A mensagem diz onde parou.",
             aprender=["Diferenciar os erros de rede.", "Usar <code>ConnectTimeout</code>.", "Ver se a rede está boa com <code>-v</code>."],
             corpo=ec_corpo, exercicios=ec_ex, missoes=ec_miss,
             ref=[("Could not resolve hostname", "nome."), ("Connection refused", "porta fechada."), ("timed out / No route to host", "ninguém responde."), ("-o ConnectTimeout=5", "desiste rápido.")],
             resumo=["Leia a mensagem: ela diz o passo.", "<code>Connection refused</code>: sshd parado ou porta errada.", "Conectou e falhou depois? Não é a rede."]),
    ]},
    {"grupo": "Projetos", "aulas": [
        aula(slug="projeto-acesso", menu="Projeto: acesso seguro", title="Projeto SSH: do zero ao servidor só com chave", h1='Projeto: <span class="hl">acesso seguro</span>',
             desc="Projeto final: criar a chave, copiar com ssh-copy-id, criar o apelido no config, desligar a senha e provar que só a chave entra.",
             intro="O roteiro completo de um servidor novo, em quatro passos seguidos.",
             aprender=["Juntar chave, config e sshd.", "Fazer na ordem certa.", "Provar o resultado."],
             corpo=pa_corpo, exercicios=pa_ex, missoes=pa_miss,
             ref=[("ssh-keygen -t ed25519", "a chave."), ("ssh-copy-id lab@servidor", "para o servidor."), ("Host srv", "o apelido."), ("PasswordAuthentication no", "fecha a senha.")],
             resumo=["Chave, teste, depois fecha a senha.", "Um apelido para cada servidor.", "Prove com <code>PubkeyAuthentication=no</code>."]),
        aula(slug="projeto-backup", menu="Projeto: backup", title="Projeto SSH: backup com rsync e um script", h1='Projeto: <span class="hl">backup</span>',
             desc="Projeto final: backup de uma pasta com rsync pelo SSH, atualização só do que mudou, recuperação de arquivo e um script para o cron.",
             intro="Um backup de verdade, com o rsync, o config e um script de duas linhas.",
             aprender=["Fazer e atualizar um backup.", "Recuperar um arquivo.", "Guardar num script."],
             corpo=pb_corpo, exercicios=pb_ex, missoes=pb_miss,
             ref=[("rsync -a pasta/ srv:destino/", "backup."), ("rsync -av --dry-run", "ensaio."), ("crontab -e", "agenda.")],
             resumo=["A barra no fim importa.", "<code>--delete</code> espelha, cuidado.", "O cron precisa de uma chave que não pergunte."]),
        aula(slug="projeto-tunel", menu="Projeto: túnel para a wiki", title="Projeto SSH: ProxyJump e LocalForward para um site interno", h1='Projeto: <span class="hl">túnel</span> para a wiki',
             desc="Projeto final: abrir no notebook um site de uma máquina interna, com ProxyJump e LocalForward guardados no ~/.ssh/config.",
             intro="Um site que só a rede interna enxerga, aberto no notebook com um comando.",
             aprender=["Juntar ProxyJump e LocalForward.", "Abrir e fechar o túnel.", "Entender o caminho."],
             corpo=pt_corpo, exercicios=pt_ex, missoes=pt_miss,
             ref=[("ProxyJump servidor", "passa pelo servidor."), ("LocalForward 8090 localhost:80", "o túnel."), ("ssh -f -N wiki", "abre."), ("pkill -f 'ssh -f -N wiki'", "fecha.")],
             resumo=["Tudo num bloco do config.", "O destino do LocalForward é visto pelo último salto.", "Feche o que não usa."]),
    ]},
]}
