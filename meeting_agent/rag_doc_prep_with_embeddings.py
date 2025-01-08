#Usign langchain for the vector DB 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocPrep:
    _instance = None
    _meeting = None
    _embeddings = None
    _text_splitter = None
    _vectore_store = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocPrep, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, meeting, embeddings):
        if self._meeting is None:
            self._meeting = meeting
        if self._text_splitter is None:
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                add_start_index=True,
                strip_whitespace=True,
                separators=["\n\n", "\n", ".", " ", ""]
            )
        if self._embeddings is None :
            self._embeddings = embeddings
        if self._vectore_store is None :
            self._vectore_store = InMemoryVectorStore(self._embeddings)
            
    def prepare_document(self, transcript_mock):
        transcript_doc = Document(page_content=transcript_mock, metadata=self._meeting)
        docs = self._text_splitter.split_documents([transcript_doc])
        return docs
    
    def add_to_vector_store(self, docs):
        ids = self.vector_store.add_documents(documents=docs)
        return ids
   
#Example of code to use the class                  
"""
transcript_mock = ""
The project timeline needs to be adjusted for the next quarter. Alice will be working on the budget review.
Bob is responsible for the new system deployment, and Charlie will focus on the marketing strategy.
The next meeting is scheduled for the following week to discuss the next steps.
""
meeting = {
            "name": "first meeting",
            "timestamp": "2025-01-07T10:00:00"
            }
doc_prep_instance = DocPrep(meeting, embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))

prepared_docs = doc_prep_instance.prepare_document(transcript_mock)
doc_prep_instance.add_to_vector_store(prepared_docs)

for doc in prepared_docs:
    print(doc.page_content)
"""


