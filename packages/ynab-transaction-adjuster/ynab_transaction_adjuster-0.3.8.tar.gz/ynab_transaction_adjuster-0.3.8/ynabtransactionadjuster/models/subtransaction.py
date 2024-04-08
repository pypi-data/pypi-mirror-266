from typing import Optional

from pydantic import BaseModel, model_validator

from ynabtransactionadjuster.models.category import Category
from ynabtransactionadjuster.models.payee import Payee


class SubTransaction(BaseModel):
	"""YNAB Subtransaction object for creating split transactions. To be used as element in subtransaction attribute of
	Transaction class

	:ivar amount: The amount of the subtransaction in milliunits
	:ivar category: The category of the subtransaction
	:ivar payee: The payee of the subtransaction
	:ivar memo: The memo of the subtransaction
	"""
	amount: int
	payee: Optional[Payee] = None
	category: Optional[Category] = None
	memo: Optional[str] = None

	def as_dict(self) -> dict:
		instance_dict = dict(amount=self.amount)
		if self.payee and self.payee.name:
			instance_dict['payee_name'] = self.payee.name
		if self.payee and self.payee.id:
			instance_dict['payee_id'] = self.payee.id
		if self.category and self.category.id:
			instance_dict['category_id'] = self.category.id
		if self.memo:
			instance_dict['memo'] = self.memo
		return instance_dict

	@model_validator(mode='after')
	def check_values(self):
		if self.amount == 0:
			raise ValueError('Amount needs to be different from 0')
		return self
