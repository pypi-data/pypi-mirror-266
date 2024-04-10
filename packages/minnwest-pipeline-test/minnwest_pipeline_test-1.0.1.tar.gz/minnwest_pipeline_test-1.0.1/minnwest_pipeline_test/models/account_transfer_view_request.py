from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.account_type import AccountType

T = TypeVar("T", bound="AccountTransferViewRequest")


@_attrs_define
class AccountTransferViewRequest:
    """
    Attributes:
        account_number (str):
        account_type (AccountType):
    """

    account_number: str
    account_type: AccountType

    def to_dict(self) -> Dict[str, Any]:
        account_number = self.account_number

        account_type = self.account_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accountNumber": account_number,
                "accountType": account_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        account_number = d.pop("accountNumber")

        account_type = AccountType(d.pop("accountType"))

        account_transfer_view_request = cls(
            account_number=account_number,
            account_type=account_type,
        )

        return account_transfer_view_request
