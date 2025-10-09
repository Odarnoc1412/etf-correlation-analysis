# etf-correlation-analysis
"Correlation analysis and portfolio efficiency using Brazilian ETFs (BOVA11, IVVB11 and XFIX11) with Python, R, and Business Intelligence tools."

While etf-correlation-analysis focuses on visualization, storytelling, and exploratory analysis using Python, R, and BI tools, portfolio-efficiency-etfs serves as the technical backbone for:

Data collection and normalization (ETFs, IFIX, Selic Over)

LFT simulation based on daily Selic rates

Efficient frontier and equal-weight portfolio modeling

Modular organization for reuse and scalability

### How to set up access to the brapi.dev API
Create a free account at brapi.dev

Generate your API key

Create a file named config_loader.py with the following content:

BRAPI_TOKEN = "your_api_key_here"

The ifix_loader.py script can be executed directly to attempt downloading data via the brapi.dev API.

For use within the pipeline, the ifix_snapshot.csv file must be present in the data_sources/ directory.

The pipeline only uses the load_ifix_data() function, which loads the data from the CSV and filters it up to December 31, 2020.
