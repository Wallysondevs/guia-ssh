# Como escrever uma aula do Guia SSH

O guia é uma **escola** para quem já usou um pouco o terminal (o [Guia Bash](https://wallysondevs.github.io/guia-bash/)) e **nunca usou SSH**. **Uma aula = um assunto.** Nunca mostre um comando "seco":
- explique cada parte;
- mostre a **saída real**, colhida no laboratório com o OpenSSH de verdade (seção 4);
- mostre o que acontece quando dá errado, com a mensagem **real**;
- termine com exercícios e duas missões “cole a saída”.

## 1. Onde fica cada coisa
As páginas `.html` **não se editam à mão**: são geradas por `tools/gerar.py` a partir de `tools/aulas_n1.py` … `aulas_n5.py`. Cada arquivo tem um `NIVEL` com os grupos e as aulas (`slug`, `menu`, `title`, `h1`, `desc`, `intro`, `aprender`, `corpo`, `exercicios`, `missoes`, `ref`, `resumo`). O `NIVEIS` de `assets/site.js` (menu, selo do nível, Anterior/Próximo) é escrito pelo gerador. Links internos só para páginas que estão no `NIVEIS`.

## 2. Ordem de uma aula
1. Intro e "Você vai aprender".
2. **De onde vêm as saídas** (o gerador põe a frase padrão: OpenSSH 10.0p2 no Linux, o laboratório e as chaves descartáveis).
3. A ideia antes do comando, com uma comparação do dia a dia.
4. Do simples ao completo, uma novidade por vez, cada exemplo com a saída real num `pre.term`.
5. **Quando dá errado** (`CEN(...)`): o comando errado e a mensagem real, explicada em português.
6. Referência, exercícios (`EX`, `MC`), missões (`M`) e resumo.

Aulas de **Projetos** são passo a passo, com as caixas seguidas (`estado="continua"`).

## 3. Caixas de terminal e missões
- `T("id", "comando", ..., notas={...})` gera um `pre.term` com a saída colhida. As `notas` são anotações (`«`) presas a um trecho que **tem de existir** na saída: se a coleta mudar e o trecho sumir, o gerador para com erro.
- `quem="servidor"` roda no servidor como `lab` (prompt `lab@servidor:~$`); o padrão é o notebook (`ana@notebook:~$`).
- `estado=` volta o laboratório a um ponto conhecido antes da caixa: `zero` (nada), `conhecido` (o `known_hosts` já tem o servidor), `chavelocal` (a ana tem chave, o servidor ainda não), `chave` (o padrão: a chave já está no servidor), `config` (mais o `~/.ssh/config` com `servidor` e `interno`) e `continua` (não volta nada).
- `prep=[[computador, usuario_ou_root, comando]]` roda preparos escondidos antes da caixa (ex.: desligar a senha no servidor). Diga no texto o que foi preparado.
- `resp=[SIM, SENHA, ERRADA(1), FRASE(...), NO(...)]` (de `tools/respostas.py`) responde às perguntas do ssh durante a coleta.
- `M("id", "tarefa", "solução", "metas")` gera uma missão “cole a saída”. Metas separadas por `;;`:

| Meta | Verdade quando… |
| --- | --- |
| `src:REGEX` | o comando da solução casa com a regex |
| `out:TEXTO` | a saída colada contém o texto |
| `outre:REGEX` | a saída casa com a regex (flag `m`) |
| `erro:TEXTO` | a saída contém a mensagem de erro |
| `semerro` | a saída não tem mensagem de erro |

- A meta **não pode depender** do que muda entre execuções: impressões digitais, números de processo, portas de origem, datas e horas, tamanhos de arquivo.
- Colar a solução (com ou sem o prompt) **não pode** cumprir a missão: o gerador e o `tools/testar-navegador.js` conferem.
- Missão que precisa de internet diz "Precisa de internet" no enunciado. (Hoje nenhuma precisa: tudo roda no laboratório.)

## 4. Saída real e privacidade
**Nenhuma saída é inventada.** Tudo foi colhido por `tools/coleta.sh` no laboratório (`tools/lab.sh`), com o OpenSSH 10.0p2 do Debian 13 em `pt_BR.UTF-8`. As mensagens saem como saíram (o OpenSSH fala inglês; o Bash e o coreutils, português): copie igual e explique.

- **Todas as chaves e impressões digitais mostradas são chaves descartáveis do laboratório, geradas na coleta e já destruídas.** As chaves do servidor do laboratório também são geradas só para ele.
- **Nunca** mostre o conteúdo de uma chave privada. Se a aula precisar mostrar como ela é, só a primeira linha, cortada com `…`.
- Só os nomes do guia: `ana@notebook`, `lab@servidor`, `lab@interno`, e os IPs `192.168.0.x` do laboratório, `127.0.0.1` e, como exemplo de IP público, `203.0.113.x` (reservado para documentação). MAC, se aparecer, só `02:00:00:00:00:xx`.
- Nada da máquina de coleta: nome, usuário, pastas, IPs, chaves, impressões digitais ou `known_hosts` reais. Nada de servidores ou domínios reais como exemplo.

## 5. Antes do commit
1. Gere e confira:
   ```bash
   python3 tools/gerar.py comandos && sudo bash tools/coleta.sh && python3 tools/gerar.py paginas
   ```
2. As missões passam:
   ```bash
   node tools/testar-missoes.js
   PUPPETEER_DIR=/caminho/puppeteer-core node tools/testar-navegador.js --todas
   ```
3. Nenhum dado de máquina real nas páginas nem no histórico:
   ```bash
   PROIBIDO=../lista.txt bash tools/checar-privacidade.sh
   ```
   A lista tem uma linha por texto proibido (nome do computador, usuário, pastas, IPs, impressões digitais das chaves reais); `re:` no começo da linha faz dela uma expressão regular. O caminho é lido a partir da raiz do guia. Guarde a lista **fora do repositório** e nunca faça commit dela.
