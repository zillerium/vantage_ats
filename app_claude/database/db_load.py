import os
from dotenv import load_dotenv
from gremlin_python.driver import client, serializer

# Load environment variables from .env
load_dotenv()

COSMOS_ENDPOINT = os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_CONNECTION_GREMLIN_ENDPOINT")
COSMOS_KEY = os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_KEY")

DATABASE = "productdbid"
GRAPH = "allproducts"

# Create Gremlin client
gremlin_client = client.Client(
    COSMOS_ENDPOINT,
    "g",
    username=f"/dbs/{DATABASE}/colls/{GRAPH}",
    password=COSMOS_KEY,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

# Test node insert
query = """
g.addV('product').
  property('id', 'aws-test-2').
  property('pk', 'aws-test-2').
  property('name', 'Test Product 2').
  property('type', 'product')
"""

try:
    result = gremlin_client.submitAsync(query).result()
    print("Node inserted successfully.")
except Exception as e:
    print("Error:", e)

