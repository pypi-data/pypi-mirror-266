from typing import List, Union, Literal, Optional, Dict

from docarray import BaseDoc, DocList
from docarray.base_doc.doc import BaseDocWithoutId
from docarray.typing import NdArray
from pydantic import Field, validator

from api_schemas.embedding import ExecutorUsage, TextDoc, Usage
from api_schemas.base import BaseInputModel


## Model to be imported by the Executor and used by the Universal API to communicate with it
class MultiEmbeddingsDoc(BaseDoc):
    """Document to be returned by the embedding backend, containing the embedding vector and the token usage for the
    corresponding input texts"""

    embeddings: NdArray = Field(
        description='A tensor of embeddings for the text', default=[]
    )
    usage: ExecutorUsage
    # truncated: Optional[bool] = Field(
    #     description='Flag to inform that the embedding is computed ', default=None
    # )


class MultiEmbeddingsObject(BaseDocWithoutId):
    """Embedding object. OpenAI compatible"""

    object: str = 'embeddings'
    index: int = Field(
        description='The index of the embedding output, corresponding to the index in the list of inputs'
    )
    embeddings: Union[List[bytes], NdArray, Dict[str, NdArray]] = Field(
        description='A tensor of embeddings for the text. It may come as the base64 encoded of the embeddings tensor '
        'if "encoding_format" is "base64". It can be rebuilt in the client as `np.frombuffer('
        'base64.b64decode(embeddings), dtype=np.float32)`. In case of multiple "encoding_format" are requested, '
                    'they will be returned in a '
                    'dictionary where the key is the encoding format.'
    )

    # truncated: Optional[bool] = Field(
    #     description='Flag to inform that the embedding is computed ', default=None
    # )

    class Config(BaseDocWithoutId.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "object": "embeddings",
                "index": 0,
                "embeddings": [[0.1, 0.2, 0.3], [0.5, 0.6, 0.7]],
            }
        }


class LateInteractionInput(BaseDoc):
    query_embeddings: NdArray = Field(
        description='The embeddings of the query',
    )
    documents_embeddings: List[NdArray] = Field(
        description='The embeddings of all the documents to rerank'
    )
    top_n: Optional[int] = Field(
        description='The number of most relevant documents or indices to return, defaults to '
        'the length of `documents`'
    )


class LateInteraction(BaseInputModel):
    """The input to the API for late interaction"""

    query_embeddings: Union[List[bytes], NdArray] = Field(
        description='The embeddings of the query. It should be of the shape (num_tokens, token_embedding_size). It '
        'can also be a base64 encoded string of the "float32" embeddings array. You can pass them as a list of base64 encoded '
        'strings with `base64.b64encode(nparray.tobytes()).decode()`',
    )
    documents_embeddings: List[Union[List[bytes], NdArray]] = Field(
        description='The embeddings of all the documents to rerank. Each matrix in the list should be of the shape ('
        'num_tokens, token_embedding_size). It can also be list of list of base64 encoded strings of the '
        '"float32" embeddings. You can pass them as a '
        'string with `base64.b64encode(nparray.tobytes()).decode()`'
    )
    top_n: Optional[int] = Field(
        description='The number of most relevant documents or indices to return, defaults to '
        'the length of `documents`'
    )

    @classmethod
    def validate(
        cls,
        value,
    ):
        if 'query_embeddings' not in value:
            raise ValueError('"query_embeddings" field missing')
        if 'documents_embeddings' not in value:
            raise ValueError('"documents_embeddings" field missing')
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
                "model": "jina-colbert-v1-en",
                "query_embeddings": [0.1, 0.1, 0.1],
                "documents_embeddings": [[0.1, 0.1, 0.1], [0.1, 0.1, 0.1]],
            },
        }


class TextEmbeddingInput(BaseInputModel):
    """The input to the API for text embedding. OpenAI compatible"""

    input: Union[List[str], str, List[TextDoc], TextDoc] = Field(
        description='List of texts to embed',
    )
    input_type: Literal['query', 'document'] = Field(
        description='Type of the embedding to compute, query or document',
        default='document',
    )
    encoding_format: Optional[Union[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary'], List[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary']]]] = Field(
        description='The format in which you want the embeddings to be returned.'
        'Possible value are `float` and `base64`. Defaults to `float`'
    )

    # truncate_input: Optional[bool] = Field(
    #     description='Flag to determine if the text needs to be truncated when exceeding the maximum token length',
    #     default=None,
    # )

    @classmethod
    def validate(
        cls,
        value,
    ):
        if 'input' not in value:
            raise ValueError('"input" field missing')
        if 'model' not in value:
            raise ValueError('you must provide a model parameter')
        return cls(**value)

    class Config(BaseDoc.Config):
        extra = 'forbid'
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "model": "jina-colbert-v1-en",
                "input": ["Hello, world!"],
            },
        }


class ColbertModelEmbeddingsOutput(BaseInputModel):
    """Output of the embedding service"""

    object: str = 'list'
    data: DocList[MultiEmbeddingsObject] = Field(
        description='A list of Embedding Objects returned by the embedding service'
    )
    usage: Usage = Field(
        description='Total usage of the request. Sums up the usage from each individual input'
    )

    class Config(BaseInputModel.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "data": [
                    {
                        "index": 0,
                        "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                        "object": "embeddings",
                    },
                    {
                        "index": 1,
                        "embeddings": [[0.6, 0.5, 0.4], [0.3, 0.2, 0.1]],
                        "object": "embeddings",
                    },
                ],
                "usage": {"total_tokens": 15, "prompt_tokens": 15},
            }
        }
