#Usign langchain for the vector DB 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from os import getenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

# Initialize a Pinecone client with your API key

load_dotenv()
pinecone_api_key = getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

class DocPrep:
    _instance = None
    _meeting = None
    _text_splitter = None
    _vectore_store = None
    
    def __init__(self, meeting):
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

        if self._vectore_store is None:
            if not pc.has_index(self._meeting["name"]):
                pc.create_index(
                    name=meeting["name"],
                    dimension=1024,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws', 
                        region='us-east-1'
                    ) 
                ) 
            self._vectore_store = pc.Index(self._meeting["name"])
            
    def prepare_document(self, transcript_mock):
        transcript_doc = Document(page_content=transcript_mock, metadata=self._meeting)
        docs = self._text_splitter.split_documents([transcript_doc])
        chunked_data = []
        for i, doc in enumerate(docs):
            chunk_data = {
                "id": f"{i+1}", 
                "text": doc.page_content
            }
            chunked_data.append(chunk_data)

        return chunked_data

    def add_to_vector_store(self, docs, embeddings):
        records = []
        for d, e in zip(docs, embeddings):
            records.append({
                "id": d['id'],
                "values": e['values'],
                "metadata": {'text': d['text']}
            })

        self._vectore_store.upsert(
            vectors=records,
            namespace=self._meeting["name"]
        )
        
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


