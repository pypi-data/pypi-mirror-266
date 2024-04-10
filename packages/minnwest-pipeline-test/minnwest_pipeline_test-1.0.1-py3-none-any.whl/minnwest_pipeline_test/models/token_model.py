from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenModel")


@_attrs_define
class TokenModel:
    """
    Attributes:
        token (Union[None, Unset, str]):
        refresh_token (Union[None, Unset, str]):
    """

    token: Union[None, Unset, str] = UNSET
    refresh_token: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        token: Union[None, Unset, str]
        if isinstance(self.token, Unset):
            token = UNSET
        else:
            token = self.token

        refresh_token: Union[None, Unset, str]
        if isinstance(self.refresh_token, Unset):
            refresh_token = UNSET
        else:
            refresh_token = self.refresh_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token
        if refresh_token is not UNSET:
            field_dict["refreshToken"] = refresh_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        token = _parse_token(d.pop("token", UNSET))

        def _parse_refresh_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        refresh_token = _parse_refresh_token(d.pop("refreshToken", UNSET))

        token_model = cls(
            token=token,
            refresh_token=refresh_token,
        )

        return token_model
