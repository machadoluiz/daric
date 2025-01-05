import io
import json
from datetime import timedelta
from typing import Optional

import polars as pl
import streamlit as st
from extractors.extractor_factory import ExtractorFactory
from transformations.transform import Transform
from visualizations.visualization import Visualization


class App:
    """Main application class for the financial tracker."""

    def __init__(
        self,
        transform: Transform,
        visualization: Visualization,
    ) -> None:
        """Initializes the App class with dependency injection.

        Args:
            transform (Transform): The transformation logic.
            visualization (Visualization): The visualization logic.
        """
        self.extractor = None
        self.transform = transform
        self.visualization = visualization
        self.data: Optional[pl.DataFrame] = None
        self.filtered_data: Optional[pl.DataFrame] = None

    @st.dialog("📊 Daric · Financial Tracker")
    def select_data_source(self):
        """Displays a dialog to select the data source."""
        data_source = st.radio(
            label="Choose your data source",
            options=["Sample data (demo)", "Local files", "Google Drive"],
        )

        if data_source == "Sample data (demo)":
            if st.button("Submit", type="primary", use_container_width=True):
                st.session_state["data_source"] = data_source
                st.session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                st.session_state["category_keywords_json"] = {}
                st.rerun()
        elif data_source == "Local files":
            account_files = st.file_uploader(
                "Upload account files", accept_multiple_files=True, type="csv"
            )
            credit_card_files = st.file_uploader(
                "Upload credit card files", accept_multiple_files=True, type="csv"
            )

            with st.expander("Category alternatives (optional)"):
                category_keywords = st.file_uploader("Upload file", type="json")
                with open(
                    "financial_tracker/data/category_keywords_template.json"
                ) as template:
                    st.download_button(
                        "Download template",
                        data=template,
                        file_name="category_keywords_template.json",
                        mime="application/json",
                        use_container_width=True,
                    )
            if st.button("Submit", type="primary", use_container_width=True):
                st.session_state["data_source"] = data_source
                st.session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                st.session_state["account_files_path"] = account_files
                st.session_state["credit_card_files_path"] = credit_card_files
                st.session_state["category_keywords_json"] = (
                    json.load(category_keywords) if category_keywords else {}
                )
                st.rerun()
        elif data_source == "Google Drive":
            st.info(
                "Remember to get new data from [Nubank's page](https://app.nubank.com.br/beta/) and upload it to your [Google Drive's folders](https://drive.google.com/drive/home)."
            )
            with st.expander("Google Cloud Platform", expanded=True):
                gcp_credentials = st.file_uploader(
                    "Upload credentials file", type="json"
                )
            with st.expander("Google Drive", expanded=True):
                account_folder_id = st.text_input("Account folder ID")
                credit_card_folder_id = st.text_input("Credit card folder ID")
            with st.expander("Category alternatives (optional)"):
                category_keywords = st.file_uploader("Upload file", type="json")
                with open(
                    "financial_tracker/data/category_keywords_template.json"
                ) as template:
                    st.download_button(
                        "Download template",
                        data=template,
                        file_name="category_keywords_template.json",
                        mime="application/json",
                        use_container_width=True,
                    )
            if st.button("Submit", type="primary", use_container_width=True):
                st.session_state["data_source"] = data_source
                st.session_state["gcp_credentials_json"] = json.load(gcp_credentials)
                st.session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                st.session_state["account"] = account_folder_id
                st.session_state["credit_card"] = credit_card_folder_id
                st.session_state["category_keywords_json"] = (
                    json.load(category_keywords) if category_keywords else {}
                )
                st.rerun()

    @st.cache_data
    def load_data(
        _self, data_source: str, folder_id: str = None, path: str = None
    ) -> pl.DataFrame:
        """Loads data from the preferred extractor.

        Args:
            data_source (str): The type of data source.
            folder_id (str, optional): The ID of the folder containing the data files.
            path (str, optional): The path to the local files.

        Returns:
            pl.DataFrame: A DataFrame containing the loaded data.
        """
        if data_source == "Sample data (demo)":
            _self.data = pl.DataFrame()
            new_data = pl.read_csv(path)
            return _self.data.vstack(new_data)
        elif data_source == "Local files":
            _self.data = pl.DataFrame()
            for file in path:
                file_path = io.BytesIO(file.read())
                new_data = pl.read_csv(file_path)
                _self.data = _self.data.vstack(new_data)
            return _self.data
        elif data_source == "Google Drive":
            files = _self.extractor.list_files(folder_id=folder_id)
            _self.data = pl.DataFrame()
            for file in files:
                file_path = _self.extractor.download_file(file_id=file["id"])
                new_data = pl.read_csv(file_path)
                _self.data = _self.data.vstack(new_data)
            return _self.data

    def transform_data(self, data_source: str) -> None:
        """Transforms the loaded data.

        Args:
            data_source (str): The type of data source.
        """
        if data_source == "Sample data (demo)":
            account_data = self.load_data(
                data_source=data_source,
                path="financial_tracker/data/sample_account_data.csv",
            )
            credit_card_data = self.load_data(
                data_source=data_source,
                path="financial_tracker/data/sample_credit_card_data.csv",
            )
        elif data_source == "Local files":
            account_files_path = st.session_state["account_files_path"]
            credit_card_files_path = st.session_state["credit_card_files_path"]
            if ("uploaded_account_data" not in st.session_state) and (
                "uploaded_credit_card_data" not in st.session_state
            ):
                account_data = self.load_data(
                    data_source=data_source, path=account_files_path
                )
                credit_card_data = self.load_data(
                    data_source=data_source, path=credit_card_files_path
                )
                st.session_state["uploaded_account_data"] = account_data
                st.session_state["uploaded_credit_card_data"] = credit_card_data
            else:
                account_data = st.session_state["uploaded_account_data"]
                credit_card_data = st.session_state["uploaded_credit_card_data"]
        elif data_source == "Google Drive":
            account_data = self.load_data(
                data_source=data_source, folder_id=st.session_state["account"]
            )
            credit_card_data = self.load_data(
                data_source=data_source, folder_id=st.session_state["credit_card"]
            )
        self.data = self.transform.concat_sort_data(
            self.transform.process_data_account(account_data),
            self.transform.process_data_credit_card(credit_card_data),
            date_column="date",
        )

    def handle_change_data_source(self) -> None:
        """Handles data source change."""
        del st.session_state["data_source"]

    def handle_refresh_data(self) -> None:
        """Handles data refreshing."""
        st.session_state["refresh_data"] = True

    def display_sidebar(self) -> None:
        """Displays options in the Streamlit sidebar."""
        with st.sidebar:
            if self.data is not None and "date" in self.data.columns:
                st.title("📁 Data options")
                st.button(
                    "🔀 Change data source",
                    on_click=self.handle_change_data_source,
                    use_container_width=True,
                )
                st.button(
                    "🔄 Refresh data",
                    on_click=self.handle_refresh_data,
                    use_container_width=True,
                )
                st.title("🔎 Filter options")
                with st.expander("Date", True):
                    date_option = st.checkbox(
                        "Filter to the previous month", value=True
                    )
                    if date_option:
                        max_date = self.data["date"].max()
                        end_date = max_date.replace(day=1) - timedelta(days=1)
                        start_date = end_date.replace(day=1)
                        st.date_input("Start date", start_date, disabled=True)
                        st.date_input("End date", end_date, disabled=True)
                    else:
                        start_date = st.date_input(
                            "Start date", self.data["date"].min()
                        )
                        end_date = st.date_input("End date", self.data["date"].max())
                types = st.multiselect(
                    "Types",
                    options=list(self.data["type"].unique(maintain_order=True).sort()),
                    default=list(self.data["type"].unique(maintain_order=True).sort()),
                )
                transactions = st.multiselect(
                    "Transactions",
                    options=list(
                        self.data["transaction"].unique(maintain_order=True).sort()
                    ),
                    default=list(
                        self.data["transaction"].unique(maintain_order=True).sort()
                    ),
                )
                categories = st.multiselect(
                    "Categories",
                    options=list(
                        self.data["category"].unique(maintain_order=True).sort()
                    ),
                    default=list(
                        self.data["category"].unique(maintain_order=True).sort()
                    ),
                )
                self.filtered_data = self.transform.filter_data(
                    self.data, start_date, end_date, types, transactions, categories
                )
            else:
                st.warning("Data is not available.")

    def display_visualizations(self) -> None:
        """Displays various data visualizations."""
        if self.filtered_data is not None and "date" in self.filtered_data.columns:
            st.header("Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                self.visualization.display_total_income(self.filtered_data)
            with col2:
                self.visualization.display_total_expenses(self.filtered_data)
            with col3:
                self.visualization.display_net_amount(self.filtered_data)

            st.header("Insights and Trends")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top income")
                self.visualization.create_top_income_table(self.filtered_data)
            with col2:
                st.subheader("Top expenses")
                self.visualization.create_top_expenses_table(self.filtered_data)
            st.subheader("Monthly trend of net amounts")
            self.visualization.create_monthly_trend_bar_chart(self.filtered_data)
            st.subheader("Amount spent per category")
            self.visualization.create_bar_chart(self.filtered_data)
            st.subheader("Transactions over time")
            self.visualization.create_line_chart(self.filtered_data)
            st.subheader("Most frequent categories")
            self.visualization.create_horizontal_bar_chart(self.filtered_data)
            st.subheader("Scatter plot of transactions")
            self.visualization.create_scatter_plot(self.filtered_data)
        else:
            st.warning("Filtered data is not available for visualization.")

    def display_table(self) -> None:
        """Displays the data table."""
        st.header("Detailed Transaction Records")
        st.write(
            "A closer look at individual transactions during the filtered timeframe."
        )
        search_term = st.text_input(
            "Transactions records search",
            placeholder="Search transactions by title...",
            label_visibility="collapsed",
        )
        if self.filtered_data is not None and "title" in self.filtered_data.columns:
            filtered_records = self.filtered_data.filter(
                pl.col("title").str.contains(rf"(?i){search_term}")
            )
        else:
            filtered_records = pl.DataFrame()
            if self.filtered_data is None:
                st.warning("Data is not available for filtering.")
            else:
                st.warning("The 'title' column is missing in the data.")
        st.dataframe(filtered_records, use_container_width=True)

    def run(self, title: str) -> None:
        """Runs the Streamlit app.

        Args:
            title (str): The main title displayed in the app.
        """
        if st.session_state["refresh_data"] is True:
            st.cache_data.clear()
            st.session_state["refresh_data"] = False

        if "data_source" not in st.session_state:
            self.select_data_source()
        else:
            selected_data_source = st.session_state["data_source"]
            st.title(title)
            self.extractor = st.session_state.extractor
            self.transform_data(data_source=selected_data_source)
            self.display_sidebar()
            self.display_visualizations()
            self.display_table()


if __name__ == "__main__":
    if "refresh_data" not in st.session_state:
        st.session_state["refresh_data"] = False

    st.set_page_config(
        page_title="Daric · Financial Tracker", page_icon="📊", layout="wide"
    )

    transform = Transform()
    visualization = Visualization()

    App(transform, visualization).run(title="📊 Daric · Financial Tracker")
