"""Genera el informe del Taller 02 leyendo los CSV crudos del repositorio."""
import csv, json, sys, re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, Preformatted)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

B = Path(sys.argv[1]); SALIDA = Path(sys.argv[2]); DIAG = Path(sys.argv[3])
csv.field_size_limit(10**9)
F = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
             ("DV-BI", "DejaVuSans-BoldOblique.ttf"), ("DVM", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, F + f))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B"); addMapping("DV", 0, 1, "DV-I"); addMapping("DV", 1, 1, "DV-BI")

AZUL = colors.HexColor("#1e3a8a"); GRIS = colors.HexColor("#475569"); FONDO = colors.HexColor("#f1f5f9")
st = {
    "t": ParagraphStyle("t", fontName="DV-B", fontSize=18, leading=23, textColor=AZUL, alignment=TA_CENTER, spaceAfter=6),
    "st": ParagraphStyle("st", fontName="DV", fontSize=10.5, leading=14, textColor=GRIS, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=13.5, leading=17, textColor=AZUL, spaceBefore=12, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=11, leading=14, textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="DV", fontSize=9.3, leading=13, alignment=TA_JUSTIFY, spaceAfter=5),
    "li": ParagraphStyle("li", fontName="DV", fontSize=9.3, leading=13, leftIndent=12, bulletIndent=2, spaceAfter=2, alignment=TA_JUSTIFY),
    "c": ParagraphStyle("c", fontName="DV", fontSize=7.6, leading=9.6),
    "cb": ParagraphStyle("cb", fontName="DV-B", fontSize=7.6, leading=9.6, textColor=colors.white),
    "cap": ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10, textColor=GRIS, spaceAfter=8),
    "pend": ParagraphStyle("pend", fontName="DV-B", fontSize=9.3, leading=13, textColor=colors.HexColor("#9a3412"),
                           backColor=colors.HexColor("#ffedd5"), borderPadding=6, spaceBefore=4, spaceAfter=8),
}
MONO = ParagraphStyle("m", fontName="DVM", fontSize=7, leading=8.6, backColor=FONDO, borderPadding=5, spaceAfter=8)

def P(t, s="p"): return Paragraph(t, st[s])
def L(items): return [Paragraph(i, st["li"], bulletText="•") for i in items]
def pre(t): return Preformatted(t, MONO)
def f3(x): return f"{float(x):.3f}".replace(".", ",")

def tabla(filas, anchos, cab=True, tam=None):
    data = [[Paragraph(str(c) if ("<br/>" in str(c) or str(c).startswith("<")) else escape(str(c)),
                       st["cb"] if (cab and i == 0) else st["c"]) for c in fila] for i, fila in enumerate(filas)]
    t = Table(data, colWidths=[a * cm for a in anchos], repeatRows=1 if cab else 0)
    estilo = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
              ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if cab: estilo += [("BACKGROUND", (0, 0), (-1, 0), AZUL)]
    for i in range(1, len(filas)):
        if i % 2 == 0: estilo.append(("BACKGROUND", (0, i), (-1, i), FONDO))
    t.setStyle(TableStyle(estilo)); return t

def leer(r): return list(csv.DictReader(open(B / r, encoding="utf-8-sig")))
def metr(r):
    d = leer(r); resp = [x for x in d if x["respondible"] == "True"]; neg = [x for x in d if x["respondible"] == "False"]
    m = lambda xs: sum(xs) / len(xs)
    return {"k": d[0]["k"], "hit": m([x["hit"] == "True" for x in resp]), "mrr": m([float(x["reciprocal_rank"]) for x in resp]),
            "ac": m([x["abstuvo"] == "True" for x in neg]), "ai": m([x["abstuvo"] == "True" for x in resp]),
            "gen": d[0]["generador"], "rows": d}

