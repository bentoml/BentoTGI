from typing import AsyncGenerator, Optional

import bentoml
from annotated_types import Ge, Le
from openai import AsyncOpenAI
from typing_extensions import Annotated

MAX_TOKENS = 1024
SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""


MODEL_ID = "casperhansen/llama-3-70B-instruct-awq"
BENTO_MODEL_TAG = MODEL_ID.lower().replace("/", "--")


@bentoml.service(
    name="bentotgi-llama3-70B-insruct-service",
    traffic={
        "timeout": 300,
    },
    resources={
        "gpu": 1,
        "gpu_type": "nvidia-a100-80gb",
    },
)
class TGI:

    bento_model_ref = bentoml.models.get(BENTO_MODEL_TAG)

    def __init__(self) -> None:
        import subprocess

        target_dir = self.bento_model_ref.path
        command = f"text-generation-launcher --model-id {target_dir} -p 8080"
        subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        self.client = AsyncOpenAI(
            base_url="http://localhost:8080/v1", api_key="not needed for a local LLM"
        )

    @bentoml.api
    async def generate(
        self,
        prompt: str = "Explain superconductors in plain English",
        system_prompt: Optional[str] = SYSTEM_PROMPT,
        max_tokens: Annotated[int, Ge(128), Le(MAX_TOKENS)] = MAX_TOKENS,
    ) -> AsyncGenerator[str, None]:
        messages = (
            [{"role": "system", "content": system_prompt}] if system_prompt else []
        )
        messages.append({"role": "user", "content": prompt})
        stream = await self.client.chat.completions.create(
            model="tgi",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
        )

        async for chunk in stream:
            yield chunk.choices[0].delta.content
