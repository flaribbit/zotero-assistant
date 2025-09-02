import logging
import httpx

logger = logging.getLogger("backend")
client = httpx.Client(base_url="http://127.0.0.1:23119/api/users/0/")


def get_collections():
    """
    获取所有文献集
    """
    res = client.get("collections")
    return [{"key": e["key"], "name": e["data"]["name"], "numItems": e["meta"]["numItems"]} for e in res.json()]


def get_items_in_collection(collection_key):
    """
    获取指定文献集中的所有文献

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中的所有文献
    """
    res = client.get(f"collections/{collection_key}/items")
    return [{"key": e["key"], "title": e["data"]["title"]} for e in res.json()]
