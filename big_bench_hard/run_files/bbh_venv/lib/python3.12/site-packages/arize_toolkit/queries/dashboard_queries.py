from typing import List, Optional, Tuple

from arize_toolkit.models import (
    BarChartWidget,
    CreateLineChartWidgetMutationInput,
    Dashboard,
    DashboardBasis,
    DashboardPerformanceSlice,
    ExperimentChartWidget,
    LineChartWidget,
    Model,
    StatisticWidget,
    TextWidget,
    WidgetBasis,
)
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetAllDashboardsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboards($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                dashboards(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + DashboardBasis.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all dashboards in a space"

    class Variables(BaseVariables):
        spaceId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting all dashboards in a space"

    class QueryResponse(DashboardBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["dashboards"]["edges"]:
            return [], False, None

        dashboard_edges = result["node"]["dashboards"]["edges"]
        has_next_page = result["node"]["dashboards"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["dashboards"]["pageInfo"]["endCursor"]
        dashboards = [cls.QueryResponse(**dashboard["node"]) for dashboard in dashboard_edges]
        return dashboards, has_next_page, end_cursor


class GetDashboardByIdQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardById($dashboardId: ID!) {
        node(id: $dashboardId) {
            ... on Dashboard {"""
        + DashboardBasis.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a detailed dashboard by ID with all widget connections"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard by ID"

    class QueryResponse(Dashboard):
        pass


class GetDashboardQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardByName($spaceId: ID!, $dashboardName: String!) {
        node(id: $spaceId) {
            ... on Space {
                dashboards(search: $dashboardName, first: 1) {
                    edges {
                        node {"""
        + DashboardBasis.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a dashboard by name"

    class Variables(BaseVariables):
        spaceId: str
        dashboardName: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard by name"

    class QueryResponse(DashboardBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["dashboards"]["edges"]:
            cls.raise_exception("No dashboard found with the given name")

        dashboard_node = result["node"]["dashboards"]["edges"][0]["node"]
        return [cls.QueryResponse(**dashboard_node)], False, None


# Get Models used in a dashboard


class GetDashboardModelsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardModels($dashboardId: ID!) {
        node(id: $dashboardId) {
            ... on Dashboard {
                models {
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
    query_description = "Get models used in a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard models"

    class QueryResponse(Model):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["models"]["edges"]:
            cls.raise_exception("No models found in the dashboard")

        model_edges = result["node"]["models"]["edges"]
        models = [cls.QueryResponse(**model["node"]) for model in model_edges]
        return models, False, None


# Widget-specific queries for paginated retrieval


class GetDashboardStatisticWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardStatisticWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                statisticWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + StatisticWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated statistic widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard statistic widgets"

    class QueryResponse(StatisticWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["statisticWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["statisticWidgets"]["edges"]
        has_next_page = result["node"]["statisticWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["statisticWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardLineChartWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                lineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + LineChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["lineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["lineChartWidgets"]["edges"]
        has_next_page = result["node"]["lineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["lineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardBarChartWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardBarChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                barChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + BarChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated bar chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard bar chart widgets"

    class QueryResponse(BarChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["barChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["barChartWidgets"]["edges"]
        has_next_page = result["node"]["barChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["barChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardTextWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardTextWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                textWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + TextWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated text widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard text widgets"

    class QueryResponse(TextWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["textWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["textWidgets"]["edges"]
        has_next_page = result["node"]["textWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["textWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardExperimentChartWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardExperimentChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                experimentChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + ExperimentChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated experiment chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard experiment chart widgets"

    class QueryResponse(ExperimentChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["experimentChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["experimentChartWidgets"]["edges"]
        has_next_page = result["node"]["experimentChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["experimentChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardDriftLineChartWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardDriftLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                driftLineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + LineChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated drift line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard drift line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["driftLineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["driftLineChartWidgets"]["edges"]
        has_next_page = result["node"]["driftLineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["driftLineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardMonitorLineChartWidgetsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardMonitorLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                monitorLineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + LineChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get paginated monitor line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard monitor line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["monitorLineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["monitorLineChartWidgets"]["edges"]
        has_next_page = result["node"]["monitorLineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["monitorLineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class LineChartWidgetQuery(BaseQuery):
    graphql_query = (
        """
    query getLineChartWidget($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                lineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + LineChartWidget.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a line chart widget by ID"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting line chart widget"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["lineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["lineChartWidgets"]["edges"]
        has_next_page = result["node"]["lineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["lineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [cls.QueryResponse(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardPerformanceSlicesQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardPerformanceSlices($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                performanceSlices(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + DashboardPerformanceSlice.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a line chart widget by ID"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting line chart widget"

    class QueryResponse(DashboardPerformanceSlice):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        pageInfo = result["node"]["performanceSlices"]["pageInfo"]
        edges = result["node"]["performanceSlices"]["edges"]
        performance_slices = []
        if len(edges) > 0:
            performance_slices = [cls.QueryResponse(**edge["node"]) for edge in edges]
        return performance_slices, pageInfo["hasNextPage"], pageInfo["endCursor"]


## Dashboard Mutations ##


class CreateDashboardMutation(BaseQuery):
    graphql_query = """
    mutation CreateDashboard($input: CreateDashboardMutationInput!) {
        createDashboard(input: $input) {
            dashboard {
                id
                name
                status
                createdAt
            }
            clientMutationId
        }
    }
    """
    query_description = "Create a new dashboard in a space"

    class Variables(BaseVariables):
        name: str
        spaceId: str
        clientMutationId: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error creating dashboard"

    class QueryResponse(BaseResponse):
        id: str
        name: str
        status: Optional[str] = None
        createdAt: Optional[str] = None

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result.get("createDashboard", {})
        if "dashboard" not in create_result:
            cls.raise_exception("No dashboard created")

        dashboard = create_result["dashboard"]
        return (
            [cls.QueryResponse(**dashboard)],
            False,
            None,
        )


class CreateLineChartWidgetMutation(BaseQuery):
    graphql_query = (
        """
    mutation CreateLineChartWidget($input: CreateLineChartWidgetMutationInput!) {
        createLineChartWidget(input: $input) {
            lineChartWidget {"""
        + WidgetBasis.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Create a line chart widget on a dashboard"

    class Variables(CreateLineChartWidgetMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error creating line chart widget"

    class QueryResponse(WidgetBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result.get("createLineChartWidget", {})
        if "lineChartWidget" not in create_result:
            cls.raise_exception("No line chart widget created")

        widget = create_result["lineChartWidget"]
        return (
            [cls.QueryResponse(**widget)],
            False,
            None,
        )
