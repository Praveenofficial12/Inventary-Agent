from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.chroma import get_chroma_client
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.embeddings = self._load_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def _load_embeddings(self):
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except ImportError:
            pass
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"HuggingFace embeddings unavailable: {e}. RAG disabled.")
            return None

    def _get_vectorstore(self, collection_name="company_policies"):
        if self.embeddings is None:
            return None
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma
        client = get_chroma_client()
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )

    async def ingest_text(self, text, metadata, collection_name="company_policies"):
        vectorstore = self._get_vectorstore(collection_name)
        if vectorstore is None:
            return 0
        chunks = self.text_splitter.split_text(text)
        vectorstore.add_texts(texts=chunks, metadatas=[metadata] * len(chunks))
        return len(chunks)

    async def query(self, query_text, k=5, threshold=0.3):
        vectorstore = self._get_vectorstore()
        if vectorstore is None:
            return []
        try:
            results = vectorstore.similarity_search_with_relevance_scores(query_text, k=k)
            filtered_results = [doc for doc, score in results if score >= threshold]
            return filtered_results
        except Exception as e:
            logger.warning(f"RAG query failed: {e}")
            return []
