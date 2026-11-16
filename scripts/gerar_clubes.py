"""Gera as páginas de clubes (PT e EN) e o índice de análises, antes do render.

Lê ``dados/`` (recorte público gravado pelo exportador do repositório de
dados) e escreve:

* ``clubes/<slug>/index.qmd`` e ``en/clubs/<slug>/index.qmd`` — uma página
  por clube, com o retrato financeiro do último exercício, a evolução, as
  análises relacionadas, as fontes e o que ainda falta coletar.
* ``clubes/index.qmd`` e ``en/clubs/index.qmd`` — a grade de clubes.
* ``dados/analises.json`` — título, data, editoria, clubes e temas de cada
  análise publicada, lido pelo Compare e pelas páginas de clubes.

Um texto editorial opcional por clube, escrito à mão, entra de
``clubes/_textos/<slug>.md`` (PT) e ``en/clubs/_texts/<slug>.md`` (EN).

Roda sozinho no ``construir.sh`` e como ``pre-render`` do Quarto; não recebe
argumentos. Todos os números da página vêm de ``dados/``; nenhum é digitado.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"

# Campos do retrato financeiro, na ordem em que aparecem.
RETRATO = ["receita_rec", "lucro_liquido", "patrimonio_liq",
           "divida_identificada_total", "caixa_final", "pessoal"]

TXT = {
    "pt": {
        "pasta": "clubes", "posts": "analises/posts", "textos": "clubes/_textos",
        "base_rel": "../../dados/", "compare": "../../compare.html", "como": "../../como-analisamos.html",
        "indice_titulo": "Clubes", "indice_desc": "Um retrato financeiro por clube, com os números publicados nos balanços.",
        "indice_intro": "Cada página reúne o que o clube publicou: receitas, resultado, patrimônio, dívidas e caixa, ano a ano, com as ressalvas que valem para cada número.",
        "saf": "SAF", "associacao": "associação", "ltda": "limitada", "sa_comum": "S.A.",
        "entidade_titulo": "Quem publica o balanço",
        "entidade_saf_desde": lambda a: f"SAF desde {a}",
        "entidade_assoc": "Associação (clube sem dono)",
        "divisoes": "Divisões disputadas",
        "retrato": lambda ano: f"Retrato de {ano}",
        "retrato_nota": "Último exercício publicado. Valores em R$ milhões nominais.",
        "evolucao": "Evolução",
        "evolucao_nota": "Ponto cheio: a entidade que publicou era SAF. Ponto vazado: associação ou outra forma jurídica. Passe o mouse para ver o valor.",
        "tabela": "Ano a ano",
        "analises": "Análises sobre o clube", "sem_analises": "Ainda não há análise publicada sobre este clube.",
        "fontes": "Fontes e ressalvas",
        "col": {"ano": "Ano", "entidade": "Entidade", "divisao": "Divisão", "auditor": "Auditor",
                "ressalva": "Ressalva", "fonte": "Fonte", "parcial": "Ano parcial", "decisao": "Ajuste"},
        "sim": "sim", "nao": "não", "nd": "não identificado",
        "fontes_nota": "Fonte: de onde os valores do ano foram lidos — o balanço do próprio ano, a coluna comparativa do balanço seguinte ou uma publicação resumida. Ajuste: algum valor passou por decisão metodológica registrada.",
        "falta": "O que ainda falta",
        "falta_txt": lambda anos: f"O clube disputou Série A, B, C ou D em {', '.join(map(str, anos))}, mas não localizamos demonstrações financeiras desses exercícios. Se você souber onde estão, avise.",
        "falta_nada": "Todos os exercícios em que o clube disputou Série A, B, C ou D estão na base.",
        "paralela": "A outra entidade do clube",
        "paralela_intro": {
            "associacao_remanescente": "O futebol passou para a SAF, mas a associação continua existindo e publicando o próprio balanço — em geral é nela que fica a dívida antiga. Os números acima são os da SAF; estes são os da associação.",
            "associacao_pre_conversao": "No período anterior à conversão, a associação publicava as próprias demonstrações. Os números acima são os da entidade que representa o clube no ano; estes são os da associação.",
            "associacao_que_disputou_saf_principal": "Neste ano a associação é que disputou o campeonato, enquanto a SAF assina as demonstrações usadas acima. Estes são os números da associação.",
        },
        "paralela_col": {"ano": "Ano", "entidade": "Entidade", "receita": "Receita comparável",
                         "divida": "Dívida identificada", "pl": "Patrimônio líquido"},
        "paralela_nota": "Não some estes valores aos de cima: são entidades diferentes, e parte das operações aparece nas duas.",
        "comparar": lambda n: f"Comparar {n} com outros clubes",
        "como_link": "Como analisamos",
        "versao": lambda v, d: f"Base {v}, atualizada em {d}.",
        "avisar": "https://github.com/contasemcampo/contasemcampo.github.io/issues",
        "fonte_comparativa": "coluna comparativa do balanço seguinte",
        "fonte_propria": "balanço do próprio ano",
        "fonte_resumida": "publicação resumida",
        "fonte_curta": {"comparativa": "comparativa", "propria": "do ano", "resumida": "resumida"},
        "moeda": "R$", "mi": "mi",
    },
    "en": {
        "pasta": "en/clubs", "posts": "en/analyses/posts", "textos": "en/clubs/_texts",
        "base_rel": "../../../dados/", "compare": "../../compare.html", "como": "../../how-we-analyse.html",
        "indice_titulo": "Clubs", "indice_desc": "A financial portrait of each club, from the figures published in its statements.",
        "indice_intro": "Each page gathers what the club published: revenue, results, equity, debt and cash, year by year, with the caveats that apply to each figure.",
        "saf": "SAF", "associacao": "association", "ltda": "limited company", "sa_comum": "corporation",
        "entidade_titulo": "Who publishes the statements",
        "entidade_saf_desde": lambda a: f"SAF since {a}",
        "entidade_assoc": "Member-owned association",
        "divisoes": "Divisions played",
        "retrato": lambda ano: f"Snapshot of {ano}",
        "retrato_nota": "Latest published financial year. Values in nominal BRL millions.",
        "evolucao": "Over time",
        "evolucao_nota": "Filled dot: the reporting entity was an SAF. Hollow dot: association or other legal form. Hover for the value.",
        "tabela": "Year by year",
        "analises": "Analyses about the club", "sem_analises": "No analysis published about this club yet.",
        "fontes": "Sources and caveats",
        "col": {"ano": "Year", "entidade": "Entity", "divisao": "Division", "auditor": "Auditor",
                "ressalva": "Qualified", "fonte": "Source", "parcial": "Partial year", "decisao": "Adjusted"},
        "sim": "yes", "nao": "no", "nd": "not identified",
        "fontes_nota": "Source: where the year's figures were read from — the year's own statement, the comparative column of the next statement, or a summary publication. Adjusted: at least one value went through a recorded methodological decision.",
        "falta": "What is still missing",
        "falta_txt": lambda anos: f"The club played Série A, B, C or D in {', '.join(map(str, anos))}, but we have not located financial statements for those years. If you know where they are, let us know.",
        "falta_nada": "Every year in which the club played Série A, B, C or D is in the dataset.",
        "paralela": "The club's other entity",
        "paralela_intro": {
            "associacao_remanescente": "Football moved to the SAF, but the association still exists and publishes its own statements — the historic debt usually stays there. The figures above are the SAF's; these are the association's.",
            "associacao_pre_conversao": "Before the conversion, the association published its own statements. The figures above are those of the entity representing the club that year; these are the association's.",
            "associacao_que_disputou_saf_principal": "This year the association played the championship while the SAF signs the statements used above. These are the association's figures.",
        },
        "paralela_col": {"ano": "Year", "entidade": "Entity", "receita": "Comparable revenue",
                         "divida": "Identified debt", "pl": "Equity"},
        "paralela_nota": "Do not add these to the figures above: they are different entities, and some operations appear in both.",
        "comparar": lambda n: f"Compare {n} with other clubs",
        "como_link": "How we analyse",
        "versao": lambda v, d: f"Dataset {v}, updated {d}.",
        "avisar": "https://github.com/contasemcampo/contasemcampo.github.io/issues",
        "fonte_comparativa": "comparative column of the next statement",
        "fonte_propria": "the year's own statement",
        "fonte_resumida": "summary publication",
        "fonte_curta": {"comparativa": "comparative", "propria": "own year", "resumida": "summary"},
        "moeda": "BRL", "mi": "m",
    },
}


def ler_csv(nome: str) -> list[dict]:
    """Lê um CSV de ``dados/`` como lista de dicionários de texto."""
    with (DADOS / nome).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def numero(v: str) -> float | None:
    """Converte o texto de uma célula em número, ou None se vazio."""
    if v is None or v.strip() == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fmt(v: float | None, formato: str, lang: str) -> str:
    """Formata um valor como o painel faz (R$ mi, %, x), no idioma pedido."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    t = TXT[lang]
    def n(x: float, casas: int) -> str:
        s = f"{x:,.{casas}f}"
        if lang == "pt":
            s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
        return s.rstrip("0").rstrip(",." if casas else "") if casas else s
    if formato == "fracao":
        return n(v * 100, 1) + "%"
    if formato == "pct":
        return n(v, 1) + "%"
    if formato in ("x", "num"):
        return n(v, 2)
    if formato == "pessoas":
        return n(v, 0)
    return f"{t['moeda']} {n(v, 1)} {t['mi']}"


