# llm-vec-db

Vector database applications using embedding vectors from LLM.

> Work in progress

## Prerequisites

### OpenAI API

Get [OpenAI API key](https://platform.openai.com/account/api-keys)

### Deploy Weaviate

First, deploy [Weaviate](https://weaviate.io) through:

- [docker-compose](https://weaviate.io/developers/weaviate/installation/docker-compose): locally, but not recommended.
- [Kubernetes](https://weaviate.io/developers/weaviate/installation/kubernetes): on a kubernetes cluster, recommended, and fit for production.

> If you need a quick Kubernetes on your home lab, see [kengz/k0s-cluster](https://github.com/kengz/k0s-cluster). It also serves as reference for generic cloud Kubernetes cluster setup.

> Kubectl commands are long; below uses [zsh kubectl plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/kubectl).

Deploy using local values file and:

```bash
export OPENAI_API_KEY=<get from https://platform.openai.com/account/api-keys>
helm upgrade -i weaviate weaviate/weaviate -n weaviate --create-namespace -f ./helm/values.yaml --set modules.text2vec-openai.enabled=true,modules.text2vec-openai.apiKey=$OPENAI_API_KEY
```

Then port forward Weaviate `kubectl port-forward svc/weaviate -n weaviate 8080:80` and visit http://localhost:8080/v1/docs

## Installation

[Install Micromamba](https://mamba.readthedocs.io/en/latest/installation.html#homebrew) if you haven't already.

Create a Conda environment for this project and install dependencies:

```bash
micromamba env create -f environment.yml --yes
```

> Activate the environment with `micromamba activate llm` before running any Python commands below

## Usage

- set `.env` as follows

  ```bash
  OPENAI_API_KEY=<get from https://platform.openai.com/account/api-keys>
  WEAVIATE_URL=http://localhost:8080
  ```

- port forward Weaviate to http://localhost:8080

  ```bash
  kubectl port-forward svc/weaviate -n weaviate 8080:80
  ```

- run the example indexer [./llm_vec_db/index_gitbook.py](./llm_vec_db/index_gitbook.py)

  ```bash
  python llm_vec_db/index_gitbook.py
  ```
