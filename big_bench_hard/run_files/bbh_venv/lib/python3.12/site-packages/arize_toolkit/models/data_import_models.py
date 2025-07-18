from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import Field, model_validator

from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType, TableStore
from arize_toolkit.utils import GraphQLModel

## File Import GraphQL Models ##


class EmbeddingFeatureInput(GraphQLModel):
    """Input model for embedding features in file import."""

    featureName: str = Field(description="The embedding feature name")
    vectorCol: str = Field(description="The name of the vector column")
    rawDataCol: str = Field(description="The name of the raw data column for text")
    linkToDataCol: str = Field(description="The name of the link to data column for images")


class AzureStorageIdentifierInput(GraphQLModel):
    """Input model for Azure storage identifier in file import."""

    tenantId: str = Field(description="The tenant ID of the storage account")
    storageAccountName: str = Field(description="The name of the storage account")


class ObjectDetectionInput(GraphQLModel):
    """Input model for object detection file import."""

    boundingBoxesCoordinatesColumnName: str = Field(description="Column name for bounding box coordinates")
    boundingBoxesCategoriesColumnName: str = Field(description="Column name for bounding box categories")
    boundingBoxesScoresColumnName: Optional[str] = Field(default=None, description="Column name for bounding box scores")


class BaseModelSchema(GraphQLModel):
    """Base model schema."""

    predictionId: Optional[str] = Field(default=None, description="Column name for prediction ID")
    timestamp: Optional[str] = Field(default=None, description="Column name for timestamp")

    tags: Optional[str] = Field(default=None, description="Prefix for tag column names")
    tagsList: Optional[List[str]] = Field(default=None, description="List of tag column names")

    features: Optional[str] = Field(default=None, description="Prefix for feature column names")

    featuresList: Optional[List[str]] = Field(default=None, description="List of feature column names")

    embeddingFeatures: Optional[Union[List[EmbeddingFeatureInput], EmbeddingFeatureInput]] = Field(default=None, description="List of embedding feature configurations")

    version: Optional[str] = Field(default=None, description="Version of the schema")

    exclude: Optional[List[str]] = Field(default=None, description="List of column names to exclude")

    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema for validation data")

    shapValues: Optional[str] = Field(default=None, description="Column prefix for SHAP value columns")

    changeTimestamp: Optional[str] = Field(default=None, description="Column name for change timestamp")


class ClassificationSchemaInput(BaseModelSchema):
    """Input model for classification file import schema."""

    predictionLabel: str = Field(description="Column name for prediction label")

    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    actualLabel: Optional[str] = Field(default=None, description="Column name for actual label")


class RegressionSchemaInput(BaseModelSchema):
    """Input model for regression file import schema."""

    predictionScore: str = Field(description="Column name for prediction score")

    actualScore: Optional[str] = Field(default=None, description="Column name for actual score")


class RankSchemaInput(BaseModelSchema):
    """Input model for ranking file import schema."""

    predictionGroupId: str = Field(description="Column name for prediction group ID")

    rank: str = Field(description="Column name for rank")

    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    relevanceScore: Optional[str] = Field(default=None, description="Column name for relevance score")

    relevanceLabel: Optional[str] = Field(default=None, description="Column name for relevance label")


class MultiClassSchemaInput(BaseModelSchema):
    """Input model for multi-class file import schema."""

    predictionScores: str = Field(description="Column name for prediction scores")

    actualScores: Optional[str] = Field(default=None, description="Column name for actual scores")

    thresholdScores: Optional[str] = Field(default=None, description="Column name for threshold scores")


class ObjectDetectionSchemaInput(BaseModelSchema):
    """Input model for object detection file import schema."""

    predictionObjectDetection: ObjectDetectionInput = Field(description="Object detection prediction")
    actualObjectDetection: Optional[ObjectDetectionInput] = Field(default=None, description="Object detection actual")


class FullSchema(
    ClassificationSchemaInput,
    RegressionSchemaInput,
    RankSchemaInput,
    MultiClassSchemaInput,
    ObjectDetectionSchemaInput,
):
    """Input model for full file import schema."""

    # Override required fields from ClassificationSchemaInput
    predictionLabel: Optional[str] = Field(default=None, description="Column name for prediction label")

    # Override required fields from RegressionSchemaInput
    predictionScore: Optional[str] = Field(default=None, description="Column name for prediction score")

    # Override required fields from RankSchemaInput
    predictionGroupId: Optional[str] = Field(default=None, description="Column name for prediction group ID")
    rank: Optional[str] = Field(default=None, description="Column name for rank")

    # Override required fields from MultiClassSchemaInput
    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    # Override required fields from ObjectDetectionSchemaInput
    predictionObjectDetection: Optional[ObjectDetectionInput] = Field(default=None, description="Object detection prediction")


