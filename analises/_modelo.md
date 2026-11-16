# Modelo de análise

Copie este arquivo para `analises/posts/AAAA-MM-slug/index.qmd` e preencha.
A estrutura abaixo é a do portal: título informativo, resumo com a conclusão
que os números sustentam, três pontos, o texto, o que os números não
mostram, e o rodapé automático com fontes e critérios.

```yaml
---
title: "Título informativo, que responda a uma pergunta"
description: "Uma frase com a principal conclusão sustentada pelos números."
date: 2026-11-15
categories: [Contas dos clubes]      # uma editoria; ver lista abaixo
clubes: [atletico-mg, cruzeiro]      # slugs dos clubes tratados (ver dados/clubes.json)
temas: [receitas, obrigacoes]        # temas do Compare: receitas, resultado, obrigacoes, caixa, futebol, dono, campo
base: "1.1.0"                        # versão da base usada nos números citados
---
```

**Editorias:** Contas dos clubes · SAFs e controle · Dinheiro do jogo · Mercado de atletas · Dívidas e financiamento · Entenda as contas

## Corpo sugerido

```markdown
::: {.obs-tres-pontos}
- Primeiro ponto, em uma frase.
- Segundo ponto.
- Terceiro ponto.
:::

Texto com os números, gráficos quando ajudarem (link para o Compare já
filtrado funciona bem: `compare.qmd?clubes=atletico-mg,cruzeiro&indicador=receita_rec`).

## O que esses números não mostram

Limites da leitura: o que o balanço não detalha, o que depende de nota
explicativa, onde a comparação entre clubes pede cuidado.

{{< include ../../_rodape.qmd >}}
```

## Correções

Se um número citado mudar depois da publicação, registre a correção em
`erratas.csv` no repositório de dados e acrescente ao fim do texto, antes do
rodapé:

```markdown
::: {.obs-correcao}
**Correção (DD/MM/AAAA).** O que mudou, de quanto para quanto, e por quê.
:::
```
