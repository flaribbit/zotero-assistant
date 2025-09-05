import chromadb
import zotero
import logging
import llm
import os
from tqdm import tqdm

logger = logging.getLogger("backend")
client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection(name="zotero")


def index_collection(collection_key):
    """
    索引指定文献集中的所有文献

    Args:
        collection_key (str): 文献集的唯一标识符
    """
    items = zotero.get_pdf_path_in_collection(collection_key)
    logger.info(f"Indexing collection {collection_key} with {len(items)} items")
    for e in tqdm(items):
        pdf_key = e["key"]
        pdf_path = e["path"]
        mod = int(os.path.getmtime(pdf_path))
        # TODO：检查是否已经索引过，且自从上次索引后没有修改过
        text = zotero.get_pdf_text(pdf_path)
        chunks = llm.split_text(text)
        count = len(chunks)
        embeddings = [e["embedding"] for e in llm.get_text_embedding(chunks)]
        collection.add(
            documents=chunks,
            metadatas=[{"key": pdf_key, "mod": mod}] * count,
            ids=[f"{pdf_key}_{i}" for i in range(count)],
            embeddings=embeddings,
        )
    return {"message": f"Indexed {len(items)} items in collection {collection_key}"}


def semantic_search(query: str, n_results: int = 10):
    """
    语义搜索

    Args:
        query (str): 查询文本
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    query_embedding = llm.get_text_embedding(query)[0]["embedding"]
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    return results
