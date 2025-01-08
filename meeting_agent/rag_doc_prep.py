#Usign langchain for the vector DB 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocPrep:
    _instance = None
    _meeting = None
    _text_splitter = None
    def __new__(cls, meeting=None):
        if cls._instance is None:
            cls._instance = super(DocPrep, cls).__new__(cls)
            cls._instance._initialize(meeting) 
        return cls._instance
    def _initialize(self, meeting):
        if meeting:
            self._meeting = meeting
        else:
            self._meeting = {}
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            add_start_index=True,
            strip_whitespace=True,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    def prepare_document(self, transcript_mock):
        transcript_doc = Document(page_content=transcript_mock, metadata=self._meeting)
        docs = self._text_splitter.split_documents([transcript_doc])
        return docs



#Example of code to try the class
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
doc_prep_instance = DocPrep(meeting)

prepared_docs = doc_prep_instance.prepare_document(transcript_mock)

for doc in prepared_docs:
    print(doc.page_content)"""


