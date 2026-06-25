from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

client = SearchClient(
    endpoint="https://skills-search-rag.search.windows.net",
    index_name="skills-rag-v3",
    credential=AzureKeyCredential("........")
)

doc = {
    "id": "test_1",
    "text": "hello",
    "source": "test",
    "topic": "test",
    "vector": [0.0] * 3072
}

result = client.upload_documents([doc])

print(result)
