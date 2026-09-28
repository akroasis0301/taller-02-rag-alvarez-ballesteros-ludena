import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def caja(ax, x, y, w, h, titulo, sub, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=color, ec="#334155", lw=1.1))
    ax.text(x + w/2, y + h*0.64, titulo, ha="center", va="center", fontsize=9.5, weight="bold", color="#0f172a")
    ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center", fontsize=7.4, color="#334155")

def flecha(ax, a, b, estilo="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=12, lw=1.1, color="#475569", ls=ls))

def dibujar(ruta):
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
    IND, CON, EVA, EXT = "#dbeafe", "#dcfce7", "#fef3c7", "#fce7f3"
    ax.text(0.1, 4.4, "Indexación (una vez)", fontsize=9, weight="bold", color="#1e3a8a")
    w, h, y = 1.75, 0.9, 3.25
    xs = [0.1, 2.05, 4.0, 5.95, 7.9]
    datos = [("Corpus", "6 papers PDF (EN)\n262 páginas", IND),
             ("Ingesta", "pypdf · descarta\n< 200 car. útiles", IND),
             ("Fragmentación", "512 tokens bge-m3\nsolapamiento 102", IND),
             ("Embeddings", "bge-m3 · 1024 dim\nH200 (Ollama)", IND),
             ("Qdrant", "contenedor Docker\nHNSW · coseno", IND)]
    for x, (t, s, c) in zip(xs, datos):
        caja(ax, x, y, w, h, t, s, c)
    for a, b in zip(xs[:-1], xs[1:]):
        flecha(ax, (a + w, y + h/2), (b, y + h/2))

    ax.text(0.1, 2.75, "Consulta (por pregunta)", fontsize=9, weight="bold", color="#166534")
    y2 = 1.65
    caja(ax, 0.1, y2, w, h, "Pregunta", "golden set (ES)\n10 preguntas", CON)
    caja(ax, 2.05, y2, w, h, "Recuperación", "top-k denso\nk = 3 y k = 5", CON)
    caja(ax, 4.0, y2, w, h, "Prompt", "solo contexto +\nfrase ABSTENCION", CON)
    caja(ax, 5.95, y2, w, h, "Generación", "qwen3:32b\nH200 (Ollama)", CON)
    caja(ax, 7.9, y2, w, h, "Respuesta", "o abstención\n(detector normalizado)", CON)
    for a, b in [(0.1, 2.05), (2.05, 4.0), (4.0, 5.95), (5.95, 7.9)]:
        flecha(ax, (a + w, y2 + h/2), (b, y2 + h/2))
    flecha(ax, (7.9 + w/2, y), (2.05 + w*0.8, y2 + h), ls="--")
    ax.text(5.6, 2.72, "vecinos más cercanos", fontsize=7, color="#475569", style="italic")

    caja(ax, 2.05, 0.2, w, 0.95, "Parte 3: BM25", "sobre los mismos\n530 fragmentos", EXT)
    caja(ax, 4.0, 0.2, w, 0.95, "RRF (k=60)", "fusiona denso + BM25\n20 candidatos c/u", EXT)
    flecha(ax, (2.05 + w, 0.67), (4.0, 0.67))
    flecha(ax, (4.0 + w/2, 1.15), (2.05 + w*0.75, y2), ls="--")
    caja(ax, 7.9, 0.2, w, 0.95, "evaluation.py", "Hit Rate · MRR ·\n2 tasas de abstención", EVA)
    flecha(ax, (7.9 + w/2, y2), (7.9 + w/2, 1.15))
    ax.text(5.95, 0.55, "→ resultados/*.csv\n(una fila por consulta)", fontsize=7.4, color="#475569")
    fig.savefig(ruta, bbox_inches="tight", facecolor="white"); plt.close(fig)

if __name__ == "__main__":
    dibujar("arquitectura.png")
