import datetime
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader
from InstructorEmbedding import INSTRUCTOR
from langchain.embeddings import HuggingFaceInstructEmbeddings


# Load and process the text files
#loader = PyPDFLoader('mydata/book1.pdf')
#loader = PyPDFLoader('mydata/misaki.pdf')
#loader = DirectoryLoader('mydata', glob="./*.pdf", loader_cls=PyPDFLoader)

#documents = loader.load()


# from langchain.document_loaders import UnstructuredPDFLoader
# loader = UnstructuredPDFLoader("mydata/...pdf")
# documents = loader.load()

#len(documents)

#splitting the text into
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
# texts = text_splitter.split_documents(documents)
# len(texts)

#texts[1]


from langchain.embeddings import HuggingFaceInstructEmbeddings

instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                      model_kwargs={"device": "cpu"})


# Embed and store the texts
# Supplying a persist_directory will store the embeddings on disk
persist_directory = './langchain_database/db_shiro'

## Here is the nmew embeddings being used
embedding = instructor_embeddings

# vectordb = Chroma.from_documents(documents=texts, 
#                                  embedding=embedding,
#                                  collection_name="misaki",
#                                  persist_directory=persist_directory)

texts1 = ["today i have to go to the market and buy stuff to my bathroom"]
vectordb = Chroma.from_texts(texts=texts1, 
                                 embedding=embedding,
                                 metadatas=[{"added_date": datetime.datetime.now().isoformat()}],
                                 collection_name="personal",
                                 persist_directory=persist_directory)

# persiste the db to disk
vectordb.persist()


if __name__ == "__main__":
   pass