golden = json.load(open(B / "golden_set.json", encoding="utf-8"))
b3, b5 = metr("resultados/parte2_k3.csv"), metr("resultados/parte2_k5.csv")
h3, h5 = metr("resultados/parte3/parte3_hibrido_k3.csv"), metr("resultados/parte3/parte3_hibrido_k5.csv")
V2 = (B / "resultados/parte3/parte3_hibrido_v2_k3.csv").exists()
if V2:
    v3, v5 = metr("resultados/parte3/parte3_hibrido_v2_k3.csv"), metr("resultados/parte3/parte3_hibrido_v2_k5.csv")
peores = json.load(open(B / "resultados/parte2_peores_casos.json", encoding="utf-8"))
s0a = leer("resultados/parte0/salida_0a.csv") if False else open(B / "resultados/parte0/salida_0a.csv", encoding="utf-8-sig").read()
s0b = {r["elemento"]: r["valor"] for r in leer("resultados/parte0/salida_0b.csv")}
s0c = leer("resultados/parte0/salida_0c.csv")
degr = leer("resultados/parte1/numeral1_degradacion.csv")
top5 = leer("resultados/parte1/numeral4_retrieval_top5.csv")
gen1 = leer("resultados/parte1/numeral5_generacion.csv")
det3 = leer("resultados/parte3/parte3_detalle_por_pregunta.csv")
detv2 = {r["id"]: r for r in leer("resultados/parte3/parte3_v2_detalle_por_pregunta.csv")} if V2 else {}

S = []
# ── Portada ──
S += [Spacer(1, 2.2 * cm), P("Taller 02 — RAG sobre un corpus real: baseline medible, abstención y una extensión", "t"),
      P("MMIA 6013 · IA Generativa y Agentes · Universidad San Francisco de Quito", "st"), Spacer(1, 10),
      P("Jessica Ballesteros · Miguel Álvarez · Darlyn Ludeña", "st"), Spacer(1, 4),
      P("Repositorio: github.com/akroasis0301/taller-02-rag-alvarez-ballesteros-ludena", "st"), Spacer(1, 24)]
S += [P("Resumen", "h2"), P(
    f"Construimos un RAG baseline sobre seis papers del curso en inglés (262 páginas, 530 fragmentos de 512 tokens), con "
    f"embeddings <b>bge-m3</b> en la H200, índice Qdrant en contenedor y generación <b>qwen3:32b</b> en el Ollama de la H200. "
    f"Sobre un golden set de 10 preguntas (8 respondibles, 2 negativas), el baseline obtiene Hit Rate {f3(b5['hit'])} y MRR "
    f"{f3(b5['mrr'])} con k=3 y k=5, abstención correcta {f3(b5['ac'])} y abstención indebida {f3(b3['ai'])} (k=3) / {f3(b5['ai'])} (k=5). "
    f"Como extensión medimos una búsqueda híbrida BM25 + densa con RRF (Opción B): la primera versión solo mejora el MRR "
    f"a {f3(h5['mrr'])} y falla por un mecanismo que diagnosticamos (palabras vacías del español con IDF alto en un corpus en inglés)."
    + (f" La versión corregida obtiene Hit Rate {f3(v5['hit'])} y MRR {f3(v5['mrr'])} (k=5)." if V2 else ""))]
S += [P("Configuración declarada", "h2"), tabla([
    ["Componente", "Fila (id) de la tabla semestral", "Modelo", "verified_at"],
    ["Embeddings (Partes 1–3)", "embed_local_multilingue", "BAAI/bge-m3 · 1024 dim · 8192 tokens", "2026-08-27"],
    ["Embeddings (solo Parte 0)", "embed_notebook_s2", "paraphrase-multilingual-MiniLM-L12-v2 · 128 tokens", "2026-08-27"],
    ["Generación y abstención", "open_weight_pequeno", "qwen3:32b (Ollama, H200)", "sin fecha en el repo (*)"],
    ["Índice", "—", "Qdrant en contenedor Docker, coseno, HNSW (m=16, ef_construct=100)", "—"],
], [3.6, 4.2, 6.2, 3.0]),
    P("(*) El archivo <font face='DVM'>fuentes/modelos/modelos-2026-1.json</font> del repositorio es el archivo de ejemplo del curso; "
      "la fila <font face='DVM'>open_weight_pequeno</font> la agregó el grupo con <font face='DVM'>verified_at: null</font>. "
      "Las filas de embeddings se citan del anexo del enunciado (generado desde la tabla oficial).", "cap"),
    P("<b>Presupuesto.</b> Todo corrió sin clave, en la H200: 0 USD. Llamadas al generador: 3 (Parte 1.5) + 20 (Parte 2, 10 preguntas × 2 valores de k) "
      f"+ 20 (Parte 3, v1){' + 20 (Parte 3, v2)' if V2 else ''}. Entorno reproducible con <b>uv</b> (Python 3.12, "
      "<font face='DVM'>uv.lock</font> y <font face='DVM'>requirements.txt</font> con versiones fijadas). Ninguna clave aparece en el repositorio: los notebooks vacían "
      "<font face='DVM'>OPENAI_API_KEY</font> y <font face='DVM'>.env</font> está excluido por <font face='DVM'>.gitignore</font>.")]
