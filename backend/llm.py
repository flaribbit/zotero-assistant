from openai import OpenAI
from config import config

client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key=config["siliconflow"]["api_key"],
)


def get_text_embedding(text: str | list[str]):
    """Get text embedding from the model.

    Args:
        text (str): The input text to embed.

    Returns:
        list: The text embeddings.
    """
    response = client.embeddings.create(model="Qwen/Qwen3-Embedding-0.6B", input=text).model_dump()
    return response["data"]
