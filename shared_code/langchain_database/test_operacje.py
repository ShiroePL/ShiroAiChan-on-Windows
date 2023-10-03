from langchain.vectorstores import Chroma

from langchain.embeddings import HuggingFaceInstructEmbeddings


def search_personal_chroma_db(query):
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                        model_kwargs={"device": "cpu"})
    persist_directory = './langchain_database/db_shiro'
    embedding = instructor_embeddings

    vectordb2 = Chroma(persist_directory=persist_directory, 
                    embedding_function=embedding,
                    collection_name="personal"
                    )
    #query = "what plant i like?"
    retriever = vectordb2.similarity_search(query=query, k=4)
    
    #peekniete = vectordb2.similarity_search(query=query, k=1)
    #peekniete = vectordb2._collection.get(where_document ={"$contains": "rxt 2070"})
    
   
    return retriever
# answer = search_chroma_db("do i seem to be crazy about anime and light novels?")

# print(answer)

# answer = search_personal_chroma_db("delete thing about plants")
# print(answer)

if __name__ == "__main__":
    pass