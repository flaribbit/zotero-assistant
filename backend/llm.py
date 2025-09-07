from tokenizers import Tokenizer
from openai import OpenAI
from config import config
import logging
import json
import re

embedding_client = OpenAI(
    base_url=config["embedding"]["base_url"],
    api_key=config["embedding"]["api_key"],
)
chat_client = OpenAI(
    base_url=config["chat"]["base_url"],
    api_key=config["chat"]["api_key"],
)
logger = logging.getLogger("backend")


def get_text_embedding(text: str | list[str]):
    """
    获取文本的嵌入表示

    Args:
        text (str): 文本

    Returns:
        list: 文本的嵌入表示
    """
    response = embedding_client.embeddings.create(model=config["embedding"]["model"], input=text).model_dump()
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
    tokenizer: Tokenizer = Tokenizer.from_pretrained(config["embedding"]["tokenizer"])
    tokens = tokenizer.encode(text).ids
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i : i + chunk_size]
        chunks.append(tokenizer.decode(chunk))
        if i + chunk_size >= len(tokens):
            break
    return chunks


def enhance_query(query: str) -> list[str]:
    """
    增强查询
    Args:
        query (str): 原始查询

    Returns:
        list[str]: 增强后的查询列表
    """
    query = config["prompt"]["enhance"].format(query=query)
    logger.info(f"增强查询完整提示词: {query}")
    response = chat_client.chat.completions.create(
        model=config["chat"]["model"],
        messages=[{"role": "user", "content": query}],
        temperature=0.8,
        top_p=0.9,
    )
    answer = response.choices[0].message.content
    logger.info(f"增强查询结果: {answer}")
    json_code_block = re.search(r"```json(.*?)```", answer, re.DOTALL)
    if json_code_block:
        json_str = json_code_block.group(1).strip()
        try:
            enhanced_queries = json.loads(json_str)
            if isinstance(enhanced_queries, list) and all(isinstance(q, str) for q in enhanced_queries):
                return enhanced_queries
        except json.JSONDecodeError:
            logger.error("无法解析增强查询的JSON，返回原始查询")
            pass
    return [query]


def get_full_prompt(query: str, knowledge: str) -> str:
    """
    根据查询和知识生成完整提示词

    Args:
        query (str): 用户查询
        knowledge (str): 相关知识

    Returns:
        str: 增强的提示词
    """
    return config["prompt"]["ask"].format(query=query, knowledge=knowledge)


if __name__ == "__main__":
    # 测试enhance_query
    print(enhance_query("这篇论文的作者是谁？"))
