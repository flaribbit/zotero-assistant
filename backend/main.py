from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger("backend")
app = FastAPI()


@app.get("/")
def get_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.setLevel(logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
