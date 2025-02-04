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






