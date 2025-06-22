class Config:
    """Configuration class for static values."""
    BASE_URL = "https://eservices.mas.gov.sg/apimg-gw/server/monthly_statistical_bulletin_non610ora/exchange_rates_end_of_period_daily/views/exchange_rates_end_of_period_daily"
    DATE_FORMAT = "%Y-%m-%d"
    API_KEY = "APIKEY" # api key from subscribed MAS GOV
    SERVICE_ACCOUNT_INFO = {
        #service account for GCP with bigquery editor access
    }
    BQ_PROJECT_ID = "project_id"
    BQ_DATASET_ID = "prject_dataset"
    BQ_TABLE_ID = "project_name"
    DIMENSIONS = ['date','currency_code']
    METRICS = ['rate']

class BigQuery:
    def __init__(self, project_id, dataset_id, table_id, client = None):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = bigquery.Client.from_service_account_info(Config.SERVICE_ACCOUNT_INFO)

    def upload_to_bigquery(self, df):  # Add config as an argument
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,  # Partition by day
                field="date"  # Replace with your partition column name
            )
        )

        job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        return "Successfully uploaded to BigQuery!"

    def get_max_date(self):
        query = f"""
        SELECT MAX(date) AS max_date
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        """
        query_job = self.client.query(query)
        result = query_job.result()

        for row in result:
            return row.max_date  # Returns the max date

class MASExchangeRateAPIFetch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "accept": "application/json; charset=UTF-8",
            "KeyId": self.api_key
        }

    def fetch_data_for_date(self, date: str) -> dict:
        """
        Fetch data from the API per date.
        Args:
            date (str): Date in the format YYYY-MM-DD.
        Returns:
            dict: JSON response from the API.
        """
        params = {
            "end_of_day": date
        }
        response = requests.get(Config.BASE_URL, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Failed to fetch data for {date}: {response.status_code}, {response.text}")

    def fetch_data_in_date_range_upload_to_bigquery(self, start_date: str, end_date: str):
        """
        Fetch data for a range of dates and compile into a DataFrame.
        Args:
            start_date (str): Start date in the format YYYY-MM-DD.
            end_date (str): End date in the format YYYY-MM-DD.
        Returns:
            pd.DataFrame: Compiled DataFrame of data for the date range.
        """
        start_date_obj = start_date
        end_date_obj = end_date

        all_data = []
        current_date = start_date_obj

        while current_date <= end_date_obj:
            date_str = current_date.strftime(Config.DATE_FORMAT)
            try:
                response = self.fetch_data_for_date(date_str)
                elements = response['elements']
                for element in elements:
                    fx_date = element['end_of_day']
                    for key, value in element.items():
                        # Skip unnecessary fields
                        if key in ['end_of_day', 'preliminary']:
                            continue
                        # Process currency_code and fx_rate
                        if key.endswith("_sgd"):
                            currency_code = key.replace("_sgd", "").upper()
                            fx_rate = float(value)
                        elif key.endswith("_sgd_100"):
                            currency_code = key.replace("_sgd_100", "").upper()
                            fx_rate = float(value) / 100
                        else:
                            continue
                        # Append to data list
                        all_data.append({'date': fx_date, 'currency_code': currency_code, 'rate': fx_rate})
                df = pd.DataFrame(all_data)
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
                df['currency_code'] = df['currency_code'].astype(str)
                df['rate'] = df['rate'].astype('float64')
                print("Uploading data to BigQuery...")
                uploader = BigQuery(Config.BQ_PROJECT_ID, Config.BQ_DATASET_ID, Config.BQ_TABLE_ID)
                uploader.upload_to_bigquery(df)
                print(f"Data for {date_str} fetched successfully.")
            except Exception as e:
                print(f"Error fetching data for {date_str}: {str(e)}")
            current_date += timedelta(days=1)
        return f"uploaded data from {start_date} to {end_date}"

class ExecutePipeline:
    def __init__(self, api_fetcher, start_date, end_date):
        """
        Initializes the pipeline with an api_fetcher and an uploader.

        :param api_fetcher: Instance of MASExtraction (handles API extraction).
        :param uploader: Instance of BigQuery (handles upload to BigQuery).
        """
        self.api_fetcher = api_fetcher
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        """
        Executes the pipeline:
        1. Extracts data from the MAS Exchange Rates API.
        2. Uploads the extracted data to BigQuery.
        """
        print("Starting data extraction...")
        status = self.api_fetcher.fetch_data_in_date_range_upload_to_bigquery(self.start_date, self.end_date)
        return status
        print("Pipeline execution completed successfully.")

# main
if __name__ == "__main__":
    MAX_DATE = BigQuery(Config.BQ_PROJECT_ID, Config.BQ_DATASET_ID, Config.BQ_TABLE_ID)
    START_DATE = MAX_DATE.get_max_date() + timedelta(days=1)
    END_DATE = datetime.now(pytz.timezone('Asia/Singapore')).date() - timedelta(days=1)
    print("Fetching exchange rate data...")
    try:
        # Initialize the API fetcher
        api_fetcher = MASExchangeRateAPIFetch(Config.API_KEY)
        pipeline = ExecutePipeline(api_fetcher, START_DATE, END_DATE)
        pipeline.run()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
      
