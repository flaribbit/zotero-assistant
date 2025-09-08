import chromadb
import zotero
import logging
import llm
import os
from tqdm import tqdm

logger = logging.getLogger("backend")
client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection(name="zotero")


def tqdm_info(msg):
    if logger.isEnabledFor(logging.INFO):
        tqdm.write(msg)


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
        res = collection.get(where={"key": pdf_key}, include=["metadatas"])
        ids = res["ids"]
        if ids:
            if res["metadatas"][0]["mod"] >= mod:
                continue
            else:
                collection.delete(ids=ids)
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


# def get_document_by_key(key: str):
#     """
#     根据key获取文档内容

#     Args:
#         key (str): 文档的唯一标识符

#     Returns:
#         dict: 文档内容和元数据
#     """
#     # TODO
#     return None

def get_document_by_key(key: str, merge: bool = True):
    """
    根据key获取文档内容

    Args:
        key (str): 文档的唯一标识符
        merge (bool): 是否合并所有分块文本为一个整体
                      - True: 返回拼接后的完整文本
                      - False: 返回按分块的文本列表

    Returns:
        dict: 包含文档内容、分块信息和元数据
    """
    res = collection.get(where={"key": key}, include=["documents", "metadatas", "ids"])

    if not res["ids"]:
        return {
            "message": f"Document with key {key} not found",
            "content": None,
            "metadata": None,
            "chunks": [],
        }

    documents = res["documents"]  # list[str]
    metadata = res["metadatas"][0]  # 取第一个即可，其他分块相同

    if merge:
        full_text = "\n".join(documents)
        return {
            "key": key,
            "content": full_text,
            "metadata": metadata,
            "chunks": documents,
        }
    else:
        return {
            "key": key,
            "content": None,  # 不拼接
            "metadata": metadata,
            "chunks": documents,
        }



def semantic_search(queries: list[str], n_results: int = 10):
    """
    语义搜索，合并所有查询结果并按距离升序排列

    Args:
        queries (list[str]): 查询文本列表
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    query_embeddings = [e["embedding"] for e in llm.get_text_embedding(queries)]
    results = collection.query(query_embeddings=query_embeddings, n_results=n_results)
    resmap = {}
    for i in range(len(queries)):
        ids = results["ids"][i]
        documents = results["documents"][i]
        # metadatas = results["metadatas"][i]  # 用不到
        distances = results["distances"][i]
        for j in range(len(ids)):
            # 如果id已经存在，取距离更小的那个
            item = {
                "document": documents[j],
                "key": ids[j],
                "distance": distances[j],
            }
            if ids[j] in resmap:
                if distances[j] < resmap[ids[j]]["distance"]:
                    resmap[ids[j]] = item
            else:
                resmap[ids[j]] = item
    merged = list(resmap.values())
    merged.sort(key=lambda x: x["distance"])
    merged = merged[: n_results * 2]
    return merged


if __name__ == "__main__":
    pass
