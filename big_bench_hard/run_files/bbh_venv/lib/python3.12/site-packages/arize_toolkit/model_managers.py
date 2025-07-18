from typing import List, Optional

from arize_toolkit.models import (
    DataQualityMonitor,
    DimensionFilterInput,
    DriftMonitor,
    DynamicAutoThreshold,
    MetricFilterItem,
    Monitor,
    MonitorContact,
    MonitorContactInput,
    MonitorDetailedType,
    PerformanceMonitor,
)
from arize_toolkit.types import DimensionCategory, ModelEnvironment, MonitorCategory


class MonitorManager:
    @classmethod
    def process_monitors(cls, space_id: str, model_name: str, monitors: List[Monitor]) -> List[MonitorDetailedType]:
        return [cls.extract_monitor_type(space_id, model_name, monitor) for monitor in monitors]

    @classmethod
    def extract_monitor_type_from_dict(cls, space_id: str, model_name: str, monitor: dict) -> MonitorDetailedType:
        return cls.extract_monitor_type(space_id, model_name, Monitor(**monitor))

    @classmethod
    def extract_monitor_type(cls, space_id: str, model_name: str, monitor: Monitor) -> MonitorDetailedType:
        if monitor.monitorCategory == MonitorCategory.performance:
            return cls.performance_monitor(space_id, model_name, monitor)
        elif monitor.monitorCategory == MonitorCategory.dataQuality:
            return cls.data_quality_monitor(space_id, model_name, monitor)
        elif monitor.monitorCategory == MonitorCategory.drift:
            return cls.drift_monitor(space_id, model_name, monitor)
        else:
            raise ValueError("Monitor type not supported")

    @classmethod
    def create_monitor_contacts(cls, monitor_contacts: Optional[List[MonitorContact]] = None) -> MonitorContactInput:
        if monitor_contacts is None:
            return None
        else:
            contacts = []
            for monitor_contact in monitor_contacts:
                if monitor_contact.notificationChannelType == "email":
                    contacts.append(
                        MonitorContactInput(
                            notificationChannelType="email",
                            emailAddress=monitor_contact.emailAddress,
                        )
                    )
                elif monitor_contact.notificationChannelType == "integration":
                    contacts.append(
                        MonitorContactInput(
                            notificationChannelType="integration",
                            integrationKeyId=monitor_contact.integration.id,
                        )
                    )
            return contacts

    @classmethod
    def create_dimension_filters(cls, filters: Optional[List[MetricFilterItem]]) -> List[DimensionFilterInput]:
        if filters is None:
            return None
        else:
            dimension_filters = []
            for filter in filters:
                params = {
                    "dimensionType": filter.filterType,
                    "operator": filter.operator,
                }

                if filter.dimension:
                    params["name"] = filter.dimension.name

                if filter.dimensionValues:
                    params["values"] = [value.value for value in filter.dimensionValues]

                if filter.binaryValues:
                    params["values"] = filter.binaryValues

                if filter.numericValues:
                    params["values"] = filter.numericValues

                if filter.categoricalValues:
                    params["values"] = filter.categoricalValues

                dimension_filters.append(DimensionFilterInput(**params))

            return dimension_filters

    @classmethod
    def performance_monitor(cls, space_id: str, model_name: str, monitor: Monitor) -> PerformanceMonitor:
        return PerformanceMonitor(
            spaceId=space_id,
            modelName=model_name,
            name=monitor.name,
            notes=monitor.notes,
            performanceMetric=monitor.performanceMetric,
            customMetricId=monitor.customMetric.id if monitor.customMetric else None,
            positiveClassValue=monitor.positiveClassValue,
            metricAtRankingKValue=monitor.metricAtRankingKValue,
            topKPercentileValue=monitor.topKPercentileValue,
            operator=monitor.operator,
            operator2=monitor.operator2,
            stdDevMultiplier2=monitor.stdDevMultiplier2,
            threshold=monitor.threshold,
            threshold2=monitor.threshold2,
            thresholdMode=monitor.thresholdMode,
            dynamicAutoThreshold=(DynamicAutoThreshold(stdDevMultiplier=monitor.stdDevMultiplier) if monitor.stdDevMultiplier else None),
            contacts=cls.create_monitor_contacts(monitor.contacts),
            downtimeStart=monitor.downtimeStart,
            downtimeDurationHrs=monitor.downtimeDurationHrs,
            downtimeFrequencyDays=monitor.downtimeFrequencyDays,
            scheduledRuntimeEnabled=monitor.scheduledRuntimeEnabled,
            scheduledRuntimeCadenceSeconds=monitor.scheduledRuntimeCadenceSeconds,
            scheduledRuntimeDaysOfWeek=monitor.scheduledRuntimeDaysOfWeek,
            modelEnvironmentName=ModelEnvironment.production,
            filters=(cls.create_dimension_filters(monitor.primaryMetricWindow.filters) if monitor.primaryMetricWindow else None),
        )

    @classmethod
    def data_quality_monitor(cls, space_id: str, model_name: str, monitor: Monitor) -> DataQualityMonitor:
        return DataQualityMonitor(
            spaceId=space_id,
            modelName=model_name,
            name=monitor.name,
            notes=monitor.notes,
            contacts=cls.create_monitor_contacts(monitor.contacts),
            downtimeStart=monitor.downtimeStart,
            downtimeDurationHrs=monitor.downtimeDurationHrs,
            downtimeFrequencyDays=monitor.downtimeFrequencyDays,
            scheduledRuntimeEnabled=monitor.scheduledRuntimeEnabled,
            scheduledRuntimeCadenceSeconds=monitor.scheduledRuntimeCadenceSeconds,
            scheduledRuntimeDaysOfWeek=monitor.scheduledRuntimeDaysOfWeek,
            dataQualityMetric=monitor.dataQualityMetric,
            dimensionCategory=monitor.dimensionCategory,
            dimensionName=(monitor.primaryMetricWindow.dimension.name if monitor.primaryMetricWindow and monitor.primaryMetricWindow.dimension else None),
            modelEnvironmentName=(ModelEnvironment.production if monitor.dimensionCategory != DimensionCategory.spanProperty else ModelEnvironment.tracing),
            threshold=monitor.threshold,
            threshold2=monitor.threshold2,
            thresholdMode=monitor.thresholdMode,
            operator=monitor.operator,
            operator2=monitor.operator2,
            stdDevMultiplier2=monitor.stdDevMultiplier2,
            dynamicAutoThreshold=(DynamicAutoThreshold(stdDevMultiplier=monitor.stdDevMultiplier) if monitor.stdDevMultiplier else None),
            filters=(cls.create_dimension_filters(monitor.primaryMetricWindow.filters) if monitor.primaryMetricWindow else None),
        )

    @classmethod
    def drift_monitor(cls, space_id: str, model_name: str, monitor: Monitor) -> DriftMonitor:
        return DriftMonitor(
            spaceId=space_id,
            modelName=model_name,
            name=monitor.name,
            notes=monitor.notes,
            driftMetric=monitor.driftMetric,
            dimensionCategory=monitor.dimensionCategory,
            dimensionName=(monitor.primaryMetricWindow.dimension.name if monitor.primaryMetricWindow and monitor.primaryMetricWindow.dimension else None),
            threshold=monitor.threshold,
            threshold2=monitor.threshold2,
            thresholdMode=monitor.thresholdMode,
            operator=monitor.operator,
            operator2=monitor.operator2,
            stdDevMultiplier2=monitor.stdDevMultiplier2,
            dynamicAutoThreshold=(DynamicAutoThreshold(stdDevMultiplier=monitor.stdDevMultiplier) if monitor.stdDevMultiplier else None),
            contacts=cls.create_monitor_contacts(monitor.contacts),
            downtimeStart=monitor.downtimeStart,
            downtimeDurationHrs=monitor.downtimeDurationHrs,
            downtimeFrequencyDays=monitor.downtimeFrequencyDays,
            scheduledRuntimeEnabled=monitor.scheduledRuntimeEnabled,
            scheduledRuntimeCadenceSeconds=monitor.scheduledRuntimeCadenceSeconds,
            scheduledRuntimeDaysOfWeek=monitor.scheduledRuntimeDaysOfWeek,
            filters=(cls.create_dimension_filters(monitor.primaryMetricWindow.filters) if monitor.primaryMetricWindow else None),
        )
