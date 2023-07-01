from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader
from InstructorEmbedding import INSTRUCTOR
from langchain.embeddings import HuggingFaceInstructEmbeddings


def search_chroma_db(query):
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cpu"})
    persist_directory = './langchain_database/db_na_large_viola1'
    embedding = instructor_embeddings

    vectordb2 = Chroma(persist_directory=persist_directory, 
                    embedding_function=embedding,
                    )

    retriever = vectordb2.as_retriever(search_kwargs={"k": 7})

    # Set up the turbo LLM
    turbo_llm = ChatOpenAI(
        temperature=1,
        model_name='gpt-3.5-turbo-16k'
    )

    # create the chain to answer questions 
    qa_chain = RetrievalQA.from_chain_type(llm=turbo_llm, 
                                    chain_type="stuff", 
                                    retriever=retriever, 
                                    return_source_documents=True)

    ## Cite sources
    def process_llm_response(llm_response):
        #print(llm_response['result'])
        #print('full llm response:' + str(llm_response))
        print('\n\nSources:')
        for source in llm_response["source_documents"]:
            print(source.metadata['source'])
        return llm_response['result']    
    llm_response = qa_chain(query)
    answer_from_database = process_llm_response(llm_response)
    #print(answer_from_database)
    return answer_from_database

#search_chroma_db("Why Viola had stomach ache? What did mr fisalis to ease her pain?")