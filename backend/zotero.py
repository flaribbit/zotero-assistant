import os
import logging
import httpx
import pymupdf
from config import config

logger = logging.getLogger("backend")
client = httpx.Client(base_url="http://127.0.0.1:23119/api/users/0/")


def get_collections():
    """
    获取所有文献集
    """
    res = client.get("collections")
    return [{"key": e["key"], "name": e["data"]["name"], "numItems": e["meta"]["numItems"]} for e in res.json()]


def get_items_in_collection(collection_key: str):
    """
    获取指定文献集中的所有文献

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中的所有文献
    """
    res = client.get(f"collections/{collection_key}/items")
    return [{"key": e["key"], "title": e["data"]["title"]} for e in res.json()]


def find_pdf_file_in_path(path: str) -> str:
    """在指定路径中查找PDF文件

    理论上应该用Zotero api，但是这个方法更高效

    Args:
        path (str): 要查找的路径

    Returns:
        str: 找到的PDF文件的路径，如果未找到则返回None
    """
    for e in os.listdir(path):
        if os.path.splitext(e)[1] == ".pdf":
            return f"{path}/{e}"
    return None


def get_pdf_path_in_collection(collection_key: str):
    """
    获取文献集中文献的PDF文件路径

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中文献的PDF文件路径
    """
    zotero_path = config["zotero_path"]
    res = client.get(f"collections/{collection_key}/items")
    ret = []
    for e in res.json():
        if "attachment" not in e["links"]:
            continue
        pdf_key = e["links"]["attachment"]["href"][-8:]
        pdf_path = find_pdf_file_in_path(f"{zotero_path}/storage/{pdf_key}")
        title = e["data"]["title"]
        if not pdf_path:
            logger.warning(f"PDF file of {title} not found. Skipping.")
            continue
        ret.append(
            {
                "key": e["key"],
                "title": title,
                "path": pdf_path,
                "publication": e["data"].get("publicationTitle", ""),
            }
        )
    return ret


def get_pdf_text(pdf_path: str):
    """
    获取PDF文件的文本内容

    Args:
        pdf_path (str): PDF文件的路径

    Returns:
        str: PDF文件的文本内容
    """
    text = ""
    anno = ""
    doc = pymupdf.open(pdf_path)
    for page in doc:
        textpage = page.get_textpage()
        text += textpage.extractText()
        for a in page.annots():
            content = a.info["content"]
            if content:
                anno += content + "\n"
    return text + "\n---\n用户笔记：" + anno
