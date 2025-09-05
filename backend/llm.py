from transformers import AutoTokenizer
from openai import OpenAI
from config import config

client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key=config["siliconflow"]["api_key"],
)


def get_text_embedding(text: str | list[str]):
    """
    获取文本的嵌入表示

    Args:
        text (str): 文本

    Returns:
        list: 文本的嵌入表示
    """
    response = client.embeddings.create(model="Qwen/Qwen3-Embedding-0.6B", input=text).model_dump()
    return response["data"]


def split_text(text: str, chunk_size: int = 1024, overlap: int = 100):
    """
    将文本分割为给定大小的块

    Args:
        text (str): 输入文本
        chunk_size (int): 每个块的最大token数
        overlap (int): 块之间重叠的token数

    Returns:
        list: 文本块列表
    """
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Embedding-0.6B")
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i : i + chunk_size]
        chunks.append(tokenizer.convert_tokens_to_string(chunk))
        if i + chunk_size >= len(tokens):
            break
    return chunks
