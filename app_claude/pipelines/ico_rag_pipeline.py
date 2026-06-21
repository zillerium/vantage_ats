import json
from pathlib import Path

class ICORagPipeline:

    def __init__(
        self,
        settings,
        vector_store,        # Injected AzureVectorSearchService
        openai_service,      # Injected AzureOpenAIService (or wrapper) to generate embeddings
        file_reader,
        file_mover,
        txt_input_dir,
        txt_processed_dir,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.settings = settings
        self.vector_store = vector_store
        self.openai_service = openai_service
        self.file_reader = file_reader
        self.file_mover = file_mover
        self.txt_input_dir = txt_input_dir
        self.txt_processed_dir = txt_processed_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_all_files(self):
        input_path = Path(self.txt_input_dir)
        txt_files = list(input_path.glob("*.txt"))
        
        print(f"\n📂 Found {len(txt_files)} ICO documents to vectorize into Azure Vector DB.")

        for index, file_path in enumerate(txt_files, 1):
            print("\n" + "=" * 70)
            print(f"🧠 Chunking & Indexing ({index}/{len(txt_files)}): {file_path.name}")
            self._process_single_rag(file_path)

        print("\n🎉 ICO RAG database ingestion finished successfully.")

    def _process_single_rag(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text_str = f.read()

            chunks = self._chunk_text(raw_text_str)
            print(f"   ✂️ Generated {len(chunks)} text chunks.")

            for i, chunk in enumerate(chunks, 1):
                chunk_id = f"{file_path.stem}_chunk_{i}"
                
                # Compute vector matrix using Azure OpenAI API embeddings deployment
                response = self.openai_service.client.embeddings.create(
                    input=[chunk],
                    model="text-embedding-3-small"
                )
                embedding_vector = response.data[0].embedding

                # Push directly into the true Azure Vector Store
                self.vector_store.insert_vector_chunk(
                    document_id=file_path.stem,
                    chunk_id=chunk_id,
                    text_content=chunk,
                    vector=embedding_vector
                )

            print(f"   ✅ Vector store indexed {len(chunks)} elements successfully.")

        except Exception as e:
            print(f"❌ Failed to execute Vector DB update for file {file_path.name}: {e}")
            return

        try:
            destination_dir = Path(self.txt_processed_dir)
            destination_dir.mkdir(parents=True, exist_ok=True)
            self.file_mover.move_file(file_path, str(destination_dir))
            print(f"📦 Archived source text file.")
        except Exception as e:
            print(f"❌ Failed to archive file: {e}")

    def _chunk_text(self, text: str) -> list:
        """Sliding-window word chunker."""
        chunks = []
        words = text.split()
        word_size = self.chunk_size // 5 
        word_overlap = self.chunk_overlap // 5
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + word_size]
            chunks.append(" ".join(chunk_words))
            i += (word_size - word_overlap)
        return chunks