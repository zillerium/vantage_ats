import csv
from pathlib import Path
from gremlin_python.driver import client, serializer


class DbProductLoadPipeline:

    def __init__(self, settings):
        self.settings = settings
        self.client = None

    def _init_client(self):
        """Lazy initialization of the network client socket."""
        username_path = f"/dbs/{self.settings.cosmos_database_id}/colls/{self.settings.cosmos_graph_id}"
        
        self.client = client.Client(
            self.settings.cosmos_gremlin_endpoint,
            "g",
            username=username_path,
            password=self.settings.cosmos_key,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

    def _generate_upsert_query(self, product_id: str, name: str) -> str:
        """Creates an idempotent Gremlin query using the coalesce pattern."""
        safe_id = product_id.replace("'", "\\'")
        safe_name = name.replace("'", "\\'")
        
        return f"""
        g.V('{safe_id}').
          fold().
          coalesce(
            unfold(),
            addV('product').
            property('id', '{safe_id}').
            property('pk', '{safe_id}').
            property('name', '{safe_name}').
            property('type', 'product')
          )
        """

    def process_load(self):
        """Executes the complete stream-parse and transactional ingest processing loop."""
        file_path = Path(self.settings.database_load_csv_dir) / self.settings.csv_file_name

        if not file_path.exists():
            print(f"❌ Error: The file '{file_path}' was not found.")
            return

        print(f"📂 Opening '{file_path}' for data migration stream...")
        self._init_client()

        success_count = 0
        error_count = 0

        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                        
                    pk_field = row[0].strip('"').strip()
                    name_field = row[1].strip('"').strip()
                    
                    if not pk_field:
                        continue

                    query = self._generate_upsert_query(pk_field, name_field)
                    
                    try:
                        result_set = self.client.submitAsync(query).result()
                        result_set.all().result()
                        print(f"  ✅ Successfully processed edge vertex: {pk_field}")
                        success_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to process '{pk_field}': {e}")
                        error_count += 1
                        
        finally:
            if self.client:
                self.client.close()
                print("🔒 Database connection socket cleanly closed.")

        print(f"\n🎉 Database loading finished! Summary: {success_count} migrated, {error_count} failed.")