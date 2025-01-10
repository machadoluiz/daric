from datetime import timedelta
from io import BytesIO
from json import load
from typing import Optional

from extractors.extractor_factory import ExtractorFactory
from polars import DataFrame, Series, col, read_csv
from streamlit import (
    button,
    cache_data,
    checkbox,
    columns,
    dataframe,
    date_input,
    dialog,
    download_button,
    expander,
    file_uploader,
    header,
    info,
    multiselect,
    radio,
    rerun,
    session_state,
    set_page_config,
    sidebar,
    subheader,
    text_input,
    title,
    warning,
    write,
)
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
        self.data: Optional[DataFrame] = None
        self.filtered_data: Optional[DataFrame] = None

    @dialog("📊 Daric · Financial Tracker")
    def select_data_source(self):
        """Displays a dialog to select the data source."""
        data_source = radio(
            label="Choose your data source",
            options=["Sample data (demo)", "Local files", "Google Drive"],
        )

        if data_source == "Sample data (demo)":
            if button("Submit", type="primary", use_container_width=True):
                session_state["data_source"] = data_source
                session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                session_state["category_keywords_json"] = {}
                rerun()
        elif data_source == "Local files":
            account_files = file_uploader(
                "Upload account files", accept_multiple_files=True, type="csv"
            )
            credit_card_files = file_uploader(
                "Upload credit card files", accept_multiple_files=True, type="csv"
            )

            with expander("Category alternatives (optional)"):
                category_keywords = file_uploader("Upload file", type="json")
                with open(
                    "financial_tracker/data/category_keywords_template.json"
                ) as template:
                    download_button(
                        "Download template",
                        data=template,
                        file_name="category_keywords_template.json",
                        mime="application/json",
                        use_container_width=True,
                    )
            if button("Submit", type="primary", use_container_width=True):
                session_state["data_source"] = data_source
                session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                session_state["account_files_path"] = account_files
                session_state["credit_card_files_path"] = credit_card_files
                session_state["category_keywords_json"] = (
                    load(category_keywords) if category_keywords else {}
                )
                rerun()
        elif data_source == "Google Drive":
            info(
                "Remember to get new data from [Nubank's page](https://app.nubank.com.br/beta/) and upload it to your [Google Drive's folders](https://drive.google.com/drive/home)."
            )
            with expander("Google Cloud Platform", expanded=True):
                gcp_credentials = file_uploader("Upload credentials file", type="json")
            with expander("Google Drive", expanded=True):
                account_folder_id = text_input("Account folder ID")
                credit_card_folder_id = text_input("Credit card folder ID")
            with expander("Category alternatives (optional)"):
                category_keywords = file_uploader("Upload file", type="json")
                with open(
                    "financial_tracker/data/category_keywords_template.json"
                ) as template:
                    download_button(
                        "Download template",
                        data=template,
                        file_name="category_keywords_template.json",
                        mime="application/json",
                        use_container_width=True,
                    )
            if button("Submit", type="primary", use_container_width=True):
                session_state["data_source"] = data_source
                session_state["gcp_credentials_json"] = (
                    load(gcp_credentials) if gcp_credentials else {}
                )
                session_state["extractor"] = ExtractorFactory.create_extractor(
                    data_source
                )
                session_state["account"] = account_folder_id
                session_state["credit_card"] = credit_card_folder_id
                session_state["category_keywords_json"] = (
                    load(category_keywords) if category_keywords else {}
                )
                rerun()

    @cache_data
    def load_data(
        _self,
        data_source: str,
        folder_id: Optional[str] = None,
        path: Optional[str] = None,
    ) -> DataFrame:
        """Loads data from the preferred extractor.

        Args:
            data_source (str): The type of data source.
            folder_id (str, optional): The ID of the folder containing the data files.
            path (str, optional): The path to the local files.

        Returns:
            DataFrame: A DataFrame containing the loaded data.
        """
        if data_source == "Sample data (demo)":
            _self.data = DataFrame()
            new_data = read_csv(path)
            return _self.data.vstack(new_data)
        elif data_source == "Local files":
            _self.data = DataFrame()
            for file in path:
                file_path = BytesIO(file.read())
                new_data = read_csv(file_path)
                _self.data = _self.data.vstack(new_data)
            return _self.data
        elif data_source == "Google Drive":
            files = _self.extractor.list_files(folder_id=folder_id)
            _self.data = DataFrame()
            for file in files:
                file_path = _self.extractor.download_file(file_id=file["id"])
                new_data = read_csv(file_path)
                _self.data = _self.data.vstack(new_data)
            return _self.data
        else:
            raise ValueError(f"Unsupported data source: {data_source}")

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
            account_files_path = session_state["account_files_path"]
            credit_card_files_path = session_state["credit_card_files_path"]
            if ("uploaded_account_data" not in session_state) and (
                "uploaded_credit_card_data" not in session_state
            ):
                account_data = self.load_data(
                    data_source=data_source, path=account_files_path
                )
                credit_card_data = self.load_data(
                    data_source=data_source, path=credit_card_files_path
                )
                session_state["uploaded_account_data"] = account_data
                session_state["uploaded_credit_card_data"] = credit_card_data
            else:
                account_data = session_state["uploaded_account_data"]
                credit_card_data = session_state["uploaded_credit_card_data"]
        elif data_source == "Google Drive":
            account_data = self.load_data(
                data_source=data_source, folder_id=session_state["account"]
            )
            credit_card_data = self.load_data(
                data_source=data_source, folder_id=session_state["credit_card"]
            )
        else:
            raise ValueError(f"Unsupported data source: {data_source}")
        self.data = self.transform.concat_sort_data(
            self.transform.process_data_account(account_data),
            self.transform.process_data_credit_card(credit_card_data),
            date_column="date",
        )

    def handle_change_data_source(self) -> None:
        """Handles data source change."""
        del session_state["data_source"]

    def handle_refresh_data(self) -> None:
        """Handles data refreshing."""
        session_state["refresh_data"] = True

    def display_sidebar(self) -> None:
        """Displays options in the Streamlit sidebar."""
        with sidebar:
            if self.data is not None and "date" in self.data.columns:
                title("📁 Data options")
                button(
                    "🔀 Change data source",
                    on_click=self.handle_change_data_source,
                    use_container_width=True,
                )
                button(
                    "🔄 Refresh data",
                    on_click=self.handle_refresh_data,
                    use_container_width=True,
                )
                title("🔎 Filter options")
                with expander("Date", True):
                    date_option = checkbox("Filter to the previous month", value=True)
                    if date_option:
                        max_date = self.data.select(col("date").max()).item()
                        max_date_start = Series([max_date]).dt.truncate("1mo")[0]

                        end_date = max_date_start - timedelta(days=1)
                        start_date = Series([end_date]).dt.truncate("1mo")[0]

                        date_input("Start date", start_date, disabled=True)
                        date_input("End date", end_date, disabled=True)
                    else:
                        start_date = date_input(
                            "Start date", self.data.select(col("date").min()).item()
                        )
                        end_date = date_input(
                            "End date", self.data.select(col("date").max()).item()
                        )
                types = multiselect(
                    "Types",
                    options=list(self.data["type"].unique(maintain_order=True).sort()),
                    default=list(self.data["type"].unique(maintain_order=True).sort()),
                )
                transactions = multiselect(
                    "Transactions",
                    options=list(
                        self.data["transaction"].unique(maintain_order=True).sort()
                    ),
                    default=list(
                        self.data["transaction"].unique(maintain_order=True).sort()
                    ),
                )
                categories = multiselect(
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
                warning("Data is not available.")

    def display_visualizations(self) -> None:
        """Displays various data visualizations."""
        if self.filtered_data is not None and "date" in self.filtered_data.columns:
            header("Overview")
            col1, col2, col3 = columns(3)
            with col1:
                self.visualization.display_total_income(self.filtered_data)
            with col2:
                self.visualization.display_total_expenses(self.filtered_data)
            with col3:
                self.visualization.display_net_amount(self.filtered_data)

            header("Insights and Trends")
            col1, col2 = columns(2)
            with col1:
                subheader("Top income")
                self.visualization.create_top_income_table(self.filtered_data)
            with col2:
                subheader("Top expenses")
                self.visualization.create_top_expenses_table(self.filtered_data)
            subheader("Monthly trend of net amounts")
            self.visualization.create_monthly_trend_bar_chart(self.filtered_data)
            subheader("Amount spent per category")
            self.visualization.create_bar_chart(self.filtered_data)
            subheader("Transactions over time")
            self.visualization.create_line_chart(self.filtered_data)
            subheader("Most frequent categories")
            self.visualization.create_horizontal_bar_chart(self.filtered_data)
            subheader("Scatter plot of transactions")
            self.visualization.create_scatter_plot(self.filtered_data)
        else:
            warning("Filtered data is not available for visualization.")

    def display_table(self) -> None:
        """Displays the data table."""
        header("Detailed Transaction Records")
        write("A closer look at individual transactions during the filtered timeframe.")
        search_term = text_input(
            "Transactions records search",
            placeholder="Search transactions by title...",
            label_visibility="collapsed",
        )
        if self.filtered_data is not None and "title" in self.filtered_data.columns:
            filtered_records = self.filtered_data.filter(
                col("title").str.contains(rf"(?i){search_term}")
            )
        else:
            filtered_records = DataFrame()
            if self.filtered_data is None:
                warning("Data is not available for filtering.")
            else:
                warning("The 'title' column is missing in the data.")
        dataframe(filtered_records, use_container_width=True)

    def run(self, app_title: str, debug_mode: bool = False) -> None:
        """Runs the Streamlit app.

        Args:
            title (str): The main title displayed in the app.
        """
        if session_state["refresh_data"] is True:
            cache_data.clear()
            session_state["refresh_data"] = False

        if "data_source" not in session_state:
            self.select_data_source()
        else:
            selected_data_source = session_state["data_source"]
            title(app_title)
            self.extractor = session_state.extractor
            self.transform_data(data_source=selected_data_source)
            if debug_mode is True:
                dataframe(self.data, use_container_width=True)
            else:
                self.display_sidebar()
                self.display_visualizations()
                self.display_table()


if __name__ == "__main__":
    if "refresh_data" not in session_state:
        session_state["refresh_data"] = False

    set_page_config(
        page_title="Daric · Financial Tracker", page_icon="📊", layout="wide"
    )

    transform = Transform()
    visualization = Visualization()

    App(transform, visualization).run(
        app_title="📊 Daric · Financial Tracker", debug_mode=False
    )
