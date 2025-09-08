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


def index_collections(collection_keys: list[str]):
    """
    索引指定文献集中的所有文献

    Args:
        collection_keys (list[str]): 文献集的唯一标识符列表
    """
    item_keys = {}
    for key in collection_keys:
        items = zotero.get_pdf_path_in_collection(key)
        item_keys.update({e["key"]: e for e in items})
    logger.info(f"Indexing collections {collection_keys} with {len(item_keys)} items")
    item_keys = list(item_keys.values())
    for i, e in tqdm(enumerate(item_keys)):
        yield f"正在索引 {i + 1}/{len(item_keys)}"
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
    logger.info("索引完成")
    return "已完成！"


def get_document_by_key(key: str):
    """
    根据key获取文档内容和信息

    Args:
        key (str): chromadb中存储的id，格式为"{item_key}_{chunk_index}"
    Returns:
        dict: 包含文档内容和信息的字典
    """
    res = collection.get(ids=[key])
    print(res)
    item_key = key.split("_")[0]
    item = zotero.get_item_info(item_key)
    title = item["title"]
    publication = item["publication"]
    pdf_key = item["pdf_key"]
    return {
        "key": item_key,
        "pdf_key": pdf_key,
        "title": title,
        "publication": publication,
        "text": res["documents"][0],
    }


def semantic_search(queries: list[str], collections: list[str], n_results: int = 10):
    """
    语义搜索，合并所有查询结果并按距离升序排列

    Args:
        queries (list[str]): 查询文本列表
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    logger.info(f"获取查询的嵌入表示: {queries}")
    query_embeddings = [e["embedding"] for e in llm.get_text_embedding(queries)]
    logger.info("获取指定文献集中的所有文献")
    keys = []
    for c in collections:
        res = zotero.get_items_in_collection(c)
        keys.extend([e["key"] for e in res])
    logger.info("在数据库中查询嵌入表示")
    results = collection.query(
        query_embeddings=query_embeddings,
        where={"key": {"$in": keys}},
        n_results=n_results,
    )
    logger.info("处理查询结果")
    resmap = {}
    for i in range(len(queries)):
        ids = results["ids"][i]
        documents = results["documents"][i]
        metadatas = results["metadatas"][i]
        distances = results["distances"][i]
        for j in range(len(ids)):
            # 如果id已经存在，取距离更小的那个
            item = {
                "document": documents[j],
                "id": ids[j],
                "key": metadatas[j]["key"],
                "distance": distances[j],
            }
            if ids[j] in resmap:
                if distances[j] < resmap[ids[j]]["distance"]:
                    resmap[ids[j]] = item
            else:
                resmap[ids[j]] = item
    merged = list(resmap.values())
    logger.info(f"合并后的结果数量: {len(merged)}")
    merged.sort(key=lambda x: x["distance"])
    merged = merged[: n_results * 2]
    return merged


def fulltext_search(query: str, n_results: int = 20):
    """
    全文搜索

    Args:
        query (str): 查询文本
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    # TODO
    return []


if __name__ == "__main__":
    pass
