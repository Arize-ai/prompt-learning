from datetime import datetime
from typing import List, Optional

from pydantic import Field, model_validator

from arize_toolkit.types import ComparisonOperator, DimensionCategory, DimensionDataType, FilterRowType, ModelType
from arize_toolkit.utils import GraphQLModel

## Common GraphQL Models ##


class BaseNode(GraphQLModel):
    id: Optional[str] = Field(default=None, description="The ID of the node")
    name: Optional[str] = Field(default=None, description="The name of the node")


class User(BaseNode):
    email: Optional[str] = Field(default=None, description="The email of the user")


class Dimension(BaseNode):
    dataType: Optional[DimensionDataType] = Field(default=None)
    category: Optional[DimensionCategory] = Field(default=None)


class DimensionValue(GraphQLModel):
    id: Optional[str] = Field(default=None)
    value: str


class DimensionFilterInput(GraphQLModel):
    dimensionType: FilterRowType
    operator: ComparisonOperator = Field(default=ComparisonOperator.equals)
    name: Optional[str] = Field(default=None)
    values: List[str] = Field(default=[])

    @model_validator(mode="after")
    def verify_values(self):
        if self.dimensionType == FilterRowType.featureLabel or self.dimensionType == FilterRowType.tagLabel:
            if self.name is None:
                raise ValueError("Name is required for feature label or tag label filter type")
        return self


## Model GraphQL Models ##


class Model(BaseNode):
    modelType: ModelType
    createdAt: datetime
    isDemoModel: bool
