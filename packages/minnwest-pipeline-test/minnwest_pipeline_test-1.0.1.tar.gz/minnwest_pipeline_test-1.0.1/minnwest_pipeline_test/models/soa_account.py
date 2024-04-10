from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.account_type import AccountType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.soa_transfer import SoaTransfer


T = TypeVar("T", bound="SoaAccount")


@_attrs_define
class SoaAccount:
    """
    Attributes:
        account_number (Union[None, Unset, str]):
        current_balance (Union[Unset, float]):
        account_type (Union[Unset, AccountType]):
        transfers (Union[List['SoaTransfer'], None, Unset]):
    """

    account_number: Union[None, Unset, str] = UNSET
    current_balance: Union[Unset, float] = UNSET
    account_type: Union[Unset, AccountType] = UNSET
    transfers: Union[List["SoaTransfer"], None, Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        account_number: Union[None, Unset, str]
        if isinstance(self.account_number, Unset):
            account_number = UNSET
        else:
            account_number = self.account_number

        current_balance = self.current_balance

        account_type: Union[Unset, str] = UNSET
        if not isinstance(self.account_type, Unset):
            account_type = self.account_type.value

        transfers: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.transfers, Unset):
            transfers = UNSET
        elif isinstance(self.transfers, list):
            transfers = []
            for transfers_type_0_item_data in self.transfers:
                transfers_type_0_item = transfers_type_0_item_data.to_dict()
                transfers.append(transfers_type_0_item)

        else:
            transfers = self.transfers

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if current_balance is not UNSET:
            field_dict["currentBalance"] = current_balance
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if transfers is not UNSET:
            field_dict["transfers"] = transfers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.soa_transfer import SoaTransfer

        d = src_dict.copy()

        def _parse_account_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_number = _parse_account_number(d.pop("accountNumber", UNSET))

        current_balance = d.pop("currentBalance", UNSET)

        _account_type = d.pop("accountType", UNSET)
        account_type: Union[Unset, AccountType]
        if isinstance(_account_type, Unset):
            account_type = UNSET
        else:
            account_type = AccountType(_account_type)

        def _parse_transfers(data: object) -> Union[List["SoaTransfer"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                transfers_type_0 = []
                _transfers_type_0 = data
                for transfers_type_0_item_data in _transfers_type_0:
                    transfers_type_0_item = SoaTransfer.from_dict(transfers_type_0_item_data)

                    transfers_type_0.append(transfers_type_0_item)

                return transfers_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["SoaTransfer"], None, Unset], data)

        transfers = _parse_transfers(d.pop("transfers", UNSET))

        soa_account = cls(
            account_number=account_number,
            current_balance=current_balance,
            account_type=account_type,
            transfers=transfers,
        )

        return soa_account
