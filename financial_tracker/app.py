from datetime import timedelta
from typing import Optional

import polars as pl
import streamlit as st
from extractors.extractor_factory import GoogleDriveExtractorFactory
from extractors.google_drive_extractor import GoogleDriveExtractor
from transformations.transform import Transform
from visualizations.visualization import Visualization


class App:
    """Main application class for the financial tracker."""

    def __init__(
        self,
        extractor: GoogleDriveExtractor,
        transform: Transform,
        visualization: Visualization,
    ) -> None:
        """Initializes the App class with dependency injection."""
        self.google_drive = extractor
        self.transform = transform
        self.visualization = visualization
        self.data: Optional[pl.DataFrame] = None
        self.filtered_data: Optional[pl.DataFrame] = None

    @st.cache_data
    def load_data(_self, folder_id: str) -> pl.DataFrame:
        """
        Loads data from Google Drive.

        Args:
            folder_id (str): The ID of the folder containing the data files.

        Returns:
            _self.data (pl.DataFrame): A DataFrame containing the loaded data.
        """
        files = _self.google_drive.list_files(folder_id=folder_id)
        _self.data = pl.DataFrame()
        for file in files:
            file_path = _self.google_drive.download_file(file_id=file["id"])
            new_data = pl.read_csv(file_path)
            _self.data = _self.data.vstack(new_data)
        return _self.data

    def transform_data(self) -> None:
        """Transforms the loaded data."""
        credit_card_data = self.load_data(
            st.secrets["google_drive_folder_id"]["nubank_credit_card"]
        )
        account_data = self.load_data(
            st.secrets["google_drive_folder_id"]["nubank_account"]
        )
        self.data = self.transform.concat_sort_data(
            self.transform.process_data_credit_card(credit_card_data),
            self.transform.process_data_account(account_data),
            date_column="date",
        )

    def handle_refresh_data(self):
        """Handle data refreshing."""
        st.session_state["refresh_data"] = True

    def display_sidebar(self) -> None:
        """Displays options in the Streamlit sidebar."""
        with st.sidebar:
            if self.data is not None and "date" in self.data.columns:
                st.title("📁 Data Control")
                if st.button("📑 Edit data", use_container_width=True):
                    st.info(
                        f'Open [Nubank\'s page]({st.secrets["secret_urls"]["nubank"]}).'
                    )
                    st.info(
                        f'Open [Google Drive\'s page]({st.secrets["secret_urls"]["google_drive"]}).'
                    )
                    st.info(
                        f'Open [Github\'s page]({st.secrets["secret_urls"]["github"]}).'
                    )
                st.button(
                    "🔄 Refresh data",
                    on_click=self.handle_refresh_data,
                    use_container_width=True,
                )
                st.title("🔎 Filter Options")
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
                    options=list(self.data["type"].unique()),
                    default=list(self.data["type"].unique()),
                )
                transactions = st.multiselect(
                    "Transactions",
                    options=list(self.data["transaction"].unique()),
                    default=list(self.data["transaction"].unique()),
                )
                categories = st.multiselect(
                    "Categories",
                    options=list(self.data["category"].unique()),
                    default=list(self.data["category"].unique()),
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
            title: The main title displayed in the app.
        """
        if st.session_state.get("refresh_data", False):
            st.cache_data.clear()
            st.session_state["refresh_data"] = False

        st.title(title)
        self.transform_data()
        self.display_sidebar()
        self.display_visualizations()
        self.display_table()


if __name__ == "__main__":
    if "refresh_data" not in st.session_state:
        st.session_state["refresh_data"] = False

    st.set_page_config(page_title="Daric · Financial Tracker", layout="wide")

    extractor = GoogleDriveExtractorFactory().create_extractor()
    transform = Transform()
    visualization = Visualization()

    App(extractor, transform, visualization).run(title="📊 Daric · Financial Tracker")
