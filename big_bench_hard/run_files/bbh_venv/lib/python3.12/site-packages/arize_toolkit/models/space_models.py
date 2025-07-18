from datetime import datetime
from typing import Optional

from pydantic import Field

from arize_toolkit.models.base_models import BaseNode


class Organization(BaseNode):
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the organization was created")
    description: Optional[str] = Field(default=None, description="The description of the organization")


class Space(BaseNode):
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the space was created")
    description: Optional[str] = Field(default=None, description="The description of the space")
    private: Optional[bool] = Field(default=None, description="Whether the space is private")
