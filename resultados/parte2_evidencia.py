"""Reproduce evidencia detallada para los tres casos más débiles de Parte 2.c."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation import acierta, load_golden_set, posicion_del_primer_acierto
from rag_pipeline import RagPipeline

pipeline = RagPipeline()
chunks = pipeline.ingest(ROOT / "corpus")
pipeline.index(chunks)
golden = load_golden_set(ROOT / "golden_set.json")

candidatos = []
for item in golden:
    if not item.get("documentos_fuente"):
        continue
    hits = pipeline.retrieve(item["pregunta"], top_k=5)
    posicion = posicion_del_primer_acierto(hits, item)
    candidatos.append((posicion or 99, item, hits))

peores = []
for posicion, item, hits in sorted(candidatos, key=lambda x: x[0], reverse=True)[:3]:
    respuesta = pipeline.answer(item["pregunta"], top_k=5)
    peores.append({
        "id": item["id"],
        "tipo": item["tipo"],
        "pregunta": item["pregunta"],
        "fuentes_esperadas": item["documentos_fuente"],
        "fragmento_esperado": item["fragmento_esperado"],
        "posicion_primer_acierto": None if posicion == 99 else posicion,
        "hits": [{
            "posicion": i,
            "documento": h["document"],
            "score": h["score"],
            "chunk_id": h["chunk_id"],
            "texto": h["text"],
            "acierto": acierta(h, item),
        } for i, h in enumerate(hits, 1)],
        "respuesta_esperada": item["respuesta_esperada"],
        "respuesta_generada": respuesta["answer"],
        "generador": respuesta["generator"],
        "abstuvo": respuesta["abstained"],
    })

out = ROOT / "resultados" / "parte2_peores_casos.json"
out.write_text(json.dumps(peores, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(peores, ensure_ascii=False, indent=2))
print(f"Evidencia detallada guardada en {out}")
