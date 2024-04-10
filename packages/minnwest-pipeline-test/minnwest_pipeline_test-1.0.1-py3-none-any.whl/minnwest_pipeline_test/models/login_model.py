from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginModel")


@_attrs_define
class LoginModel:
    """
    Attributes:
        user_name (Union[None, Unset, str]):
        password (Union[None, Unset, str]):
    """

    user_name: Union[None, Unset, str] = UNSET
    password: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        user_name: Union[None, Unset, str]
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        password: Union[None, Unset, str]
        if isinstance(self.password, Unset):
            password = UNSET
        else:
            password = self.password

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if user_name is not UNSET:
            field_dict["userName"] = user_name
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_user_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_name = _parse_user_name(d.pop("userName", UNSET))

        def _parse_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        password = _parse_password(d.pop("password", UNSET))

        login_model = cls(
            user_name=user_name,
            password=password,
        )

        return login_model