class FileImportJobInput(GraphQLModel):
    """Input model for creating a file import job."""

    blobStore: BlobStore = Field(description="Type of blob store (s3, gcs, or azure)")
    prefix: str = Field(description="Prefix path in the bucket")
    azureStorageIdentifier: Optional[AzureStorageIdentifierInput] = Field(default=None, description="Azure storage identifier")
    bucketName: str = Field(description="Name of the bucket")
    spaceId: str = Field(description="ID of the space")
    modelName: str = Field(description="Name of the model")
    modelVersion: Optional[str] = Field(default=None, description="Version of the model")
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")

    modelType: ModelType = Field(description="Type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="Environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    dryRun: Optional[bool] = Field(default=False, description="Whether to run the import as a dry run")


class FileImportJobCheck(GraphQLModel):
    """Model representing a file import status check."""

    id: str = Field(description="The import job's unique identifier")
    jobId: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    totalFilesPendingCount: int = Field(description="Number of files pending import")
    totalFilesSuccessCount: int = Field(description="Number of files successfully imported")
    totalFilesFailedCount: int = Field(description="Number of files that failed to import")


class FileImportJob(FileImportJobCheck):
    """Model representing a file import job."""

    jobId: str = Field(description="The import job's unique identifier")
    createdAt: datetime = Field(description="The time the import job was created")
    modelName: str = Field(description="The name of the model")
    modelId: str = Field(description="The ID of the model")
    modelVersion: Optional[str] = Field(default=None, description="The version of the model")
    modelType: ModelType = Field(description="The type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="The environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")
    blobStore: BlobStore = Field(description="Type of blob store (s3, gcs, or azure)")
    bucketName: str = Field(description="Name of the bucket")
    prefix: str = Field(description="Prefix path in the bucket")


class BigQueryTableConfig(GraphQLModel):
    """Input model for BigQuery table configuration."""

    projectId: str = Field(description="Project ID of the BigQuery table")
    dataset: str = Field(description="Dataset of the BigQuery table")
    tableName: str = Field(description="Table name of the BigQuery table")


class SnowflakeTableConfig(GraphQLModel):
    """Input model for Snowflake table configuration."""

    accountID: str = Field(description="Database of the Snowflake table")
    snowflakeSchema: str = Field(
        alias="schema",
        alias_priority=1,
        description="Schema of the Snowflake table",
    )
    database: str = Field(description="Database of the Snowflake table")
    tableName: str = Field(description="Table name of the Snowflake table")


class DatabricksTableConfig(GraphQLModel):
    """Input model for Databricks table configuration."""

    hostName: str = Field(description="Host name of the Databricks table")
    endpoint: str = Field(description="Endpoint of the Databricks table")
    port: str = Field(description="Port of the Databricks table")
    token: Optional[str] = Field(default=None, description="Token of the Databricks table")
    azureResourceId: Optional[str] = Field(default=None, description="Azure resource ID of the Databricks table")
    azureTenantId: Optional[str] = Field(default=None, description="Azure tenant ID of the Databricks table")
    catalog: str = Field(description="Catalog of the Databricks table")
    databricksSchema: str = Field(description="Databricks schema of the table")
    tableName: str = Field(description="Table name of the Databricks table")


class TableIngestionParameters(GraphQLModel):
    """Input model for table ingestion parameters."""

    refreshIntervalSeconds: int = Field(description="Refresh interval in seconds")
    queryWindowSizeSeconds: int = Field(description="Query window size in seconds")


class TableImportJobInput(GraphQLModel):
    """Input model for creating a table import job."""

    tableStore: TableStore = Field(description="Type of table store (bigquery, snowflake, or databricks)")
    bigQueryTableConfig: Optional[BigQueryTableConfig] = Field(default=None, description="BigQuery table configuration")
    snowflakeTableConfig: Optional[SnowflakeTableConfig] = Field(default=None, description="Snowflake table configuration")
    databricksTableConfig: Optional[DatabricksTableConfig] = Field(default=None, description="Databricks table configuration")
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")
    spaceId: str = Field(description="ID of the space")
    modelName: str = Field(description="Name of the model")
    modelVersion: Optional[str] = Field(default=None, description="Version of the model")
    modelType: ModelType = Field(description="Type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="Environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    dryRun: Optional[bool] = Field(default=False, description="Whether to run the import as a dry run")

    @model_validator(mode="after")
    def validate_table_config(self) -> "TableImportJobInput":
        """Validate that the appropriate table config is provided based on tableStore."""
        if self.tableStore == TableStore.BigQuery and not self.bigQueryTableConfig:
            raise ValueError("bigQueryTableConfig is required for BigQuery table store")
        if self.tableStore == TableStore.Snowflake and not self.snowflakeTableConfig:
            raise ValueError("snowflakeTableConfig is required for Snowflake table store")
        if self.tableStore == TableStore.Databricks and not self.databricksTableConfig:
            raise ValueError("databricksTableConfig is required for Databricks table store")
        return self


class TableImportJob(GraphQLModel):
    id: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    jobId: str = Field(description="The import job's unique identifier")
    createdAt: datetime = Field(description="The time the import job was created")
    modelName: str = Field(description="The name of the model")
    modelId: str = Field(description="The ID of the model")
    modelVersion: Optional[str] = Field(default=None, description="The version of the model")
    modelType: ModelType = Field(description="The type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="The environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    batchId: Optional[str] = Field(default=None, description="Batch ID for validation data")
    table: str = Field(description="The name of the table")
    tableStore: TableStore = Field(description="The type of table store")
    projectId: str = Field(description="Project ID of the table")
    dataset: str = Field(description="Dataset of the table")
    totalQueriesSuccessCount: int = Field(description="Number of queries successfully executed")
    totalQueriesFailedCount: int = Field(description="Number of queries failed to execute")
    totalQueriesPendingCount: int = Field(description="Number of queries pending execution")
    tableIngestionParameters: Optional[TableIngestionParameters] = Field(default=None, description="Table ingestion parameters")


class TableImportJobCheck(GraphQLModel):
    """Model representing a table import job status check."""

    id: str = Field(description="The import job's unique identifier")
    jobId: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    totalQueriesSuccessCount: int = Field(description="Number of queries successfully executed")
    totalQueriesFailedCount: int = Field(description="Number of queries failed to execute")
    totalQueriesPendingCount: int = Field(description="Number of queries pending execution")
