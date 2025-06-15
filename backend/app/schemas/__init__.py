# backend/app/schemas/__init__.py
from .machine import (
    MachineBase, MachineCreate, MachineUpdate, Machine, MachineList,
    MachineRegistration, MachineStats
)
from .metrics import (
    MetricDataBase, MetricDataCreate, MetricData, MetricsList,
    MetricsExport, MetricsQuery
)
from .hardware import (
    HardwareComponentBase, HardwareComponentCreate, HardwareComponentUpdate,
    HardwareComponent, HardwareComponentList
)
from .alerts import (
    AlertRuleBase, AlertRuleCreate, AlertRuleUpdate, AlertRule,
    AlertBase, AlertCreate, AlertUpdate, Alert, AlertsList
)
from .configuration import (
    SystemConfigurationBase, SystemConfigurationUpdate, SystemConfiguration,
    InfluxDBConfig, MQTTConfig, AlertConfig, UIConfig
)

__all__ = [
    # Machine schemas
    "MachineBase", "MachineCreate", "MachineUpdate", "Machine", "MachineList",
    "MachineRegistration", "MachineStats",
    # Metrics schemas
    "MetricDataBase", "MetricDataCreate", "MetricData", "MetricsList",
    "MetricsExport", "MetricsQuery",
    # Hardware schemas
    "HardwareComponentBase", "HardwareComponentCreate", "HardwareComponentUpdate",
    "HardwareComponent", "HardwareComponentList",
    # Alerts schemas
    "AlertRuleBase", "AlertRuleCreate", "AlertRuleUpdate", "AlertRule",
    "AlertBase", "AlertCreate", "AlertUpdate", "Alert", "AlertsList",
    # Configuration schemas
    "SystemConfigurationBase", "SystemConfigurationUpdate", "SystemConfiguration",
    "InfluxDBConfig", "MQTTConfig", "AlertConfig", "UIConfig"
]