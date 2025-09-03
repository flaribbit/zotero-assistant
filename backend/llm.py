from llama_index.core.embeddings import BaseEmbedding
from llama_index.llms.siliconflow import SiliconFlow
from typing import Any, List
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


# https://docs.llamaindex.ai/en/stable/examples/embeddings/custom_embeddings/
class InstructorEmbeddings(BaseEmbedding):
    """使用SiliconFlow的嵌入模型需要继承BaseEmbedding类自己实现"""

    def __init__(
        self,
        instructor_model_name: str = "Qwen/Qwen3-Embedding-0.6B",
        instruction: str = "Represent a document for semantic search:",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._instructor_model_name = instructor_model_name
        self._instruction = instruction

    @classmethod
    def class_name(cls) -> str:
        return "instructor"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = get_text_embedding([self._instruction + query])
        return embeddings[0]["embedding"]

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = get_text_embedding([[self._instruction + text]])
        return embeddings[0]["embedding"]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = get_text_embedding([self._instruction + text for text in texts])
        return [e["embedding"] for e in embeddings]


def test_llama_index():
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.core import Settings

    llm = SiliconFlow(api_key=config["siliconflow"]["api_key"], model="Pro/deepseek-ai/DeepSeek-V3")
    documents = SimpleDirectoryReader("./data").load_data()
    embed_model = InstructorEmbeddings()
    Settings.embed_model = embed_model
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    while True:
        response = index.as_query_engine(llm=llm, streaming=True, verbose=True).query(input("\n>>> "))
        response.print_response_stream()
