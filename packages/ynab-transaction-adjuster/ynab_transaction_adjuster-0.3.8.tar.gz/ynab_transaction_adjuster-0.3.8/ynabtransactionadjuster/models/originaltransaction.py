from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Literal, Optional, Tuple

from ynabtransactionadjuster.models.category import Category
from ynabtransactionadjuster.models.payee import Payee
from ynabtransactionadjuster.models.originalsubtransaction import OriginalSubTransaction


@dataclass(frozen=True, eq=True)
class OriginalTransaction:
	"""Represents original transaction from YNAB

	:ivar id: The original transaction id
	:ivar amount: The transaction amount in milliunits format
	:ivar category: The category of the original transaction
	:ivar transaction_date: The date of the original transaction
	:ivar memo: The memo of the original transaction
	:ivar payee: The payee of the original transaction
	:ivar flag_color: The flag color of the original transaction
	:ivar import_payee_name: The payee as recorded by YNAB on import
	:ivar import_payee_name_original: The original payee or memo as recorded by the bank
	:ivar approved: approval status of the original transaction
	:ivar cleared: clearance state of the original transaction
	"""
	id: str
	transaction_date: date
	category: Optional[Category]
	amount: int
	memo: Optional[str]
	payee: Payee
	flag_color: Optional[Literal['red', 'green', 'blue', 'orange', 'purple', 'yellow']]
	import_payee_name_original: Optional[str]
	import_payee_name: Optional[str]
	subtransactions: Tuple[OriginalSubTransaction, ...]
	cleared: Literal['uncleared', 'cleared', 'reconciled']
	approved: bool

	@classmethod
	def from_dict(cls, t_dict: dict) -> 'OriginalTransaction':

		def build_category(t_dict: dict) -> Optional[Category]:
			if not t_dict['category_name'] in ('Uncategorized', 'Split'):
				return Category(id=t_dict['category_id'], name=t_dict['category_name'])

		def build_payee(t_dict: dict) -> Payee:
			return Payee(id=t_dict['payee_id'], name=t_dict['payee_name'],
						 transfer_account_id=t_dict['transfer_account_id'])

		def build_subtransaction(s_dict: dict) -> OriginalSubTransaction:
			return OriginalSubTransaction(payee=build_payee(s_dict),
										  category=build_category(s_dict),
										  amount=s_dict['amount'],
										  memo=s_dict['memo'])

		return OriginalTransaction(id=t_dict['id'],
								   transaction_date=datetime.strptime(t_dict['date'], '%Y-%m-%d').date(),
								   category=build_category(t_dict),
								   memo=t_dict['memo'],
								   import_payee_name_original=t_dict['import_payee_name_original'],
								   import_payee_name=t_dict['import_payee_name'],
								   flag_color=t_dict['flag_color'],
								   payee=build_payee(t_dict),
								   subtransactions=tuple([build_subtransaction(st) for st in t_dict['subtransactions']]),
								   amount=t_dict['amount'],
								   approved=t_dict['approved'],
								   cleared=t_dict['cleared'])

	def as_dict(self) -> dict:
		return asdict(self)