def front_matter(arquivo: Path) -> dict:
    """Lê o front matter YAML simples de um .qmd (campos e listas em linha)."""
    texto = arquivo.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", texto, re.S)
    meta: dict = {}
    if not m:
        return meta
    for linha in m.group(1).splitlines():
        mm = re.match(r"^(\w[\w-]*):\s*(.*)$", linha)
        if not mm:
            continue
        chave, valor = mm.group(1), mm.group(2).strip()
        if valor.startswith("[") and valor.endswith("]"):
            meta[chave] = [x.strip().strip('"').strip("'") for x in valor[1:-1].split(",") if x.strip()]
        else:
            meta[chave] = valor.strip('"').strip("'")
    return meta


def indice_analises() -> list[dict]:
    """Varre os posts das duas línguas e devolve os metadados de cada um."""
    itens = []
    for lang in ("pt", "en"):
        pasta = RAIZ / TXT[lang]["posts"]
        for qmd in sorted(pasta.glob("*/index.qmd")):
            meta = front_matter(qmd)
            if not meta.get("title") or meta.get("draft") == "true":
                continue
            itens.append({
                "lang": lang,
                # Relativo à raiz do idioma (en/ para o inglês)
                "href": f"{TXT[lang]['posts'].removeprefix('en/')}/{qmd.parent.name}/index.html",
                "title": meta["title"], "description": meta.get("description", ""),
                "date": meta.get("date", ""), "categories": meta.get("categories", []),
                "clubes": meta.get("clubes", []), "temas": meta.get("temas", []),
                "base": meta.get("base", ""),
            })
    return itens


