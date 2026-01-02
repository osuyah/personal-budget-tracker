import pandas as pd
import os

class Budget:
    def __init__(self, month: str, income: float, currency: str = "USD"):
        self.month = month
        self.income = max(0.0, income)
        self.currency = currency  # Stores "USD" or "JPY"
        self.expenses = {}  # {category: amount}
        self.limits = {}    # {category: limit}

    def add_expense(self, category: str, amount: float):
        if category and amount > 0:
            self.expenses[category] = self.expenses.get(category, 0.0) + amount

    def set_limit(self, category: str, limit: float):
        if category and limit >= 0:
            self.limits[category] = limit

    def total_expenses(self) -> float:
        return sum(self.expenses.values())

    def remaining_income(self) -> float:
        return self.income - self.total_expenses()

    def expense_percentages(self) -> dict:
        if self.income <= 0:
            return {cat: 0.0 for cat in self.expenses}
        return {cat: (amt / self.income) * 100 for cat, amt in self.expenses.items()}

    def overspent_categories(self) -> list:
        overspent = []
        for cat, amt in self.expenses.items():
            limit = self.limits.get(cat, float('inf'))
            if amt > limit:
                overspent.append({"category": cat, "spent": amt, "limit": limit})
        return overspent

    def to_dataframe(self) -> pd.DataFrame:
        all_categories = sorted(list(set(self.expenses.keys()) | set(self.limits.keys())))
        data = []
        percentages = self.expense_percentages()
        
        for cat in all_categories:
            spent = self.expenses.get(cat, 0.0)
            limit = self.limits.get(cat, 0.0)
            pct = percentages.get(cat, 0.0)
            data.append({
                "Month": self.month,
                "Category": cat,
                "Amount Spent": spent,
                "Limit": limit,
                "Percentage of Income": f"{pct:.2f}%"
            })
        return pd.DataFrame(data)

    def to_csv(self, filepath: str):
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)