import faiss
import os
import pickle
import numpy as np

from fastembed import TextEmbedding
from services.incident_triage.utils.query import get_closed_incidents

# Paths
FAISS_INDEX_PATH = "incidents_index.bin"
MAPPING_PATH = "incidents_mapping.pkl"

# Load lightweight model
model = TextEmbedding()

# Globals
faiss_index = None
id_mapping = []

# In-memory cache
embedding_cache = {}


# Embedding function with cache
def generate_embedding(text: str):
    if text in embedding_cache:
        return embedding_cache[text]

    if len(embedding_cache) > 1000:
        embedding_cache.clear()
    
    embedding = list(model.embed([text]))[0]
    embedding = np.array(embedding, dtype="float32")

    embedding_cache[text] = embedding
    return embedding


def generate_embeddings_batch(texts: list[str]) -> np.ndarray:
    embeddings = []

    for text in texts:
        emb = generate_embedding(text)
        embeddings.append(emb)

    return np.vstack(embeddings)


# Build FAISS index
def build_incidents_faiss_index():
    global faiss_index, id_mapping

    incidents = get_closed_incidents()

    texts = []
    id_mapping = []

    for inc in incidents:
        text = f"{inc['short_description']}. {inc['description']}"
        texts.append(text)
        id_mapping.append(inc["number"])

    if not texts:
        raise ValueError("No resolved/closed incidents found for FAISS index")

    embeddings = generate_embeddings_batch(texts)

    dim = embeddings.shape[1]

    # Cosine similarity
    faiss.normalize_L2(embeddings)
    faiss_index = faiss.IndexFlatIP(dim)

    faiss_index.add(embeddings)

    # Persist
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)

    with open(MAPPING_PATH, "wb") as f:
        pickle.dump(id_mapping, f)

    print(f"FAISS index built and saved with {len(id_mapping)} incidents")


# Load FAISS index
def load_incident_faiss_index():
    global faiss_index, id_mapping

    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(MAPPING_PATH):
        print("FAISS index not found. Building new index...")
        build_incidents_faiss_index()
        return

    faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    with open(MAPPING_PATH, "rb") as f:
        id_mapping = pickle.load(f)

    print(f"Pre-loaded FAISS index found with {len(id_mapping)} incidents")


# Search similar incidents
def search_similar_incidents(query_text: str, top_k: int = 5):
    global faiss_index, id_mapping

    if faiss_index is None:
        raise ValueError("FAISS index not initialized")

    query_embedding = generate_embedding(query_text).reshape(1, -1)

    faiss.normalize_L2(query_embedding)

    scores, indices = faiss_index.search(query_embedding, top_k)

    results = []

    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue

        results.append({
            "incident_id": id_mapping[idx],
            "similarity": float(scores[0][i])
        })

    return results