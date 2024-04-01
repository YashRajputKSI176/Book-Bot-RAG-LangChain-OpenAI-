from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.app_init import app
from app.app_init import DATA_PATH, PROMPT_TEMPLATE, keyspace, session, table_name
from flask import jsonify
from langchain_community.vectorstores import Cassandra

import os
import shutil


def create_doc_vectors():
    try:
        generate_data_store()
        return "success"
    except Exception as e:
        app.logger.info(str(e))
        raise e


def generate_data_store():
    print("Hello 1")
    documents = load_documents()
    chunks = split_text(documents)
    save_to_casendra(chunks)


def load_documents():
    print("Hello 2")
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf")
    documents = loader.load()
    return documents


def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    app.logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    return chunks


def save_to_casendra(chunks):
    # Clear out the database first.

    embeddings = OpenAIEmbeddings(openai_api_key='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')
    vstore = Cassandra(
        embedding=embeddings,
        table_name=table_name,
        session=session, keyspace=keyspace  # Uncomment on older versions of LangChain
    )
    print(f"Documents from PDF: {len(chunks)}.")
    inserted_ids_from_pdf = vstore.add_documents(chunks)
    print(f"Inserted {len(inserted_ids_from_pdf)} documents.")


def input_query(query):
    query_text = query
    embeddings = OpenAIEmbeddings(openai_api_key='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')
    db = Cassandra(
        embedding=embeddings,
        table_name=table_name,
        session=session, keyspace=keyspace  # Uncomment on older versions of LangChain
    )

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        app.logger.info(f"Unable to find matching result")
        return jsonify({'status': 'failed'})

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI(openai_api_key='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')
    response_text = model.predict(prompt)
    if response_text:
        return response_text
    else:
        return "failed"