S.append(PageBreak())

# ── Parte 0 ──
S += [P("Parte 0 — Tres fallas que no fallan", "h1"), P("0.a — El PDF que se indexa vacío", "h2"),
      P("Ingesta de <font face='DVM'>ejemplos/</font> con <font face='DVM'>python rag_pipeline.py</font> (MiniLM local, Qdrant :memory:). Salida cruda de la ingesta:")]
lin = [l for l in s0a.splitlines() if l.startswith(("ingesta:", "AVISO", "indexados", "embeddings:", '"embeddings:'))]
import textwrap
S.append(pre("\n".join("\n    ".join(textwrap.wrap(l.strip('"'), 104)) for l in lin)))
S += L(["<b>Qué comprueba <font face='DVM'>load_corpus</font>:</b> cuenta, para cada documento, los caracteres útiles (letras y dígitos, sin las marcas "
        "<font face='DVM'>[page=N]</font>) y, si no llegan a <font face='DVM'>MIN_CARACTERES_UTILES</font> (200), lo anuncia y no lo indexa; "
        "<font face='DVM'>instructivo_escaneado.pdf</font> tiene 0 caracteres útiles en 2 páginas.",
        "<b>Qué pasaría sin esa comprobación:</b> pypdf devolvería texto vacío en cada página y la ingesta produciría un único fragmento hecho de "
        "<font face='DVM'>[page=1] [page=2]</font>, que se indexaría sin ninguna excepción: el índice diría que el documento está, pero ninguna de sus palabras sería recuperable."])
S += [P("0.b — El fragmento que se corta a 128", "h2"),
      pre("AVISO ingesta: chunk_tokens=900 supera el tope del modelo (128 tokens): lo que pase de 126 tokens\n"
          "no llega al índice —el MiniLM lo trunca en silencio; la H200 rechaza la petición—."),
      tabla([["Texto de prueba", "Tokens del texto", "Tope del modelo (max_seq_length)", "Coseno(texto entero, texto recortado)"],
             ["900 palabras", s0b["tokens_del_texto"], s0b["max_seq_length"], f"{float(s0b['coseno']):.4f}".replace('.', ',')]], [3.4, 3.2, 4.8, 5.6]),
      Spacer(1, 6),
      P(f"El vector del texto entero y el del texto recortado a 128 tokens son el mismo: los {int(s0b['tokens_del_texto']) - 128} tokens restantes nunca llegaron al índice. "
        "<b>chunk_tokens para la Parte 1: 512.</b> Que bge-m3 admita 8192 tokens dice qué cabe, no qué sirve: un fragmento de 8192 tokens sería casi todo el paper de "
        "Vaswani y su vector promediaría muchos temas; 512 tokens (2–3 párrafos) llevan una afirmación con su contexto y siguen representando una idea.")]
