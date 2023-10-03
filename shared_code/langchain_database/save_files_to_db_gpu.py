from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader
from InstructorEmbedding import INSTRUCTOR
from langchain.embeddings import HuggingFaceInstructEmbeddings
from .. import api_keys
path_to_langchain = api_keys.path_to_langchain
# Load and process the text files
#loader = PyPDFLoader('mydata/book1.pdf')
loader = PyPDFLoader(path_to_langchain  + 'mydata\\misaki.pdf')
#loader = DirectoryLoader('mydata', glob="./*.pdf", loader_cls=PyPDFLoader)

documents = loader.load()


# from langchain.document_loaders import UnstructuredPDFLoader
# loader = UnstructuredPDFLoader("mydata/...pdf")
# documents = loader.load()

len(documents)

#splitting the text into
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
texts = text_splitter.split_documents(documents)
len(texts)

#texts[1]


from langchain.embeddings import HuggingFaceInstructEmbeddings

instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", 
                                                      model_kwargs={"device": "cuda"})


# Embed and store the texts
# Supplying a persist_directory will store the embeddings on disk
persist_directory = 'db_testetstets'

## Here is the nmew embeddings being used
embedding = instructor_embeddings

vectordb = Chroma.from_documents(documents=texts, 
                                 embedding=embedding,
                                 collection_name="misaki",
                                 persist_directory=persist_directory)

# persiste the db to disk
vectordb.persist()
vectordb = None

# to use it again, load it from disk
# Now we can load the persisted database from disk, and use it as normal. 
vectordb = Chroma(persist_directory=persist_directory, 
                  embedding_function=embedding)

if __name__ == "__main__":
   pass