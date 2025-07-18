from datetime import datetime
from typing import List, Literal, Optional, Tuple

from pydantic import Field

from arize_toolkit.models import Model
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables
from arize_toolkit.types import DataGranularity, ModelEnvironment, PerformanceMetric


class GetModelByIDQuery(BaseQuery):
    graphql_query = (
        """
    query getModel($model_id: ID!) {
        node(id: $model_id) {
            ... on Model {"""
        + Model.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a model by id"

    class Variables(BaseVariables):
        model_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting a model by id"

    class QueryResponse(Model):
        pass


class GetModelQuery(BaseQuery):
    graphql_query = (
        """
    query getModel($space_id: ID!, $model_name: String) {
        node(id: $space_id) {
            ... on Space {
                models(search: $model_name, first: 1) {
                    edges {
                        node {"""
        + Model.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get the id of a model in the space"

    class Variables(BaseVariables):
        space_id: str
        model_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting the id of a named model in the space"

    class QueryResponse(Model):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or "models" not in result["node"] or "edges" not in result["node"]["models"]:
            cls.raise_exception("No model found with the given name")
        result = result["node"]["models"]["edges"]
        if len(result) == 0:
            cls.raise_exception("No model found with the given name")
        model_result = result[0]["node"]
        return (
            [cls.QueryResponse(**model_result)],
            False,
            None,
        )


class GetAllModelsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllModels($space_id:ID!, $endCursor: String){
        node(id: $space_id){
            ...on Space{
                models(first: 10, after: $endCursor){
                    pageInfo{
                        hasNextPage
                        endCursor
                    }
                    edges{
                        node{"""
        + Model.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all models in a space"

    class Variables(BaseVariables):
        space_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting all models in space"

    class QueryResponse(Model):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        page_info = result["node"]["models"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        models = result["node"]["models"]["edges"]
        model_list = [cls.QueryResponse(**model["node"]) for model in models]
        return model_list, has_next_page, end_cursor


class GetModelVolumeQuery(BaseQuery):
    graphql_query = """
    query getModelVolume($model_id: ID!, $start_time: DateTime, $end_time: DateTime) {
        node(id: $model_id) {
            ... on Model {
                modelPredictionVolume(startTime: $start_time, endTime: $end_time) {
                    totalVolume
                }
            }
        }
    }"""
    query_description = "Get the prediction volume for a model"

    class Variables(BaseVariables):
        model_id: str
        start_time: Optional[datetime] = None
        end_time: Optional[datetime] = None

    class QueryException(ArizeAPIException):
        message: str = "Error in getting the prediction volume for a model"

    class QueryResponse(BaseResponse):
        totalVolume: int

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        result = result["node"]
        if "modelPredictionVolume" not in result:
            cls.raise_exception("No model prediction volume found with the given id")
        return [cls.QueryResponse(**result["modelPredictionVolume"])], False, None


class DeleteDataMutation(BaseQuery):
    graphql_query = """
    mutation deleteData($input: DeleteDataMutationInput!) {
        deleteData(input: $input) {
            clientMutationId
        }
    }
    """
    query_description = "Delete data from a model for a given time range and environment"

    class Variables(BaseVariables):
        modelId: str
        startTime: datetime
        endTime: datetime = datetime.now()
        environment: Literal["PRODUCTION", "PREPRODUCTION"] = "PRODUCTION"

    class QueryException(ArizeAPIException):
        message: str = "Error in deleting data from a model"

    class QueryResponse(BaseResponse):
        success: bool

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "deleteData" not in result:
            cls.raise_exception("No data deleted")
        return [cls.QueryResponse(success=True)], False, None


class GetPerformanceMetricValuesQuery(BaseQuery):
    graphql_query = """
    query getMetricValue(
        $modelId: ID!,
        $startDate: DateTime!,
        $endDate: DateTime!,
        $metric: PerformanceMetric!,
        $environment: ModelEnvironmentName!,
        $granularity: DataGranularity!
    ){
        node(id:$modelId){
            ... on Model{
            performanceMetricOverTime(
                startTime:$startDate,
                endTime:$endDate,
                performanceMetric:$metric,
                environmentName:$environment,
                timeZone: "UTC",
                timeSeriesDataGranularity:$granularity,
            ){
                dataWindows{
                        metricDisplayDate
                        metricValue
                    }
                }
            }
        }
    }
    """
    query_description = "Get the performance metric values for a model"

    class Variables(BaseVariables):
        modelId: str
        startDate: datetime
        endDate: datetime
        metric: PerformanceMetric
        environment: ModelEnvironment
        granularity: DataGranularity

    class QueryException(ArizeAPIException):
        message: str = "Error in getting the performance metric values for a model"

    class QueryResponse(BaseResponse):
        metricDisplayDate: datetime
        metricValue: Optional[float] = Field(default=-1.0)

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        result = result["node"]
        if "performanceMetricOverTime" not in result or "dataWindows" not in result["performanceMetricOverTime"]:
            cls.raise_exception("No performance metric values found")
        data_windows = result["performanceMetricOverTime"]["dataWindows"]
        if len(data_windows) == 0:
            cls.raise_exception("Empty data windows - no performance metric values found during the given time range")
        return (
            [cls.QueryResponse(**data_window) for data_window in data_windows],
            False,
            None,
        )
