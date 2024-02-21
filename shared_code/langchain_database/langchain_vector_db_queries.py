from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import datetime
from .. import api_keys
#import api_keyss

def search_db_with_llm_response(query):
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cpu"})
    persist_directory = 'shared_code/langchain_database/shiro_vector_db'
    embedding = instructor_embeddings

    vectordb2 = Chroma(persist_directory=persist_directory, 
                    embedding_function=embedding,
                    collection_name="pdfs"
                    )

        # Get the count of documents in the collection
    document_count = vectordb2._collection.count()
        # Set k to the lesser of 4 or the document count
    k_value = min(4, document_count)
    
    retriever = vectordb2.as_retriever(search_kwargs={"k": k_value})
        # Set up the turbo LLM
    turbo_llm = ChatOpenAI(
        temperature=1,
        model_name='gpt-3.5-turbo'
    )
    # create the chain to answer questions 
    qa_chain = RetrievalQA.from_chain_type(llm=turbo_llm, 
                                    chain_type="stuff", 
                                    retriever=retriever, 
                                    return_source_documents=True)

    ## Cite sources
    def process_llm_response(llm_response):
        #print(llm_response['result'])
        print('full llm response:' + str(llm_response))
        print('\n\nSources:')
        # for source in llm_response["source_documents"]:
        #     print(source.metadata['source'])
        
        return llm_response['result']    
    llm_response = qa_chain(query)
    print(str(llm_response))
    answer_from_database = process_llm_response(llm_response)
    #print(answer_from_database)
    return answer_from_database

def search_db_with_chroma_buildin_search(query):
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cpu"})
    persist_directory = 'shared_code/langchain_database/shiro_vector_db'
    embedding = instructor_embeddings

    vectordb2 = Chroma(persist_directory=persist_directory, 
                    embedding_function=embedding,
                    collection_name="pdfs"
                    )
    
    # Get the count of documents in the collection
    document_count = vectordb2._collection.count()
    
    # Set k to the lesser of 4 or the document count
    k_value = min(4, document_count)
    
    retriever = vectordb2.similarity_search(query=query, k=k_value)
    
    return retriever



# def show_collections(): $ for testing
#     instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
#                                                         model_kwargs={"device": "cpu"})
#     persist_directory = 'shared_code/langchain_database/shiro_vector_db'
#     embedding = instructor_embeddings

#     vectordb2 = Chroma(persist_directory=persist_directory, 
#                     embedding_function=embedding,
#                     collection_name="pdfs"
#                     )
   

#     print("There are", vectordb2._collection.count(), "in the collection")
#     # Fetch all data; you might want to set a limit or implement pagination for large collections
#     get_result = vectordb2.get(limit=None)  
    
#     unique_ids = set()  # Initialize an empty set to store unique IDs
    
    

#     print("There are", len(get_result), "chunks in the collection.")
#     print("Unique IDs in the collection are:", unique_ids)

#     print(type(get_result))
#     print("pront_resutl:" + str(get_result))

#     return vectordb2._collection.count()

def save_to_db(type: str, query: str = None, name_of_pdf: str = None):
    """type = 'pdf' or 'text'

    'name_of_pdf' is name of file you want to save to db"""

    path_to_langchain = api_keys.path_to_langchain
        # Supplying a persist_directory will store the embeddings on disk
    persist_directory = 'shared_code/langchain_database/shiro_vector_db'

        # Load and process the pdf file
    if type == "pdf":
        loader = PyPDFLoader(path_to_langchain  + f'pdfs\\{name_of_pdf}.pdf')
        documents = loader.load()
        len(documents)
            #splitting the text into
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
        texts = text_splitter.split_documents(documents)
        len(texts)
        
    #loader = DirectoryLoader('mydata', glob="./*.pdf", loader_cls=PyPDFLoader)

    # loader = UnstructuredPDFLoader("mydata/...pdf")

        # Here we use the HuggingFaceInstructEmbeddings to embedd the text/pdf
    if type == "pdf":
        
        
        instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cuda"})
    else: # not used now
        instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cpu"})

    if type == "pdf":
        vectordb = Chroma.from_documents(documents=texts, 
                                    embedding=instructor_embeddings,
                                    collection_name="pdfs",
                                    persist_directory=persist_directory)
    else: # not used now
        vectordb = Chroma.from_texts(texts=[query], 
                                    embedding=instructor_embeddings,
                                    metadatas=[{"added_date": datetime.datetime.now().isoformat()}],
                                    collection_name="texts",
                                    persist_directory=persist_directory)

        # persiste the db to disk
    vectordb.persist()

    #             !!  # to use it again, load it from disk !! 
        # Now we can load the persisted database from disk, and use it as normal. 
    # vectordb = Chroma(persist_directory=persist_directory, 
    #                 embedding_function=embedding)

if __name__ == "__main__":
    # answer = search_db_with_llm_response("of what misaka is fond of?")
    # answer = search_db_with_chroma_buildin_search("delete thing about plants")
    # print(answer)
    pass