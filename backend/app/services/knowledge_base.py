"""Persistent document ingestion and retrieval backed by ChromaDB.

Documents are stored as chunks instead of as original files.  That keeps the
knowledge base focused on the information needed for generation and avoids
retaining an unnecessary second copy of a user's upload.  Every Chroma record
is tagged with its owner, so retrieval is always isolated to one user.
"""

from __future__ import annotations

import csv
import io
import logging
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import chromadb
from docx import Document as DocxDocument
from google import genai
from pypdf import PdfReader

from app import config

logger = logging.getLogger(__name__)


class KnowledgeBaseError(RuntimeError):
    """Base exception for user-facing knowledge-base failures."""


class UnsupportedDocumentError(KnowledgeBaseError):
    """Raised when an upload is not a supported document type."""


class DocumentParsingError(KnowledgeBaseError):
    """Raised when text cannot be extracted from a supported document."""


class EmbeddingError(KnowledgeBaseError):
    """Raised when the embedding provider cannot create a vector."""


class DocumentNotFoundError(KnowledgeBaseError):
    """Raised when a user tries to remove a document they do not own."""


@dataclass(frozen=True)
class TextPage:
    """Text extracted from one source page (or the whole non-PDF document)."""

    text: str
    page_number: int


@dataclass(frozen=True)
class TextChunk:
    """A chunk ready for embedding, with a source location for citations."""

    text: str
    page_number: int


@dataclass(frozen=True)
class DocumentSummary:
    """Metadata returned to the API after ingesting or listing a document."""

    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    uploaded_at: str
    campaign_id: str | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    """A source chunk returned by semantic search."""

    document_id: str
    filename: str
    text: str
    page_number: int
    distance: float | None


SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


