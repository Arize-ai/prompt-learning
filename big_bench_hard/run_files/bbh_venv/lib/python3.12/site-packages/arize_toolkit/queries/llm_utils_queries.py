from typing import List, Optional, Tuple

from arize_toolkit.models import AnnotationMutationInput, CreatePromptMutationInput, CreatePromptVersionMutationInput, Prompt, PromptVersion
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class CreateAnnotationMutation(BaseQuery):
    graphql_query = """
    mutation createAnnotation($input: UpdateAnnotationsInput!) {
        updateAnnotations(input: $input) {
            clientMutationId
        }
    }
    """
    query_description = "Create an annotation for a model"

    class Variables(AnnotationMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating an annotation for a model"

    class QueryResponse(BaseResponse):
        success: bool

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "updateAnnotations" not in result:
            cls.raise_exception("No annotations updated")
        return [cls.QueryResponse(success=True)], False, None


class GetPromptByIDQuery(BaseQuery):
    graphql_query = (
        """
    query getPromptById($prompt_id: ID!) {
        node(id: $prompt_id) {
            ... on Prompt {"""
        + Prompt.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a prompt by ID"

    class Variables(BaseVariables):
        prompt_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting a prompt by ID"

    class QueryResponse(Prompt):
        pass


class GetPromptQuery(BaseQuery):
    graphql_query = (
        """
    query getPrompt($space_id: ID!, $prompt_name: String!) {
        node(id: $space_id) {
            ... on Space {
                prompts(search: $prompt_name, first: 1) {
                    edges {
                        node {"""
        + Prompt.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a prompt by name"

    class Variables(BaseVariables):
        space_id: str
        prompt_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting a prompt by name"

    class QueryResponse(Prompt):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["prompts"]["edges"] or len(result["node"]["prompts"]["edges"]) == 0:
            cls.raise_exception("No prompts found")
        prompt = result["node"]["prompts"]["edges"][0]["node"]
        return [cls.QueryResponse(**prompt)], False, None


class GetPromptVersionByIDQuery(BaseQuery):
    graphql_query = (
        """
    query getPromptVersionById($prompt_version_id: ID!) {
        node(id: $prompt_version_id) {
            ... on PromptVersion {"""
        + PromptVersion.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a prompt version by ID"

    class Variables(BaseVariables):
        prompt_version_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting a prompt version by ID"

    class QueryResponse(PromptVersion):
        pass


class GetAllPromptVersionsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllPromptVersions($space_id: ID!, $prompt_name: String!, $endCursor: String) {
        node(id: $space_id) {
            ... on Space {
                prompts(search: $prompt_name, first: 1) {
                    edges {
                        node {
                            versionHistory(first: 10, after: $endCursor) {
                                pageInfo {
                                    hasNextPage
                                    endCursor
                                }
                                edges {
                                    node {"""
        + PromptVersion.to_graphql_fields()
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
    query_description = "Get all prompt versions"

    class Variables(BaseVariables):
        space_id: str
        prompt_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error in getting all prompt versions"

    class QueryResponse(PromptVersion):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["prompts"]["edges"] or len(result["node"]["prompts"]["edges"]) == 0:
            cls.raise_exception("No prompts found")
        prompt = result["node"]["prompts"]["edges"][0]["node"]
        version_edges = prompt["versionHistory"]["edges"]
        if len(version_edges) == 0:
            cls.raise_exception("No versions found")
        has_next_page = prompt["versionHistory"]["pageInfo"]["hasNextPage"]
        end_cursor = prompt["versionHistory"]["pageInfo"]["endCursor"]
        versions = [cls.QueryResponse(**version["node"]) for version in version_edges]
        return versions, has_next_page, end_cursor


class GetAllPromptsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllPrompts($space_id: ID!, $endCursor: String) {
        node(id: $space_id) {
            ... on Space {
                prompts(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {"""
        + Prompt.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all prompts in a space"

    class Variables(BaseVariables):
        space_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting all prompts in a space"

    class QueryResponse(Prompt):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["prompts"]["edges"] or len(result["node"]["prompts"]["edges"]) == 0:
            cls.raise_exception("No prompts found")
        prompt_edges = result["node"]["prompts"]["edges"]
        has_next_page = result["node"]["prompts"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["prompts"]["pageInfo"]["endCursor"]
        prompts = [cls.QueryResponse(**prompt["node"]) for prompt in prompt_edges]
        return prompts, has_next_page, end_cursor


class CreatePromptMutation(BaseQuery):
    graphql_query = (
        """
    mutation createPrompt($input: CreatePromptMutationInput!) {
        createPrompt(input: $input) {
            prompt {"""
        + Prompt.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Create a prompt"

    class Variables(CreatePromptMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating a prompt"

    class QueryResponse(Prompt):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createPrompt" not in result:
            cls.raise_exception("No prompt created")
        return [cls.QueryResponse(**result["createPrompt"]["prompt"])], False, None


class CreatePromptVersionMutation(BaseQuery):
    graphql_query = (
        """
    mutation createPromptVersion($input: CreatePromptVersionMutationInput!) {
        createPromptVersion(input: $input) {
            promptVersion {"""
        + PromptVersion.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Create a prompt version"

    class Variables(CreatePromptVersionMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating a prompt version"

    class QueryResponse(PromptVersion):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createPromptVersion" not in result:
            cls.raise_exception("No prompt version created")
        return (
            [cls.QueryResponse(**result["createPromptVersion"]["promptVersion"])],
            False,
            None,
        )


class UpdatePromptMutation(BaseQuery):
    graphql_query = (
        """
    mutation editPrompt($input: EditPromptMutationInput!) {
        editPrompt(input: $input) {
            prompt {"""
        + Prompt.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Update a prompt"

    class Variables(BaseVariables):
        spaceId: str
        promptId: str
        name: str
        description: Optional[str]
        tags: Optional[List[str]]

    class QueryException(ArizeAPIException):
        message: str = "Error in updating a prompt"

    class QueryResponse(Prompt):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "editPrompt" not in result:
            cls.raise_exception("No prompt updated")
        return [cls.QueryResponse(**result["editPrompt"]["prompt"])], False, None


class DeletePromptMutation(BaseQuery):
    graphql_query = """
    mutation deletePrompt($input: DeletePromptMutationInput!) {
        deletePrompt(input: $input) {
            clientMutationId
        }
    }
    """
    query_description = "Delete a prompt"

    class Variables(BaseVariables):
        promptId: str
        spaceId: str

    class QueryException(ArizeAPIException):
        message: str = "Error in deleting a prompt"

    class QueryResponse(BaseResponse):
        success: bool

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "deletePrompt" not in result:
            cls.raise_exception("No prompt deleted")
        return (
            [cls.QueryResponse(success=result["deletePrompt"].get("success", False))],
            False,
            None,
        )
