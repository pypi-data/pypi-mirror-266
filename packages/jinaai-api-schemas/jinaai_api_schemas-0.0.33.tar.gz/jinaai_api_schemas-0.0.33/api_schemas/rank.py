from typing import List, Union, Optional

from docarray import BaseDoc, DocList
from docarray.base_doc.doc import BaseDocWithoutId
from pydantic import Field, BaseModel, validator

from api_schemas.base import BaseInputModel


class ExecutorUsage(BaseDoc):
    """The usage of the embedding services to report, e.g. number of tokens in case of text input"""

    total_tokens: int = Field(description='The number of tokens used for the documents')


# EXECUTOR MODELS
## Models to be imported by the Executor and used by the Universal API to communicate with it
class TextDoc(BaseDoc):
    """Document containing a text field"""

    text: str


class RankInput(BaseDoc):
    query: Union[str, TextDoc] = Field(
        description='The search query',
    )

    documents: List[TextDoc] = Field(
        description='A list of text documents or strings to rerank. If a document is provided the text fields is required and all other fields will be preserved in the response.',
    )

    top_n: Optional[int] = Field(
        description='The number of most relevant documents or indices to return, defaults to '
        'the length of `documents`'
    )


class RankedObjectOutput(BaseDoc):
    """Ranked object"""

    index: int = Field(description='The index of the result in the input documents')
    document: Optional[TextDoc] = Field(description='The document returned')

    relevance_score: float = Field(description='The relevance score')
    usage: ExecutorUsage

    class Config(BaseDocWithoutId.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "index": 0,
                "document": {"text": "Document text"},
                "relevance_score": 0.9,
            }
        }


class RankOutput(BaseDoc):
    query_usage: ExecutorUsage = Field(
        description='The usage corresponding to the Query'
    )
    docs_usage: ExecutorUsage = Field(
        description='The usage corresponding to all the Documents processed. It may differ with the sum of the results usages when `top_n` is provided in input'
    )
    results: DocList[RankedObjectOutput] = Field(
        description='An ordered list of ranked documents'
    )


# UNIVERSAL API MODELS (mimic Cohere API)
class TextDocWithoutId(BaseDocWithoutId):
    """Document containing a text field"""

    text: str


class TextRankInput(BaseInputModel):
    """The input to the API for text embedding. OpenAI compatible"""

    query: Union[str, TextDoc] = Field(
        description='The search query',
    )

    documents: Union[List[str], List[TextDoc]] = Field(
        description='A list of text documents or strings to rerank. If a document is provided the text fields is required and all other fields will be preserved in the response.',
    )

    top_n: Optional[int] = Field(
        description='The number of most relevant documents or indices to return, defaults to '
        'the length of `documents`'
    )

    return_documents: bool = Field(
        description='If false, returns results without the doc text - the api will return '
        'a list of {index, relevance score} where index is inferred from the '
        'list passed into the request. If true, returns results with the doc '
        'text passed in - the api will return an ordered list of {index, text, '
        'relevance score} where index + text refers to the list passed into '
        'the request. Defaults to true',
        default=True,
    )

    @classmethod
    def validate(
        cls,
        value,
    ):
        if 'query' not in value:
            raise ValueError('"query" field missing')
        if 'documents' not in value:
            raise ValueError('"documents" field missing')
        if 'model' not in value:
            raise ValueError('you must provide a model parameter')
        return cls(**value)

    @validator('top_n')
    def positive_top_n(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('"top_n" must be greater than 0')
        return v

    class Config(BaseDoc.Config):
        extra = 'forbid'
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "model": "jina-reranker-v1-base-en",
                "query": "Search query",
                "documents": ["Document to rank 1", "Document to rank 2"],
            },
        }


class RankedObject(BaseDocWithoutId):
    """Ranked object"""

    index: int = Field(description='The index of the result in the input documents')
    document: Optional[TextDocWithoutId] = Field(description='The document returned')

    relevance_score: float = Field(description='The relevance score')

    class Config(BaseDocWithoutId.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "index": 0,
                "document": {"text": "Document text"},
                "relevance_score": 0.9,
            }
        }


class Usage(BaseModel):
    total_tokens: int = Field(
        description='The number of tokens used by all the texts in the input'
    )
    prompt_tokens: int = Field(description='Same as total_tokens')

    class Config(BaseModel.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "total_tokens": 15,
                "prompt_tokens": 15,
            }
        }


class RankingOutput(BaseInputModel):
    """Output of the embedding service"""

    results: DocList[RankedObject] = Field(
        description='An ordered list of ranked documents'
    )
    usage: Usage = Field(description='Total usage of the request.')

    class Config(BaseInputModel.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "results": [
                    {
                        "index": 0,
                        "document": {"text": "Document to rank 1"},
                        "relevance_score": 0.9,
                    },
                    {
                        "index": 1,
                        "document": {"text": "Document to rank 2"},
                        "relevance_score": 0.8,
                    },
                ],
                "usage": {"total_tokens": 15, "prompt_tokens": 15},
            }
        }
