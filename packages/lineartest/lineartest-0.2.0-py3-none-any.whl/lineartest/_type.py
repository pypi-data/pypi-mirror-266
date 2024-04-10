from typing import TypeVar

from pydantic import BaseModel

BaseModelType = TypeVar('BaseModelType', bound=BaseModel)


class DefaultResponse(BaseModel):
    class Config:
        extra = 'allow'
