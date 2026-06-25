from pathlib import Path


class ICORagPipeline:

    def __init__(
        self,
        settings,
        vector_store,
        openai_service,
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

                print(
                    f"   Chunk {i}/{len(chunks)} | "
                    f"ID={chunk_id} | "
                    f"Length={len(chunk)} chars"
                )

                response = self.openai_service.client.embeddings.create(
                    input=[chunk],
                    model=self.settings.azure_openai_embedding_model
                )

                embedding_vector = response.data[0].embedding

                print(f"   Vector length={len(embedding_vector)}")

                self.vector_store.insert_vector_chunk(
                    document_id=file_path.stem,
                    chunk_id=chunk_id,
                    text_content=chunk,
                    vector=embedding_vector,
                    topic="ico"
                )

            print(f"   ✅ Vector store indexed {len(chunks)} elements successfully.")

        except Exception as e:
            print(f"❌ Failed to execute Vector DB update for file {file_path.name}: {e}")
            return

        try:
            destination_dir = Path(self.txt_processed_dir)
            destination_dir.mkdir(parents=True, exist_ok=True)
            self.file_mover.move_file(file_path, str(destination_dir))
            print("📦 Archived source text file.")
        except Exception as e:
            print(f"❌ Failed to archive file: {e}")

    def _chunk_text(self, text: str) -> list:
        """Sliding-window word chunker."""
        chunks = []
        words = text.split()

        word_size = self.chunk_size // 5
        word_overlap = self.chunk_overlap // 5

        step = word_size - word_overlap

        if step <= 0:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        i = 0
        while i < len(words):
            chunk_words = words[i:i + word_size]
            chunk = " ".join(chunk_words)

            if chunk.strip():
                chunks.append(chunk)

            i += step

        return chunks