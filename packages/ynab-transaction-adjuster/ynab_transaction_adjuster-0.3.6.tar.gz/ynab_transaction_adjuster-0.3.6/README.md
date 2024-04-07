# ynab-transaction-adjuster

[![GitHub Release](https://img.shields.io/github/release/dnbasta/ynab-transaction-adjuster?style=flat)]() 
[![Github Release](https://img.shields.io/maintenance/yes/2100)]()

[!["Buy Me A Coffee"](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/dnbasta)

This library helps you to automatically adjust transactions in YNAB based on your logic. It allows you to implement 
your adjustments in a simple factory class which you can run against your existing transactions and update relevant 
fields like date, payee, category, memo and flags. It also allows you to split transactions.

## Preparations
1. Create a personal access token for YNAB as described [here](https://api.ynab.com/)
2. Get the IDs of your budget and account which records are faulty. You can find both IDs if you go to 
https://app.ynab.com/ and open the target account by clicking on the name on the left hand side menu. 
The URL does now contain both IDs `https://app.ynab.com/<budget_id>/accounts/<account_id>`

## Installation 
Install library from PyPI
```bash
pip install ynab-transaction-adjuster
```

## Usage
A detailed documentation is available at https://ynab-transaction-adjuster.readthedocs.io

### Fetch transactions
Fetch current transactions from YNAB backend with all available information and check for useful values. All records 
come with two additional attributes (`import_payee_name` and `import_payee_name_original`) which are not shown in the user 
interface.

```py
from ynabtransactionadjuster import YnabTransactionAdjuster

ynab_transaction_adjuster = YnabTransactionAdjuster(token='<token>', budget='<budget>', account='<account>')
orig_transactions = ynab_transaction_adjuster.fetch()
```

### Create a `AdjusterFactory` child class
This class is for implementing your actual logic. It needs to implement a `run()` method which receives on runtime 
the `OriginalTransaction` and a `TransactionModifier`. The 
latter is prefilled with values from the original transaction. Its attributes can be modified and it needs to be 
returned at the end of the function.

```py
from ynabtransactionadjuster import AdjusterFactory
from ynabtransactionadjuster.models import OriginalTransaction, TransactionModifier


class MyAdjusterFactory(AdjusterFactory):

	def run(self, original: OriginalTransaction, modifier: TransactionModifier) -> TransactionModifier:
		# your implementation

		# return the altered modifier
		return modifier
```

### Test your Factory class
Test the factory on records fetched via the `fetch()`method. If only a subset of these transactions should
get adjusted, filter them before handing the list over to the `adjust()` method. The method returns a list 
of `ModifiedTransaction` objects which can be inspected for the changed properties.

```py
transations = ynab_transaction_adjuster.fetch()
# optionally filter transactions before passing them to method below
mod_transactions = ynab_transaction_adjuster.adjust(transactions=transactions, factory_class=MyAdjusterFactory)
```

### Update records in YNAB
If you are satisfied with your parsing results you can pass the list of the 
`ModifedTransaction` objects to the `update()` method. It will update  
the changed transactions in YNAB and return an integer with the number of successfully updated records.

```py
count = ynab_transaction_adjuster.update(transactions=mod_transactions)
```
