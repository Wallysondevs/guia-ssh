#!/usr/bin/env bash
# preparar-notebook.sh — cria os arquivos de exemplo do Guia SSH no computador CLIENTE (o "notebook").
# Uso: cd ~ && bash preparar-notebook.sh      (rode de novo para voltar os arquivos ao original)
set -e
cd "${1:-$HOME}"
printf 'Anotações da Ana\n- testar o SSH\n- copiar o projeto\n' > notas.txt
mkdir -p projeto/img site
printf '# Projeto da Ana\nUm site simples.\n' > projeto/README.md
printf '<h1>Olá</h1>\n' > projeto/index.html
printf 'body { color: navy; }\n' > projeto/estilo.css
head -c 2048 /dev/zero > projeto/img/logo.png
echo '<h1>Site da Ana</h1><p>Rodando no notebook (127.0.0.1:3000).</p>' > site/index.html
echo "Arquivos do notebook criados em $(pwd)"
