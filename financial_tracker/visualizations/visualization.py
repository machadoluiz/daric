from datetime import timedelta

from altair import Chart
from polars import DataFrame, Series, col, sum
from streamlit import altair_chart, dataframe, metric


class Visualization:
    """Handles the creation of various types of visualizations."""

    @staticmethod
    def get_last_month_amount(data: DataFrame, metric_type: str) -> float:
        """Calculates the total amount for the specified metric in the previous month.

        Args:
            data: The DataFrame containing the financial data.
            metric_type: The type of metric to calculate ('income', 'expenses', or 'net').

        Returns:
            The total amount for the specified metric in the previous month.
        """
        max_date = data.select(col("date").max()).item()
        max_date_start = Series([max_date]).dt.truncate("1mo")[0]

        end_date = max_date_start - timedelta(days=1)
        start_date = Series([end_date]).dt.truncate("1mo")[0]

        last_month_data = data.filter(
            (col("date") >= start_date) & (col("date") <= end_date)
        )

        if metric_type == "income":
            return (
                last_month_data.filter(col("amount") > 0).select(sum("amount")).item()
            )
        if metric_type == "expenses":
            return (
                last_month_data.filter(col("amount") < 0).select(sum("amount")).item()
            )
        return last_month_data.select(sum("amount")).item()

    def display_total_income(self, data: DataFrame) -> None:
        """Displays total income metric.

        Args:
            data: The DataFrame containing the financial data.
        """
        total_income = data.filter(col("amount") > 0).select(sum("amount")).item()
        last_month_income = self.get_last_month_amount(data, "income")
        currency_prefix_income = "-R$" if last_month_income < 0 else "+R$"
        metric(
            label="Total income",
            value=f"R$ {total_income:,.2f}",
            delta=f"{currency_prefix_income} {abs(last_month_income):,.2f} last month",
        )

    def display_total_expenses(self, data: DataFrame) -> None:
        """Displays total expenses metric.

        Args:
            data: The DataFrame containing the financial data.
        """
        total_expenses = data.filter(col("amount") < 0).select(sum("amount")).item()
        last_month_expenses = self.get_last_month_amount(data, "expenses")
        currency_prefix_expenses = "-R$" if last_month_expenses < 0 else "+R$"
        metric(
            label="Total expenses",
            value=f"R$ {total_expenses:,.2f}",
            delta=f"{currency_prefix_expenses} {abs(last_month_expenses):,.2f} last month",
        )

    def display_net_amount(self, data: DataFrame) -> None:
        """Displays net amount metric.

        Args:
            data: The DataFrame containing the financial data.
        """
        net_amount = data.select(sum("amount")).item()
        last_month_net = self.get_last_month_amount(data, "net")
        currency_prefix_net = "-R$" if last_month_net < 0 else "+R$"
        metric(
            label="Net amount",
            value=f"R$ {net_amount:,.2f}",
            delta=f"{currency_prefix_net} {abs(last_month_net):,.2f} last month",
        )

    @staticmethod
    def create_top_income_table(data: DataFrame) -> None:
        """Creates a table of the top income.

        Args:
            data: The DataFrame containing the data.
        """
        dataframe(
            data=(
                data.filter(col("type") == "Entrada")
                .sort(by="amount", descending=True)
                .select(["title", "amount"])
                .limit(5)
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_top_expenses_table(data: DataFrame) -> None:
        """Creates a table of the top expenses.

        Args:
            data: The DataFrame containing the data.
        """
        dataframe(
            data=(
                data.filter(col("type") == "Saída")
                .sort(by="amount", descending=False)
                .select(["title", "amount"])
                .limit(5)
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_monthly_trend_bar_chart(data: DataFrame) -> None:
        """Creates a monthly net trend bar chart.

        Args:
            data: The DataFrame containing the data.
        """
        monthly_trend_data = (
            data.group_by(col("date").dt.strftime("%Y-%m"))
            .agg(sum("amount"))
            .sort("date")
        )
        altair_chart(
            Chart(monthly_trend_data)
            .mark_bar()
            .encode(
                x="date:O",
                y="amount:Q",
                tooltip=["date", "amount"],
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_bar_chart(data: DataFrame) -> None:
        """Creates a bar chart.

        Args:
            data: The DataFrame containing the data.
        """
        grouped_data = data.group_by(
            [col("date").dt.strftime("%Y-%m"), "category"], maintain_order=True
        ).sum()
        altair_chart(
            Chart(grouped_data)
            .mark_bar()
            .encode(
                x="date:O",
                y="amount:Q",
                color="category:N",
                tooltip=["date", "category", "amount"],
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_line_chart(data: DataFrame) -> None:
        """Creates a line chart.

        Args:
            data: The DataFrame containing the data.
        """
        total_expense_over_time = (
            data.group_by("date").agg(sum("amount")).sort(by="date")
        )
        altair_chart(
            Chart(total_expense_over_time)
            .mark_line()
            .encode(x="date:T", y="amount:Q", tooltip=["date", "amount"]),
            use_container_width=True,
        )

    @staticmethod
    def create_horizontal_bar_chart(data: DataFrame) -> None:
        """Creates a horizontal bar chart.

        Args:
            data: The DataFrame containing the data.
        """
        data_counts = data["category"].value_counts()
        altair_chart(
            Chart(data_counts)
            .mark_bar()
            .encode(x="count:Q", y="category:N", tooltip=["category", "count"]),
            use_container_width=True,
        )

    @staticmethod
    def create_scatter_plot(data: DataFrame) -> None:
        """Creates a scatter plot.

        Args:
            data: The DataFrame containing the data.
        """
        altair_chart(
            Chart(data)
            .mark_circle()
            .encode(
                x="date:T",
                y="amount:Q",
                color="category:N",
                tooltip=["date", "amount", "category"],
            ),
            use_container_width=True,
        )
