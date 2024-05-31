from typing import AsyncGenerator, Optional

import bentoml
from annotated_types import Ge, Le
from typing_extensions import Annotated
from openai import AsyncOpenAI


MAX_TOKENS = 1024
SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""


MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
BENTO_MODEL_TAG = MODEL_ID.lower().replace("/", "--")


@bentoml.service(
    name="bentotgi-llama3-8b-insruct-service",
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
        import docker

        client = docker.from_env()
        target_dir = self.bento_model_ref.path
        container = client.containers.run(
            image="ghcr.io/huggingface/text-generation-inference:2.0",
            runtime="nvidia",
            shm_size="1g",
            volumes={target_dir: {"bind": "/models", "mode": "ro"}},
            ports={"80/tcp": 8080},
            command=f"--model-id /models",
            detach=True,
        )
        print("Container started with ID:", container.id)

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
        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        messages.append({"role": "user", "content": prompt})
        stream = await self.client.chat.completions.create(
            model="tgi",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
        )

        async for chunk in stream:
            yield chunk.choices[0].delta.content