S += [P("0.c — El índice que no se queja", "h2")]
filas = [["Pregunta", "Rank", "Puntaje", "Documento"]]
for r in s0c: filas.append([r["pregunta"] if r["rank"] == "1" else "", r["rank"], f3(r["score"]), r["documento"]])
S += [tabla(filas, [9.4, 1.2, 1.8, 4.6]), Spacer(1, 6),
      P("Los seis vecinos tienen aspecto sano: el índice siempre devuelve k resultados ordenados. Los puntajes no sirven de umbral: la pregunta cuya respuesta sí existe "
        "(en el PDF no indexado) puntúa más alto (0,23) que la de mascotas (0,06). <b>Ningún Hit Rate puede detectarlo</b> porque el Hit Rate solo se calcula cuando existe un "
        "documento fuente contra el cual comparar; aquí no existe (mascotas) o no está en el índice (seguro de accidentes). El fallo solo aparece en la respuesta: por eso el "
        "golden set lleva negativas y se mide la abstención.")]
S.append(PageBreak())

# ── Parte 1 ──
S += [P("Parte 1 — Baseline RAG funcional", "h1"), P("Arquitectura", "h2"), Image(str(DIAG), width=17 * cm, height=17 * cm * 4.6 / 10.3),
      P("Figura 1. Arquitectura del sistema. En azul, la indexación; en verde, el flujo por pregunta; en rosado, la extensión de la Parte 3.", "cap")]
S += [P("1.1 — Corpus e ingesta", "h2"), P(
    "Opción B del enunciado: papers del curso, en inglés. Seis PDF con capa de texto (Bai 2022, 34 p.; Brown 2020, 75 p.; Ouyang 2022, 68 p.; Rafailov 2023, 27 p.; "
    "Vaswani 2017, 15 p.; Wei 2022, 43 p.; 262 páginas). <b>Ningún documento fue rechazado.</b> La advertencia del tokenizador «30809 &gt; 8192» no es un truncamiento: "
    "aparece al contar los tokens del documento entero para cortarlo. Lo que la ingesta degrada, medido sobre los 530 fragmentos:")]
S.append(tabla([["Degradación", "Ocurrencias"]] + [[r["degradación"], r["ocurrencias"]] for r in degr], [12.5, 3]))
S += [Spacer(1, 4)] + L(["<b>Tablas</b> aplanadas en secuencias de números sin encabezados (p. ej., resultados aritméticos de GPT-3); <b>figuras</b> sin extraer, solo su pie; "
                         "<b>ecuaciones</b> rotas (DPO); <b>palabras cortadas</b> por guion de fin de línea; <b>cabeceras y pies</b> de arXiv mezclados con el cuerpo.",
                         "<b>Primer fragmento de cada paper:</b> título, autores, afiliaciones y correos ocupan entre 244 y 844 caracteres antes del «Abstract» y comparten vector con el resumen."])
S += [P("1.2 — Fragmentación", "h2"), P(
    "<b>chunk_tokens = 512, overlap_tokens = 102</b> (un quinto), en tokens del tokenizador de bge-m3. Las preguntas piden afirmaciones concretas de un paper; un párrafo ocupa "
    "del orden de 100–250 tokens y el resumen 250–300, así que 512 tokens llevan la afirmación con su contexto inmediato. Más grande (hasta 8192) promediaría secciones enteras "
    "en un vector y llenaría el prompt de texto irrelevante con k=5; más chico partiría las definiciones y obligaría a recuperar muchos más vecinos para las preguntas "
    "multi-fragmento. El solapamiento garantiza que una afirmación en el borde aparezca completa en algún fragmento.")]
S += [P("1.3 — Embeddings e indexación", "h2"), P(
    "Fila <b>embed_local_multilingue</b> (BAAI/bge-m3, 1024 dimensiones, 8192 tokens, multilingüe, 0 USD), <b>verified_at 2026-08-27</b>, servida por el Ollama de la H200 "
    "con <font face='DVM'>truncate: false</font>. Indexado en Qdrant en contenedor: 530 vectores, igual al número de fragmentos (verificado con <font face='DVM'>count</font>).")]
