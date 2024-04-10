from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PortfolioTransferViewRequest")


@_attrs_define
class PortfolioTransferViewRequest:
    """
    Attributes:
        portfolio (str):
    """

    portfolio: str

    def to_dict(self) -> Dict[str, Any]:
        portfolio = self.portfolio

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "portfolio": portfolio,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        portfolio = d.pop("portfolio")

        portfolio_transfer_view_request = cls(
            portfolio=portfolio,
        )

        return portfolio_transfer_view_request
