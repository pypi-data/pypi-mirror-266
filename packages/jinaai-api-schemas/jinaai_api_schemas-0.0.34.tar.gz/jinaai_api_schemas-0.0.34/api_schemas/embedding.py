from typing import List, Union, Optional, Literal, Dict

from docarray import BaseDoc, DocList
from docarray.base_doc.doc import BaseDocWithoutId
from docarray.typing import NdArray
from docarray.typing.url import ImageUrl
from docarray.typing.bytes import ImageBytes
from pydantic import Field, BaseModel

from api_schemas.base import BaseInputModel


class ExecutorUsage(BaseDoc):
    """The usage of the embedding services to report, e.g. number of tokens in case of text input"""

    total_tokens: int = Field(
        description='The number of tokens used to embed the input text'
    )


# EXECUTOR MODELS
## Model to be imported by the Executor and used by the Universal API to communicate with it
class TextDoc(BaseDoc):
    """Document containing a text field"""

    text: str


# class TextDocWithTruncationFlag(TextDoc):
#     """Document containing a text field and a flag to know if it needs to be truncated"""
#
#     truncate: Optional[bool] = Field(
#         description='Flag to determine if the text needs to be truncated when exceeding the maximum token length',
#         default=None,
#     )


class ImageDoc(BaseDoc):
    url: Optional[ImageUrl] = Field(
        description='URL of an image file',
        default=None,
    )
    bytes: Optional[ImageBytes] = Field(
        description='Bytes representation of the Image.',
        default=None,
    )


## Model to be imported by the Executor and used by the Universal API to communicate with it
class EmbeddingDoc(BaseDoc):
    """Document to be returned by the embedding backend, containing the embedding vector and the token usage for the
    corresponding input texts"""

    embedding: NdArray = Field(description='The embedding of the texts', default=[])
    usage: ExecutorUsage
    # truncated: Optional[bool] = Field(
    #     description='Flag to inform that the embedding is computed ', default=None
    # )


# UNIVERSAL API MODELS (mimic OpenAI API)
class TextEmbeddingInput(BaseInputModel):
    """The input to the API for text embedding. OpenAI compatible"""

    input: Union[List[str], str, List[TextDoc], TextDoc] = Field(
        description='List of texts to embed',
    )
    encoding_format: Optional[Union[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary'], List[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary']]]] = Field(
        description='The format in which you want the embeddings to be returned.'
        'Possible value are `float` and `base64`. Defaults to `float`'
    )

    # truncate: Optional[bool] = Field(
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
                "model": "jina-embeddings-v2-base-en",
                "input": ["Hello, world!"],
            },
        }


class ImageEmbeddingInput(BaseInputModel):
    """The input to the API for text embedding. OpenAI compatible"""

    input: Union[List[ImageDoc], ImageDoc] = Field(
        description='List of images to embed',
    )
    encoding_format: Optional[Union[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary'], List[Literal['float', 'base64', 'int8', 'uint8', 'binary', 'ubinary']]]] = Field(
        description='The format in which you want the embeddings to be returned.'
        'Possible value are `float` and `base64`. Defaults to `float`'
    )

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
                "model": "clip",
                "input": ["bytes or URL"],
            },
        }


class EmbeddingObject(BaseDocWithoutId):
    """Embedding object. OpenAI compatible"""

    object: str = 'embedding'
    index: int = Field(
        description='The index of the embedding output, corresponding to the index in the list of inputs'
    )
    embedding: Union[NdArray, bytes, Dict[str, Union[NdArray, bytes]]] = Field(
        description='The embedding of the texts. It may come as the base64 '
        'encoded of the embeddings tensor '
        'if "encoding_format" is "base64". It can be rebuilt in the '
        'client as `np.frombuffer(base64.b64decode(embeddings), '
        'dtype=np.float32)`. In case of multiple "encoding_format" are requested, they will be returned in a '
                    'dictionary where the key is the encoding format.',
        default=[],
    )

    # truncated: Optional[bool] = Field(
    #     description='Flag to inform that the embedding is computed ', default=None
    # )

    class Config(BaseDocWithoutId.Config):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "object": "embedding",
                "index": 0,
                "embedding": [0.1, 0.2, 0.3],
            }
        }


class Usage(BaseModel):
    total_tokens: int = Field(
        description='The number of tokens used by all the texts in the input'
    )
    prompt_tokens: int = Field(description='Same as total_tokens')


class ModelEmbeddingOutput(BaseInputModel):
    """Output of the embedding service"""

    object: str = 'list'
    data: DocList[EmbeddingObject] = Field(
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
                    {"index": 0, "embedding": [0.1, 0.2, 0.3], "object": "embedding"},
                    {"index": 1, "embedding": [0.3, 0.2, 0.1], "object": "embedding"},
                ],
                "usage": {"total_tokens": 15, "prompt_tokens": 15},
            }
        }
