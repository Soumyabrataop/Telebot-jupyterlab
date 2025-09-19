import openai
import faiss
import numpy as np
import pickle
import hashlib
import re
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Tuple, Dict

_openai_client = None
_current_api_key = None

def get_openai_client(api_key: str):
    global _openai_client, _current_api_key
    if _openai_client is None or _current_api_key != api_key:
        _openai_client = openai.OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key,
        )
        _current_api_key = api_key
    return _openai_client

def generate_embeddings_for_texts(texts: List[str], api_key: str) -> np.ndarray:
    if not texts:
        return np.array([])
    
    all_embeddings = []
    client = get_openai_client(api_key)
    
    # Larger batch size for better performance
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(
                model="E5-Mistral-7B-Instruct",
                input=batch
            )
            batch_embeddings = [embedding.embedding for embedding in response.data]
            all_embeddings.extend(batch_embeddings)
        except:
            # Use correct 4096 dimensions for E5-Mistral-7B-Instruct
            empty_embedding = [0.0] * 4096
            all_embeddings.extend([empty_embedding] * len(batch))
    
    return np.array(all_embeddings)

# Wrapper function to handle async execution in different environments
def run_async_safely(coro):
    """Run async function safely, handling Jupyter notebook event loops"""
    try:
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(coro)
    except:
        # Fallback to sync method
        return None

# Add async embedding generation for better performance
async def generate_embeddings_async(texts: List[str], api_key: str) -> np.ndarray:
    if not texts:
        return np.array([])
    
    all_embeddings = []
    batch_size = 5  # Smaller batches for better rate limit handling
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            payload = {
                "model": "E5-Mistral-7B-Instruct",
                "input": batch
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.post(
                    "https://api.sambanova.ai/v1/embeddings",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        batch_embeddings = [emb["embedding"] for emb in data["data"]]
                        all_embeddings.extend(batch_embeddings)
                    else:
                        # Handle rate limits with exponential backoff
                        if response.status == 429:
                            await asyncio.sleep(2 ** (i // batch_size))
                        empty_embedding = [0.0] * 4096
                        all_embeddings.extend([empty_embedding] * len(batch))
            except:
                empty_embedding = [0.0] * 4096
                all_embeddings.extend([empty_embedding] * len(batch))
            
            # Add delay between batches to avoid rate limits
            await asyncio.sleep(0.1)
    
    return np.array(all_embeddings)

def chunk_document(text: str) -> List[str]:
    if len(text) < 200:
        return [text] if text.strip() else []
    
    # Larger chunks = fewer API calls = faster processing
    chunk_size = 800  # Increased from 300
    overlap = 100
    
    # Improved sentence splitting for better context
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

def save_embeddings_cache(docs_dir: Path, embeddings: np.ndarray, chunks: List[str], metadata: List[Dict]):
    cache_path = get_cache_path(docs_dir)
    
    cache_data = {
        'docs_hash': calculate_docs_hash(docs_dir),
        'embeddings': embeddings,
        'chunks': chunks,
        'metadata': metadata
    }
    
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
    except:
        pass

def load_and_process_documents(docs_dir: Path, api_key: str) -> Tuple[np.ndarray, List[str], List[Dict]]:
    cache_valid, cache_data = load_embeddings_cache(docs_dir)
    if cache_valid:
        return cache_data['embeddings'], cache_data['chunks'], cache_data['metadata']
    
    chunks = []
    metadata = []
    files = list(docs_dir.glob('*.md'))
    
    if not files:
        return np.array([]), [], []
    
    for md_file in files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        if len(content) < 100:
            continue
            
        file_chunks = chunk_document(content)
        
        for i, chunk in enumerate(file_chunks):
            chunks.append(chunk)
            metadata.append({
                'file': md_file.name,
                'chunk_id': i,
                'file_size': len(content),
                'chunk_size': len(chunk)
            })
    
    if not chunks:
        return np.array([]), [], []
    
    # Try async embedding generation with better error handling
    try:
        embeddings = run_async_safely(generate_embeddings_async(chunks, api_key))
        # If async returns None (failed), fall back to sync
        if embeddings is None:
            embeddings = generate_embeddings_for_texts(chunks, api_key)
    except Exception:
        # Fall back to synchronous method if async fails
        embeddings = generate_embeddings_for_texts(chunks, api_key)
    
    save_embeddings_cache(docs_dir, embeddings, chunks, metadata)
    
    return embeddings, chunks, metadata

def create_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_documents(query: str, index: faiss.Index, chunks: List[str], metadata: List[Dict], api_key: str) -> List[Tuple[str, Dict]]:
    if not chunks:
        return []
    
    query_embedding = generate_embeddings_for_texts([query], api_key)[0]
    query_embedding = np.array(query_embedding).reshape(1, -1)
    
    # Search for more results to have better filtering options
    distances, indices = index.search(query_embedding, min(10, len(chunks)))
    
    relevant_chunks = []
    priority_files = ['getting-started.md', 'command-in-tpy.md', 'tpy-language-reference.md']
    
    # First, prioritize chunks from critical TBC documentation files
    priority_chunks = []
    other_chunks = []
    
    for i, dist in zip(indices[0], distances[0]):
        if i < len(chunks):
            chunk_data = (chunks[i], metadata[i], dist)
            if metadata[i]['file'] in priority_files:
                priority_chunks.append(chunk_data)
            else:
                other_chunks.append(chunk_data)
    
    # Sort by distance (similarity) and combine priority first
    priority_chunks.sort(key=lambda x: x[2])
    other_chunks.sort(key=lambda x: x[2])
    
    # Take top 2 from priority files and 1 from others, or adjust based on availability
    final_chunks = []
    final_chunks.extend(priority_chunks[:2])
    if len(final_chunks) < 3:
        final_chunks.extend(other_chunks[:3-len(final_chunks)])
    
    # Return without distance information
    return [(chunk, meta) for chunk, meta, _ in final_chunks[:3]]

def load_system_prompt() -> str:
    """Load the system prompt from systemprompt.md file"""
    try:
        with open("systemprompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # Fallback to default prompt if file is not found
        return "You are a helpful assistant for Telebot Creator documentation."

def call_sambanova_chat(prompt: str, api_key: str, index: faiss.Index = None, chunks: List[str] = None, metadata: List[Dict] = None) -> str:
    if index is None or chunks is None or metadata is None:
        docs_path = Path("telebot_docs")
        embeddings, chunks, metadata = load_and_process_documents(docs_path, api_key)
        if embeddings.size == 0:
            return "Error: No documents found"
        index = create_faiss_index(embeddings)
    
    try:
        relevant_chunks = search_documents(prompt, index, chunks, metadata, api_key)
        
        # Load system prompt from file
        system_prompt = load_system_prompt()
        
        if relevant_chunks:
            system_prompt += "\n\nRelevant Documentation Sections:\n"
            for i, (chunk, meta) in enumerate(relevant_chunks, 1):
                system_prompt += f"\n--- Section {i} (from {meta['file']}) ---\n"
                system_prompt += chunk
                system_prompt += "\n"
        else:
            system_prompt += "\n\nNo specific documentation found for this query. Please provide general assistance.\n"
        
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
        return f"Error: {str(e)}"