S += [P("1.4 — Recuperación: top-5 de tres preguntas de prueba", "h2")]
filas = [["Pregunta", "Rank", "Puntaje", "Fragmento"]]
for r in top5: filas.append([r["pregunta"][:55] + "…" if r["rank"] == "1" else "", r["rank"], f3(r["score"]), r["chunk_id"]])
S += [tabla(filas, [7.2, 1.1, 1.6, 7.1])]
S += [P("1.5 — Generación", "h2"), P(
    "Ruta sin clave: fila <b>open_weight_pequeno</b> (qwen3:32b) en el Ollama de la H200, el mismo generador en las Partes 1, 2 y 3. El prompt delimita el contexto, obliga a usar "
    "solo el contexto y autoriza la abstención con la frase fija <i>«El corpus no contiene información suficiente.»</i>, la misma del golden set y del detector. "
    f"Las tres preguntas de prueba se respondieron sin abstención (generador: {gen1[0]['generador']}); el texto completo está en "
    "<font face='DVM'>resultados/parte1/numeral5_generacion.json</font>.")]
S.append(PageBreak())

# ── Parte 2 ──
S += [P("Parte 2 — Evaluación con golden set", "h1"), P("2.a — Golden set", "h2"), P(
    "Diez preguntas en español, anotadas por documento fuente y frase literal (no por chunk_id). Tipos: 5 simples, 2 multi-fragmento, 2 negativas y 1 adversarial. "
    "<b>Decisión sobre la adversarial:</b> es respondible (tiene documento fuente); el sistema debe responder ignorando la instrucción inyectada.")]
filas = [["id", "Tipo", "Pregunta", "Fuente"]]
for g in golden: filas.append([g["id"], g["tipo"], g["pregunta"][:92] + ("…" if len(g["pregunta"]) > 92 else ""), ", ".join(d.split("-")[0] for d in g["documentos_fuente"]) or "— (negativa)"])
S += [tabla(filas, [0.8, 2.0, 11.2, 3.0])]
S += [P("2.b — Métricas (derivadas de los CSV crudos)", "h2"),
      tabla([["k", "Hit Rate (8 respondibles)", "MRR", "Abstención correcta (2 negativas)", "Abstención indebida (8 respondibles)"],
             ["3", f3(b3["hit"]), f3(b3["mrr"]), f3(b3["ac"]), f3(b3["ai"])],
             ["5", f3(b5["hit"]), f3(b5["mrr"]), f3(b5["ac"]), f3(b5["ai"])]], [1, 3.8, 2.2, 5, 5]),
      Spacer(1, 6)]
S += L(["<b>Hit Rate y MRR no cambian de k=3 a k=5:</b> las respondibles que aciertan lo hacen en la posición 1 (cuatro) o 3 (una); ninguna tiene su primer acierto en la 4 o la 5. "
        "MRR = (1+1+1+1+1/3+0+0+0)/8 ≈ 0,542: es la media de los recíprocos, no la posición promedio.",
        "<b>La abstención indebida sube a 0,25 con k=5</b> porque la adversarial (id 10) se abstuvo con cinco fragmentos de contexto (con tres respondió). No obedeció la "
        "inyección, pero tampoco respondió: más contexto no siempre ayuda al generador.",
        "Las dos tasas se leen juntas: un sistema que siempre se abstiene tendría la correcta en 1,0 y sería inútil."])
S += [P("2.c — Los tres peores casos", "h2")]
diag = {2: ("Recuperación (orden)", "Los 5 vecinos son de InstructGPT (0,535–0,554); la pregunta no nombra DPO y «alineamiento» cae cerca de InstructGPT. El fragmento correcto está 9.º (k=10 lo recuperaría). El generador se abstuvo, correctamente con ese contexto: la abstención indebida la causa la recuperación."),
        3: ("Ingesta/fragmentación y rigor de la anotación", "Los 5 vecinos son de Wei et al., pero la frase esperada solo está en el fragmento 0000 (cabecera + resumen + inicio de introducción), 21.º. La respuesta generada es correcta: el fallo lo marca el criterio de frase literal."),
        4: ("Recuperación (consulta ES vs. documento EN)", "La pregunta equivalente en inglés de la Parte 1 recupera ese mismo fragmento 0000 en la posición 1 (0,780); en español queda 7.º. La cabecera de 20 autores no explica el fallo sola. La respuesta generada es correcta.")}
