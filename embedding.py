import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

from services.incident_triage.utils.query import get_closed_incidents

# Paths for persistence
FAISS_INDEX_PATH = "incidents_index.bin"
MAPPING_PATH = "incidents_mapping.pkl"

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Globals
faiss_index = None
id_mapping = []


def build_incidents_faiss_index():
    global faiss_index, id_mapping

    incidents = get_closed_incidents()

    texts = []
    id_mapping = []

    for inc in incidents:
        text = f"{inc['short_description']} {inc['description']}"
        texts.append(text)
        id_mapping.append(inc["number"])

    if not texts:
        raise ValueError("No resolved/closed incidents found for FAISS index")

    embeddings = model.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]

    # Cosine similarity via inner product
    faiss.normalize_L2(embeddings)
    faiss_index = faiss.IndexFlatIP(dim)

    faiss_index.add(embeddings)

    # Persist to disk
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)

    with open(MAPPING_PATH, "wb") as f:
        pickle.dump(id_mapping, f)

    print(f"FAISS index built and saved with {len(id_mapping)} incidents")

def load_incident_faiss_index():
    global faiss_index, id_mapping

    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(MAPPING_PATH):
        print("FAISS index not found. Building new index...")
        build_incidents_faiss_index()
        return

    faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    with open(MAPPING_PATH, "rb") as f:
        id_mapping = pickle.load(f)

    print(f"FAISS index loaded with {len(id_mapping)} incidents")

def search_similar_incidents(query_text: str, top_k: int = 5):
    global faiss_index, id_mapping

    if faiss_index is None:
        raise ValueError("FAISS index not initialized")

    query_embedding = model.encode([query_text], convert_to_numpy=True)
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