from datetime import datetime
from typing import List, Optional

from pydantic import Field

from arize_toolkit.models.base_models import BaseNode, Dimension, DimensionValue, Model, User

# Import common models that are used by dashboard models
from arize_toolkit.models.custom_metrics_models import CustomMetric
from arize_toolkit.models.space_models import Space
from arize_toolkit.types import (
    BarChartWidgetDataValueObjectType,
    DashboardStatus,
    DataQualityMetric,
    DimensionCategory,
    ModelEnvironment,
    ModelType,
    PerformanceMetric,
    TimeSeriesMetricCategory,
    WidgetCreationStatus,
)
from arize_toolkit.utils import GraphQLModel

## Dashboard GraphQL Models ##


class DashboardBasis(BaseNode):
    creator: Optional[User] = Field(default=None, description="The user who created the dashboard")
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the dashboard was created")
    status: Optional[DashboardStatus] = Field(default=None, description="The status of the dashboard")


class WidgetBasis(GraphQLModel):
    """Base model for dashboard widgets with common fields"""

    id: str = Field(description="The ID of the widget")
    dashboardId: Optional[str] = Field(default=None, description="The dashboard ID of the widget")
    title: Optional[str] = Field(default=None, description="The title of the widget")
    gridPosition: Optional[List[int]] = Field(default=None, description="The grid position of the widget")
    creationStatus: Optional[WidgetCreationStatus] = Field(default=None, description="The creation status of the widget")


# Supporting models for widgets
class WidgetModel(GraphQLModel):
    """A model on a dashboard widget"""

    id: Optional[str] = Field(default=None, description="The ID of the widget model")
    externalModelId: Optional[str] = Field(default=None, description="The external model ID")
    createdAt: Optional[datetime] = Field(default=None, description="When the model was created")
    modelType: Optional[ModelType] = Field(default=None, description="The type of the model")


class PredictionValueClass(BaseNode):
    """A prediction value class"""

    pass


class StatisticWidgetFilterItem(GraphQLModel):
    """Filter item for statistic widgets"""

    id: Optional[str] = Field(default=None, description="The ID of the filter item")
    filterType: Optional[str] = Field(default=None, description="The type of filter")
    operator: Optional[str] = Field(default=None, description="The comparison operator")
    dimension: Optional[Dimension] = Field(
        default=None,
        description="The dimension being filtered",
    )
    dimensionValues: Optional[List[DimensionValue]] = Field(default=None, description="The dimension values")
    binaryValues: Optional[List[str]] = Field(default=None, description="Binary values for filter")
    numericValues: Optional[List[str]] = Field(default=None, description="Numeric values for filter")
    categoricalValues: Optional[List[str]] = Field(default=None, description="Categorical values for filter")


class BarChartPlot(GraphQLModel):
    """A plot within a bar chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    modelId: Optional[str] = Field(default=None, description="The model ID for the plot")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category")
    aggregation: Optional[DataQualityMetric] = Field(default=None, description="The aggregation type")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    predictionValueClass: Optional[PredictionValueClass] = Field(default=None, description="The prediction value class")
    rankingAtK: Optional[int] = Field(default=None, description="The ranking at K value")
    colors: Optional[List[str]] = Field(default=None, description="Colors for the plot")


class BarChartWidgetAxisConfig(GraphQLModel):
    """Axis configuration for bar chart widgets"""

    legend: Optional[str] = Field(default=None, description="The axis legend")


class BarChartWidgetConfig(GraphQLModel):
    """Configuration for bar chart widgets"""

    keys: Optional[List[str]] = Field(default=None, description="The keys for the chart")
    indexBy: Optional[str] = Field(default=None, description="The index by field")
    axisBottom: Optional[BarChartWidgetAxisConfig] = Field(default=None, description="Bottom axis configuration")
    axisLeft: Optional[BarChartWidgetAxisConfig] = Field(default=None, description="Left axis configuration")


class LineChartPlot(GraphQLModel):
    """A plot within a line chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    modelId: Optional[str] = Field(default=None, description="The model ID for the plot")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category")
    splitByEnabled: Optional[bool] = Field(default=None, description="Whether split by is enabled")
    splitByDimension: Optional[str] = Field(default=None, description="The split by dimension")
    splitByDimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The split by dimension category")
    splitByOverallMetricEnabled: Optional[bool] = Field(default=None, description="Whether split by overall metric is enabled")
    cohorts: Optional[List[str]] = Field(default=None, description="Cohorts for the plot")
    colors: Optional[List[str]] = Field(default=None, description="Colors for the plot")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    predictionValueClass: Optional[PredictionValueClass] = Field(default=None, description="The prediction value class")
    rankingAtK: Optional[int] = Field(default=None, description="The ranking at K value")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")


