from typing import List, Optional, Tuple

from arize_toolkit.models import FileImportJob, FileImportJobCheck, FileImportJobInput, FullSchema, TableImportJob, TableImportJobCheck, TableImportJobInput
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetFileImportJobQuery(BaseQuery):
    """Query for getting a file import job status."""

    graphql_query = (
        """
    query GetFileImportJobStatus($spaceId: ID!, $jobId: String!) {
        node(id: $spaceId) {
            ... on Space {
                importJobs(search: $jobId, first: 1) {
                    edges {
                        node {
                            """
        + FileImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a file import job"

    class Variables(BaseVariables):
        spaceId: str
        jobId: str

    class QueryException(ArizeAPIException):
        """Exception raised when file import job status check fails."""

        message: str = "Error getting file import job"

    class QueryResponse(FileImportJob):
        """Response from getting a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJob response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "importJobs" not in result["node"] or not result["node"]["importJobs"]["edges"]:
            cls.raise_exception("No import jobs found")

        job_data = result["node"]["importJobs"]["edges"][0]["node"]
        if not job_data:
            cls.raise_exception("No file import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetAllFileImportJobsQuery(BaseQuery):
    """Query for getting all file import jobs."""

    graphql_query = (
        """
    query GetAllFileImportJobs($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                importJobs(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            """
        + FileImportJobCheck.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all file import jobs"

    class Variables(BaseVariables):
        """Input variables for getting all file import jobs."""

        spaceId: str

    class QueryException(ArizeAPIException):
        """Exception raised when getting all file import jobs fails."""

        message: str = "Error getting all file import jobs"

    class QueryResponse(FileImportJob):
        """Response from a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJobCheck response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "importJobs" not in result["node"] or not result["node"]["importJobs"]["edges"]:
            cls.raise_exception("No import jobs found")

        edges = result["node"]["importJobs"]["edges"]
        page_info = result["node"]["importJobs"]["pageInfo"]
        job_data = [cls.QueryResponse(**job["node"]) for job in edges]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return job_data, has_next_page, end_cursor


class CreateFileImportJobMutation(BaseQuery):
    """Mutation for creating a file import job."""

    graphql_query = (
        """
    mutation CreateFileImportJob($input: CreateFileImportJobInput!) {
        createFileImportJob(input: $input) {
            fileImportJob { """
        + FileImportJobCheck.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create a new file import job"

    class Variables(FileImportJobInput):
        """Input variables for creating a file import job."""

        pass

    class QueryException(ArizeAPIException):
        """Exception raised when file import job creation fails."""

        message: str = "Error creating file import job"

    class QueryResponse(FileImportJobCheck):
        """Response from creating a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJob response."""
        if "createFileImportJob" not in result:
            cls.raise_exception("No file import job created")

        job_data = result["createFileImportJob"]["fileImportJob"]
        if not job_data:
            cls.raise_exception("No file import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetTableImportJobQuery(BaseQuery):
    """Query for getting a table import job status."""

    graphql_query = (
        """
    query GetTableImportJobStatus($spaceId: ID!, $jobId: String!) {
        node(id: $spaceId) {
            ... on Space {
                tableJobs(search: $jobId, first: 1) {
                    edges {
                        node {
                            """
        + TableImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a table import job"

    class Variables(BaseVariables):
        """Input variables for getting a table import job."""

        spaceId: str
        jobId: str

    class QueryException(ArizeAPIException):
        """Exception raised when table import job status check fails."""

        message: str = "Error getting table import job"

    class QueryResponse(TableImportJob):
        """Response from getting a table import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJob response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "tableJobs" not in result["node"] or not result["node"]["tableJobs"]["edges"]:
            cls.raise_exception("No table import jobs found")

        job_data = result["node"]["tableJobs"]["edges"][0]["node"]
        if not job_data:
            cls.raise_exception("No table import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetAllTableImportJobsQuery(BaseQuery):
    """Query for getting all table import jobs."""

    graphql_query = (
        """
    query GetAllTableImportJobs($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                tableJobs(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            """
        + TableImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all table import jobs"

    class Variables(BaseVariables):
        """Input variables for getting all table import jobs."""

        spaceId: str

    class QueryException(ArizeAPIException):
        """Exception raised when getting all table import jobs fails."""

        message: str = "Error getting all table import jobs"

    class QueryResponse(TableImportJob):
        """Response from getting all table import jobs."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJobCheck response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "tableJobs" not in result["node"] or not result["node"]["tableJobs"]["edges"]:
            cls.raise_exception("No table import jobs found")

        edges = result["node"]["tableJobs"]["edges"]
        page_info = result["node"]["tableJobs"]["pageInfo"]
        job_data = [cls.QueryResponse(**job["node"]) for job in edges]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return job_data, has_next_page, end_cursor


class CreateTableImportJobMutation(BaseQuery):
    """Mutation for creating a table import job."""

    graphql_query = (
        """
    mutation CreateTableImportJob($input: CreateTableImportJobInput!) {
        createTableImportJob(input: $input) {
            tableImportJob { """
        + TableImportJobCheck.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create a new table import job"

    class Variables(TableImportJobInput):
        """Input variables for creating a table import job."""

        pass

    class QueryException(ArizeAPIException):
        """Exception raised when table import job creation fails."""

        message: str = "Error creating table import job"

    class QueryResponse(TableImportJobCheck):
        """Response from creating a table import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJobCheck response."""
        if "createTableImportJob" not in result:
            cls.raise_exception("No table import job created")
        import_job = result["createTableImportJob"]

        if "tableImportJob" not in import_job:
            cls.raise_exception("No table import job data returned")

        job_data = import_job["tableImportJob"]

        return [cls.QueryResponse(**job_data)], False, None


class UpdateFileImportJobMutation(BaseQuery):
    """Mutation for updating a file import job."""

    graphql_query = (
        """
    mutation UpdateFileImportJob(
        $jobId: ID!,
        $jobStatus: JobStatus,
        $modelSchema: FileImportSchemaInputType!
    ){
        updateFileImportJob(
            input: {
                jobId: $jobId
                jobStatus: $jobStatus,
                schema: $modelSchema
            }
        ){
            fileImportJob{ """
        + FileImportJobCheck.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Update a file import job"

    class Variables(BaseVariables):
        """Input variables for updating a file import job."""

        jobId: str
        jobStatus: Optional[str] = None
        modelSchema: FullSchema

    class QueryException(ArizeAPIException):
        """Exception raised when file import job update fails."""

        message: str = "Error updating file import job"

    class QueryResponse(FileImportJobCheck):
        """Response from updating a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a response."""
        if "updateFileImportJob" not in result:
            cls.raise_exception("No update file import job response")

        update_response = result["updateFileImportJob"]
        if "fileImportJob" not in update_response:
            cls.raise_exception("No file import job data returned")

        job_data = update_response["fileImportJob"]
        return [cls.QueryResponse(**job_data)], False, None


class UpdateTableImportJobMutation(BaseQuery):
    """Mutation for updating a table import job."""

    graphql_query = (
        """
    mutation UpdateTableImportJob(
        $jobId: ID!,
        $jobStatus: JobStatus,
        $modelVersion: String,
        $modelSchema: TableImportSchemaInputType!,
        $refreshInterval: Int,
        $queryWindowSize: Int
    ){
        updateTableImportJob(
            input: {
                jobId: $jobId
                jobStatus: $jobStatus,
                modelVersion: $modelVersion,
                schema: $modelSchema,
                tableIngestionParameters: {
                    refreshIntervalMinutes: $refreshInterval,
                    queryWindowSizeHours: $queryWindowSize
                }
            }
        ){
            tableImportJob{"""
        + TableImportJobCheck.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Update a table import job"

    class Variables(BaseVariables):
        """Input variables for updating a table import job."""

        jobId: str
        jobStatus: Optional[str] = None
        modelVersion: Optional[str] = None
        modelSchema: FullSchema
        refreshInterval: Optional[int] = None
        queryWindowSize: Optional[int] = None

    class QueryException(ArizeAPIException):
        """Exception raised when table import job update fails."""

        message: str = "Error updating table import job"

    class QueryResponse(TableImportJobCheck):
        """Response from updating a table import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a response."""
        if "updateTableImportJob" not in result:
            cls.raise_exception("No update table import job response")

        update_response = result["updateTableImportJob"]
        if "tableImportJob" not in update_response:
            cls.raise_exception("No table import job data returned")

        job_data = update_response["tableImportJob"]
        return [cls.QueryResponse(**job_data)], False, None


class DeleteFileImportJobMutation(BaseQuery):
    """Mutation for deleting a file import job."""

    graphql_query = """
    mutation DeleteFileImportJob($id: ID!) {
        deleteFileImportJob(input: { jobId: $id }) {
            fileImportJob {
                jobStatus
            }
        }
    }
    """
    query_description = "Delete a file import job"

    class Variables(BaseVariables):
        """Input variables for deleting a file import job."""

        id: str

    class QueryException(ArizeAPIException):
        """Exception raised when file import job deletion fails."""

        message: str = "Error deleting file import job"

    class QueryResponse(BaseResponse):
        """Response from deleting a file import job."""

        jobStatus: Optional[str] = None

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a response."""
        if "deleteFileImportJob" not in result:
            cls.raise_exception("No delete file import job response")

        delete_response = result["deleteFileImportJob"]
        if "fileImportJob" not in delete_response:
            cls.raise_exception("No file import job data returned")

        job_data = delete_response["fileImportJob"]
        return [cls.QueryResponse(**job_data)], False, None


class DeleteTableImportJobMutation(BaseQuery):
    """Mutation for deleting a table import job."""

    graphql_query = """
    mutation DeleteTableImportJob($id: ID!){
        deleteTableImportJob(input: { jobId: $id }){
            tableImportJob{
                jobStatus
                jobId
            }
        }
    }
    """
    query_description = "Delete a table import job"

    class Variables(BaseVariables):
        """Input variables for deleting a table import job."""

        id: str

    class QueryException(ArizeAPIException):
        """Exception raised when table import job deletion fails."""

        message: str = "Error deleting table import job"

    class QueryResponse(BaseResponse):
        """Response from deleting a table import job."""

        jobStatus: Optional[str] = None

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a response."""
        if "deleteTableImportJob" not in result:
            cls.raise_exception("No delete table import job response")

        delete_response = result["deleteTableImportJob"]
        if "tableImportJob" not in delete_response:
            cls.raise_exception("No table import job data returned")

        job_data = delete_response["tableImportJob"]
        return [cls.QueryResponse(**job_data)], False, None
