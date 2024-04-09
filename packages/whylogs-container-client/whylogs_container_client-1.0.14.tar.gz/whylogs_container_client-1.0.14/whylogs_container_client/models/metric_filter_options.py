from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricFilterOptions")


@_attrs_define
class MetricFilterOptions:
    """
    Attributes:
        by_required_inputs (Union[List[List[str]], None, Unset]):
    """

    by_required_inputs: Union[List[List[str]], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        by_required_inputs: Union[List[List[str]], None, Unset]
        if isinstance(self.by_required_inputs, Unset):
            by_required_inputs = UNSET
        elif isinstance(self.by_required_inputs, list):
            by_required_inputs = UNSET
            if not isinstance(self.by_required_inputs, Unset):
                by_required_inputs = []
                for by_required_inputs_type_0_item_data in self.by_required_inputs:
                    by_required_inputs_type_0_item = by_required_inputs_type_0_item_data

                    by_required_inputs.append(by_required_inputs_type_0_item)

        else:
            by_required_inputs = self.by_required_inputs

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if by_required_inputs is not UNSET:
            field_dict["by_required_inputs"] = by_required_inputs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_by_required_inputs(data: object) -> Union[List[List[str]], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                by_required_inputs_type_0 = UNSET
                _by_required_inputs_type_0 = data
                for by_required_inputs_type_0_item_data in _by_required_inputs_type_0 or []:
                    by_required_inputs_type_0_item = cast(List[str], by_required_inputs_type_0_item_data)

                    by_required_inputs_type_0.append(by_required_inputs_type_0_item)

                return by_required_inputs_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[List[str]], None, Unset], data)

        by_required_inputs = _parse_by_required_inputs(d.pop("by_required_inputs", UNSET))

        metric_filter_options = cls(
            by_required_inputs=by_required_inputs,
        )

        metric_filter_options.additional_properties = d
        return metric_filter_options

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
