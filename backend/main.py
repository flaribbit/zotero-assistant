from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
import uvicorn
import logging
import zotero
import llm

logger = logging.getLogger("backend")
app = FastAPI(title="Zotero Assistant API")


@app.get("/")
def get_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        title=app.title,
        openapi_url=app.openapi_url,
    )


@app.get("/collections")
def get_collections():
    """获取所有文献集"""
    return zotero.get_collections()


@app.get("/collection/{collection_key}")
def get_collection(collection_key):
    """获取指定文献集中的所有文献"""
    return zotero.get_items_in_collection(collection_key)


@app.post("/embedding_text")
def embedding_text(text: str):
    """获取文本的嵌入表示"""
    return llm.get_text_embedding(text)


@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.setLevel(logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