class LineChartWidgetAxisConfig(GraphQLModel):
    """Axis configuration for line chart widgets"""

    legend: Optional[str] = Field(default=None, description="The axis legend")


class LineChartWidgetXScaleConfig(GraphQLModel):
    """X-axis scale configuration for line chart widgets"""

    max: Optional[str] = Field(default=None, description="Maximum value")
    min: Optional[str] = Field(default=None, description="Minimum value")
    scaleType: Optional[str] = Field(default=None, description="Scale type")
    format: Optional[str] = Field(default=None, description="Format string")
    precision: Optional[str] = Field(default=None, description="Precision type")


class LineChartWidgetYScaleConfig(GraphQLModel):
    """Y-axis scale configuration for line chart widgets"""

    max: Optional[str] = Field(default=None, description="Maximum value")
    min: Optional[str] = Field(default=None, description="Minimum value")
    scaleType: Optional[str] = Field(default=None, description="Scale type")
    stacked: Optional[bool] = Field(default=None, description="Whether the chart is stacked")


class LineChartWidgetConfig(GraphQLModel):
    """Configuration for line chart widgets"""

    axisBottom: Optional[LineChartWidgetAxisConfig] = Field(default=None, description="Bottom axis configuration")
    axisLeft: Optional[LineChartWidgetAxisConfig] = Field(default=None, description="Left axis configuration")
    curve: Optional[str] = Field(default=None, description="Curve type")
    xScale: Optional[LineChartWidgetXScaleConfig] = Field(default=None, description="X-axis scale configuration")
    yScale: Optional[LineChartWidgetYScaleConfig] = Field(default=None, description="Y-axis scale configuration")


