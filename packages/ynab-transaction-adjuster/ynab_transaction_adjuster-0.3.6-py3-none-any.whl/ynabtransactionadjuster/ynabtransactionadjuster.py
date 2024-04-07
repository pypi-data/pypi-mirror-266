from abc import abstractmethod
from typing import List

from ynabtransactionadjuster.adjuster import Adjuster
from ynabtransactionadjuster.client import Client
from ynabtransactionadjuster.models import OriginalTransaction, ModifiedTransaction
from ynabtransactionadjuster.models import TransactionModifier
from ynabtransactionadjuster.repos import CategoryRepo
from ynabtransactionadjuster.repos import PayeeRepo


class YnabTransactionAdjuster:
	"""Abstract class which modifies transactions according to concrete implementation. You need to create your own
	child class and implement the `filter()`and `adjust()` method in it according to your needs. It has attributes
	which allow you to lookup categories and payees from your budget.

	:param budget: The YNAB budget id to use
	:param account: The YNAB account id to use
	:param token: The YNAB token to use

	:ivar categories: Collection of current categories in YNAB budget
	:ivar payees: Collection of current payees in YNAB budget
	"""
	def __init__(self, budget: str, account: str, token: str) -> None:
		self._budget = budget
		self._account = account
		self._client = Client(token=token, budget=budget, account=account)
		self.categories: CategoryRepo = CategoryRepo(self._client.fetch_categories())
		self.payees: PayeeRepo = PayeeRepo(self._client.fetch_payees())

	def run(self) -> int:
		"""Run the adjuster. It will fetch transactions from the YNAB account, filter & adjust them as per
		implementation of the two methods and push the updated transactions back to YNAB

		:return: count of adjusted transactions which have been updated in YNAB
		:raises AdjustError: if there is any error during the adjust process
		:raises HTTPError: if there is any error with the YNAB API (e.g. wrong credentials)
		"""
		transactions = self._client.fetch_transactions()
		filtered_transactions = self.filter(transactions)
		adjuster = Adjuster(transactions=filtered_transactions, adjust_func=self.adjust, categories=self.categories)
		modified_transactions = adjuster.run()
		updated = self._client.update_transactions(modified_transactions)
		return updated

	def test(self) -> List[dict]:
		"""Tests the adjuster. It will fetch transactions from the YNAB account, filter & adjust them as per
		implementation of the two methods. This function doesn't update records in YNAB but returns the modified
		transactions so that they can be inspected. `#! select * from source`

		The returned dicts have the following structure:

			{
				"original": "<OriginalTransaction>",
			 	"changes": {
			 		"<Attribute>": {
			 			"original": "<Original Value>",
			 			"changed": "<Changed Value>"
			 			}
					}
				}

		:return: List of modified transactions in the format
		:raises AdjustError: if there is any error during the adjust process
		:raises HTTPError: if there is any error with the YNAB API (e.g. wrong credentials)
		"""
		transactions = self._client.fetch_transactions()
		filtered_transactions = self.filter(transactions)
		sa = Adjuster(transactions=filtered_transactions, adjust_func=self.adjust, categories=self.categories)
		modified_transactions = [{'original': mt.original_transaction, 'changes': mt.changed_attributes()} for mt in sa.run()]
		return modified_transactions

	@abstractmethod
	def filter(self, transactions: List[OriginalTransaction]) -> List[OriginalTransaction]:
		"""Function which implements filtering for the list of transactions from YNAB account. It receives a list of
		the original transactions which can be filtered. Must return the filtered list or just the list if no filtering
		is intended.

		:param transactions: List of original transactions from YNAB
		:return: Method needs to return a list of filtered transactions"""
		pass

	@abstractmethod
	def adjust(self, original: OriginalTransaction, modifier: TransactionModifier) -> TransactionModifier:
		"""Function which implements the actual modification of a transaction. It receives the original transaction from
		YNAB and a prefilled modifier. The modifier can be altered and must be returned.

		:param original: Original transaction
		:param modifier: Transaction modifier prefilled with values from original transaction. All attributes can be
		changed and will modify the transaction
		:returns: Method needs to return the transaction modifier after modification
		"""
		pass
