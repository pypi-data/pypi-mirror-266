# __init__.py
from enum import Enum

from .models.database_span_attributes import DatabaseSpanAttributes
from .models.framework_span_attributes import FrameworkSpanAttributes
from .models.llm_span_attributes import LLMSpanAttributes


class Event(Enum):
    STREAM_START = "stream.start"
    STREAM_OUTPUT = "stream.output"
    STREAM_END = "stream.end"


class OpenAIMethods(Enum):
    CHAT_COMPLETION = "openai.chat.completions.create"
    IMAGES_GENERATION = "openai.images.generate"
    EMBEDDINGS_CREATE = "openai.embeddings.create"


class ChromaDBMethods(Enum):
    ADD = "chromadb.collection.add"
    GET = "chromadb.collection.get"
    QUERY = "chromadb.collection.query"
    DELETE = "chromadb.collection.delete"
    PEEK = "chromadb.collection.peek"
    UPDATE = "chromadb.collection.update"
    UPSERT = "chromadb.collection.upsert"
    MODIFY = "chromadb.collection.modify"
    COUNT = "chromadb.collection.count"


class PineconeMethods(Enum):
    UPSERT = "pinecone.index.upsert"
    QUERY = "pinecone.index.query"
    DELETE = "pinecone.index.delete"


# Export only what you want to be accessible directly through `import my_package`
__all__ = ['LLMSpanAttributes', 'DatabaseSpanAttributes', 'FrameworkSpanAttributes', 'Event',
           'OpenAIMethods', 'ChromaDBMethods', 'PineconeMethods']
