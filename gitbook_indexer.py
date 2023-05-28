from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import GitbookLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Weaviate
import openai
import os
import pydash as ps
import weaviate

load_dotenv()  # set `OPENAI_API_KEY, WEAVIATE_URL` in .env file

client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))
index_name = 'SLMLab_001'  # weaviate index format is <index_name>_<index_version>
attributes = ['text', 'source', 'title']
embeddings = OpenAIEmbeddings(max_retries=15)  # Langchain has built in retry; rate limit is per minute, built in retry is 4s, so 60/4 = 15 tries
db = Weaviate(client=client, index_name=index_name, attributes=attributes, embedding=embeddings, text_key='text')

loader = GitbookLoader(
    "https://slm-lab.gitbook.io/slm-lab/",
    load_all_paths=True,
)
docs = loader.load()

text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(docs)

for c_docs in ps.chunk(docs, 20):
    db.add_documents(c_docs)

# db = Weaviate.from_documents(docs, embeddings, weaviate_url=os.getenv('WEAVIATE_URL'), index_name='SLMLab_4', by_text=False)

query = "What is SLM Lab and what does it do?"
query = "What deep RL algorithms are implemented in SLM Lab?"
res_docs = db.similarity_search(query, by_text=False, k=2)
res_docs[0].page_content
res_docs[0].metadata

sim_res_docs = db.similarity_search_with_score(query, by_text=False)
sim_res_docs

# NOTE don't use MMR, will send large prompt with more tokens
retriever = db.as_retriever(search_kwargs={'k': 2})
retriever.get_relevant_documents(query)

llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo')
chain = RetrievalQAWithSourcesChain.from_chain_type(llm, chain_type="stuff", retriever=retriever)

with get_openai_callback() as cb:
    res = chain(
        {"question": query},
    )
    res
    print(cb)
print(res['answer'])
# TODO error, getting: ValueError: Document prompt requires documents to have metadata variables: ['source']. Received document with missing metadata: ['source'].

# TODO handle rate limit with throttle
# TODO implement cache
# TODO implement aim

# from redis import Redis
# from langchain.cache import RedisCache

# langchain.llm_cache = RedisCache(redis_=Redis())
