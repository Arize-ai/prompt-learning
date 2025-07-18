from typing import List, Optional, Tuple

from arize_toolkit.models import CustomMetric, CustomMetricInput
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetAllCustomMetricsByModelIdQuery(BaseQuery):
    graphql_query = (
        """
    query getAllCustomMetricsById($model_id:ID!, $endCursor:String){
        node(id: $model_id){
            ... on Model{
                customMetrics(first: 10, after: $endCursor){
                    pageInfo{
                        hasNextPage
                        endCursor
                    }
                    edges{
                        node{"""
        + CustomMetric.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all custom metrics for a model by ID"

    class Variables(BaseVariables):
        model_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting all custom metrics by model ID"

    class QueryResponse(CustomMetric):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        edges = result["node"]["customMetrics"]["edges"]
        if not edges:
            cls.raise_exception("No custom metrics found for the given model ID")
        page_info = result["node"]["customMetrics"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        custom_metric_list = [cls.QueryResponse(**custom_metric["node"]) for custom_metric in edges]
        return custom_metric_list, has_next_page, end_cursor


class GetAllCustomMetricsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllCustomMetrics($space_id:ID!, $model_name:String, $endCursor:String){
        node(id: $space_id){
            ... on Space{
                models(search:$model_name, useExactSearchMatch:true, first: 1){
                    edges{
                        node{
                            customMetrics(first: 10, after: $endCursor){
                                pageInfo{
                                    hasNextPage
                                    endCursor
                                }
                                edges{
                                    node{"""
        + CustomMetric.to_graphql_fields()
        + """}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all custom metrics"

    class Variables(BaseVariables):
        space_id: str
        model_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting all custom metrics"

    class QueryResponse(CustomMetric):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["models"]["edges"]:
            cls.raise_exception(details="No model found with the given name")
        model_result = result["node"]["models"]["edges"][0]["node"]
        if not model_result["customMetrics"]["edges"]:
            cls.raise_exception("No custom metric found with the given name")
        page_info = model_result["customMetrics"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        custom_metrics = model_result["customMetrics"]["edges"]
        custom_metric_list = [cls.QueryResponse(**custom_metric["node"]) for custom_metric in custom_metrics]
        return custom_metric_list, has_next_page, end_cursor


class GetCustomMetricQuery(BaseQuery):
    graphql_query = (
        """
    query getCustomMetric($space_id:ID!, $model_name:String, $metric_name:String){
        node(id: $space_id){
            ... on Space{
                models(search:$model_name, useExactSearchMatch:true, first: 1){
                    edges{
                        node{
                            customMetrics(searchTerm:$metric_name, first: 1){
                                edges{
                                    node{"""
        + CustomMetric.to_graphql_fields()
        + """}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a custom metric by name"

    class Variables(BaseVariables):
        space_id: str
        model_name: str
        metric_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting a custom metric by name"

    class QueryResponse(CustomMetric):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["models"]["edges"]:
            cls.raise_exception("No model found with the given name")
        model_result = result["node"]["models"]["edges"][0]["node"]
        if not model_result["customMetrics"]["edges"]:
            cls.raise_exception("No custom metric found with the given name")
        custom_metric_result = model_result["customMetrics"]["edges"][0]["node"]
        return [cls.QueryResponse(**custom_metric_result)], False, None


class GetCustomMetricByIDQuery(BaseQuery):
    graphql_query = (
        """
    query getCustomMetricByID($custom_metric_id: ID!){
        node(id: $custom_metric_id){
            ... on CustomMetric{
                """
        + CustomMetric.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a custom metric by ID"

    class Variables(BaseVariables):
        custom_metric_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting a custom metric by ID"

    class QueryResponse(CustomMetric):
        pass


class CreateCustomMetricMutation(BaseQuery):
    graphql_query = """
    mutation createCustomMetric($input: CreateCustomMetricMutationInput!) {
        createCustomMetric(input: $input) {
            customMetric{
                id
            }
        }
    }
    """
    query_description = "Create a custom metric"

    class Variables(CustomMetricInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating a custom metric"

    class QueryResponse(BaseResponse):
        metric_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result["createCustomMetric"]
        if "customMetric" not in create_result:
            cls.raise_exception("no custom metric id returned")
        return (
            [cls.QueryResponse(metric_id=create_result["customMetric"]["id"])],
            False,
            None,
        )


class DeleteCustomMetricMutation(BaseQuery):
    graphql_query = """
    mutation deleteCustomMetric($input: DeleteCustomMetricMutationInput!){
        deleteCustomMetric(input:$input){
            model{
                id
            }
        }
    }
    """
    query_description = "Delete a custom metric"

    class Variables(BaseVariables):
        customMetricId: str
        modelId: str

    class QueryException(ArizeAPIException):
        message: str = "Error in deleting a custom metric"

    class QueryResponse(BaseResponse):
        model_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        delete_result = result["deleteCustomMetric"]
        if "model" not in delete_result or "id" not in delete_result["model"]:
            cls.raise_exception("no model id returned")
        return [cls.QueryResponse(model_id=delete_result["model"]["id"])], False, None


class UpdateCustomMetricMutation(BaseQuery):
    graphql_query = (
        """
    mutation updateCustomMetric($input: UpdateCustomMetricMutationInput!) {
        updateCustomMetric(input: $input) {
            customMetric {"""
        + CustomMetric.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Update a custom metric"

    class Variables(CustomMetricInput):
        customMetricId: str

    class QueryException(ArizeAPIException):
        message: str = "Error in updating a custom metric"

    class QueryResponse(CustomMetric):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        update_result = result["updateCustomMetric"]
        if "customMetric" not in update_result:
            cls.raise_exception("no custom metric id returned")
        return [cls.QueryResponse(**update_result["customMetric"])], False, None
