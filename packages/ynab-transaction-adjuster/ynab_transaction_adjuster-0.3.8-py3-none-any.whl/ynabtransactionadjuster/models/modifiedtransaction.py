from datetime import datetime

from pydantic import BaseModel, model_validator

from ynabtransactionadjuster.models.originaltransaction import OriginalTransaction
from ynabtransactionadjuster.models.transactionmodifier import TransactionModifier


class ModifiedTransaction(BaseModel):
	original_transaction: OriginalTransaction
	transaction_modifier: TransactionModifier

	def is_changed(self) -> bool:
		"""Helper function to determine if transaction has been altered as compared to original one

		:returns: True if values from original transaction have been altered, False otherwise
		"""
		if self.changed_attributes():
			return True
		return False

	def as_dict(self) -> dict:
		"""Returns a dictionary representation of the transaction which is used for the update call to YNAB"""
		t_dict = dict(id=self.original_transaction.id,
					payee_name=self.transaction_modifier.payee.name,
					payee_id=self.transaction_modifier.payee.id,
					date=datetime.strftime(self.transaction_modifier.transaction_date, '%Y-%m-%d'),
					approved=self.transaction_modifier.approved,
					cleared=self.transaction_modifier.cleared)
		if len(self.transaction_modifier.subtransactions) > 0:
			t_dict['subtransactions'] = [s.as_dict() for s in self.transaction_modifier.subtransactions]
		if self.transaction_modifier.category:
			t_dict['category_id'] = self.transaction_modifier.category.id
		if self.transaction_modifier.flag_color:
			t_dict['flag_color'] = self.transaction_modifier.flag_color
		if self.transaction_modifier.memo:
			t_dict['memo'] = self.transaction_modifier.memo

		return t_dict

	def changed_attributes(self) -> dict:
		"""Returns a dictionary representation of the modified values and the original transaction"""
		changed_attributes = dict()

		for a in ('payee', 'category', 'flag_color', 'memo', 'approved', 'cleared'):
			if self._attribute_changed(a):
				changed_attributes[a] = self._create_changed_dict(a)

		if (self.transaction_modifier.transaction_date.isocalendar() !=
				self.original_transaction.transaction_date.isocalendar()):
			changed_attributes['transaction_date'] = self._create_changed_dict('transaction_date')

		if len(self.transaction_modifier.subtransactions) > 0:
			changed_attributes['subtransactions'] = self._create_changed_dict('subtransactions')

		return changed_attributes

	def _attribute_changed(self, attribute: str) -> bool:
		o = self.original_transaction.__getattribute__(attribute)
		m = self.transaction_modifier.__getattribute__(attribute)
		if o != m:
			return True

	def _create_changed_dict(self, attribute: str) -> dict:
		return dict(original=self.original_transaction.__getattribute__(attribute),
											  changed=self.transaction_modifier.__getattribute__(attribute))

	@model_validator(mode='after')
	def check_values(self):
		if len(self.transaction_modifier.subtransactions) > 1:
			if len(self.original_transaction.subtransactions) > 1:
				raise ValueError(f"Existing Subtransactions can not be updated")
			if sum(a.amount for a in self.transaction_modifier.subtransactions) != self.original_transaction.amount:
				raise ValueError('Amount of subtransactions needs to be equal to amount of original transaction')
		return self
