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


def get_pdf_path_in_collection(collection_key: str):
    """
    获取文献集中文献的PDF文件路径

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中文献的PDF文件路径
    """
    # TODO
    return []


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
