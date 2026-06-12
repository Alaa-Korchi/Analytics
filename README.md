# Analytics Module - E-commerce Price Intelligence Platform

This folder contains the analytics component of the Real-Time E-commerce Price Intelligence Platform. The goal of this module is to analyze transformed e-commerce price data using descriptive and inferential statistics.

## Objectives

- Load transformed price data from BigQuery
- Validate data quality
- Perform descriptive statistical analysis
- Analyze price trends and volatility
- Conduct inferential statistical tests
- Build regression models for price explanation
- Generate final insights and business recommendations

## Data Sources

The analytics module uses BigQuery tables from the `price_staging` dataset:

- `stg_prices`: raw staging table
- `clean_prices`: cleaned product price observations
- `agg_prices`: aggregated product-level price metrics
- `price_time_series`: time-series product price observations
- `price_intelligence`: latest product-level price intelligence view

The main analysis is based on:

- `clean_prices`
- `price_time_series`
- `price_intelligence`

## Notebook Structure

| Notebook | Purpose |
|---|---|
| `01_data_loading_and_understanding.ipynb` | Loads data from BigQuery and explores the dataset structure |
| `02_data_quality_validation.ipynb` | Checks missing values, duplicates, invalid prices, and time-series coverage |
| `03_descriptive_statistics.ipynb` | Computes mean, median, standard deviation, volatility, price change distribution, category trends, and time-series plots |
| `04_inferential_statistics.ipynb` | Performs normality tests, Mann-Whitney test, Kruskal-Wallis test, post-hoc tests, regression, confidence intervals, and power analysis |
| `05_final_insights_and_recommendations.ipynb` | Summarizes analytical findings, limitations |

## Main Findings

- The dataset contains 10,523 cleaned observations and 934 unique products.
- Prices are highly right-skewed, with a global mean of approximately 1,801.67 MAD and a median of 979 MAD.
- Electroplanet has higher observed prices than Jumia Morocco, but catalog composition must be considered.
- Product category is the strongest driver of price differences.
- Premium categories such as `pc-gamer`, `ultrabook`, `macbook`, and `pc-hybride` have the highest price levels.
- Rating has a weak positive relationship with price.
- Review count has a moderate negative relationship with price.
- Adding product category to the regression model increases R-squared from approximately 0.29 to 0.70.

## Statistical Methods Used

- Descriptive statistics: mean, median, variance, standard deviation, quartiles, IQR
- Normality testing: Shapiro-Wilk test
- Platform comparison: Mann-Whitney U test
- Category comparison: Kruskal-Wallis test
- Post-hoc analysis: pairwise Mann-Whitney tests with Benjamini-Hochberg correction
- Correlation: Spearman rank correlation
- Regression: OLS regression with log-transformed price
- Confidence intervals: bootstrap confidence intervals
- Power analysis: Cohen's d and required sample size for 80% power

## How to Run

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt

gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID


##  Notebook Automation with Papermill

The analytics notebooks are automatically executed using Papermill], orchestrated by Apache Airflow as part of the dbt post-transformation pipeline.

### Notebooks executed (in order)

| # | Notebook | Description |
|---|----------|-------------|
| 01 | `01_data_loading_and_understanding.ipynb` | Data loading & EDA from BigQuery |
| 02 | `02_data_quality_validation.ipynb` | Data quality checks & validation |
| 03 | `03_descriptive_statistics.ipynb` | Descriptive statistics & visualizations |
| 04 | `04_inferential_statistics.ipynb` | Inferential statistics (t-test, ANOVA, regression) |

### Run manually (local)

```bash
python scripts/run_notebook.py \
  --project-id price-intel-prod \
  --dataset-id price_staging \
  --run-date 2026-06-11 \
  --output-dir reports
```

### Parameters (injected by Papermill)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PROJECT_ID` | GCP Project ID | `price-intel-prod` |
| `DATASET_ID` | BigQuery dataset | `price_staging` |
| `RUN_DATE` | Execution date | today's date |
| `OUTPUT_DIR` | Output directory | `reports` |

### Output

- Executed notebooks → `reports/executed_notebooks/`
- CSV exports → `reports/tables/`

> Generated files are excluded from Git via `.gitignore`.
> They are recreated automatically at each Airflow run.


## CI/CD

The CI pipeline is defined in `.github/workflows/analytics-ci.yml` and runs on every push or pull request to `main` and `develop`.

| Job | Description |
|---|---|
| `lint` | Checks all Python files for critical errors (syntax, undefined variables) using Flake8 |
| `validate-imports` | Verifies that all core analytics libraries import correctly (pandas, numpy, scipy, statsmodels, scikit-learn, pingouin, plotly, matplotlib, seaborn) |
| `validate-notebooks` | Validates that all notebooks are well-formed and parseable using nbformat |
| `validate-streamlit` | Checks `dashboard/streamlit_app.py` for syntax errors |
| `validate-runner` | Checks `run_notebook.py` for syntax errors |

> Package versions in the CI are pinned to match `requirements.txt`. Only direct dependencies are installed — not the full frozen environment — to keep the pipeline fast and stable across runs.