# services/azure_rag_query_service.py
from azure.search.documents.models import VectorizedQuery

class AzureRagQueryService:
    def __init__(self, settings, vector_store, openai_service):
        self.settings = settings
        self.vector_store = vector_store      # AzureVectorSearchService
        self.openai_service = openai_service  # AzureTextClassifierWrapper

    def query(self, query_text: str):
        """Executes the pure RAG semantic search and generation workflow."""
        print(f"Generating query embedding vector using: {self.settings.azure_openai_embedding_model}...")
        
        response = self.openai_service.client.embeddings.create(
            input=[query_text],
            model=self.settings.azure_openai_embedding_model
        )
        query_vector = response.data[0].embedding

        print(f"Searching Azure Vector Index: '{self.settings.azure_search_index}'...")
        vector_query = VectorizedQuery(
            vector=query_vector, 
            k_nearest_neighbors=3, 
            fields="vector"  # 🟢 Matches the "vector" key explicitly defined in your v4 spec
        )
        
        search_results = self.vector_store.client.search(
            search_text=query_text,
            vector_queries=[vector_query],
            top=3,
            select=["id", "text", "source", "topic"]  # 🟢 Aligns with the fields from your v4 spec
        )

        context_blocks = []
        for doc in search_results:
            text_data = doc.get("text", "")
            source_data = doc.get("source", "Unknown")
            if text_data:
                context_blocks.append(f"[Source: {source_data}]\n{text_data}")

        if not context_blocks:
            print("❌ No matching context found in the vector search index.")
            return

        context_str = "\n\n".join(context_blocks)

        print("Synthesizing context answer via OpenAI Chat completions...")
        system_msg = "You are an assistant answering questions using only the provided context blocks."
        user_msg = f"Context:\n{context_str}\n\nQuestion: {query_text}\n\nAnswer:"
        
        chat_res = self.openai_service.client.chat.completions.create(
            model=self.settings.azure_openai_model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.0
        )

        print("\n======================= RAG QUERY ANSWER =======================")
        print(chat_res.choices[0].message.content)
        print("================================================================\n")