filas = [["Caso", "Top-5 (fragmento: puntaje)", "Fragmento esperado en top-50", "Etapa", "Evidencia"]]
for c in peores:
    hits = "<br/>".join(f"{h['chunk_id'].split('-')[0]}-{h['chunk_id'].split('-')[-1]}: {h['score']:.3f}".replace(".", ",") for h in c["hits"])
    et, ev = diag.get(c["id"], ("", ""))
    filas.append([f"{c['id']} ({c['tipo']})", hits, str(c["posicion_fragmento_esperado_top50"]), et, ev])
S += [tabla(filas, [1.5, 3.8, 2.1, 2.9, 6.7])]
ing = {"rafailov": "rafailov-2023-dpo.pdf: 27 página(s), 71700 caracteres útiles → 66 fragmento(s)",
       "wei": "wei-2022-chain-of-thought.pdf: 43 página(s), 105503 caracteres útiles → 90 fragmento(s)",
       "ouyang": "ouyang-2022-instructgpt.pdf: 68 página(s), 143167 caracteres útiles → 118 fragmento(s)"}
filas = [["Caso", "Ingesta del documento fuente", "Respuesta generada (k=5, extracto)"]]
for c in peores:
    doc = c["documentos_fuente"][0].split("-")[0]
    r = (c.get("respuesta_generada") or "").replace("**", "").replace("\n", " ")
    filas.append([str(c["id"]), ing.get(doc, ""), (r[:230] + "…") if len(r) > 230 else r])
S += [Spacer(1, 4), tabla(filas, [1.2, 6.2, 9.6]),
      P("La ingesta de los tres documentos fuente es completa (sin avisos): ninguno de los tres fallos viene de un documento sin texto.", "cap")]
S += [Spacer(1, 6), P("<b>Las fallas silenciosas de la Parte 0 en nuestro corpus.</b> PDF sin texto: no está (ningún documento rechazado). Fragmento truncado: no está "
      "(512 ≪ 8192, y la H200 rechaza en vez de truncar). Índice que no se queja: <b>sí está</b>: el mejor vecino de las negativas puntúa 0,567 y 0,577, dentro del rango de las "
      "respondibles (0,554–0,699), y el caso 2 trae cinco vecinos «sanos» del documento equivocado. Lo detecta la abstención, no el Hit Rate. "
      "<b>Limitación:</b> una multi-fragmento cuenta como acierto con un fragmento de cualquiera de sus fuentes; eso no prueba que la respuesta combine ambas.")]
S.append(PageBreak())

# ── Parte 3 ──
S += [P("Parte 3 — Extensión: búsqueda híbrida BM25 + densa con RRF (Opción B)", "h1"), P("Declaración previa (antes de medir)", "h2")]
S += L(["<b>Modo de falla medido:</b> fragmentos que el vector no pone arriba pero que comparten términos exactos con la pregunta; las preguntas en español citan nombres "
        "propios (Rafailov, Ouyang, Bai) que solo aparecen en el fragmento 0000 de cada paper.",
        "<b>Predicción:</b> corrige los casos 2 y 4; mejora el MRR del caso 5; no corrige el caso 3.",
        "<b>Riesgo:</b> fuera de nombres propios y siglas, la pregunta en español casi no comparte vocabulario con el corpus en inglés; BM25 puede aportar ruido."])
S += [P("Método", "h2"), P("Denso (20 candidatos, bge-m3) + BM25 (20 candidatos, rank_bm25 sobre los mismos 530 fragmentos; tokenización en minúsculas, sin tildes, "
      "alfanumérica; fragmentos con BM25 = 0 excluidos) fusionados con RRF: score(d) = Σ 1/(60 + posición). Mismo prompt, generador e índice que el baseline "
      "(<font face='DVM'>hibrido.py</font>).")]
filas = [["Sistema", "k", "Hit Rate", "MRR", "Abst. correcta", "Abst. indebida"]]
sistemas = [("Baseline (denso)", b3, b5), ("Híbrido v1", h3, h5)] + ([("Híbrido v2 (sin stopwords)", v3, v5)] if V2 else [])
for k in ("3", "5"):
    for n, a, b in sistemas:
        m = a if k == "3" else b
        filas.append([n, k, f3(m["hit"]), f3(m["mrr"]), f3(m["ac"]), f3(m["ai"])])
