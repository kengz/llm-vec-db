from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Weaviate
from llm_vec_db.index_gitbook import get_db
from loguru import logger

# do not use from_documents() from Langchain doc because it recreates index per run


def run(query: str, db: Weaviate, k: int = 2):
    '''QnA query using top-k relevant documents indexed in vector db'''
    logger.info(f'Query: {query}')
    sim_docs = db.similarity_search(query, by_text=False, k=k)
    logger.info(f'Similarity search results: {sim_docs}')
    logger.info(f'First result content: {sim_docs[0].page_content}, metadata: {sim_docs[0].metadata}')

    sim_score_docs = db.similarity_search_with_score(query, by_text=False, k=k)
    logger.info(f'Similarity search with score results: {sim_score_docs}')

    # NOTE don't use MMR, will send large prompt with more tokens
    retriever = db.as_retriever(search_kwargs={'k': k})
    sim_ret_docs = retriever.get_relevant_documents(query)
    logger.info(f'Similarity search results from retriever: {sim_ret_docs}')

    logger.info('Calling LLM')
    llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo')
    chain = RetrievalQAWithSourcesChain.from_chain_type(llm, chain_type="stuff", retriever=retriever)

    with get_openai_callback() as cb:
        res = chain({"question": query})
        logger.info(f'result: {res}')
        logger.info(f'API usage info: {cb}')
    logger.info(res['answer'])
    # TODO error, getting: ValueError: Document prompt requires documents to have metadata variables: ['source']. Received document with missing metadata: ['source'].

    # TODO handle rate limit with throttle
    # TODO implement cache
    # TODO implement aim

    # from redis import Redis
    # from langchain.cache import RedisCache

    # langchain.llm_cache = RedisCache(redis_=Redis())


if __name__ == '__main__':
    index_name = 'SLMLab_001'  # weaviate index format is <index_name>_<index_version>
    db = get_db(index_name=index_name)
    k = 2

    query = "What is SLM Lab and what does it do?"
    query = "What deep RL algorithms are implemented in SLM Lab?"

    run(query=query, db=db, k=k)
