from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field, model_validator

from arize_toolkit.models.base_models import BaseNode, Dimension, DimensionFilterInput, DimensionValue, User
from arize_toolkit.models.custom_metrics_models import CustomMetric
from arize_toolkit.types import ComparisonOperator, DataQualityMetric, DimensionCategory, DriftMetric, FilterRowType, ModelEnvironment, MonitorCategory, PerformanceMetric
from arize_toolkit.utils import GraphQLModel

## Monitor GraphQL Models ##


class IntegrationKey(BaseNode):
    providerName: Literal["slack", "pagerduty", "opsgenie"]
    createdAt: Optional[datetime] = Field(default=None)
    channelName: Optional[str] = Field(default=None)
    alertSeverity: Optional[str] = Field(default=None)


class MonitorContact(GraphQLModel):
    id: Optional[str] = Field(default=None)
    notificationChannelType: Literal["email", "integration"]
    emailAddress: Optional[str] = Field(default=None)
    integration: Optional[IntegrationKey] = Field(default=None)


class MonitorContactInput(GraphQLModel):
    notificationChannelType: Literal["email", "integration"]
    emailAddress: Optional[str] = Field(default=None)
    integrationKeyId: Optional[str] = Field(default=None)


class MetricFilterItem(GraphQLModel):
    id: Optional[str] = Field(default=None)
    filterType: Optional[FilterRowType] = Field(default=None)
    operator: Optional[ComparisonOperator] = Field(default=None)
    dimension: Optional[Dimension] = Field(default=None)
    dimensionValues: Optional[List[DimensionValue]] = Field(default=None)
    binaryValues: Optional[List[str]] = Field(default=None)
    numericValues: Optional[List[str]] = Field(default=None)
    categoricalValues: Optional[List[str]] = Field(default=None)


class MetricWindow(GraphQLModel):
    id: Optional[str] = Field(default=None)
    type: Optional[Literal["moving", "fixed"]] = Field(default="moving")
    windowLengthMs: Optional[float] = Field(default=86400000)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimension: Optional[Dimension] = Field(default=None)
    filters: Optional[List[MetricFilterItem]] = Field(default_factory=list)


class DynamicAutoThreshold(GraphQLModel):
    stdDevMultiplier: Optional[float] = Field(default=2.0)


class BasicMonitor(BaseNode):
    monitorCategory: MonitorCategory
    createdDate: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    creator: Optional[User] = Field(default=None)


class Monitor(BasicMonitor):
    evaluationIntervalSeconds: Optional[int] = Field(default=259200)
    evaluatedAt: Optional[datetime] = Field(default=None)
    contacts: Optional[List[MonitorContact]] = Field(default=None)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    status: Optional[Literal["triggered", "cleared", "noData"]] = Field(default="noData")
    isTriggered: Optional[bool] = Field(default=False)
    isManaged: Optional[bool] = Field(default=None)
    threshold: Optional[float] = Field(default=None)
    thresholdMode: Optional[Literal["single", "range"]] = Field(default="single")
    threshold2: Optional[float] = Field(default=None)
    dynamicAutoThresholdEnabled: Optional[bool] = Field(default=False)
    stdDevMultiplier: Optional[float] = Field(default=2.0)
    stdDevMultiplier2: Optional[float] = Field(default=None)
    notificationsEnabled: Optional[bool] = Field(default=False)
    updatedAt: Optional[datetime] = Field(default=None)
    downtimeStart: Optional[datetime] = Field(default=None)
    downtimeDurationHrs: Optional[int] = Field(default=None)
    downtimeFrequencyDays: Optional[int] = Field(default=None)
    scheduledRuntimeEnabled: Optional[bool] = Field(default=False)
    scheduledRuntimeCadenceSeconds: Optional[int] = Field(default=None)
    scheduledRuntimeDaysOfWeek: Optional[List[int]] = Field(default_factory=list)
    latestComputedValue: Optional[float] = Field(default=None)
    performanceMetric: Optional[PerformanceMetric] = Field(default=None)
    dataQualityMetric: Optional[DataQualityMetric] = Field(default=None)
    driftMetric: Optional[DriftMetric] = Field(default=None)
    customMetric: Optional[CustomMetric] = Field(default=None)
    operator: ComparisonOperator = Field(default=ComparisonOperator.greaterThan)
    operator2: Optional[ComparisonOperator] = Field(default=None)
    topKPercentileValue: Optional[float] = Field(default=None)
    positiveClassValue: Optional[str] = Field(default=None)
    metricAtRankingKValue: Optional[int] = Field(default=None)
    primaryMetricWindow: Optional[MetricWindow] = Field(default=None)
    comparisonMetricWindow: Optional[MetricWindow] = Field(default=None)


class MonitorDetailedType(GraphQLModel):
    spaceId: str
    modelName: str
    name: str
    notes: Optional[str] = Field(default=None)
    contacts: Optional[List[MonitorContactInput]] = Field(default=None)
    downtimeStart: Optional[datetime] = Field(default=None)
    downtimeDurationHrs: Optional[int] = Field(default=None)
    downtimeFrequencyDays: Optional[int] = Field(default=None)
    scheduledRuntimeEnabled: Optional[bool] = Field(default=False)
    scheduledRuntimeCadenceSeconds: Optional[int] = Field(default=None)
    scheduledRuntimeDaysOfWeek: Optional[List[int]] = Field(default=None)
    evaluationWindowLengthSeconds: float = Field(default=259200)
    delaySeconds: float = Field(default=0)
    threshold: Optional[float] = Field(default=None)
    threshold2: Optional[float] = Field(default=None)
    thresholdMode: Literal["single", "range"] = Field(default="single")
    operator: ComparisonOperator = Field(default=ComparisonOperator.greaterThan)
    operator2: Optional[ComparisonOperator] = Field(default=None)
    dynamicAutoThreshold: Optional[DynamicAutoThreshold] = Field(default=None)
    stdDevMultiplier2: Optional[float] = Field(default=None)
    filters: Optional[List[DimensionFilterInput]] = Field(default=None)

    @model_validator(mode="after")
    def validate_filters(self):
        if self.threshold and self.dynamicAutoThreshold:
            self.dynamicAutoThreshold = None
        return self


class PerformanceMonitor(MonitorDetailedType):
    performanceMetric: Optional[PerformanceMetric] = Field(default=None)
    customMetricId: Optional[str] = Field(default=None)
    positiveClassValue: Optional[str] = Field(default=None)
    predictionClassValue: Optional[str] = Field(default=None)
    metricAtRankingKValue: Optional[int] = Field(default=None)
    topKPercentileValue: Optional[float] = Field(default=None)
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)


class DataQualityMonitor(MonitorDetailedType):
    dataQualityMetric: Optional[DataQualityMetric] = Field(default=None)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimensionName: Optional[str] = Field(default=None)
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)


class DriftMonitor(MonitorDetailedType):
    driftMetric: Optional[DriftMetric] = Field(default=DriftMetric.psi)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimensionName: Optional[str] = Field(default=None)


## Time Series Models ##


class DataPoint(GraphQLModel):
    """Represents a single data point in a time series."""

    x: datetime = Field(description="Timestamp of the data point")
    y: Optional[float] = Field(description="Value at this timestamp")


class TimeSeriesWithThresholdDataType(GraphQLModel):
    """Represents time series data with optional threshold data points."""

    key: str = Field(description="Key identifier for the time series")
    dataPoints: List[DataPoint] = Field(default_factory=list, description="List of data points in the time series")
    thresholdDataPoints: Optional[List[DataPoint]] = Field(default=None, description="List of threshold data points")
