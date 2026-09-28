"""
Parte 3 — Opción B: búsqueda híbrida (BM25 + densa) fusionada con Reciprocal Rank Fusion.

    from hibrido import PipelineHibrido
    p = PipelineHibrido()
    p.index(p.ingest("corpus", chunk_tokens=512, overlap_tokens=102))
    p.retrieve("¿Qué propone Rafailov et al.?", top_k=5)

Cómo funciona:

1. **Denso**: los `CANDIDATOS` vecinos más cercanos en Qdrant (bge-m3), igual que el baseline.
2. **Léxico**: los `CANDIDATOS` fragmentos con mayor puntaje BM25 (rank_bm25) sobre los
   MISMOS fragmentos que se indexaron en Qdrant.
3. **RRF**: cada fragmento suma 1 / (RRF_K + posición) por cada lista en la que aparece.
   RRF usa solo las posiciones, no los puntajes: el coseno (0–1) y BM25 (sin tope) no son
   comparables, y RRF no necesita normalizarlos. RRF_K = 60 es el valor de Cormack et al.
   (2009) y el que se usó en el notebook del jueves.

`PipelineHibrido` hereda de `RagPipeline`: solo cambia `retrieve`, así que `answer`,
`build_prompt`, `generate` y `evaluation.evaluate_retrieval` funcionan sin modificarse,
y la comparación contra el baseline es con el mismo índice, prompt y generador.
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
from rank_bm25 import BM25Okapi

from rag_pipeline import COLLECTION, RagPipeline

RRF_K = 60
CANDIDATOS = 20


def tokenizar(texto: str) -> list[str]:
    """Minúsculas, sin tildes, solo secuencias alfanuméricas. Es deliberadamente simple
    y la MISMA para la pregunta y para los fragmentos."""
    t = unicodedata.normalize("NFKD", texto.casefold())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t)


class PipelineHibrido(RagPipeline):
    def __init__(self, collection: str = COLLECTION, candidatos: int = CANDIDATOS,
                 rrf_k: int = RRF_K):
        super().__init__(collection)
        self.candidatos = candidatos
        self.rrf_k = rrf_k
        self._chunks = []
        self._bm25 = None

    def index(self, chunks) -> None:
        """Indexa en Qdrant (denso) y construye el índice BM25 sobre los mismos fragmentos."""
        super().index(chunks)
        self._chunks = list(chunks)
        self._bm25 = BM25Okapi([tokenizar(c.text) for c in self._chunks])

    def retrieve_denso(self, question: str, top_k: int = 5) -> list[dict]:
        return super().retrieve(question, top_k=top_k)

    def retrieve_bm25(self, question: str, top_k: int = 5) -> list[dict]:
        if self._bm25 is None:
            raise RuntimeError("Llama a index() antes de recuperar: el índice BM25 vive en memoria")
        puntajes = self._bm25.get_scores(tokenizar(question))
        orden = np.argsort(-puntajes)[:top_k]
        # Un fragmento con BM25 = 0 no comparte ningún término con la pregunta: no es un
        # candidato léxico. Si entrara, RRF le daría crédito por una posición arbitraria
        # (el orden entre ceros no significa nada). Con preguntas en español sobre papers
        # en inglés, esto pasa a menudo.
        return [
            {"score": float(puntajes[i]), "chunk_id": self._chunks[i].id,
             "document": self._chunks[i].document, "text": self._chunks[i].text}
            for i in orden if puntajes[i] > 0
        ]

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        listas = {"denso": self.retrieve_denso(question, self.candidatos),
                  "bm25": self.retrieve_bm25(question, self.candidatos)}
        fusion: dict[str, dict] = {}
        for nombre, lista in listas.items():
            for posicion, hit in enumerate(lista, start=1):
                item = fusion.setdefault(hit["chunk_id"], {
                    "chunk_id": hit["chunk_id"], "document": hit["document"], "text": hit["text"],
                    "score": 0.0, "rank_denso": None, "rank_bm25": None,
                })
                item["score"] += 1.0 / (self.rrf_k + posicion)
                item[f"rank_{nombre}"] = posicion
        return sorted(fusion.values(), key=lambda h: h["score"], reverse=True)[:top_k]


class SoloDenso:
    """Adaptador para evaluar el baseline con el MISMO índice que el híbrido."""

    def __init__(self, pipeline: PipelineHibrido):
        self.pipeline = pipeline

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        return self.pipeline.retrieve_denso(question, top_k=top_k)