def cor_texto(hexa: str) -> str:
    """Escolhe branco ou quase-preto para o texto sobre a cor de fundo do medalhão."""
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#0d0d0d" if lum > 0.55 else "#ffffff"


def periodo(anos: list[int], lang: str) -> str:
    """Escreve o intervalo e a contagem de exercícios, com singular e plural."""
    n = len(anos)
    faixa = f"{anos[0]}" if anos[0] == anos[-1] else f"{anos[0]}–{anos[-1]}"
    if lang == "pt":
        return f"{faixa} · {n} exercício{'s' if n != 1 else ''}"
    return f"{faixa} · {n} year{'s' if n != 1 else ''}"


def regime_legivel(regime: str | None, lang: str) -> str:
    """Traduz o código do regime da entidade para texto."""
    if not regime:
        return TXT[lang]["nd"]
    return TXT[lang].get(regime, regime)


def pagina_clube(c: dict, linhas: list[dict], inds: dict, analises: list[dict],
                 versao: dict, lang: str) -> str:
    """Monta o .qmd de um clube num idioma.

    Args:
        c: registro do clube em ``clubes.json``.
        linhas: linhas do painel desse clube, em ordem de ano.
        inds: dicionário campo -> metadados do indicador.
        analises: índice de análises (todas as línguas).
        versao: conteúdo de ``versao.json``.
        lang: "pt" ou "en".
    """
    t = TXT[lang]
    ultimo = linhas[-1]
    ano_ult = ultimo["ano"]
    rot = lambda campo: (inds[campo]["rotulo_pt"] if lang == "pt" else inds[campo]["rotulo_en"]) if campo in inds else campo
    fmto = lambda campo: inds[campo]["formato"] if campo in inds else "rs"

    # Entidade: SAF a partir de que ano, ou associação
    anos_saf = [int(l["ano"]) for l in linhas if l.get("regime_entidade") == "SAF"]
    regimes = sorted({l.get("regime_entidade") for l in linhas if l.get("regime_entidade")})
    if anos_saf:
        entidade = t["entidade_saf_desde"](min(anos_saf))
        if len(regimes) > 1:
            outros = [regime_legivel(r, lang) for r in regimes if r != "SAF"]
            entidade += f" · {', '.join(outros)} " + ("antes" if lang == "pt" else "before")
    elif regimes == ["associacao"]:
        entidade = t["entidade_assoc"]
    else:
        entidade = ", ".join(regime_legivel(r, lang) for r in regimes) or t["nd"]
    divisoes = ", ".join(f"{l['ano']} {l['divisao_disputada']}" for l in linhas if l.get("divisao_disputada")) or "—"

    # Retrato: os campos com valor no último exercício
    cartoes = []
    for campo in RETRATO:
        v = numero(ultimo.get(campo, ""))
        if v is None:
            continue
        classe = " obs-negativo" if v < 0 and fmto(campo) in ("rs",) else ""
        cartoes.append(f'<div class="obs-cartao"><span class="obs-cartao-rotulo">{rot(campo)}</span>'
                       f'<span class="obs-num{classe}">{fmt(v, fmto(campo), lang)}</span></div>')
    notas = []
    if str(ultimo.get("exercicio_parcial", "")).startswith("S"):
        notas.append(t["col"]["parcial"])
    if re.search("comparativ", str(ultimo.get("fonte_exercicio", "")), re.I):
        notas.append(t["fonte_comparativa"])
    if ultimo.get("tem_ressalva") == "S":
        notas.append(t["col"]["ressalva"])
    nota_retrato = t["retrato_nota"] + (f" ({'; '.join(notas)}.)" if notas else "")

    # Tabela ano a ano com os campos do retrato
    campos_tab = [cp for cp in RETRATO if any(numero(l.get(cp, "")) is not None for l in linhas)]
    cab = "".join(f"<th>{rot(cp)}</th>" for cp in campos_tab)
    corpo = ""
    for l in linhas:
        cels = "".join(f"<td>{fmt(numero(l.get(cp, '')), fmto(cp), lang)}</td>" for cp in campos_tab)
        corpo += f"<tr><th>{l['ano']}</th>{cels}</tr>"
    tabela = f'<table class="obs-tabela"><thead><tr><th>{t["col"]["ano"]}</th>{cab}</tr></thead><tbody>{corpo}</tbody></table>'

    # Fontes e ressalvas, ano a ano
    def fonte(l: dict) -> str:
        f = str(l.get("fonte_exercicio", "") or "")
        if re.search("comparativ", f, re.I):
            return t["fonte_curta"]["comparativa"]
        if re.search("resum", f, re.I):
            return t["fonte_curta"]["resumida"]
        return t["fonte_curta"]["propria"] if f else "—"
    fontes = "".join(
        f"<tr><th>{l['ano']}</th><td>{regime_legivel(l.get('regime_entidade'), lang)}</td>"
        f"<td>{l.get('divisao_disputada') or '—'}</td><td>{l.get('nome_auditor_padronizado') or t['nd']}</td>"
        f"<td>{t['sim'] if l.get('tem_ressalva') == 'S' else t['nao']}</td><td>{fonte(l)}</td>"
        f"<td>{t['sim'] if str(l.get('exercicio_parcial', '')).startswith('S') else t['nao']}</td>"
        f"<td>{t['sim'] if l.get('tem_decisao') == 'S' else t['nao']}</td></tr>" for l in linhas)
    c_ = t["col"]
    tabela_fontes = (f'<table class="obs-tabela obs-fontes"><thead><tr><th>{c_["ano"]}</th><th>{c_["entidade"]}</th>'
                     f'<th>{c_["divisao"]}</th><th>{c_["auditor"]}</th><th>{c_["ressalva"]}</th><th>{c_["fonte"]}</th>'
                     f'<th>{c_["parcial"]}</th><th>{c_["decisao"]}</th></tr></thead><tbody>{fontes}</tbody></table>')

    # Análises relacionadas (mesma língua, clube citado)
    rel = sorted([a for a in analises if a["lang"] == lang and c["slug"] in a["clubes"]],
                 key=lambda a: a["date"], reverse=True)
    pref = "../../" if lang == "pt" else "../../"
    lista_rel = ("<ul class='obs-lista-analises'>" + "".join(
        f"<li><a href='{pref}{a['href']}'>{a['title']}</a> <span class='obs-ui'>{a['date']}</span></li>" for a in rel)
        + "</ul>") if rel else f"<p class='obs-vazio'>{t['sem_analises']}</p>"

    # Entidade paralela: a associação que continua publicando depois da SAF.
    par = c.get("entidade_paralela") or []
    bloco_par = ""
    if par:
        papeis = [r["papel"] for r in par if r.get("papel")]
        intro = t["paralela_intro"].get(papeis[0] if papeis else "", "") if papeis else ""
        cp = t["paralela_col"]
        linhas_par = "".join(
            f"<tr><th>{r['ano']}</th><td>{r.get('nome_entidade') or '—'}</td>"
            f"<td>{fmt(r.get('receita_rec'), 'rs', lang)}</td>"
            f"<td>{fmt(r.get('divida_identificada_total'), 'rs', lang)}</td>"
            f"<td>{fmt(r.get('patrimonio_liq'), 'rs', lang)}</td></tr>" for r in par)
        bloco_par = f'''
## {t["paralela"]}

{intro}

```{{=html}}
<table class="obs-tabela obs-paralela"><thead><tr><th>{cp["ano"]}</th><th>{cp["entidade"]}</th>
<th>{cp["receita"]}</th><th>{cp["divida"]}</th><th>{cp["pl"]}</th></tr></thead>
<tbody>{linhas_par}</tbody></table>
<p class="obs-indicador-nota">{t["paralela_nota"]}</p>
```
'''

    pend = c.get("anos_sem_demonstracao") or []
    falta = t["falta_txt"](pend) if pend else t["falta_nada"]

    texto_extra = RAIZ / t["textos"] / f"{c['slug']}.md"
    editorial = texto_extra.read_text(encoding="utf-8").strip() if texto_extra.exists() else ""

    compare_url = f"{t['compare']}?clubes={c['slug']}&indicador=receita_rec"
    titulo = c["nome"]
    desc = (f"Receitas, resultado, patrimônio, dívidas e caixa do {titulo}, ano a ano, a partir dos balanços publicados."
            if lang == "pt" else
            f"{titulo}'s revenue, results, equity, debt and cash, year by year, from its published statements.")

    return f'''---
title: "{titulo}"
description: "{desc}"
pagetitle: "{titulo} · Contas em Campo"
---

```{{=html}}
<header class="obs-clube-cab">
  <div class="obs-medalhao" style="--c1:{c['cor1']};--c2:{c['cor2']};--ct:{cor_texto(c['cor1'])}" aria-hidden="true">{c['sigla']}</div>
  <div>
    <p class="obs-ui obs-clube-meta">{c['uf']} · {entidade}</p>
    <p class="obs-ui obs-clube-meta"><strong>{t['divisoes']}:</strong> {divisoes}</p>
  </div>
</header>
```

{editorial}

## {t['retrato'](ano_ult)}

```{{=html}}
<div class="obs-cartoes">{''.join(cartoes)}</div>
<p class="obs-indicador-nota">{nota_retrato}</p>
```

## {t['evolucao']}

```{{ojs}}
//| echo: false
lang = "{lang}"
base = "{t['base_rel']}"
clubeAtual = "{c['clube']}"
```

{{{{< include {'../../_clube_graficos.qmd' if lang == 'pt' else '../../../_clube_graficos.qmd'} >}}}}

```{{=html}}
<p class="obs-legenda-saf">{t['evolucao_nota']}</p>
<p class="obs-acoes"><a class="obs-botao" href="{compare_url}">{t['comparar'](titulo)}</a></p>
```

### {t['tabela']}

```{{=html}}
{tabela}
```

{bloco_par}
## {t['analises']}

```{{=html}}
{lista_rel}
```

## {t['fontes']}

```{{=html}}
{tabela_fontes}
<p class="obs-indicador-nota">{t['fontes_nota']} {t['versao'](versao['versao'], versao['data'])} <a href="{t['como']}">{t['como_link']}</a>.</p>
```

## {t['falta']}

{falta}
'''


