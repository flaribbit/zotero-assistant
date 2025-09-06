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


def enhance_query(query: str) -> list[str]:
    """
    增强查询
    Args:
        query (str): 原始查询

    Returns:
        list[str]: 增强后的查询列表
    """
    # TODO：实现查询增强逻辑
    
    enhanced_queries = [query]  # 原始查询始终包含在内
    max_queries = 10
    
    try:
        # 1. 使用LLM生成查询变体和相关问题
        enhanced_queries.extend(_generate_query_variants(query))
        
        # 2. 添加同义词和相关词扩展
        enhanced_queries.extend(_expand_with_synonyms(query))
        
        # 3. 去重并限制数量
        unique_queries = []
        seen = set()
        for q in enhanced_queries:
            q_clean = q.strip().lower()
            if q_clean and q_clean not in seen:
                unique_queries.append(q)
                seen.add(q_clean)
                if len(unique_queries) >= max_queries:
                    break
        
        return unique_queries
    except Exception as e:
        # 如果增强失败，返回原始查询
        print(f"Query enhancement failed: {e}")
        return [query]
def _generate_query_variants(query: str) -> list[str]:
    """
    使用LLM生成查询变体

    Args:
        query (str): 原始查询

    Returns:
        list[str]: 查询变体列表
    """
    try:
        prompt = f"""
基于用户的查询，生成2-3个相关的查询变体，用于改善文献搜索效果。
变体应该：
1. 使用不同的表达方式
2. 包含相关的学术术语
3. 从不同角度描述同一问题

原始查询：{query}

请直接返回查询变体，每行一个，不要编号或其他格式：
"""
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct", 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        variants = response.choices[0].message.content.strip().split('\n')
        return [v.strip() for v in variants if v.strip()]
    
    except Exception as e:
        print(f"Failed to generate query variants: {e}")
        return []


def _expand_with_synonyms(query: str) -> list[str]:
    """
    使用同义词和相关词扩展查询

    Args:
        query (str): 原始查询

    Returns:
        list[str]: 扩展后的查询列表
    """
    try:
        prompt = f"""
分析以下查询中的关键词，提供1-2个使用同义词或相关学术术语的查询版本。
保持查询的核心含义不变，但使用不同的词汇表达。

原始查询：{query}

请直接返回扩展查询，每行一个：
"""
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        
        expansions = response.choices[0].message.content.strip().split('\n')
        return [exp.strip() for exp in expansions if exp.strip()]
    
    except Exception as e:
        print(f"Failed to expand with synonyms: {e}")
        return []


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