class KnowledgeBaseService:
    """Owns parsing, Chroma persistence, embedding, and scoped retrieval."""

    def __init__(self) -> None:
        self._client: chromadb.PersistentClient | None = None
        self._collection: Any | None = None
        self._embedding_client: genai.Client | None = None

    def ingest(
        self,
        *,
        user_id: str,
        filename: str,
        contents: bytes,
        campaign_id: str | None = None,
    ) -> DocumentSummary:
        """Parse, chunk, embed, and persist one uploaded document."""
        pages = extract_text_pages(filename, contents)
        chunks = list(chunk_pages(pages))
        if not chunks:
            raise DocumentParsingError(
                "No readable text was found in this document. Scanned PDFs need OCR before upload."
            )
        if len(chunks) > config.RAG_MAX_CHUNKS_PER_DOCUMENT:
            raise DocumentParsingError(
                f"This document creates more than {config.RAG_MAX_CHUNKS_PER_DOCUMENT} chunks. "
                "Please upload a smaller document."
            )

        document_id = str(uuid.uuid4())
        uploaded_at = datetime.now(timezone.utc).isoformat()
        embeddings = self._embed_many(
            [chunk.text for chunk in chunks], task_type="RETRIEVAL_DOCUMENT"
        )
        metadatas: list[dict[str, str | int]] = []
        for index, chunk in enumerate(chunks):
            metadata: dict[str, str | int] = {
                "document_id": document_id,
                "user_id": user_id,
                "filename": filename,
                "file_type": Path(filename).suffix.lower().lstrip("."),
                "chunk_index": index,
                "page_number": chunk.page_number,
                "uploaded_at": uploaded_at,
            }
            if campaign_id:
                metadata["campaign_id"] = campaign_id
            metadatas.append(metadata)

        try:
            self._get_collection().upsert(
                ids=[f"{document_id}:{index}" for index in range(len(chunks))],
                documents=[chunk.text for chunk in chunks],
                embeddings=embeddings,
                metadatas=metadatas,
            )
        except Exception as exc:
            logger.exception("Unable to persist document %s to Chroma", document_id)
            raise KnowledgeBaseError("Unable to save the document to the knowledge base.") from exc

        return DocumentSummary(
            document_id=document_id,
            filename=filename,
            file_type=Path(filename).suffix.lower().lstrip("."),
            chunk_count=len(chunks),
            uploaded_at=uploaded_at,
            campaign_id=campaign_id,
        )

    def search(self, *, user_id: str, query: str, limit: int = 5) -> list[RetrievedChunk]:
        """Find the most relevant chunks belonging to one user."""
        if not query.strip() or not self.has_documents(user_id=user_id):
            return []

        query_embedding = self._embed_many([query], task_type="RETRIEVAL_QUERY")[0]
        try:
            result = self._get_collection().query(
                query_embeddings=[query_embedding],
                n_results=min(max(limit, 1), config.RAG_RETRIEVAL_LIMIT),
                where={"user_id": user_id},
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.exception("Unable to query Chroma for user %s", user_id)
            raise KnowledgeBaseError("Unable to search the uploaded documents.") from exc

        documents = _first_result_list(result.get("documents"))
        metadatas = _first_result_list(result.get("metadatas"))
        distances = _first_result_list(result.get("distances"))
        retrieved: list[RetrievedChunk] = []
        for index, text in enumerate(documents):
            if not isinstance(text, str):
                continue
            metadata = metadatas[index] if index < len(metadatas) else {}
            if not isinstance(metadata, dict):
                metadata = {}
            distance = distances[index] if index < len(distances) else None
            retrieved.append(
                RetrievedChunk(
                    document_id=str(metadata.get("document_id", "")),
                    filename=str(metadata.get("filename", "Uploaded document")),
                    text=text,
                    page_number=_as_int(metadata.get("page_number"), default=1),
                    distance=float(distance) if isinstance(distance, (int, float)) else None,
                )
            )
        return retrieved

    def list_documents(self, *, user_id: str) -> list[DocumentSummary]:
        """List each user's document once, rather than once per stored chunk."""
        try:
            result = self._get_collection().get(
                where={"user_id": user_id}, include=["metadatas"]
            )
        except Exception as exc:
            logger.exception("Unable to list documents for user %s", user_id)
            raise KnowledgeBaseError("Unable to list uploaded documents.") from exc

        documents: dict[str, DocumentSummary] = {}
        for metadata in result.get("metadatas") or []:
            if not isinstance(metadata, dict):
                continue
            document_id = metadata.get("document_id")
            if not isinstance(document_id, str) or document_id in documents:
                continue
            documents[document_id] = DocumentSummary(
                document_id=document_id,
                filename=str(metadata.get("filename", "Uploaded document")),
                file_type=str(metadata.get("file_type", "")),
                chunk_count=0,
                uploaded_at=str(metadata.get("uploaded_at", "")),
                campaign_id=_optional_string(metadata.get("campaign_id")),
            )

        chunk_counts = {document_id: 0 for document_id in documents}
        for metadata in result.get("metadatas") or []:
            if isinstance(metadata, dict) and isinstance(metadata.get("document_id"), str):
                document_id = metadata["document_id"]
                if document_id in chunk_counts:
                    chunk_counts[document_id] += 1

        return sorted(
            [
                replace(summary, chunk_count=chunk_counts[summary.document_id])
                for summary in documents.values()
            ],
            key=lambda item: item.uploaded_at,
            reverse=True,
        )

    def delete_document(self, *, user_id: str, document_id: str) -> None:
        """Remove all chunks belonging to one user-owned document."""
        collection = self._get_collection()
        try:
            existing = collection.get(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"document_id": document_id},
                    ]
                },
                include=[],
                limit=1,
            )
            if not existing.get("ids"):
                raise DocumentNotFoundError("Document not found.")
            collection.delete(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"document_id": document_id},
                    ]
                }
            )
        except DocumentNotFoundError:
            raise
        except Exception as exc:
            logger.exception("Unable to delete document %s", document_id)
            raise KnowledgeBaseError("Unable to delete the uploaded document.") from exc

    def has_documents(self, *, user_id: str) -> bool:
        """Return whether the user has at least one indexed chunk."""
        try:
            result = self._get_collection().get(
                where={"user_id": user_id}, include=[], limit=1
            )
            return bool(result.get("ids"))
        except Exception as exc:
            logger.warning("Unable to check knowledge-base documents: %s", exc)
            return False

    def _get_collection(self) -> Any:
        if self._collection is not None:
            return self._collection
        try:
            if self._client is None:
                self._client = chromadb.PersistentClient(
                    path=str(config.CHROMA_PERSIST_DIRECTORY)
                )
            self._collection = self._client.get_or_create_collection(
                name=config.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            return self._collection
        except Exception as exc:
            logger.exception("Unable to initialise ChromaDB")
            raise KnowledgeBaseError("The document knowledge base is unavailable.") from exc

    def _embed_many(self, texts: list[str], *, task_type: str) -> list[list[float]]:
        if not texts:
            return []
        if not config.GOOGLE_API_KEY:
            raise EmbeddingError(
                "Document embeddings require GOOGLE_API_KEY to be configured on the server."
            )

        if self._embedding_client is None:
            self._embedding_client = genai.Client(api_key=config.GOOGLE_API_KEY)

        embeddings: list[list[float]] = []
        try:
            for batch in _batches(texts, config.RAG_EMBEDDING_BATCH_SIZE):
                response = self._embedding_client.models.embed_content(
                    model=config.RAG_EMBEDDING_MODEL,
                    contents=batch,
                    config={"task_type": task_type},
                )
                batch_embeddings = getattr(response, "embeddings", None) or []
                vectors = [list(embedding.values) for embedding in batch_embeddings]
                if len(vectors) != len(batch):
                    raise EmbeddingError("The embedding provider returned an incomplete result.")
                embeddings.extend(vectors)
        except EmbeddingError:
            raise
        except Exception as exc:
            logger.exception("Embedding generation failed")
            raise EmbeddingError("Unable to generate embeddings for this document.") from exc
        return embeddings


def extract_text_pages(filename: str, contents: bytes) -> list[TextPage]:
    """Extract text from one of the allowed document formats."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_DOCUMENT_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_DOCUMENT_EXTENSIONS))
        raise UnsupportedDocumentError(f"Unsupported document type. Use: {allowed}.")
    if not contents:
        raise DocumentParsingError("The uploaded document is empty.")

    try:
        if suffix == ".pdf":
            reader = PdfReader(io.BytesIO(contents))
            pages = [
                TextPage(text=page.extract_text() or "", page_number=index + 1)
                for index, page in enumerate(reader.pages)
            ]
        elif suffix == ".docx":
            document = DocxDocument(io.BytesIO(contents))
            table_text = [
                " | ".join(cell.text.strip() for cell in row.cells)
                for table in document.tables
                for row in table.rows
            ]
            text = "\n".join(
                [paragraph.text for paragraph in document.paragraphs] + table_text
            )
            pages = [TextPage(text=text, page_number=1)]
        elif suffix == ".csv":
            decoded = _decode_text(contents)
            rows = csv.reader(io.StringIO(decoded))
            pages = [TextPage(text="\n".join(" | ".join(row) for row in rows), page_number=1)]
        else:
            pages = [TextPage(text=_decode_text(contents), page_number=1)]
    except DocumentParsingError:
        raise
    except Exception as exc:
        logger.info("Could not parse %s", filename, exc_info=True)
        raise DocumentParsingError(f"Could not read text from '{filename}'.") from exc

    cleaned_pages = [
        TextPage(text=_normalise_text(page.text), page_number=page.page_number)
        for page in pages
        if _normalise_text(page.text)
    ]
    if not cleaned_pages:
        raise DocumentParsingError(
            "No readable text was found in this document. Scanned PDFs need OCR before upload."
        )
    total_characters = sum(len(page.text) for page in cleaned_pages)
    if total_characters > config.RAG_MAX_DOCUMENT_CHARACTERS:
        raise DocumentParsingError(
            f"This document exceeds the {config.RAG_MAX_DOCUMENT_CHARACTERS:,}-character limit."
        )
    return cleaned_pages


def chunk_pages(pages: Iterable[TextPage]) -> Iterable[TextChunk]:
    """Split pages on natural whitespace with a small overlap for context."""
    for page in pages:
        text = page.text
        start = 0
        while start < len(text):
            proposed_end = min(start + config.RAG_CHUNK_SIZE, len(text))
            end = proposed_end
            if proposed_end < len(text):
                natural_break = text.rfind(
                    " ", start + (config.RAG_CHUNK_SIZE // 2), proposed_end
                )
                if natural_break > start:
                    end = natural_break
            chunk = text[start:end].strip()
            if chunk:
                yield TextChunk(text=chunk, page_number=page.page_number)
            if end >= len(text):
                break
            start = max(end - config.RAG_CHUNK_OVERLAP, start + 1)


def _decode_text(contents: bytes) -> str:
    try:
        return contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return contents.decode("cp1252")
        except UnicodeDecodeError as exc:
            raise DocumentParsingError("The text document must use UTF-8 or Windows-1252 encoding.") from exc


def _normalise_text(text: str) -> str:
    return " ".join(text.replace("\x00", " ").split())


def _batches(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _first_result_list(value: Any) -> list[Any]:
    if isinstance(value, list) and value and isinstance(value[0], list):
        return value[0]
    return []


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _as_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


knowledge_base = KnowledgeBaseService()