S += [P("Resultados (derivados de los CSV crudos)", "h2"), tabla(filas, [5.4, 0.9, 2.4, 2.4, 2.9, 3.0]), Spacer(1, 6)]
filas = [["id", "Tipo", "Pos. baseline", "Pos. híbrido v1", "Pos. híbrido v2", "Rank denso (v1)", "Rank BM25 (v1)"]]
for r in det3:
    fx = lambda v: str(int(float(v))) if v else "—"
    v2p = fx(detv2[r["id"]]["pos_híbrido v2 (sin stopwords)"]) if V2 else "pend."
    filas.append([r["id"], r["tipo"], fx(r["pos_baseline"]), fx(r["pos_hibrido"]), v2p, fx(r["rank_denso_del_acierto"]), fx(r["rank_bm25_del_acierto"])])
S += [tabla(filas, [0.9, 2.3, 2.3, 2.5, 2.5, 3.2, 3.3]), P("Tabla. Detalle por pregunta respondible, k=5. «—» en las posiciones: sin acierto en el top-5; en los ranks: el fragmento del acierto no está entre los 20 candidatos de esa lista.", "cap")]
S += [P("Interpretación (v1)", "h2"), P(
    f"El Hit Rate no cambia ({f3(h5['hit'])}); el MRR sube de {f3(b5['mrr'])} a {f3(h5['mrr'])} por una sola pregunta: el caso 5 pasa de la posición 3 a la 2 "
    "(su fragmento esperado era 3.º en la lista densa y 8.º en BM25). La abstención no cambia. <b>La predicción falló para los casos 2 y 4</b> y se cumplió para el 3. "
    "El diagnóstico muestra por qué: para casi todas las preguntas, BM25 pone arriba los mismos fragmentos, pasajes en francés y español de los apéndices de GPT-3 "
    "(traducción) y de InstructGPT (ejemplos multilingües). Las palabras vacías de nuestras preguntas («que», «de», «la», «se») casi no aparecen en un corpus en inglés, "
    "reciben un IDF alto y pesan más que el nombre del autor. Es el riesgo declarado, por un mecanismo que no previmos: BM25 no deja de encontrar, encuentra con fuerza lo equivocado.")]
if V2:
    S += [P("Iteración declarada: v2 sin palabras vacías del español en la consulta", "h2"),
          P("<b>Cambio único:</b> se quitan de la <i>pregunta</i> las palabras vacías del español (y «et», de «et al.») antes de BM25. Índice BM25, fragmentos, lista densa, "
            "RRF, prompt y generador son los mismos; la v2 reutiliza el índice de la v1. <b>Predicción escrita antes de medir:</b> corrige el caso 2 («rafailov» solo aparece "
            "en el resumen de DPO, que ya estaba 9.º en la lista densa); probablemente no el 4 («ouyang» aparece en las referencias de muchos fragmentos); no el 3."),
          P("Interpretación (v2)", "h2"),
          P(f"La v2 sube el Hit Rate a <b>{f3(v5['hit'])}</b> y el MRR a <b>{f3(v5['mrr'])}</b>, igual con k=3 y k=5. Las tres predicciones se cumplen: el caso 2 pasa a la "
            "posición 1 (en la v1 su fragmento estaba 35.º en BM25; ahora «rafailov» domina la consulta y RRF lo combina con su 9.º puesto denso), y los casos 3 y 4 siguen sin "
            "acierto. Ninguna pregunta que acertaba empeoró su posición."),
          P(f"<b>La abstención no mejora: indebida {f3(v3['ai'])} (k=3) y {f3(v5['ai'])} (k=5), frente a {f3(b3['ai'])} y {f3(b5['ai'])} del baseline.</b> Cambió quién se "
            "abstiene. El caso 2 ya no se abstiene: recibe el resumen de DPO y responde. El caso 6 (multi-fragmento GPT-3 + InstructGPT) ahora sí: la v2 sacó del contexto el "
            "único fragmento de GPT-3 que traía el baseline (brown-2020-gpt3-0071) y dejó solo InstructGPT, y sin esa mitad el modelo se abstuvo. El Hit Rate lo cuenta como "
            "acierto porque hay un fragmento de una de sus fuentes: es la limitación declarada en la Parte 2, ahora medida. La adversarial (id 10) también se abstiene con k=3."),
          P(f"<b>Conclusión.</b> La extensión mejora la recuperación medida (+{f3(v5['hit'] - b5['hit'])} de Hit Rate, +{f3(v5['mrr'] - b5['mrr'])} de MRR), pero no la respuesta "
            "final: la ganancia del caso 2 se paga con el caso 6. Con 8 respondibles cada pregunta mueve el Hit Rate 0,125, así que la diferencia es un caso y no es estadísticamente "
            "concluyente; además depende de que nuestras preguntas nombran autores. Lo que sí queda probado es el mecanismo: en un corpus en inglés consultado en español, BM25 "
            "necesita quitar las palabras vacías del idioma de la consulta; sin eso, la búsqueda léxica trae con fuerza lo equivocado.")]
