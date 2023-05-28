from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import GitbookLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Weaviate
import os
import weaviate

load_dotenv()  # set `OPENAI_API_KEY, WEAVIATE_URL` in .env file

client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))
index_name = 'SLMLab_5'  # weaviate index format is <index_name>_<index_version>
attributes = ['text', 'source', 'title']
embeddings = OpenAIEmbeddings()
db = Weaviate(client=client, index_name=index_name, attributes=attributes, embedding=embeddings, text_key='text')

loader = GitbookLoader(
    "https://slm-lab.gitbook.io/slm-lab/",
    # load_all_paths=True,
)
docs = loader.load()

text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(docs)

db.add_documents(docs)
# db = Weaviate.from_documents(docs, embeddings, weaviate_url=os.getenv('WEAVIATE_URL'), index_name='SLMLab_4', by_text=False)

query = "What is SLM Lab?"
res_docs = db.similarity_search(query, by_text=False)
res_docs[0].page_content
# TODO debug why metadata is missing. need to check weaviate directly
res_docs[0].metadata

sim_res_docs = db.similarity_search_with_score(query, by_text=False)
sim_res_docs

# NOTE don't use MMR, will send large prompt with more tokens
retriever = db.as_retriever()
# retriever.get_relevant_documents(query)[0]

llm = OpenAI(temperature=0.0)
chain = RetrievalQAWithSourcesChain.from_chain_type(llm, chain_type="stuff", retriever=retriever)

with get_openai_callback() as cb:
    res = chain(
        {"question": "What is SLM Lab?"},
    )
    res
    print(cb)
    # TODO error, getting: ValueError: Document prompt requires documents to have metadata variables: ['source']. Received document with missing metadata: ['source'].

# TODO implement cache
# TODO implement aim
