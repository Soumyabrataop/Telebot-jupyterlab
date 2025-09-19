import openai
import faiss
import numpy as np
import pickle
import hashlib
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Global caches to avoid redundant loads
_cached_embeddings = None
_cached_chunks = None
_cached_metadata = None
_cached_index = None
_cached_system_prompt = None
_current_api_key = None
_openai_client = None


def get_openai_client(api_key: str):
    global _openai_client, _current_api_key
    if _openai_client is None or _current_api_key != api_key:
        _openai_client = openai.OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key,
        )
        _current_api_key = api_key
    return _openai_client


def chunk_document(text: str) -> List[str]:
    if len(text) < 200:
        return [text] if text.strip() else []

    chunk_size = 800
    overlap = 100

    sentences = re.split(r'[.!?]+(?=\s+[A-Z])', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            words = current_chunk.split()
            overlap_words = words[-overlap//10:] if len(words) > overlap//10 else []
            current_chunk = " ".join(overlap_words) + " " + sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def get_cache_path(docs_dir: Path) -> Path:
    return docs_dir / "embeddings_cache.pkl"


def calculate_docs_hash(docs_dir: Path) -> str:
    hasher = hashlib.md5()
    for md_file in sorted(docs_dir.glob('*.md')):
        with open(md_file, 'rb') as f:
            hasher.update(f.read())
    return hasher.hexdigest()


def load_embeddings_cache(docs_dir: Path) -> Tuple[bool, Dict]:
    cache_path = get_cache_path(docs_dir)

    if not cache_path.exists():
        return False, {}

    try:
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)

        current_hash = calculate_docs_hash(docs_dir)
        if cache_data.get('docs_hash') == current_hash:
            return True, cache_data
        else:
            return False, {}
    except:
        return False, {}


def get_cached_embeddings(docs_dir: Path) -> Tuple[np.ndarray, List[str], List[Dict]]:
    global _cached_embeddings, _cached_chunks, _cached_metadata

    if _cached_embeddings is not None:
        return _cached_embeddings, _cached_chunks, _cached_metadata

    cache_valid, cache_data = load_embeddings_cache(docs_dir)
    if cache_valid:
        _cached_embeddings = cache_data['embeddings']
        _cached_chunks = cache_data['chunks']
        _cached_metadata = cache_data['metadata']
        return _cached_embeddings, _cached_chunks, _cached_metadata

    return np.array([]), [], []


def get_cached_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    global _cached_index
    if _cached_index is not None:
        return _cached_index

    if embeddings.size == 0:
        return None

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    _cached_index = index
    return index


def load_system_prompt() -> str:
    global _cached_system_prompt
    if _cached_system_prompt:
        return _cached_system_prompt

    try:
        with open("systemprompt.md", 'r', encoding='utf-8') as f:
            _cached_system_prompt = f.read()
    except:
        _cached_system_prompt = "You are a helpful assistant for Telebot Creator documentation."

    return _cached_system_prompt


def search_documents(query: str, index: faiss.Index, chunks: List[str], metadata: List[Dict], api_key: str) -> List[Tuple[str, Dict]]:
    if not chunks:
        return []

    query_words = query.lower().split()
    scored_chunks = []

    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower)
        if score > 0:
            scored_chunks.append((score, i, chunk, metadata[i]))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [(chunk, meta) for _, _, chunk, meta in scored_chunks[:3]]


def call_sambanova_chat(prompt: str, api_key: str) -> str:
    docs_path = Path("telebot_docs")
    embeddings, chunks, metadata = get_cached_embeddings(docs_path)

    if embeddings.size == 0:
        return "Error: No cached embeddings found. Please ensure embeddings_cache.pkl exists."

    index = get_cached_faiss_index(embeddings)
    if index is None:
        return "Error: Unable to create FAISS index from embeddings."

    try:
        relevant_chunks = search_documents(prompt, index, chunks, metadata, api_key)
        system_prompt = load_system_prompt()

        if relevant_chunks:
            system_prompt += "\n\nRelevant Documentation Sections:\n"
            for i, (chunk, meta) in enumerate(relevant_chunks, 1):
                system_prompt += f"\n--- Section {i} (from {meta['file']}) ---\n{chunk}\n"
        else:
            system_prompt += "\n\nNo specific documentation found for this query."

        client = get_openai_client(api_key)

        response = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error occurred – {str(e)}"
