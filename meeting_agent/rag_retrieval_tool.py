from smolagents import Tool
from pinecone.grpc import PineconeGRPC as pinecone

class PineconeRetrieverTool(Tool):
    name = "pinecone_retriever"
    description = "Uses Pinecone's vector-based retrieval to find the most relevant parts of meeting transcription based on the query."
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        }
    }
    output_type = "string"

    def __init__(self, index_name, embedding_model, pc, top_k=3, **kwargs):
        """
        Initialize the PineconeRetrieverTool.

        :param index_name: Name of the Pinecone index to query.
        :param embedding_model: Model to use for generating query embeddings.
        :param namespace: Namespace to limit the search scope (default is 'default').
        :param top_k: Number of top results to retrieve (default is 3).
        """
        super().__init__(**kwargs)
        self.index = pinecone.Index(index_name)
        self.embedding_model = embedding_model
        self.namespace = index_name
        self.top_k = top_k
        self.pc = pc

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"
        query_embedding = self.pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={"input_type": "query"}
        )[0].values

        results = self.index.query(
            namespace=self.namespace,
            vector=query_embedding,
            top_k=self.top_k,
            include_values=False,
            include_metadata=True
        )

        if not results.matches:
            return "No relevant documents found."

        return "\nRetrieved documents:\n" + "\n".join(
            [
                f"\n\n===== Document {i+1} =====\nMetadata: {match.metadata}\nScore: {match.score}"
                for i, match in enumerate(results.matches)
            ]
        )
