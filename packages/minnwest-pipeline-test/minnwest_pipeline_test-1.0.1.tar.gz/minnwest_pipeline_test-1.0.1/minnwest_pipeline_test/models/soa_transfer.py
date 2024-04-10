import datetime
from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.account_type import AccountType
from ..models.transfer_credit_type import TransferCreditType
from ..models.transfer_frequency import TransferFrequency
from ..types import UNSET, Unset

T = TypeVar("T", bound="SoaTransfer")


@_attrs_define
class SoaTransfer:
    """
    Attributes:
        from_account_number (Union[None, Unset, str]):
        to_account_number (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        remaining_transfers (Union[Unset, int]):
        transfer_frequency_code (Union[None, Unset, int]):
        transfer_frequency (Union[Unset, TransferFrequency]):
        transfer_amount_code (Union[None, Unset, int]):
        next_transfer_date (Union[None, Unset, datetime.datetime]):
        next_transfer_amount (Union[Unset, float]):
        last_transfer_date (Union[None, Unset, datetime.datetime]):
        last_transfer_amount (Union[Unset, float]):
        priority_code (Union[Unset, int]):
        credit_to_type_code (Union[Unset, int]):
        credit_to_type (Union[Unset, TransferCreditType]):
        credit_to_account_type (Union[Unset, AccountType]):
        transfer_day (Union[Unset, int]):
        transfer_cycle_code (Union[Unset, int]):
        record_id (Union[Unset, int]):
        record_number (Union[Unset, int]):
    """

    from_account_number: Union[None, Unset, str] = UNSET
    to_account_number: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    remaining_transfers: Union[Unset, int] = UNSET
    transfer_frequency_code: Union[None, Unset, int] = UNSET
    transfer_frequency: Union[Unset, TransferFrequency] = UNSET
    transfer_amount_code: Union[None, Unset, int] = UNSET
    next_transfer_date: Union[None, Unset, datetime.datetime] = UNSET
    next_transfer_amount: Union[Unset, float] = UNSET
    last_transfer_date: Union[None, Unset, datetime.datetime] = UNSET
    last_transfer_amount: Union[Unset, float] = UNSET
    priority_code: Union[Unset, int] = UNSET
    credit_to_type_code: Union[Unset, int] = UNSET
    credit_to_type: Union[Unset, TransferCreditType] = UNSET
    credit_to_account_type: Union[Unset, AccountType] = UNSET
    transfer_day: Union[Unset, int] = UNSET
    transfer_cycle_code: Union[Unset, int] = UNSET
    record_id: Union[Unset, int] = UNSET
    record_number: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from_account_number: Union[None, Unset, str]
        if isinstance(self.from_account_number, Unset):
            from_account_number = UNSET
        else:
            from_account_number = self.from_account_number

        to_account_number: Union[None, Unset, str]
        if isinstance(self.to_account_number, Unset):
            to_account_number = UNSET
        else:
            to_account_number = self.to_account_number

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        remaining_transfers = self.remaining_transfers

        transfer_frequency_code: Union[None, Unset, int]
        if isinstance(self.transfer_frequency_code, Unset):
            transfer_frequency_code = UNSET
        else:
            transfer_frequency_code = self.transfer_frequency_code

        transfer_frequency: Union[Unset, str] = UNSET
        if not isinstance(self.transfer_frequency, Unset):
            transfer_frequency = self.transfer_frequency.value

        transfer_amount_code: Union[None, Unset, int]
        if isinstance(self.transfer_amount_code, Unset):
            transfer_amount_code = UNSET
        else:
            transfer_amount_code = self.transfer_amount_code

        next_transfer_date: Union[None, Unset, str]
        if isinstance(self.next_transfer_date, Unset):
            next_transfer_date = UNSET
        elif isinstance(self.next_transfer_date, datetime.datetime):
            next_transfer_date = self.next_transfer_date.isoformat()
        else:
            next_transfer_date = self.next_transfer_date

        next_transfer_amount = self.next_transfer_amount

        last_transfer_date: Union[None, Unset, str]
        if isinstance(self.last_transfer_date, Unset):
            last_transfer_date = UNSET
        elif isinstance(self.last_transfer_date, datetime.datetime):
            last_transfer_date = self.last_transfer_date.isoformat()
        else:
            last_transfer_date = self.last_transfer_date

        last_transfer_amount = self.last_transfer_amount

        priority_code = self.priority_code

        credit_to_type_code = self.credit_to_type_code

        credit_to_type: Union[Unset, str] = UNSET
        if not isinstance(self.credit_to_type, Unset):
            credit_to_type = self.credit_to_type.value

        credit_to_account_type: Union[Unset, str] = UNSET
        if not isinstance(self.credit_to_account_type, Unset):
            credit_to_account_type = self.credit_to_account_type.value

        transfer_day = self.transfer_day

        transfer_cycle_code = self.transfer_cycle_code

        record_id = self.record_id

        record_number = self.record_number

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if from_account_number is not UNSET:
            field_dict["fromAccountNumber"] = from_account_number
        if to_account_number is not UNSET:
            field_dict["toAccountNumber"] = to_account_number
        if description is not UNSET:
            field_dict["description"] = description
        if remaining_transfers is not UNSET:
            field_dict["remainingTransfers"] = remaining_transfers
        if transfer_frequency_code is not UNSET:
            field_dict["transferFrequencyCode"] = transfer_frequency_code
        if transfer_frequency is not UNSET:
            field_dict["transferFrequency"] = transfer_frequency
        if transfer_amount_code is not UNSET:
            field_dict["transferAmountCode"] = transfer_amount_code
        if next_transfer_date is not UNSET:
            field_dict["nextTransferDate"] = next_transfer_date
        if next_transfer_amount is not UNSET:
            field_dict["nextTransferAmount"] = next_transfer_amount
        if last_transfer_date is not UNSET:
            field_dict["lastTransferDate"] = last_transfer_date
        if last_transfer_amount is not UNSET:
            field_dict["lastTransferAmount"] = last_transfer_amount
        if priority_code is not UNSET:
            field_dict["priorityCode"] = priority_code
        if credit_to_type_code is not UNSET:
            field_dict["creditToTypeCode"] = credit_to_type_code
        if credit_to_type is not UNSET:
            field_dict["creditToType"] = credit_to_type
        if credit_to_account_type is not UNSET:
            field_dict["creditToAccountType"] = credit_to_account_type
        if transfer_day is not UNSET:
            field_dict["transferDay"] = transfer_day
        if transfer_cycle_code is not UNSET:
            field_dict["transferCycleCode"] = transfer_cycle_code
        if record_id is not UNSET:
            field_dict["recordId"] = record_id
        if record_number is not UNSET:
            field_dict["recordNumber"] = record_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_from_account_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        from_account_number = _parse_from_account_number(d.pop("fromAccountNumber", UNSET))

        def _parse_to_account_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        to_account_number = _parse_to_account_number(d.pop("toAccountNumber", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        remaining_transfers = d.pop("remainingTransfers", UNSET)

        def _parse_transfer_frequency_code(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        transfer_frequency_code = _parse_transfer_frequency_code(d.pop("transferFrequencyCode", UNSET))

        _transfer_frequency = d.pop("transferFrequency", UNSET)
        transfer_frequency: Union[Unset, TransferFrequency]
        if isinstance(_transfer_frequency, Unset):
            transfer_frequency = UNSET
        else:
            transfer_frequency = TransferFrequency(_transfer_frequency)

        def _parse_transfer_amount_code(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        transfer_amount_code = _parse_transfer_amount_code(d.pop("transferAmountCode", UNSET))

        def _parse_next_transfer_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                next_transfer_date_type_0 = isoparse(data)

                return next_transfer_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        next_transfer_date = _parse_next_transfer_date(d.pop("nextTransferDate", UNSET))

        next_transfer_amount = d.pop("nextTransferAmount", UNSET)

        def _parse_last_transfer_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_transfer_date_type_0 = isoparse(data)

                return last_transfer_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_transfer_date = _parse_last_transfer_date(d.pop("lastTransferDate", UNSET))

        last_transfer_amount = d.pop("lastTransferAmount", UNSET)

        priority_code = d.pop("priorityCode", UNSET)

        credit_to_type_code = d.pop("creditToTypeCode", UNSET)

        _credit_to_type = d.pop("creditToType", UNSET)
        credit_to_type: Union[Unset, TransferCreditType]
        if isinstance(_credit_to_type, Unset):
            credit_to_type = UNSET
        else:
            credit_to_type = TransferCreditType(_credit_to_type)

        _credit_to_account_type = d.pop("creditToAccountType", UNSET)
        credit_to_account_type: Union[Unset, AccountType]
        if isinstance(_credit_to_account_type, Unset):
            credit_to_account_type = UNSET
        else:
            credit_to_account_type = AccountType(_credit_to_account_type)

        transfer_day = d.pop("transferDay", UNSET)

        transfer_cycle_code = d.pop("transferCycleCode", UNSET)

        record_id = d.pop("recordId", UNSET)

        record_number = d.pop("recordNumber", UNSET)

        soa_transfer = cls(
            from_account_number=from_account_number,
            to_account_number=to_account_number,
            description=description,
            remaining_transfers=remaining_transfers,
            transfer_frequency_code=transfer_frequency_code,
            transfer_frequency=transfer_frequency,
            transfer_amount_code=transfer_amount_code,
            next_transfer_date=next_transfer_date,
            next_transfer_amount=next_transfer_amount,
            last_transfer_date=last_transfer_date,
            last_transfer_amount=last_transfer_amount,
            priority_code=priority_code,
            credit_to_type_code=credit_to_type_code,
            credit_to_type=credit_to_type,
            credit_to_account_type=credit_to_account_type,
            transfer_day=transfer_day,
            transfer_cycle_code=transfer_cycle_code,
            record_id=record_id,
            record_number=record_number,
        )

        return soa_transfer