else:
    S += [P("Iteración declarada: v2 sin palabras vacías del español en la consulta", "h2"),
          P("PENDIENTE: ejecutar la sección 3.3 del notebook de la Parte 3 y regenerar este informe con sus cifras.", "pend")]
S.append(PageBreak())

# ── Parte 4 ──
nb4 = json.load(open(B / "notebooks/4. Parte4.ipynb", encoding="utf-8")) if (B / "notebooks/4. Parte4.ipynb").exists() else None
S += [P("Parte 4 — Reflexión", "h1")]
if nb4:
    for c in nb4["cells"][2:]:
        t = "".join(c["source"])
        tit, cuerpo = t.split("\n\n", 1)
        S.append(P(escape(tit.lstrip("# ")), "h2"))
        for par in cuerpo.split("\n\n"):
            par = escape(par); par = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", par)
            S.append(P(par))

S += [P("Anexo — Reproducibilidad", "h1"), P(
    "El repositorio contiene el código (<font face='DVM'>ingestion.py</font>, <font face='DVM'>rag_pipeline.py</font>, <font face='DVM'>evaluation.py</font>, "
    "<font face='DVM'>hibrido.py</font>), los cinco notebooks (Partes 0–4), <font face='DVM'>golden_set.json</font>, <font face='DVM'>pyproject.toml</font>, "
    "<font face='DVM'>uv.lock</font> y <font face='DVM'>requirements.txt</font> con versiones fijadas (p. ej. qdrant-client 1.19.1, sentence-transformers 6.1.0, "
    "rank-bm25 0.2.2, pypdf 6.19.0). Todas las tablas de este informe se derivan de los CSV crudos de <font face='DVM'>resultados/</font> (una fila por consulta, "
    "con id, tipo, modelo de embeddings, k, posición del primer acierto, acierto, recíproco, puntaje del mejor vecino, abstención y generador); el propio informe se "
    "genera con <font face='DVM'>informe/generar_informe.py</font> leyendo esos archivos.")]
S.append(pre("uv sync\ncp .env.example .env          # claves vacías: todo corre sin clave, en la H200\n"
             "docker start qdrant-taller02    # o: docker run -d --name qdrant-taller02 -p 6333:6333 qdrant/qdrant\n"
             "# GlobalProtect conectada; luego Run All en notebooks/ 0 → 1 → 2 → 3 → 4"))

def pie(canvas, doc):
    canvas.saveState(); canvas.setFont("DV", 7.5); canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, 1.2 * cm, "MMIA 6013 · Taller 02 · Ballesteros, Álvarez, Ludeña")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}"); canvas.restoreState()

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Taller 02 — RAG sobre un corpus real", author="Jessica Ballesteros, Miguel Álvarez, Darlyn Ludeña")
doc.build(S, onFirstPage=pie, onLaterPages=pie)
print("PDF:", SALIDA, "| v2 incluida:", V2)
