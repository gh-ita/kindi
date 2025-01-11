from smolagents import Tool
from pinecone.grpc import PineconeGRPC as pinecone

class PineconeRecapRetrieverTool(Tool):
    name = "pinecone_recap_retriever"
    description = (
        "Retrieves relevant chunks of meeting transcriptions from the Pinecone DB "
        "based on a given meeting name (used as the namespace) and query."
    )
    inputs = {
        "meeting_name": {
            "type": "string",
            "description": "The name of the meeting (used as the index in Pinecone).",
        },
        "query": {
            "type": "string",
            "description": "The query to search for. Should be semantically related to the target chunks.",
        }
    }
    output_type = "string"

    def __init__(self, index_name, embedding_model,pc, top_k=5, **kwargs):
        """
        Initialize the PineconeRecapRetrieverTool.

        :param index_name: The Pinecone index to query.
        :param embedding_model: The embedding model to generate query embeddings.
        :param top_k: Number of top results to retrieve (default is 5).
        """
        super().__init__(**kwargs)
        self.index = pc.Index(index_name)
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.pc = pc

    def forward(self, meeting_name: str, query: str) -> str:
        assert isinstance(meeting_name, str) and meeting_name.strip(), "Meeting name must be a valid non-empty string."
        assert isinstance(query, str) and query.strip(), "Query must be a valid non-empty string."

        query_embedding = self.oc.inference.embed(
            model=self.embedding_model,
            inputs=[query],
            parameters={"input_type": "query"}
        )[0].values

        results = self.index.query(
            namespace=meeting_name,
            vector=query_embedding,
            top_k=self.top_k,
            include_values=False,
            include_metadata=True
        )

        if not results.matches:
            return f"No relevant chunks found for meeting '{meeting_name}'."

        return "\nRetrieved documents:\n" + "\n".join(
            [
                f"\n\n===== Chunk {i+1} =====\nText: {match.metadata.get('text', 'No text available')}\nScore: {match.score}"
                for i, match in enumerate(results.matches)
            ]
        )

    

