from typing import Union

from polars import DataFrame, Date, Expr, col, concat, lit, when
from streamlit import session_state


class Transform:
    """Handles data transformation operations."""

    @staticmethod
    def categorize_data(
        data: DataFrame,
        category_keywords: dict[str, list[str]],
        alternative_category: Union[str, Expr],
    ) -> DataFrame:
        """Categorizes data based on title keywords.

        Args:
            data: The DataFrame containing credit card data.
            category_keywords: A dictionary containing category keywords for transactions.
            alternative_category: A string or expression used as the default category.

        Returns:
            A DataFrame with categorized data.
        """
        if category_keywords:
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    data = data.with_columns(
                        when(col("title").str.contains(keyword))
                        .then(lit(category))
                        .otherwise(alternative_category)
                        .alias("category")
                    )
        else:
            if "category" not in data.columns:
                return data.with_columns(lit("Outros").alias("category"))
            return data.with_columns(col("category").str.to_titlecase())
        return data

    @staticmethod
    def process_data(
        data: DataFrame,
        date_format: str,
        amount_multiplier: int,
        transaction_type: Union[str, Expr],
        unwanted_keywords: list[str],
    ) -> DataFrame:
        """Processes data with common operations.

        Args:
            data: The DataFrame containing the data.
            date_format: The format of the date column.
            amount_multiplier: The multiplier for the amount column.
            transaction_type: If a string, sets the entire column to that string. If an expression, evaluates row-by-row.
            unwanted_keywords: A list of unwanted keywords in the title.

        Returns:
            A DataFrame with processed data.
        """
        data = (
            data.with_columns(
                col("date").str.strptime(Date, format=date_format).alias("date")
            )
            .with_columns((col("amount") * amount_multiplier).alias("amount"))
            .with_columns(
                when(col("amount") > 0)
                .then(lit("Entrada"))
                .otherwise(lit("Saída"))
                .alias("type")
            )
        )

        if isinstance(transaction_type, Expr):
            data = data.with_columns(transaction_type.alias("transaction"))
        else:
            data = data.with_columns(lit(transaction_type).alias("transaction"))

        return data.filter(~col("title").is_in(unwanted_keywords))

    @staticmethod
    def process_data_account(data: DataFrame) -> DataFrame:
        """Processes account data.

        Args:
            data: The DataFrame containing account data.

        Returns:
            A DataFrame with processed account data.
        """
        data = data.rename({"Data": "date", "Valor": "amount", "Descrição": "title"})
        data = Transform.process_data(
            data,
            date_format="%d/%m/%Y",
            amount_multiplier=1,
            transaction_type=(
                when(col("title").str.starts_with("Transferência"))
                .then(lit("Transferência"))
                .when(col("title").str.starts_with("Estorno"))
                .then(lit("Estorno"))
                .when(col("title").str.starts_with("Compra no débito"))
                .then(lit("Débito"))
                .otherwise(lit("Outros"))
            ),
            unwanted_keywords=["Pagamento de fatura"],
        )
        return Transform.categorize_data(
            data,
            category_keywords=session_state["category_keywords_json"],
            alternative_category=lit("Outros"),
        ).select(["date", "type", "transaction", "category", "title", "amount"])

    @staticmethod
    def process_data_credit_card(data: DataFrame) -> DataFrame:
        """Processes credit card data.

        Args:
            data: The DataFrame containing credit card data.

        Returns:
            A DataFrame with processed credit card data.
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
            category_keywords=session_state["category_keywords_json"],
            alternative_category=col("category").str.to_titlecase(),
        ).select(["date", "type", "transaction", "category", "title", "amount"])

    @staticmethod
    def concat_sort_data(*data: DataFrame, date_column: str) -> DataFrame:
        """Concatenates multiple DataFrames and sorts them by date.

        Args:
            *data: The DataFrames to concatenate.
            date_column: The date column to sort by.

        Returns:
            A single DataFrame containing all the data sorted by date.
        """
        return concat(data).sort(date_column, descending=True)

    @staticmethod
    def filter_data(
        data: DataFrame,
        start_date: Date,
        end_date: Date,
        types: list[str],
        transactions: list[str],
        categories: list[str],
    ) -> DataFrame:
        """Filters data based on date, type, transactions, and categories.

        Args:
            data: The DataFrame to filter.
            start_date: The start date for filtering.
            end_date: The end date for filtering.
            types: The types to include.
            transactions: The transactions to include.
            categories: The categories to include.

        Returns:
            A DataFrame containing the filtered data.
        """
        return data.filter(
            (col("date") >= lit(start_date))
            & (col("date") <= lit(end_date))
            & (col("type").is_in(types))
            & (col("transaction").is_in(transactions))
            & (col("category").is_in(categories))
        )
