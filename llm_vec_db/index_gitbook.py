from dotenv import load_dotenv
from langchain.document_loaders import GitbookLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Weaviate
from loguru import logger
import os
import pydash as ps
import time
import weaviate

load_dotenv()  # set `OPENAI_API_KEY, WEAVIATE_URL` in .env file
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
ATTRIBUTES = ['text', 'source', 'title']  # attributes used by langchain documents


def get_db(index_name: str) -> Weaviate:
    embeddings = OpenAIEmbeddings(max_retries=15)  # Langchain has built in retry; rate limit is per minute, built in retry is 4s, so 60/4 = 15 tries
    client = weaviate.Client(url=WEAVIATE_URL)
    db = Weaviate(client=client, index_name=index_name, attributes=ATTRIBUTES, embedding=embeddings, text_key='text')
    return db


def run(gitbook_url: str, index_name: str):
    logger.info(f'Indexing {gitbook_url} into Weaviate index {index_name}')
    db = get_db(index_name)
    loader = GitbookLoader(gitbook_url, load_all_paths=True)
    docs = loader.load()  # crawl all pages and load into Documents object
    # safeguard and split so each document is less than 1000 tokens
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(docs)

    # TODO OpenAI API has rate limit but langchain's internal retry is unreliable and doesn't return error for control. Need to fix; can monkeypatch langchain.embeddings.openai.embed_with_retry
    chunks = ps.chunk(docs, 20)
    for idx, c_docs in enumerate(chunks):
        logger.info(f'Indexing chunk {idx+1} of {len(chunks)}')
        db.add_documents(c_docs)
        time.sleep(20)

    logger.info('Indexing complete')


if __name__ == '__main__':
    gitbook_url = "https://slm-lab.gitbook.io/slm-lab/"
    index_name = 'SLMLab_001'  # weaviate index format is <index_name>_<index_version>
    run(gitbook_url, index_name)
