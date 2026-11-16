# Contas em Campo — site (público)

Portal de análise das finanças do futebol brasileiro, em Quarto, publicado no
GitHub Pages em https://contasemcampo.github.io/. Este repositório é
**público** e **não guarda dados**: `dados/` é gerado no build a partir de
`contasemcampo/dados` (repositório privado), pasta `data/site/`.

## Estrutura

```
_quarto.yml            projeto em português (raiz)
en/_quarto.yml         projeto em inglês, renderizado em _site/en
index.qmd              capa editorial
analises/              listagem + posts (editorias como categorias)
compare.qmd            comparador por temas (inclui _compare.qmd)
clubes/                páginas por clube, GERADAS no build (scripts/gerar_clubes.py)
clubes/_textos/        texto editorial opcional por clube, escrito à mão
como-analisamos.qmd    método, indicadores públicos, limites, correções, acesso acadêmico
correcoes.qmd          erratas lidas de dados/erratas.csv
termos.qmd             termos de uso e transição de licença
glossario.qmd, sobre.qmd
theme/                 base.scss + claro.scss + escuro.scss (tokens --obs-*)
scripts/               geradores que rodam antes do quarto render
construir.sh           copia dados do vizinho ../dados/data/site (se existir), gera clubes, renderiza PT e EN
```

Tudo que é gerado (`dados/`, `clubes/*/index.qmd`, `en/clubs/*/index.qmd`,
`_site/`) está no `.gitignore`.

## Publicar um texto novo

Crie `analises/posts/AAAA-MM-slug/index.qmd` com o front matter do modelo em
`analises/_modelo.md`: `title`, `description`, `date`, `categories`
(editoria), `clubes` (slugs), `temas`, `base` (versão da base usada).
Commit e push: o workflow renderiza e publica. Tradução, se houver, em
`en/analyses/posts/AAAA-MM-slug/index.qmd`.

Editorias: Contas dos clubes · SAFs e controle · Dinheiro do jogo · Mercado de
atletas · Dívidas e financiamento · Entenda as contas.

## Construir localmente

```bash
./construir.sh      # precisa de quarto e de ../dados/data/site (ou de dados/ já preenchido)
```

O painel usa OJS e carrega d3/Plot de um CDN; em ambiente sem acesso ao CDN
os gráficos não renderizam, mas o build termina.

## Regras

- Nenhum número é escrito à mão em página gerada; vem de `dados/`.
- Texto editorial que cite valores informa `base:` no front matter.
- Português primeiro; inglês espelha estrutura, não exige tradução de todo post.
- Estilo: tokens em `theme/*.scss`; nada de cores soltas em páginas.
- Commits em português, explicando o porquê.
