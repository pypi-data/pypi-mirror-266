from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.run_perf_metrics_time_sec import RunPerfMetricsTimeSec


T = TypeVar("T", bound="RunPerf")


@_attrs_define
class RunPerf:
    """
    Attributes:
        metrics_time_sec (RunPerfMetricsTimeSec):
        workflow_total_sec (float):
        metrics_total_sec (float):
        validation_total_sec (float):
    """

    metrics_time_sec: "RunPerfMetricsTimeSec"
    workflow_total_sec: float
    metrics_total_sec: float
    validation_total_sec: float
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metrics_time_sec = self.metrics_time_sec.to_dict()

        workflow_total_sec = self.workflow_total_sec

        metrics_total_sec = self.metrics_total_sec

        validation_total_sec = self.validation_total_sec

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metrics_time_sec": metrics_time_sec,
                "workflow_total_sec": workflow_total_sec,
                "metrics_total_sec": metrics_total_sec,
                "validation_total_sec": validation_total_sec,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_perf_metrics_time_sec import RunPerfMetricsTimeSec

        d = src_dict.copy()
        metrics_time_sec = RunPerfMetricsTimeSec.from_dict(d.pop("metrics_time_sec"))

        workflow_total_sec = d.pop("workflow_total_sec")

        metrics_total_sec = d.pop("metrics_total_sec")

        validation_total_sec = d.pop("validation_total_sec")

        run_perf = cls(
            metrics_time_sec=metrics_time_sec,
            workflow_total_sec=workflow_total_sec,
            metrics_total_sec=metrics_total_sec,
            validation_total_sec=validation_total_sec,
        )

        run_perf.additional_properties = d
        return run_perf

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
