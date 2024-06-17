# 📊 Daric · Financial Tracker

Daric is a Python-based web app that allows you to track your financial transactions and visualize your spending patterns.

## 🔥 Features

- **Multiple Data Sources**: Supports loading data from sample files, local CSV files, and Google Drive folders.
- **Customizable Categories**: Allows mapping transaction titles to custom categories using a JSON template.
- **Sidebar Filtering**: Filter transactions by date range, type, transaction category, and more using the sidebar.
- **Metrics and KPIs**: Displays key metrics like net amount, top income/expenses, and monthly trends.

## 🚀 Getting Started

### Using the Hosted App

1. Access the Daric app at https://daric-financial-tracker.streamlit.app/

2. Choose one of the three data source options:

   a) **Sample Data**: Select "Sample data (demo)" to quickly explore the app with pre-loaded data.

   b) **Local Files**: 
      - Select "Local files" as the data source.
      - Upload CSV files for account and credit card transactions. See [this guide](https://comunidade.nubank.com.br/t/extratos-em-cvs-ou-xls/505800/3) for exporting data from Nubank.
      - (Optional) Upload a JSON file mapping transaction titles to categories. Download the template to get started.

   c) **Google Drive**:  
      - Select "Google Drive" as the data source.
      - Create a Google Cloud Platform (GCP) project and enable the Google Drive API. Follow [these instructions](https://developers.google.com/workspace/guides/create-credentials#api-key) to create a service account and download the JSON credentials file.
      - Upload the GCP service account JSON credentials file in the Daric app.
      - Export your account and credit card transaction data as CSV files. See [this guide](https://comunidade.nubank.com.br/t/extratos-em-cvs-ou-xls/505800/3) for exporting data from Nubank.
      - Upload the exported CSV files to an account data folder and a credit card data folder, in your Google Drive.
      - Share the Google Drive folders containing the CSV files with the service account, using the service account's client email address. 
      - Copy the folders ID from the Google Drive folder URL and enter it into the corresponding fields in the Daric app. The folder ID is the string of characters after the last slash in the URL.
        ```
        Format: https://drive.google.com/drive/folders/FOLDER_ID_GOES_HERE
        Example: 1Abcdefgh2ijkLMNop3qrSTUV4wxYZ567
        ```
      - (Optional) To map transaction titles to custom categories, create a JSON file using the provided template. Upload this file to the Daric app.

3. Click "Submit" and _voila_! Enjoy tracking your financial health and making data-driven decisions with Daric. 

### Self-Hosting

Want to run Daric on your own machine? It's easy!

1. Ensure you have Python 3.7+ installed
2. Clone this repository:
   ```shell
   git clone https://github.com/machadoluiz/daric.git
   ```
3. Navigate to the project directory:
   ```shell
   cd daric
   ```
4. Install the required Python packages: 
   ```shell
   pip install -r requirements.txt
   ```
5. Run the Streamlit app:
   ```shell
   streamlit run financial_tracker/app.py
   ``` 
6. Open the displayed URL in your web browser and start tracking your finances!

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue on the [GitHub Issues](https://github.com/machadoluiz/daric/issues) page. If you'd like to contribute code, please fork the repository and create a pull request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).