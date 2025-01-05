from datetime import timedelta

import altair as alt
import polars as pl
import streamlit as st


class Visualization:
    """Handles the creation of various types of visualizations."""

    @staticmethod
    def get_last_month_amount(data: pl.DataFrame, metric_type: str) -> float:
        """Calculates the total amount for the specified metric in the previous month.

        Args:
            data (pl.DataFrame): The DataFrame containing the financial data.
            metric_type (str): The type of metric to calculate ('income', 'expenses', or 'net').

        Returns:
            float: The total amount for the specified metric in the previous month.
        """
        max_date = data["date"].max()
        end_date = max_date.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)

        last_month_data = data.filter(
            (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
        )

        if metric_type == "income":
            return (
                last_month_data.filter(pl.col("amount") > 0)
                .select(pl.sum("amount"))
                .item()
            )
        elif metric_type == "expenses":
            return (
                last_month_data.filter(pl.col("amount") < 0)
                .select(pl.sum("amount"))
                .item()
            )
        else:
            return last_month_data.select(pl.sum("amount")).item()

    def display_total_income(
        self, data: pl.DataFrame
    ) -> st.delta_generator.DeltaGenerator:
        """Displays total income metric.

        Args:
            data (pl.DataFrame): The DataFrame containing the financial data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the metric.
        """
        total_income = data.filter(pl.col("amount") > 0).select(pl.sum("amount")).item()
        last_month_income = self.get_last_month_amount(data, "income")
        currency_prefix_income = "-R$" if last_month_income < 0 else "+R$"
        return st.metric(
            label="Total income",
            value=f"R$ {total_income:,.2f}",
            delta=f"{currency_prefix_income} {abs(last_month_income):,.2f} last month",
        )

    def display_total_expenses(
        self, data: pl.DataFrame
    ) -> st.delta_generator.DeltaGenerator:
        """Displays total expenses metric.

        Args:
            data (pl.DataFrame): The DataFrame containing the financial data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the metric.
        """
        total_expenses = (
            data.filter(pl.col("amount") < 0).select(pl.sum("amount")).item()
        )
        last_month_expenses = self.get_last_month_amount(data, "expenses")
        currency_prefix_expenses = "-R$" if last_month_expenses < 0 else "+R$"
        return st.metric(
            label="Total expenses",
            value=f"R$ {total_expenses:,.2f}",
            delta=f"{currency_prefix_expenses} {abs(last_month_expenses):,.2f} last month",
        )

    def display_net_amount(
        self, data: pl.DataFrame
    ) -> st.delta_generator.DeltaGenerator:
        """Displays net amount metric.

        Args:
            data (pl.DataFrame): The DataFrame containing the financial data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the metric.
        """
        net_amount = data.select(pl.sum("amount")).item()
        last_month_net = self.get_last_month_amount(data, "net")
        currency_prefix_net = "-R$" if last_month_net < 0 else "+R$"
        return st.metric(
            label="Net amount",
            value=f"R$ {net_amount:,.2f}",
            delta=f"{currency_prefix_net} {abs(last_month_net):,.2f} last month",
        )

    @staticmethod
    def create_top_income_table(
        data: pl.DataFrame,
    ) -> st.delta_generator.DeltaGenerator:
        """Creates a table of the top income.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the table.
        """
        return st.dataframe(
            data=(
                data.filter(pl.col("type") == "Entrada")
                .sort(by="amount", descending=True)
                .select(["title", "amount"])
                .limit(5)
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_top_expenses_table(
        data: pl.DataFrame,
    ) -> st.delta_generator.DeltaGenerator:
        """Creates a table of the top expenses.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the table.
        """
        return st.dataframe(
            data=(
                data.filter(pl.col("type") == "Saída")
                .sort(by="amount", descending=False)
                .select(["title", "amount"])
                .limit(5)
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_monthly_trend_bar_chart(
        data: pl.DataFrame,
    ) -> st.delta_generator.DeltaGenerator:
        """Creates a monthly net trend bar chart.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the chart.
        """
        monthly_trend_data = (
            data.group_by(pl.col("date").dt.strftime("%Y-%m"))
            .agg(pl.sum("amount"))
            .sort("date")
        )
        return st.altair_chart(
            altair_chart=(
                alt.Chart(monthly_trend_data)
                .mark_bar()
                .encode(
                    x="date:O",
                    y="amount:Q",
                    tooltip=["date", "amount"],
                )
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_bar_chart(data: pl.DataFrame) -> st.delta_generator.DeltaGenerator:
        """Creates a bar chart.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the chart.
        """
        grouped_data = data.group_by(
            [pl.col("date").dt.strftime("%Y-%m"), "category"], maintain_order=True
        ).sum()
        return st.altair_chart(
            altair_chart=(
                alt.Chart(grouped_data)
                .mark_bar()
                .encode(
                    x="date:O",
                    y="amount:Q",
                    color="category:N",
                    tooltip=["date", "category", "amount"],
                )
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_line_chart(data: pl.DataFrame) -> st.delta_generator.DeltaGenerator:
        """Creates a line chart.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the chart.
        """
        total_expense_over_time = (
            data.group_by("date").agg(pl.sum("amount")).sort(by="date")
        )
        return st.altair_chart(
            altair_chart=(
                alt.Chart(total_expense_over_time)
                .mark_line()
                .encode(x="date:T", y="amount:Q", tooltip=["date", "amount"])
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_horizontal_bar_chart(
        data: pl.DataFrame,
    ) -> st.delta_generator.DeltaGenerator:
        """Creates a horizontal bar chart.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the chart.
        """
        data_counts = data["category"].value_counts()
        return st.altair_chart(
            altair_chart=(
                alt.Chart(data_counts)
                .mark_bar()
                .encode(x="count:Q", y="category:N", tooltip=["category", "count"])
            ),
            use_container_width=True,
        )

    @staticmethod
    def create_scatter_plot(data: pl.DataFrame) -> st.delta_generator.DeltaGenerator:
        """Creates a scatter plot.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.

        Returns:
            st.delta_generator.DeltaGenerator: A Streamlit DeltaGenerator object representing the chart.
        """
        return st.altair_chart(
            altair_chart=(
                alt.Chart(data)
                .mark_circle()
                .encode(
                    x="date:T",
                    y="amount:Q",
                    color="category:N",
                    tooltip=["date", "amount", "category"],
                )
            ),
            use_container_width=True,
        )
