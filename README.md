# Guia SSH

[Abra o Guia SSH](https://wallysondevs.github.io/guia-ssh/).

Curso de SSH em português para quem **já usou um pouco o terminal, mas nunca usou SSH**. Complementa o [Guia Bash](https://wallysondevs.github.io/guia-bash/): lá você aprende a usar o terminal; aqui, a acessar outro computador, copiar arquivos e abrir túneis pela rede.

São **41 páginas: a capa e 40 aulas em cinco níveis**, com uma aula por assunto:

- **Nível 1 · Base** (7 páginas, incluindo a capa): o laboratório, a primeira conexão, fingerprints, `known_hosts`, comandos e sessões remotas.
- **Nível 2 · Chaves** (8 aulas): `ssh-keygen`, `ssh-copy-id`, `authorized_keys`, frase secreta, agente, permissões e várias chaves.
- **Nível 3 · Config e arquivos** (7 aulas): `~/.ssh/config`, conexões reaproveitadas, `scp`, `sftp`, `rsync` e pipes remotos.
- **Nível 4 · Túneis e saltos** (6 aulas): túneis locais e remotos, proxy SOCKS, `ProxyJump` e túneis no arquivo de configuração.
- **Nível 5 · Servidor e depuração** (13 aulas): `sshd`, autenticação, logs, `fail2ban`, diagnóstico de erros e três projetos (acesso seguro, backup e túnel para uma wiki interna).

Cada aula explica o comando parte por parte, mostra a saída real e o que acontece quando dá errado. As saídas foram colhidas com o **OpenSSH 10.0p2 no Linux** (Debian 13, Bash 5.2, `pt_BR.UTF-8`), num laboratório isolado. As mensagens do OpenSSH aparecem em inglês, com a explicação em português; com outras versões, alguns detalhes podem mudar.

Os exemplos acompanham a usuária fictícia `ana`, no `notebook`, e o usuário `lab`, no `servidor`. Uma terceira máquina, `interno`, aparece nas aulas de túneis. **Todas as chaves e impressões digitais mostradas são descartáveis, do laboratório, e já foram destruídas.** Não copie essas chaves para uso real; gere as suas. Nenhuma chave privada completa é publicada.

## Como praticar

As páginas trazem **80 missões** no modo “Rode no seu terminal”. Não há simulador: você usa o OpenSSH de verdade e um ambiente de teste.

1. Prepare o ambiente seguindo [O laboratório](preparando.html): pode ser outra máquina, uma máquina virtual ou o próprio Linux com SSH em `localhost`.
2. Leia a missão, copie os comandos e rode no terminal indicado pela aula (cliente ou servidor).
3. Cole a saída na caixa e clique em **Conferir**.
4. Depois da primeira tentativa, consulte **Ver solução** se precisar.

Nenhuma missão precisa de internet depois que o ambiente e as ferramentas estiverem preparados. A instalação inicial de pacotes pode precisar de acesso à internet. O código e a saída colada nas caixas ficam só na página: não são enviados nem armazenados pelo avaliador.

Os scripts [preparar-notebook.sh](arquivos/preparar-notebook.sh) e [preparar-servidor.sh](arquivos/preparar-servidor.sh) criam os arquivos usados nos exercícios. Eles sobrescrevem os arquivos de exemplo com os mesmos nomes: use uma conta ou pasta reservada para o laboratório, sem documentos pessoais.

As aulas de administração alteram o servidor de teste. Não experimente mudanças de autenticação num servidor de produção ou no seu único acesso remoto. No laboratório da coleta, `lab` usa `sudo` sem senha; isso não é uma recomendação para servidores reais. A aula explica a diferença e o uso de `ssh -t` quando o comando precisa de um terminal.

## Abrir o site

Abra `index.html` no navegador ou publique a pasta no GitHub Pages. O site é estático (HTML, CSS e JavaScript), sem build; os links são relativos e o arquivo `.nojekyll` desliga o Jekyll. Os comandos das aulas rodam no seu terminal, não dentro da página.

## Manutenção

| Arquivo | Para quê |
| --- | --- |
| `tools/aulas_n1.py` … `aulas_n5.py` | O texto das aulas, os comandos de cada caixa e as missões. |
| `tools/index_pagina.py` | A capa (`index.html`). |
| `tools/gerar.py comandos` | Escreve `tools/comandos.txt`: cada caixa, com o estado do laboratório, quem roda e as respostas às perguntas. |
| `tools/lab.sh` | Monta e desmonta o laboratório (três *network namespaces* do Linux com `sshd`, `rsyslog` e `fail2ban` próprios, chaves de teste geradas na hora) e o volta a um estado conhecido antes de cada caixa. |
| `tools/coleta.sh` | Sobe o laboratório, roda de verdade cada caixa num terminal (pty) e desmonta tudo no fim; grava `_saidas/` e `_saidas-anon/`. Nenhuma das duas pastas vai para o git. |
| `tools/gerar.py paginas` | Gera as páginas `.html` e o `NIVEIS` do `assets/site.js` só a partir de `_saidas-anon/`. Se faltar coleta, para com erro. |
| `tools/checar-privacidade.sh` | Procura dados da máquina de coleta nas páginas e no histórico (lista real fora do repo, `PROIBIDO=../lista.txt`). |
| `tools/testar-missoes.js` | Confere a estrutura das missões e as metas `src`. |
| `tools/testar-navegador.js --todas` | Abre cada página num Chrome headless e testa as missões (positivos e negativos). |

Fluxo completo:

```bash
python3 tools/gerar.py comandos && sudo bash tools/coleta.sh && python3 tools/gerar.py paginas
PROIBIDO=../lista.txt bash tools/checar-privacidade.sh
node tools/testar-missoes.js
PUPPETEER_DIR=/caminho/puppeteer-core node tools/testar-navegador.js --todas
```

A coleta roda como root (cria os namespaces e um usuário de teste, que ela mesma apaga no fim) e precisa de `openssh-server`, `rsync`, `rsyslog`, `fail2ban`, `nftables`, `curl`, `iputils-ping` e do locale `pt_BR.UTF-8`. Ela não liga o `sshd` da máquina: cada computador do laboratório tem o seu, com chaves próprias. Para coletar só algumas caixas: `sudo bash tools/coleta.sh PREFIXO`.

Veja [CONTRIBUINDO.md](CONTRIBUINDO.md) para escrever ou mudar uma aula.
