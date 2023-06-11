# llm-vec-db

Vector database applications using embedding vectors from LLM.

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
k create namespace weaviate
# change namespace
kcn weaviate
# install weaviate
helm upgrade -i weaviate weaviate/weaviate -n weaviate -f ./helm/values.yaml
```

## Installation

[Install Micromamba](https://mamba.readthedocs.io/en/latest/installation.html#homebrew) if you haven't already.

Create a Conda environment for this project and install dependencies:

```bash
micromamba env create -f environment.yml --yes
```

## Usage

- set `.env` as follows

  ```bash
  OPENAI_API_KEY=<get https://platform.openai.com/account/api-keys>
  WEAVIATE_URL=http://localhost:8080
  ```

- port forward Weaviate to http://localhost:8080

  ```bash
  k port-forward svc/weaviate -n weaviate 8080:80
  ```

- run the example indexer `gitbook_indexer.py`

  ```bash
  python gitbook_indexer.py
  ```
