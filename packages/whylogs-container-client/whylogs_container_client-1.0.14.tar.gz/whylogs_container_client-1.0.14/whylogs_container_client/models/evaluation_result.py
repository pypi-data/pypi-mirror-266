from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.block_action import BlockAction
    from ..models.evaluation_result_metrics_item import EvaluationResultMetricsItem
    from ..models.pass_action import PassAction
    from ..models.run_perf import RunPerf
    from ..models.validation_result import ValidationResult


T = TypeVar("T", bound="EvaluationResult")


@_attrs_define
class EvaluationResult:
    """
    Attributes:
        metrics (List['EvaluationResultMetricsItem']):
        validation_results (ValidationResult):
        perf_info (Union['RunPerf', None]):
        action (Union['BlockAction', 'PassAction']):
    """

    metrics: List["EvaluationResultMetricsItem"]
    validation_results: "ValidationResult"
    perf_info: Union["RunPerf", None]
    action: Union["BlockAction", "PassAction"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.pass_action import PassAction
        from ..models.run_perf import RunPerf

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        validation_results = self.validation_results.to_dict()

        perf_info: Union[Dict[str, Any], None]
        if isinstance(self.perf_info, RunPerf):
            perf_info = self.perf_info.to_dict()
        else:
            perf_info = self.perf_info

        action: Dict[str, Any]
        if isinstance(self.action, PassAction):
            action = self.action.to_dict()
        else:
            action = self.action.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metrics": metrics,
                "validation_results": validation_results,
                "perf_info": perf_info,
                "action": action,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.block_action import BlockAction
        from ..models.evaluation_result_metrics_item import EvaluationResultMetricsItem
        from ..models.pass_action import PassAction
        from ..models.run_perf import RunPerf
        from ..models.validation_result import ValidationResult

        d = src_dict.copy()
        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = EvaluationResultMetricsItem.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        validation_results = ValidationResult.from_dict(d.pop("validation_results"))

        def _parse_perf_info(data: object) -> Union["RunPerf", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                perf_info_type_0 = RunPerf.from_dict(data)

                return perf_info_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunPerf", None], data)

        perf_info = _parse_perf_info(d.pop("perf_info"))

        def _parse_action(data: object) -> Union["BlockAction", "PassAction"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                action_type_0 = PassAction.from_dict(data)

                return action_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            action_type_1 = BlockAction.from_dict(data)

            return action_type_1

        action = _parse_action(d.pop("action"))

        evaluation_result = cls(
            metrics=metrics,
            validation_results=validation_results,
            perf_info=perf_info,
            action=action,
        )

        evaluation_result.additional_properties = d
        return evaluation_result

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
