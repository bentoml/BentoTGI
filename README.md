<div align="center">
    <h1 align="center">Self-host LLMs with TGI and BentoML</h1>
</div>

This is a BentoML example project, showing you how to serve and deploy open-source Large Language Models using [Hugging Face TGI](https://github.com/huggingface/text-generation-inference), a toolkit that enables high-performance text generation for LLMs.

See [here](https://github.com/bentoml/BentoML/tree/main/examples) for a full list of BentoML example projects.

💡 This example is served as a basis for advanced code customization, such as custom model, inference logic or LMDeploy options. For simple LLM hosting with OpenAI compatible endpoint without writing any code, see [OpenLLM](https://github.com/bentoml/OpenLLM).

## Prerequisites

- You have installed Python 3.8+ and `pip`. See the [Python downloads page](https://www.python.org/downloads/) to learn more.
- You have a basic understanding of key concepts in BentoML, such as Services. We recommend you read [Quickstart](https://docs.bentoml.com/en/1.2/get-started/quickstart.html) first.
- If you want to test the Service locally, you need a Nvidia GPU with at least 20G VRAM.
- You have installed Docker as this example depends on a base Docker image `ghcr.io/huggingface/text-generation-inference:2.0.4` to set up TGI.
- This example uses Llama 3. Make sure you have [gained access to the model](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct).
- (Optional) We recommend you create a virtual environment for dependency isolation for this project. See the [Conda documentation](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) or the [Python documentation](https://docs.python.org/3/library/venv.html) for details.

## Set up the environment

Clone the repo.

```bash
git clone https://github.com/bentoml/BentoTGI.git
cd BentoTGI
```

Make sure you are in the `BentoTGI` directory and mount it from your host machine (`${PWD}`) into a Docker container at `/BentoTGI`. This means that the files and folders in the current directory are available inside the container at the `/BentoTGI`.

```bash
docker run --runtime=nvidia --gpus all -v ${PWD}:/BentoTGI -v ~/bentoml:/root/bentoml -p 3000:3000 --entrypoint /bin/bash -it --workdir /BentoTGI ghcr.io/huggingface/text-generation-inference:2.0.4
```

Install dependencies.

```bash
cd llama-3-8b-instruct
pip install -r requirements.txt
```

## Download the model

Run the script to download Llama 3 to the BentoML [Model Store](https://docs.bentoml.com/en/latest/guides/model-store.html).

```bash
python import_model.py
```

## Run the BentoML Service

We have defined a BentoML Service in `service.py`. Run `bentoml serve` in your project directory to start the Service.

```bash
$ bentoml serve .
2024-06-06T10:31:45+0000 [INFO] [cli] Starting production HTTP BentoServer from "service:TGI" listening on http://localhost:3000 (Press CTRL+C to quit)
```

The server is now active at [http://localhost:3000](http://localhost:3000/). You can interact with it using the Swagger UI or in other different ways.

<details>

<summary>CURL</summary>

```bash
curl -X 'POST' \
  'http://localhost:3000/generate' \
  -H 'accept: text/event-stream' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "Explain superconductors like I'\''m five years old",
  "max_tokens": 1024
}'
```

</details>

<details>

<summary>Python client</summary>

```python
import bentoml

with bentoml.SyncHTTPClient("http://localhost:3000") as client:
    response_generator = client.generate(
        prompt="Explain superconductors like I'm five years old",
        max_tokens=1024
    )
    for response in response_generator:
        print(response, end='')
```

</details>

## Deploy to BentoCloud

After the Service is ready, you can deploy the application to BentoCloud for better management and scalability. [Sign up](https://www.bentoml.com/) if you haven't got a BentoCloud account.

Make sure you have [logged in to BentoCloud](https://docs.bentoml.com/en/latest/bentocloud/how-tos/manage-access-token.html), then run the following command to deploy it.

```bash
bentoml deploy .
```

Once the application is up and running on BentoCloud, you can access it via the exposed URL.

**Note**: For custom deployment in your own infrastructure, use [BentoML to generate an OCI-compliant image](https://docs.bentoml.com/en/latest/guides/containerization.html).