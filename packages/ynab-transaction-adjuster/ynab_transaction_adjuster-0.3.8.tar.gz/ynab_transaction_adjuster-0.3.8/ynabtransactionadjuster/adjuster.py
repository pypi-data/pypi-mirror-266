from typing import List, Callable, Optional

from ynabtransactionadjuster.exceptions import AdjustError, NoMatchingCategoryError
from ynabtransactionadjuster.models import OriginalTransaction, ModifiedTransaction, TransactionModifier, Category
from ynabtransactionadjuster.repos import CategoryRepo


class Adjuster:

	def __init__(self, transactions: List[OriginalTransaction], adjust_func: Callable, categories: CategoryRepo):
		self._transactions = transactions
		self._adjust_func = adjust_func
		self._categories = categories

	def run(self) -> List[ModifiedTransaction]:
		modified_transactions = [self.adjust_single(original=t, adjust_func=self._adjust_func)
								 for t in self._transactions]
		filtered_transactions = [t for t in modified_transactions if t.is_changed()]
		return filtered_transactions

	def adjust_single(self, original: OriginalTransaction, adjust_func: Callable) -> ModifiedTransaction:
		modifier = TransactionModifier.from_original_transaction(original_transaction=original)
		try:
			modifier_return = adjust_func(original=original, modifier=modifier)
			self.validate_instance(modifier_return)
			self.validate_attributes(modifier_return)
			self.validate_category(modifier_return.category)
			modified_transaction = ModifiedTransaction(original_transaction=original,
													 transaction_modifier=modifier_return)
			return modified_transaction
		except Exception as e:
			raise AdjustError(f"Error while adjusting {original.as_dict()}") from e

	def validate_category(self, category: Category):
		if category:
			self._categories.fetch_by_id(category.id)

	@staticmethod
	def validate_attributes(modifier: TransactionModifier):
		TransactionModifier.model_validate(modifier.__dict__)

	@staticmethod
	def validate_instance(modifier: Optional[TransactionModifier]):
		if not isinstance(modifier, TransactionModifier):
			raise AdjustError(f"Adjust function doesn't return TransactionModifier object")
