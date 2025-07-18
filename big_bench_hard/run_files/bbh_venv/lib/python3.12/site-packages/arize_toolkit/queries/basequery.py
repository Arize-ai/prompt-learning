from time import sleep
from typing import List, Optional, Tuple

from gql import Client as GraphQLClient
from gql import gql

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.utils import Dictable


class BaseVariables(Dictable):
    """Base class for all query variables"""

    endCursor: Optional[str] = None


class BaseResponse(Dictable):
    """Base class for all query responses"""

    pass


class BaseQuery:
    """Base class for all queries"""

    graphql_query: str
    query_description: str

    class Variables(BaseVariables):
        """Validation for the query variables"""

        pass

    class QueryException(ArizeAPIException):
        """Exception for the query"""

        pass

    class QueryResponse(BaseResponse):
        """Response for the query"""

        pass

    @classmethod
    def _graphql_query(cls, client: GraphQLClient, **kwargs) -> Tuple[List[QueryResponse], bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)
            variable_values = cls.Variables(**kwargs).to_dict(exclude_none=False)
            result = client.execute(
                query,
                variable_values=variable_values,
            )
            if "errors" in result:
                cls.raise_exception(str(result["errors"]))
            return cls._parse_graphql_result(result)
        except ArizeAPIException as qe:
            raise qe
        except Exception as e:
            cls.raise_exception(str(e))

    @classmethod
    def _graphql_mutation(cls, client: GraphQLClient, **kwargs) -> Tuple[List[QueryResponse], bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)
            variable_values = cls.Variables(**kwargs).to_dict(exclude_none=True)
            result = client.execute(
                query,
                variable_values={"input": variable_values},
            )
            if "errors" in result:
                cls.raise_exception(str(result["errors"]))
            return cls._parse_graphql_result(result)
        except ArizeAPIException as qe:
            raise qe
        except Exception as e:
            cls.raise_exception(str(e))

    @classmethod
    def run_graphql_query(cls, client: GraphQLClient, **kwargs) -> QueryResponse:
        response, _, _ = cls._graphql_query(client, **kwargs)
        return response[0]

    @classmethod
    def run_graphql_query_to_list(cls, client: GraphQLClient, **kwargs) -> List[QueryResponse]:
        response, _, _ = cls._graphql_query(client, **kwargs)
        return response

    @classmethod
    def run_graphql_mutation(cls, client, **kwargs) -> QueryResponse:
        response, _, _ = cls._graphql_mutation(client, **kwargs)
        return response[0]

    @classmethod
    def iterate_over_pages(cls, client: GraphQLClient, sleep_time: int = 0, **kwargs) -> List[QueryResponse]:
        result = []
        cursorCount = 100
        currentPage, hasNextPage, endCursor = cls._graphql_query(client, **kwargs)
        result.extend(currentPage)
        while hasNextPage and cursorCount > 0:
            currentPage, hasNextPage, endCursor = cls._graphql_query(client, endCursor=endCursor, **kwargs)
            result.extend(currentPage)
            cursorCount -= 1
            sleep(sleep_time)
        return result

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        # Default behavior for queries of objects by id
        if "node" in result and result["node"] is not None:
            result_node = result["node"]
            return [cls.QueryResponse(**result_node)], False, None
        else:
            cls.raise_exception("Object not found")

    @classmethod
    def raise_exception(cls, details: Optional[str] = None) -> None:
        raise cls.QueryException(details=details) from None
