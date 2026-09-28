# Taller 02 — RAG sobre un corpus real · MMIA 6013

Repositorio del grupo para el Taller 02 (IA Generativa y Agentes, USFQ). Parte del
andamiaje `Lab-02-RAG-VectorSearch` del profesor, reorganizado como proyecto **uv**.

## Integrantes

- Darlyn Ludeña
- Jessica Ballesteros
- Miguel Alvarez

## Requisitos

- [uv](https://docs.astral.sh/uv/) (gestiona Python 3.12 y las dependencias)
- Docker (para Qdrant)
- VPN GlobalProtect de la USFQ (embeddings `bge-m3` en la H200). Sin VPN: `EMBEDDING_BACKEND=openai`

## Puesta en marcha

```bash
git clone https://github.com/akroasis0301/taller-02-rag-alvarez-ballesteros-ludena.git
cd taller-02-rag-alvarez-ballesteros-ludena
uv sync                     # crea .venv con las versiones exactas de uv.lock
cp .env.example .env        # cada uno pone su clave aquí; .env NUNCA se sube
```

> **No uses `pip install -r requirements.txt`** (la instrucción del README original, más abajo).
> `requirements.txt` existe solo como entregable de reproducibilidad y se regenera desde uv.

## Qdrant

```bash
docker run -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

`qdrant_storage/` guarda el índice entre corridas y está en `.gitignore`.
Para depurar sin Docker: `QDRANT_URL=":memory:"`.

## Cómo se ejecuta

```bash
# Parte 0 (MiniLM local, sin VPN ni Docker)
EMBEDDING_BACKEND=local QDRANT_URL=":memory:" CORPUS_DIR=ejemplos uv run python rag_pipeline.py "¿cuántos días de vacaciones puedo transferir?"

# Parte 1 (corpus real en corpus/)
uv run python rag_pipeline.py "una pregunta de prueba"

# Parte 2 (10 preguntas definidas en golden_set.json)
# También se puede ejecutar paso a paso en notebooks/2. Parte2.ipynb.
# Con VPN GlobalProtect: EMBEDDING_BACKEND=h200 (valor por defecto), Qdrant levantado,
# .env configurado para generación con propietario_economico u Ollama. Sin clave,
# puedes usar el Ollama de la H200: export OLLAMA_URL=http://172.28.230.10:11434
# El notebook guarda los dos CSV por k y resultados/resultados.csv combinado (20 filas).
uv run python evaluation.py --golden golden_set.json --k 3 --csv resultados/parte2_k3.csv
uv run python evaluation.py --golden golden_set.json --k 5 --csv resultados/parte2_k5.csv

# Sin VPN: usa embeddings de OpenAI (requiere OPENAI_API_KEY en .env) y reindexa.
EMBEDDING_BACKEND=openai uv run python evaluation.py --golden golden_set.json --k 3 --csv resultados/parte2_k3.csv
EMBEDDING_BACKEND=openai uv run python evaluation.py --golden golden_set.json --k 5 --csv resultados/parte2_k5.csv

# Recuperación únicamente (sin generar ni medir las tasas de abstención):
uv run python evaluation.py --golden golden_set.json --k 3 --sin-generar --csv resultados/parte2_k3_sin_generar.csv
```

## Orden de ejecución de los notebooks

Con GlobalProtect conectada y Qdrant levantado (`docker start qdrant-taller02`), ejecutar **Run All** en orden:
`notebooks/0. Parte0.ipynb` → `1. Parte1.ipynb` → `2. Parte2.ipynb` → `3. Parte3.ipynb`.
Todos usan el mismo generador (`open_weight_pequeno`, qwen3:32b en el Ollama de la H200) y vacían
las claves de API en el propio notebook, así que no dependen de lo que haya en `.env`.

## Estructura

```
corpus/         Corpus del grupo (Parte 1)
ejemplos/       Corpus mínimo + PDF escaneado (Parte 0)
fuentes/        Tabla semestral de modelos (modelos-2026-1.json)
hibrido.py      Parte 3: búsqueda híbrida BM25 + densa con RRF
salidas/parte0/ Salidas crudas de 0.a, 0.b y 0.c
resultados/     CSV crudos de evaluation.py (entregable)
notebooks/      Pruebas y análisis
informe/        Informe final en PDF
```

## Reglas del equipo

- **Pull antes de empezar** y antes de cada commit.
- **Un notebook, una persona**: los `.ipynb` no se fusionan bien.
- **Solo una persona agrega dependencias** (`uv add ...`) y después regenera:
  `uv export --format requirements-txt --no-hashes --no-dev -o requirements.txt`.
  Los demás hacen pull y `uv sync`.
- **Ninguna clave** en código, notebooks, capturas ni commits (política de credenciales del curso).

---

# Andamiaje original del profesor (Lab 02)

Andamiaje del Taller 2. Trae la ingesta, la fragmentación, el índice, la recuperación, el
prompt, **la llamada al LLM** y el evaluador; lo que el estudiante pone es el corpus, el
golden set, los parámetros con su justificación y el análisis.

> **Los embeddings son de `bge-m3`, servido en la H200 de la USFQ.** Hace falta la VPN
> GlobalProtect. Sin VPN, la alternativa es la API de OpenAI (`EMBEDDING_BACKEND=openai`).
> Cuatro cosas que no fallarían por sí solas y aquí fallan o se miden: el PDF escaneado que
> se indexaría vacío, el fragmento que se truncaría en silencio, las preguntas negativas que
> pondrían un techo al Hit Rate, y la abstención que ningún detector por igualdad de cadena
> podría ver. El detalle está en la cabecera de cada archivo.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env            # y pon la clave de OpenAI que reparte el curso, si la usas
# GlobalProtect conectada: los embeddings se calculan en la H200 (bge-m3)
docker run -p 6333:6333 qdrant/qdrant       # o QDRANT_URL=":memory:" para correr sin Docker
```

`QDRANT_URL=":memory:"` es la misma API sin contenedor: sirve para la Parte 0 y para
depurar. El sábado se evalúa contra el contenedor, que es lo que persiste el índice.

## Estructura

```
Lab-02-RAG-VectorSearch/
├── README.md
├── requirements.txt
├── .env.example
├── ingestion.py               Carga, parseo y fragmentación EN TOKENS del modelo
├── rag_pipeline.py            Ingesta → índice → recuperación → prompt → generación
├── evaluation.py              Hit Rate y MRR sobre respondibles; dos tasas de abstención; CSV crudo
├── golden_set_plantilla.json  Plantilla (10 preguntas, anotadas por documento y fragmento)
├── ejemplos/                  Corpus mínimo + un PDF escaneado, para la Parte 0 del taller
└── corpus/                    Tu corpus (lo creas tú)
```

## Baseline

1. Copia tus PDFs o `.txt`/`.md` en `corpus/`.
2. Revisa/ajusta `golden_set.json` para que sus fuentes correspondan exactamente a los documentos de `corpus/`.
3. `python rag_pipeline.py "una pregunta de prueba"`: ingesta, indexa, recupera y genera.
4. `python evaluation.py --k 5`: métricas y `resultados.csv`, una fila por consulta.

RAGAS, búsqueda híbrida y reranking son extensiones. Primero debe funcionar el baseline.

## Las tres fallas que no fallan (Parte 0 del taller)

La Parte 0 corre con el MiniLM de los notebooks **en tu máquina** (`EMBEDDING_BACKEND=local`):
sin clave, sin VPN, sin Docker y en un minuto. Es la **única** parte del taller que no usa
`bge-m3`, y es a propósito: la 0.b necesita un modelo que trunque a 128 tokens.

```bash
EMBEDDING_BACKEND=local QDRANT_URL=":memory:" python rag_pipeline.py "¿cuántos días de vacaciones puedo transferir?"
```

- **El PDF escaneado.** `ejemplos/instructivo_escaneado.pdf` no tiene capa de texto. Sin
  comprobación se indexaría como un fragmento hecho de `[page=1] [page=2]`, sin ninguna
  excepción. La ingesta avisa: `0 caracteres útiles en 2 página(s) … NO se indexa`. Si tu
  corpus real trae uno, ese documento no está aunque el índice diga que sí.
- **El fragmento que se corta.** El MiniLM trunca a **128 tokens** de secuencia
  (`fuentes/modelos/modelos-2026-1.json`, fila `embed_notebook_s2`, verificado 2026-08-27),
  y lo hace sin avisar. La ingesta fragmenta en tokens del **mismo** tokenizador y lee el
  tope del modelo; si pides un fragmento mayor, avisa cuánto se pierde. Pide
  `chunk_tokens=900` y míralo.
- **El índice que no se queja.** Pregunta algo que no está (`"¿cuál es la política de
  mascotas?"`): devuelve cinco vecinos con puntajes de aspecto sano. Ningún Hit Rate
  detecta esto; por eso el golden set lleva negativas y el evaluador mide si el sistema
  **se abstiene**.

## El modelo de embeddings: `bge-m3` en la H200

`rag_pipeline.py` calcula los embeddings con **`bge-m3`** (fila `embed_local_multilingue` de
la tabla semestral): multilingüe —el corpus por defecto del taller está en español—, 1024
dimensiones y un tope de **8192 tokens**. Lo sirve el Ollama de la H200 de la USFQ
(`H200_EMBED_URL`, por defecto `http://172.28.230.10:11434`); el cliente busca en su catálogo
el id servido que empieza por `bge-m3`, en vez de escribirlo, y le pide `truncate: false`:
si un texto no cabe, el servidor da error en vez de recortarlo en silencio. El tokenizador
con el que se fragmenta es el de `BAAI/bge-m3` —se descarga solo el tokenizador—, para que
la ingesta cuente en los mismos tokens que el servidor.

El fragmento por defecto es de **512 tokens** con un quinto de solapamiento: con 8192 de
tope, «el fragmento más grande que cabe» ya no es un buen valor por defecto, y 512 es el
tamaño de las notas del curso. Cámbialo con `chunk_tokens` y justifícalo en el informe.

| `EMBEDDING_BACKEND` | Modelo (fila) | Tope | Hace falta |
|---|---|---|---|
| `h200` (por defecto) | `bge-m3` (`embed_local_multilingue`) | 8192 | VPN GlobalProtect |
| `openai` | `text-embedding-3-small` (`embed_api_economico`); `EMBEDDING_MODEL` elige otro | 8192 | `OPENAI_API_KEY` |
| `local` | MiniLM multilingüe (`embed_notebook_s2`) | 128 | nada; **solo para la Parte 0** |

**Sin VPN, la alternativa es OpenAI**, y cuesta poco: los embeddings de un corpus de 50
páginas son unas decenas de miles de tokens. Lo que no se puede es **mezclar**: un índice
construido con un modelo solo se consulta con ese mismo modelo, así que si cambias de ruta,
reindexa. Y se declara en el informe con qué modelo se construyó el índice.

## La generación, y la abstención

`rag_pipeline.generate` elige la ruta por la clave disponible: `OPENAI_API_KEY` → fila
`propietario_economico`; `ANTHROPIC_API_KEY` → fila `juez_economico`; ninguna → Ollama con
la fila `open_weight_pequeno`; y sin Ollama, «modo inspección», que devuelve el prompt.
`GENERATION_MODEL` sobreescribe el modelo. Ningún nombre está escrito a mano en el código:
salen de la tabla semestral por su `id`.

La frase de abstención es **una** en todo el curso: `ABSTENCION` en `rag_pipeline.py`, la
misma en el prompt, en el golden set y en el notebook del miércoles. `se_abstuvo()` la
detecta **normalizada** (minúsculas, sin tildes, sin puntuación): con una tilde de más o un
punto final de menos, un detector por igualdad de cadena no dispararía nunca.

## Qué mide `evaluation.py`

| Métrica | Sobre qué | Qué significa |
|---|---|---|
| `hit_rate` | preguntas **respondibles** | ¿algún fragmento recuperado pertenece al documento fuente (y contiene el fragmento esperado, si lo diste)? |
| `mrr` | respondibles | media de 1/posición del primer acierto |
| `abstencion_correcta` | negativas | fracción en la que el sistema se abstuvo — lo correcto |
| `abstencion_indebida` | respondibles | fracción en la que se abstuvo — lo incorrecto |

Las negativas **no entran** en `hit_rate` ni en `mrr`: no hay nada que recuperar. Con la
plantilla anterior sí entraban, y un sistema perfecto reportaba 0,70 como techo.
`--sin-generar` salta el LLM: las dos tasas salen «sin medir» y las otras dos, igual.

El golden set se anota **por documento y por fragmento literal**, no por `chunk_id`: los
identificadores cambian al re-fragmentar y la Opción A del taller los invalidaba sin fallar.

## Recursos

- Qdrant docs: https://qdrant.tech/documentation (consultado 2026-09-19: `create_collection`
  + `query_points`; HNSW es el único índice denso, `m=16`, `ef_construct=100`)
- sentence-transformers: https://www.sbert.net
- RAGAS: https://docs.ragas.io
