from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_app_json_body_policy_execution_mode import UpdateAppJsonBodyPolicyExecutionMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_app_json_body_policy_triggerables import UpdateAppJsonBodyPolicyTriggerables


T = TypeVar("T", bound="UpdateAppJsonBodyPolicy")


@_attrs_define
class UpdateAppJsonBodyPolicy:
    """
    Attributes:
        triggerables (Union[Unset, UpdateAppJsonBodyPolicyTriggerables]):
        execution_mode (Union[Unset, UpdateAppJsonBodyPolicyExecutionMode]):
        on_behalf_of (Union[Unset, str]):
        on_behalf_of_email (Union[Unset, str]):
    """

    triggerables: Union[Unset, "UpdateAppJsonBodyPolicyTriggerables"] = UNSET
    execution_mode: Union[Unset, UpdateAppJsonBodyPolicyExecutionMode] = UNSET
    on_behalf_of: Union[Unset, str] = UNSET
    on_behalf_of_email: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        triggerables: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.triggerables, Unset):
            triggerables = self.triggerables.to_dict()

        execution_mode: Union[Unset, str] = UNSET
        if not isinstance(self.execution_mode, Unset):
            execution_mode = self.execution_mode.value

        on_behalf_of = self.on_behalf_of
        on_behalf_of_email = self.on_behalf_of_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if triggerables is not UNSET:
            field_dict["triggerables"] = triggerables
        if execution_mode is not UNSET:
            field_dict["execution_mode"] = execution_mode
        if on_behalf_of is not UNSET:
            field_dict["on_behalf_of"] = on_behalf_of
        if on_behalf_of_email is not UNSET:
            field_dict["on_behalf_of_email"] = on_behalf_of_email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_app_json_body_policy_triggerables import UpdateAppJsonBodyPolicyTriggerables

        d = src_dict.copy()
        _triggerables = d.pop("triggerables", UNSET)
        triggerables: Union[Unset, UpdateAppJsonBodyPolicyTriggerables]
        if isinstance(_triggerables, Unset):
            triggerables = UNSET
        else:
            triggerables = UpdateAppJsonBodyPolicyTriggerables.from_dict(_triggerables)

        _execution_mode = d.pop("execution_mode", UNSET)
        execution_mode: Union[Unset, UpdateAppJsonBodyPolicyExecutionMode]
        if isinstance(_execution_mode, Unset):
            execution_mode = UNSET
        else:
            execution_mode = UpdateAppJsonBodyPolicyExecutionMode(_execution_mode)

        on_behalf_of = d.pop("on_behalf_of", UNSET)

        on_behalf_of_email = d.pop("on_behalf_of_email", UNSET)

        update_app_json_body_policy = cls(
            triggerables=triggerables,
            execution_mode=execution_mode,
            on_behalf_of=on_behalf_of,
            on_behalf_of_email=on_behalf_of_email,
        )

        update_app_json_body_policy.additional_properties = d
        return update_app_json_body_policy

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
