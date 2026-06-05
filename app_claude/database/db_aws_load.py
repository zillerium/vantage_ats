import os
import csv
from dotenv import load_dotenv
from gremlin_python.driver import client, serializer

# Load environment variables from .env
load_dotenv()

COSMOS_ENDPOINT = os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_CONNECTION_GREMLIN_ENDPOINT")
COSMOS_KEY = os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_KEY")

DATABASE = "productdbid"
GRAPH = "allproducts"
CSV_FILE_PATH = "dataload.csv"  # Name of your file on disk

# Create Gremlin client
gremlin_client = client.Client(
    COSMOS_ENDPOINT,
    "g",
    username=f"/dbs/{DATABASE}/colls/{GRAPH}",
    password=COSMOS_KEY,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

def generate_upsert_query(product_id, name):
    """
    Creates an idempotent Gremlin query using the coalesce pattern.
    """
    # Escape single quotes to prevent Gremlin syntax injection errors
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

def load_csv_file_to_cosmos(file_path):
    # Check if file actually exists before starting
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found in the current directory.")
        return

    print(f"Opening '{file_path}' for reading...")
    
    # Open file with utf-8 encoding to support diverse product names safely
    with open(file_path, mode='r', encoding='utf-8') as f:
        # csv.reader automatically handles the outer quotes and splits fields by commas
        reader = csv.reader(f)
        
        success_count = 0
        error_count = 0

        for row in reader:
            # Skip empty lines
            if not row or len(row) < 2:
                continue
                
            # Strip remaining inner quotes and whitespace
            pk_field = row[0].strip('"').strip()
            name_field = row[1].strip('"').strip()
            
            # Skip if primary identifier is missing
            if not pk_field:
                continue

            query = generate_upsert_query(pk_field, name_field)
            
            try:
                # Submit query and block for server response
                result_set = gremlin_client.submitAsync(query).result()
                result_set.all().result()
                print(f" Successfully processed: {pk_field}")
                success_count += 1
            except Exception as e:
                print(f" Failed to process '{pk_field}': {e}")
                error_count += 1

    print(f"\nProcessing complete! Summary: {success_count} processed, {error_count} failed.")

try:
    load_csv_file_to_cosmos(CSV_FILE_PATH)
finally:
    # Always cleanly close network sockets
    gremlin_client.close()
    print("Database client connection closed.")