class ExperimentChartPlot(GraphQLModel):
    """A plot within an experiment chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    datasetId: Optional[str] = Field(default=None, description="The dataset ID")
    evaluationMetric: Optional[str] = Field(default=None, description="The evaluation metric")


# Enhanced Widget Models
class StatisticWidget(WidgetBasis):
    """A statistic widget on a dashboard"""

    modelId: Optional[str] = Field(default=None, description="The model ID on the widget")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs on the widget")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category of the widget")
    performanceMetric: Optional[PerformanceMetric] = Field(default=None, description="The performance metric function of the widget")
    aggregation: Optional[DataQualityMetric] = Field(default=None, description="The data quality metric type of the widget")
    predictionValueClass: Optional[PredictionValueClass] = Field(default=None, description="The class of the classification model on the widget")
    rankingAtK: Optional[int] = Field(default=None, description="The @K value for the performance metric")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment of the widget")
    timeSeriesMetricType: Optional[TimeSeriesMetricCategory] = Field(default=None, description="The type of timeseries metric on the widget")
    filters: Optional[List[StatisticWidgetFilterItem]] = Field(default=None, description="Filters applied to the widget")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")
    customMetric: Optional[CustomMetric] = Field(default=None, description="Custom metric if used")


class BarChartWidget(WidgetBasis):
    """A bar chart widget on a dashboard"""

    sortOrder: Optional[str] = Field(default=None, description="Sort order for the bars")
    yMin: Optional[float] = Field(default=None, description="Minimum Y-axis value")
    yMax: Optional[float] = Field(default=None, description="Maximum Y-axis value")
    yAxisLabel: Optional[str] = Field(default=None, description="Y-axis label")
    topN: Optional[float] = Field(default=None, description="Top N value")
    isNormalized: Optional[bool] = Field(default=None, description="Whether the chart is normalized")
    binOption: Optional[str] = Field(default=None, description="Bin option")
    numBins: Optional[int] = Field(default=None, description="Number of bins")
    customBins: Optional[List[float]] = Field(default=None, description="Custom bin values")
    quantiles: Optional[List[float]] = Field(default=None, description="Quantile values")
    performanceMetric: Optional[PerformanceMetric] = Field(default=None, description="Performance metric")
    plots: Optional[List[BarChartPlot]] = Field(default=None, description="Plots in the bar chart")
    config: Optional[BarChartWidgetConfig] = Field(default=None, description="Widget configuration")


class LineChartWidget(WidgetBasis):
    """A line chart widget on a dashboard"""

    yMin: Optional[float] = Field(default=None, description="The minimum domain on the y-axis")
    yMax: Optional[float] = Field(default=None, description="The maximum domain on the y-axis")
    yAxisLabel: Optional[str] = Field(default=None, description="The label for the y-axis")
    timeSeriesMetricType: Optional[str] = Field(default=None, description="The type of timeseries metric on the widget")
    config: Optional[LineChartWidgetConfig] = Field(default=None, description="Widget configuration")
    plots: Optional[List[LineChartPlot]] = Field(default=None, description="Plots in the line chart")


class ExperimentChartWidget(WidgetBasis):
    """An experiment chart widget on a dashboard"""

    plots: Optional[List[ExperimentChartPlot]] = Field(default=None, description="Plots in the experiment chart")


class TextWidget(WidgetBasis):
    """A text widget on a dashboard"""

    content: Optional[str] = Field(default=None, description="The content of the text widget")


class BarChartWidgetDataKeysAndValuesObject(GraphQLModel):
    """An object that represents a part of the data used to render a single bar in a bar chart"""

    k: str = Field(description="A key to be used in rendering a bar chart")
    v: Optional[str] = Field(
        default=None,
        description="A value to be used in rendering a bar chart. Allows nullable values to better handle No Data cases",
    )
    vType: BarChartWidgetDataValueObjectType = Field(description="The type of the value for 'v' above: 'number' or 'string'")
    secondaryValue: Optional[str] = Field(
        default=None,
        description="A secondary value, e.g. accuracy %, to be used in rendering a bar chart",
    )
    secondaryValueType: Optional[BarChartWidgetDataValueObjectType] = Field(
        default=None,
        description="The type of the value for 'secondary value' above: 'number' or 'string'",
    )
    secondaryValueColorIndex: Optional[int] = Field(
        default=None,
        description="The color rank index of the secondary value used to color the bar",
    )
    plotKey: Optional[str] = Field(
        default=None,
        description="A user-supplied plot key (e.g. title of plot 'Prediction Class' etc.)",
    )


class BarChartWidgetData(GraphQLModel):
    """A bar chart plot on a dashboard"""

    keysAndValues: List[BarChartWidgetDataKeysAndValuesObject] = Field(description="A list of objects of the form {k: 'some_key', v: 'some_value'} that provide data for a single bar in a bar chart")
    performanceImpactValue: Optional[float] = Field(
        default=None,
        description="The performance impact value of a single bar in a bar chart",
    )
    evalMetricMin: Optional[float] = Field(
        default=None,
        description="The evaluation metric min value to be used for the heatmap legend",
    )
    evalMetricMax: Optional[float] = Field(
        default=None,
        description="The evaluation metric max value to be used for the heatmap legend",
    )


class DashboardPerformanceSlice(GraphQLModel):
    """A performance slice of a dashboard"""

    id: str = Field(description="The ID of an object")
    evalMetricMin: Optional[float] = Field(
        default=None,
        description="The evaluation metric min value to be used for the heatmap legend",
    )
    evalMetricMax: Optional[float] = Field(
        default=None,
        description="The evaluation metric max value to be used for the heatmap legend",
    )
    performanceMetric: Optional[PerformanceMetric] = Field(
        default=None,
        description="The performance metric used for the performance slice",
    )
    metricValue: Optional[str] = Field(
        default=None,
        description="A secondary value, e.g. accuracy %, to be used in rendering a bar chart",
    )
    metricValueType: Optional[BarChartWidgetDataValueObjectType] = Field(
        default=None,
        description="The type of the value for 'secondary value' above: 'number' or 'string'",
    )
    metricValueColorIndex: Optional[int] = Field(
        default=None,
        description="The color rank index of the secondary value used to color the bar",
    )
    metricValueKey: Optional[str] = Field(default=None, description="The x-axis value that this metric applies to")
    metricValueKeyType: Optional[BarChartWidgetDataValueObjectType] = Field(
        default=None,
        description="The type of metricValueKey, e.g. if metricValueKey = '0.65 to 0.89823' then metricValueKeyType = 'range'",
    )
    widget: Optional[BarChartWidget] = Field(default=None, description="The dashboard widget that this slice pertains to")
    barChartBarNode: Optional[BarChartWidgetData] = Field(
        default=None,
        description="The bar in a bar chart corresponding to this performance metric",
    )


class Dashboard(DashboardBasis):
    """Extended dashboard model with all connections"""

    space: Optional[Space] = Field(default=None, description="The space that the dashboard belongs to")
    models: Optional[List[Model]] = Field(default=None, description="A list of unique models referenced in this dashboard")
    statisticWidgets: Optional[List[StatisticWidget]] = Field(default=None, description="The statistic widgets on the dashboard")
    barChartWidgets: Optional[List[BarChartWidget]] = Field(default=None, description="The bar chart widgets on the dashboard")
    lineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The line chart widgets on the dashboard")
    experimentChartWidgets: Optional[List[ExperimentChartWidget]] = Field(default=None, description="The experiment chart widgets on the dashboard")
    driftLineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The drift line chart widgets on the dashboard")
    monitorLineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The monitor line chart widgets on the dashboard")
    textWidgets: Optional[List[TextWidget]] = Field(default=None, description="The text widgets on the dashboard")


## Dashboard Mutation Input Models ##


class CreateDashboardMutationInput(GraphQLModel):
    """Input for creating a new dashboard"""

    name: str = Field(description="The name of the dashboard")
    spaceId: str = Field(description="The ID of the space to create the dashboard in")
    clientMutationId: Optional[str] = Field(default=None, description="Client mutation ID for tracking")


class LineChartPlotInput(GraphQLModel):
    """Input for a line chart plot"""

    modelId: str = Field(description="The model ID for the plot")
    modelVersionIds: List[Optional[str]] = Field(default=[], description="The model version IDs")
    modelEnvironmentName: ModelEnvironment = Field(description="The model environment")
    title: str = Field(description="The title of the plot")
    position: int = Field(description="The position of the plot")
    metric: str = Field(description="The metric to plot")
    filters: List[StatisticWidgetFilterItem] = Field(description="Filters applied to the widget")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category of the plot")


class CreateLineChartWidgetMutationInput(GraphQLModel):
    """Input for creating a line chart widget"""

    title: str = Field(description="The title of the widget")
    dashboardId: str = Field(description="The dashboard ID to add the widget to")
    timeSeriesMetricType: str = Field(default="modelDataMetric", description="The type of time series metric")
    plots: List[LineChartPlotInput] = Field(description="The plots for the line chart")
