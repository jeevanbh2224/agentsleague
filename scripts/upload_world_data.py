"""
Upload world data markdown files to Azure Blob Storage and
create/populate an Azure AI Search index (Foundry IQ knowledge base).

Run once before starting the game:
    python scripts/upload_world_data.py

Requires:
    AZURE_STORAGE_CONNECTION_STRING
    AZURE_SEARCH_ENDPOINT
    AZURE_SEARCH_API_KEY
    AZURE_SEARCH_INDEX_NAME
"""

import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from config import Config

WORLD_DATA_DIR = pathlib.Path(__file__).parent.parent / "world_data"
SEARCH_INDEX_SCHEMA = {
    "name": Config.AZURE_SEARCH_INDEX_NAME,
    "fields": [
        {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
        {"name": "source", "type": "Edm.String", "filterable": True, "sortable": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {"name": "tags", "type": "Edm.String", "searchable": True, "filterable": True},
    ],
    "corsOptions": {"allowedOrigins": ["*"]},
    "suggesters": [],
}


def upload_to_blob() -> list[str]:
    """Upload all world data files to Azure Blob Storage."""
    from azure.storage.blob import BlobServiceClient

    print("Uploading world data to Azure Blob Storage...")
    client = BlobServiceClient.from_connection_string(Config.AZURE_STORAGE_CONNECTION_STRING)
    container_client = client.get_container_client(Config.AZURE_STORAGE_CONTAINER)

    try:
        container_client.create_container()
        print(f"  Created container: {Config.AZURE_STORAGE_CONTAINER}")
    except Exception:
        print(f"  Container already exists: {Config.AZURE_STORAGE_CONTAINER}")

    uploaded = []
    for md_file in WORLD_DATA_DIR.glob("*.md"):
        blob_name = f"world_data/{md_file.name}"
        content = md_file.read_bytes()
        container_client.upload_blob(blob_name, content, overwrite=True)
        print(f"  ✓ Uploaded: {blob_name}")
        uploaded.append(md_file.name)

    return uploaded


def create_search_index() -> None:
    """Create the Azure AI Search index if it doesn't exist."""
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
    from azure.core.credentials import AzureKeyCredential

    print("\nCreating Azure AI Search index...")
    index_client = SearchIndexClient(
        endpoint=Config.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(Config.AZURE_SEARCH_API_KEY),
    )

    fields = [
        SimpleField(name="id", type="Edm.String", key=True, filterable=True),
        SimpleField(name="source", type="Edm.String", filterable=True, sortable=True),
        SearchableField(name="content", type="Edm.String"),
        SearchableField(name="tags", type="Edm.String", filterable=True),
    ]

    index = SearchIndex(name=Config.AZURE_SEARCH_INDEX_NAME, fields=fields)
    index_client.create_or_update_index(index)
    print(f"  ✓ Index ready: {Config.AZURE_SEARCH_INDEX_NAME}")


def index_documents() -> None:
    """Push world data documents into the search index."""
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential

    print("\nIndexing world data documents...")
    search_client = SearchClient(
        endpoint=Config.AZURE_SEARCH_ENDPOINT,
        index_name=Config.AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(Config.AZURE_SEARCH_API_KEY),
    )

    documents = []
    for md_file in WORLD_DATA_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Extract tags from frontmatter if present
        tags = ""
        for line in content.split("\n")[:5]:
            if line.startswith("tags:"):
                tags = line.replace("tags:", "").strip().strip("[]")
                break

        # Split large files into chunks (~1500 chars) for better retrieval
        chunks = _chunk_text(content, chunk_size=1500)
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{md_file.stem}-{i}",
                "source": md_file.name,
                "content": chunk,
                "tags": tags,
            })

    if documents:
        # Upload in batches of 100
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i: i + batch_size]
            search_client.upload_documents(batch)
            print(f"  ✓ Indexed {min(i + batch_size, len(documents))}/{len(documents)} chunks")

    print(f"\n  Total documents indexed: {len(documents)}")


def _chunk_text(text: str, chunk_size: int = 1500) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) > chunk_size and current:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para

    if current.strip():
        chunks.append(current.strip())

    return chunks or [text[:chunk_size]]


def main() -> None:
    print("=" * 55)
    print("  FRACTURED ORBIT — KNOWLEDGE BASE SETUP")
    print("=" * 55 + "\n")

    if not Config.AZURE_STORAGE_CONNECTION_STRING:
        print("⚠ AZURE_STORAGE_CONNECTION_STRING not set — skipping blob upload")
    else:
        try:
            upload_to_blob()
        except Exception as e:
            print(f"  ✗ Blob upload failed: {e}")

    if not Config.has_search():
        print("⚠ Azure Search credentials not set — skipping index creation")
        print("  The game will use local file fallback instead.")
        return

    try:
        create_search_index()
        index_documents()
        print("\n✓ Knowledge base ready. You can now start the game.\n")
    except Exception as e:
        print(f"\n✗ Search setup failed: {e}")
        print("  The game will use local file fallback instead.\n")


if __name__ == "__main__":
    main()
