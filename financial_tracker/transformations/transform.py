from typing import List

import polars as pl
import streamlit as st


class Transform:
    """Handles data transformation operations."""

    @staticmethod
    def categorize_data(
        data: pl.DataFrame,
        category_keywords: dict[str, list[str]],
        alternative_category: str | pl.Expr,
    ) -> pl.DataFrame:
        """Categorize data based on title keywords.

        Args:
            data (pl.DataFrame): The DataFrame containing credit card data.
            category_keywords (dict): The dictionary containing category keywords for transactions.
            alternative_category (str): The string containing a value when the category criteria it met.

        Returns:
            data (pl.DataFrame): A DataFrame with processed categorized data.
        """
        if category_keywords:
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    data = data.with_columns(
                        pl.when(pl.col("title").str.contains(keyword))
                        .then(pl.lit(category))
                        .otherwise(alternative_category)
                        .alias("category")
                    )
        else:
            if "category" not in data.columns:
                return data.with_columns(pl.lit("Outros").alias("category"))
            return data.with_columns(pl.col("category").str.to_titlecase())
        return data

    @staticmethod
    def process_data(
        data: pl.DataFrame,
        date_format: str,
        amount_multiplier: int,
        transaction_type: str | pl.Expr,
        unwanted_keywords: List,
    ) -> pl.DataFrame:
        """
        Processes data with common operations.

        Args:
            data (pl.DataFrame): The DataFrame containing the data.
            date_format (str): The format of the date column.
            amount_multiplier (int): The multiplier for the amount column.
            transaction_type (str | pl.Expr): If a string, sets the entire column to that string. If an expression, evaluates row-by-row.
            unwanted_keywords (List): The list of unwanted keywords in the title.

        Returns:
            pl.DataFrame: A DataFrame with processed data.
        """
        data = (
            data.with_columns(
                pl.col("date").str.strptime(pl.Date, format=date_format).alias("date")
            )
            .with_columns((pl.col("amount") * amount_multiplier).alias("amount"))
            .with_columns(
                pl.when(pl.col("amount") > 0)
                .then(pl.lit("Entrada"))
                .otherwise(pl.lit("Saída"))
                .alias("type")
            )
        )

        if isinstance(transaction_type, pl.Expr):
            data = data.with_columns(transaction_type.alias("transaction"))
        else:
            data = data.with_columns(pl.lit(transaction_type).alias("transaction"))

        return data.filter(~pl.col("title").is_in(unwanted_keywords))

    @staticmethod
    def process_data_account(data: pl.DataFrame) -> pl.DataFrame:
        """Processes account data.

        Args:
            data (pl.DataFrame): The DataFrame containing account data.

        Returns:
            pl.DataFrame: A DataFrame with processed account data.
        """
        data = data.rename({"Data": "date", "Valor": "amount", "Descrição": "title"})
        data = Transform.process_data(
            data,
            date_format="%d/%m/%Y",
            amount_multiplier=1,
            transaction_type=(
                pl.when(pl.col("title").str.starts_with("Transferência"))
                .then(pl.lit("Transferência"))
                .when(pl.col("title").str.starts_with("Estorno"))
                .then(pl.lit("Estorno"))
                .when(pl.col("title").str.starts_with("Compra no débito"))
                .then(pl.lit("Débito"))
                .otherwise(pl.lit("Outros"))
            ),
            unwanted_keywords=["Pagamento de fatura"],
        )
        return Transform.categorize_data(
            data,
            category_keywords=st.session_state["category_keywords_json"],
            alternative_category=pl.lit("Outros"),
        ).select(["date", "type", "transaction", "category", "title", "amount"])

    @staticmethod
    def process_data_credit_card(data: pl.DataFrame) -> pl.DataFrame:
        """Processes credit card data.

        Args:
            data (pl.DataFrame): The DataFrame containing credit card data.

        Returns:
            pl.DataFrame: A DataFrame with processed credit card data.
        """
        data = Transform.process_data(
            data,
            date_format="%Y-%m-%d",
            amount_multiplier=-1,
            transaction_type="Crédito",
            unwanted_keywords=["Pagamento recebido"],
        )
        return Transform.categorize_data(
            data,
            category_keywords=st.session_state["category_keywords_json"],
            alternative_category=pl.col("category").str.to_titlecase(),
        ).select(["date", "type", "transaction", "category", "title", "amount"])

    @staticmethod
    def concat_sort_data(*data: pl.DataFrame, date_column: str) -> pl.DataFrame:
        """Concatenates multiple DataFrames and sort by date

        Args:
            *data (pl.DataFrame): The DataFrames to concatenate.
            date_column (str): The date column to sort by.

        Returns:
            pl.DataFrame: A single DataFrame containing all the data sorted by date.
        """
        return pl.concat(data).sort(date_column, descending=True)

    @staticmethod
    def filter_data(
        data: pl.DataFrame,
        start_date: pl.Date,
        end_date: pl.Date,
        types: List[str],
        transactions: List[str],
        categories: List[str],
    ) -> pl.DataFrame:
        """Filters data based on date and categories.

        Args:
            data (pl.DataFrame): The DataFrame to filter.
            start_date (pl.Date): The start date for filtering.
            end_date (pl.Date): The end date for filtering.
            types (List[str]): The types to include.
            transactions (List[str]): The transactions to include.
            categories (List[str]): The categories to include.

        Returns:
            pl.DataFrame: A DataFrame containing the filtered data.
        """
        return data.filter(
            (pl.col("date") >= pl.lit(start_date))
            & (pl.col("date") <= pl.lit(end_date))
            & (pl.col("type").is_in(types))
            & (pl.col("transaction").is_in(transactions))
            & (pl.col("category").is_in(categories))
        )
