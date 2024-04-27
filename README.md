# 📊 Daric · Financial Tracker

Daric is a Python-based web app that allows you to track your financial transactions and visualize your spending patterns. It uses Streamlit, Google Drive API, and Altair to provide an interactive and user-friendly interface.

## 🔥 Features

- **Data Integration**: Seamlessly connects with Google Drive API to fetch and process financial data.
- **Transaction Filtering**: Supports filtering transactions by date range and categories.
- **Rich Visualizations**: Generates a variety of charts including bar, pie, line, horizontal bar, and scatter plots to visualize data effectively.
- **Detailed Transaction View**: Provides a comprehensive data table for viewing all transaction details.

## 🧑‍💻 Local Development

To run Daric locally, use the following command:

   ```shell
   python -m streamlit run financial_tracker/app.py
   ```

## 🚀 Usage

1. Set up your Google Drive API credentials and store them as secrets in Streamlit Cloud:

   - Follow the instructions in the [Google Drive API documentation](https://developers.google.com/drive) to obtain the necessary credentials JSON file.
   - Open the Streamlit Cloud Dashboard at [https://share.streamlit.io](https://share.streamlit.io) and navigate to your Daric project.
   - Go to "Settings" > "Secrets" and add a new secret called `GCP_SERVICE_ACCOUNT`.
   - Copy the contents of your Google Drive API credentials JSON file into the value field, following the template below:

```plaintext
[gcp_service_account]
type =
project_id =
private_key_id =
private_key =
client_email =
client_id =
auth_uri =
token_uri =
auth_provider_x509_cert_url =
client_x509_cert_url =
universe_domain =
```

2. Set up the Google Drive folder that will store credit card and account data in CSV format:

   - Share the folders with the service account's client e-mail address, created in the last step.
   - Copy the ID from each folder and paste them into the value field, following the template below:

```plaintext
[google_drive_folder_id]
nubank_credit_card =
nubank_account =
```

3. Commit and push your changes to the repository.

4. Streamlit Cloud will automatically build and deploy your app. Once the deployment is complete, you will be provided with an address to access your app.

5. Access your Daric app using the provided address. Enjoy tracking your financial transactions and visualizing your spending patterns!
