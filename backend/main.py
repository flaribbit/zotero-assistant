from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
import json
import uvicorn
import logging
import zotero
import llm
import database

logger = logging.getLogger("backend")
app = FastAPI(title="Zotero Assistant API")


@app.get("/")
def get_root():
    content = """<html>
<head>
    <title>Zotero Assistant API</title>
</head>
<body>
    <h1>Zotero Assistant API</h1>
    <p>Welcome to the Zotero Assistant API. You can find the API documentation <a href="/scalar">here</a>.</p>
</body>
</html>"""
    return HTMLResponse(content=content)


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


@app.get("/collection")
def get_collection(collection_key):
    """获取指定文献集中的所有文献"""
    return zotero.get_items_in_collection(collection_key)


@app.post("/embedding_text")
def embedding_text(text: str):
    """获取文本的嵌入表示"""
    return llm.get_text_embedding(text)


@app.get("/update_index")
def update_index():
    """更新索引"""
    # TODO: 更新全文搜索数据库和llamaindex索引
    return {"message": "Index updated"}


@app.get("/index_collection")
def index_collection(collection_key: str):
    """索引指定文献集中的所有文献"""
    return database.index_collection(collection_key)


@app.post("/semantic_search")
def semantic_search(query: list[str], n_results: int = 10):
    """语义搜索"""
    return database.semantic_search(query, n_results)


@app.post("/get_full_prompt")
def get_full_prompt(query: str):
    """根据用户查询生成完整提示词"""
    enhanced_query = llm.enhance_query(query)
    knowledge = database.semantic_search(enhanced_query, n_results=10)
    return llm.get_full_prompt(query, json.dumps(knowledge, ensure_ascii=False))


@app.get("/get_document")
def get_document(key: str):
    """根据key获取文档内容"""
    return database.get_document_by_key(key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.setLevel(logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
