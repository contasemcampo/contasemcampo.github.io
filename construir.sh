#!/usr/bin/env bash
# Constrói o site completo em _site/.
#
# 1. Garante os dados em dados/: se existir um checkout do repositório privado
#    ao lado (../dados/data/site), copia SEMPRE de lá, para não construir com
#    um recorte velho. No GitHub Actions a cópia é feita pelo workflow antes
#    deste script, e nesse caso não há pasta vizinha para sobrescrever nada.
# 2. Gera as páginas de clubes (PT e EN) a partir de dados/.
# 3. Renderiza o português (raiz) e depois o inglês (en/ -> _site/en).
#    A ordem importa: a renderização da raiz limpa _site/.
set -euo pipefail
cd "$(dirname "$0")"

if [ -f ../dados/data/site/painel.csv ]; then
  mkdir -p dados && cp ../dados/data/site/* dados/
  echo "dados/ atualizado a partir de ../dados/data/site"
elif [ ! -f dados/painel.csv ]; then
  echo "ERRO: dados/painel.csv não existe e ../dados/data/site não foi encontrado." >&2
  echo "Rode o exportador no repositório de dados ou copie data/site para dados/." >&2
  exit 1
fi

python3 scripts/gerar_clubes.py

quarto render
quarto render en
touch _site/.nojekyll
echo "Site pronto em _site/ (base $(python3 -c 'import json;print(json.load(open("dados/versao.json"))["versao"])'))"
