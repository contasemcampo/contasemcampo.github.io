# Contas em Campo — site

Código-fonte de [contasemcampo.github.io](https://contasemcampo.github.io/), portal de análise das finanças do futebol brasileiro, feito com [Quarto](https://quarto.org/).

Este repositório é público e **não guarda dados**. O recorte público da base (indicadores, clubes, erratas) é gerado no build a partir do repositório privado de dados, e só o que o site exibe sai de lá.

| Caminho | Conteúdo |
|---|---|
| `index.qmd` | Capa |
| `analises/` | Análises por editoria (uma pasta por texto em `posts/`); modelo em `_modelo.md` |
| `compare.qmd`, `_compare.qmd` | Comparador por temas, até quatro clubes |
| `clubes/` | Páginas por clube, **geradas no build** por `scripts/gerar_clubes.py`; texto editorial opcional em `_textos/` |
| `como-analisamos.qmd`, `correcoes.qmd`, `termos.qmd`, `sobre.qmd`, `glossario.qmd` | Páginas de apoio |
| `en/` | Versão em inglês (projeto Quarto próprio, publicado em `/en/`) |
| `theme/` | Cores, tipografia e estilos (claro e escuro) |

O manual de operação (atualizar a base, publicar textos, mudar o que é público) está em `docs/MANUTENCAO.md`, no repositório privado de dados. Orientações para quem edita este repositório estão em `CLAUDE.md`.

## Renderizar localmente

```bash
./construir.sh          # copia os dados do repositório vizinho, gera as páginas de clubes e renderiza PT e EN
```

## Publicar uma análise

1. Copie o modelo de `analises/_modelo.md` para `analises/posts/AAAA-MM-slug/index.qmd`.
2. Preencha `title`, `description`, `date`, `categories` (editoria), `clubes`, `temas` e `base`.
3. Faça *commit* e *push*: o site é republicado sozinho.

Textos a partir de 15/11/2026: todos os direitos reservados (ver [Termos de uso](https://contasemcampo.github.io/termos.html)). Textos anteriores: CC BY-NC 4.0. Código sob licença MIT.
