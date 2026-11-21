#!/usr/bin/env bash
# preparar-servidor.sh — cria os arquivos de exemplo do Guia SSH no SERVIDOR (na pasta do usuário lab).
# Uso, no servidor, como lab: cd ~ && bash preparar-servidor.sh
set -e
cd "${1:-$HOME}"
printf 'Relatório mensal\nvendas: 42\nclientes novos: 7\n' > relatorio.txt
mkdir -p site
echo '<h1>Painel do servidor</h1><p>Esta página só abre no próprio servidor (127.0.0.1:8080).</p>' > site/index.html
echo "Arquivos do servidor criados em $(pwd)"