def pagina_indice(clubes: list[dict], lang: str) -> str:
    """Monta a grade de clubes de um idioma."""
    t = TXT[lang]
    cartoes = "".join(
        f'<a class="obs-clube-card" href="{c["slug"]}/index.html">'
        f'<span class="obs-medalhao obs-medalhao-p" style="--c1:{c["cor1"]};--c2:{c["cor2"]};--ct:{cor_texto(c["cor1"])}" aria-hidden="true">{c["sigla"]}</span>'
        f'<span class="obs-clube-card-nome">{c["nome"]}</span>'
        f'<span class="obs-ui obs-clube-card-anos">{periodo(c["anos"], lang)}</span></a>'
        for c in clubes)
    return f'''---
title: "{t['indice_titulo']}"
description: "{t['indice_desc']}"
page-layout: full
---

[{t['indice_intro']}]{{.obs-coluna-intro}}

```{{=html}}
<div class="obs-clubes-grade">{cartoes}</div>
```
'''


def main() -> None:
    """Gera índice de análises, páginas de clubes e grades, nas duas línguas."""
    if not (DADOS / "painel.csv").exists():
        raise SystemExit("dados/painel.csv não existe; rode construir.sh ou copie data/site do repositório de dados.")
    painel = ler_csv("painel.csv")
    clubes = json.loads((DADOS / "clubes.json").read_text(encoding="utf-8"))
    inds = {d["campo"]: d for d in ler_csv("indicadores.csv")}
    versao = json.loads((DADOS / "versao.json").read_text(encoding="utf-8"))

    analises = indice_analises()
    (DADOS / "analises.json").write_text(json.dumps(analises, ensure_ascii=False, indent=1), encoding="utf-8")

    por_clube: dict[str, list[dict]] = {}
    for l in painel:
        por_clube.setdefault(l["clube"], []).append(l)
    for lista in por_clube.values():
        lista.sort(key=lambda l: int(l["ano"]))

    for lang in ("pt", "en"):
        pasta = RAIZ / TXT[lang]["pasta"]
        for antiga in pasta.glob("*/"):
            if antiga.name not in ("_textos", "_texts"):
                shutil.rmtree(antiga)
        gerados = 0
        for c in clubes:
            linhas = por_clube.get(c["clube"])
            if not linhas:
                continue
            destino = pasta / c["slug"]
            destino.mkdir(parents=True, exist_ok=True)
            (destino / "index.qmd").write_text(pagina_clube(c, linhas, inds, analises, versao, lang), encoding="utf-8")
            gerados += 1
        (pasta / "index.qmd").write_text(pagina_indice([c for c in clubes if c["clube"] in por_clube], lang), encoding="utf-8")
        print(f"{lang}: {gerados} páginas de clubes em {pasta.relative_to(RAIZ)}/")
    print(f"analises.json: {len(analises)} textos indexados")


if __name__ == "__main__":
    main()
