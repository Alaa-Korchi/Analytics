# 📊 E-commerce Price Intelligence Platform — Analytics Module

> Statistical analysis pipeline for a real-time e-commerce price monitoring system, tracking product prices across two major Moroccan online retailers (**Jumia Morocco** and **Electroplanet**).

---

## 🎯 Project Overview

This module is the analytical core of a larger **Real-Time E-commerce Price Intelligence Platform**. Its goal is to transform raw scraped price data into actionable business insights using rigorous descriptive and inferential statistics.

The analysis answers key business questions:

- How are product prices distributed, and how do they vary by category and platform?
- Are price differences between Jumia Morocco and Electroplanet statistically significant?
- Which factors (rating, review count, time, category) explain price variation?
- How volatile are prices over time, and which products see the biggest swings?

**Dataset at a glance:**

| Metric | Value |
|---|---|
| Cleaned observations | 10,523 |
| Unique products | 934 |
| E-commerce platforms | 2 (Jumia Morocco, Electroplanet) |
| Product categories | 18 |
| Observation period | May 1, 2026 – June 10, 2026 |
| Average price | ≈ 1,801.67 MAD |
| Median price | 979 MAD |

---

## 🏗️ Pipeline Architecture

Data flows from BigQuery staging tables, through a 5-stage notebook pipeline, into final business insights:

```
BigQuery (price_staging dataset)
        │
        ▼
┌─────────────────────────────────────────────────┐
│ 01 │ Data Loading & Understanding                │
│ 02 │ Data Quality Validation                     │
│ 03 │ Descriptive Statistics & Trends             │
│ 04 │ Inferential Statistics & Modeling           │
│ 05 │ Final Insights & Recommendations            │
└─────────────────────────────────────────────────┘
        │
        ▼
   reports/ (executed notebooks + CSV exports)
```

### BigQuery Data Sources (`price_staging` dataset)

| Table | Description |
|---|---|
| `stg_prices` | Raw staging table |
| `clean_prices` | Cleaned product-level price observations (main table) |
| `agg_prices` | Aggregated product-level price metrics |
| `price_time_series` | Time-series price observations per product |
| `price_intelligence` | Latest product-level price intelligence view |

---

## 📓 Notebook Breakdown

### `01_data_loading_and_understanding.ipynb`
Connects to BigQuery, loads all five analytical tables, inspects schema and shape, converts date columns, and produces a structural summary of the dataset (row counts, unique products, sites, categories).

### `02_data_quality_validation.ipynb`
Validates dataset integrity before any statistical work:
- Missing value analysis (column-level, % and counts)
- Duplicate detection (exact + business-key duplicates)
- Invalid price checks (≤ 0 values)
- Date range consistency
- Distribution of observations by site and category
- Time-series coverage per product

**Result:** 0 missing values in core fields, 0 duplicates, 0 invalid prices — dataset confirmed clean for analysis.

### `03_descriptive_statistics.ipynb`
Computes the statistical backbone of the project:
- Global and group-level descriptive statistics (mean, median, std, variance, IQR, range) by site and by category
- Price distributions (raw and log-transformed), histograms and boxplots
- Price volatility per product (std dev, range)
- Time-series trends (daily average price, category-level trends)
- Top movers: largest price increases, decreases, and most volatile products

### `04_inferential_statistics.ipynb`
The statistical hypothesis-testing core of the project:

| Test | Purpose | Result |
|---|---|---|
| Shapiro-Wilk | Normality of price distributions | Not normal (raw & log) → non-parametric tests used |
| Mann-Whitney U | Jumia vs Electroplanet price comparison | Statistically significant difference (p < 0.05) |
| Kruskal-Wallis | Price differences across categories | Statistically significant (p < 0.05) |
| Post-hoc (Mann-Whitney + Benjamini-Hochberg) | Pairwise category comparisons | 146 / 153 pairs significant |
| Spearman correlation | Price vs rating / review count / time | Weak positive (rating), moderate negative (reviews) |
| OLS Regression (log-price) | Explain price variation | R² = 0.29 (without category) → 0.70 (with category) |
| Bootstrap Confidence Intervals | Robust estimates of mean/median price by site | Non-overlapping CIs → Electroplanet higher |
| Power Analysis (Cohen's d) | Statistical power of site comparison | Very large effect size (d ≈ 1.39), well-powered |

### `05_final_insights.ipynb`
Synthesizes all findings into an executive summary, key dataset facts, descriptive and inferential insight summaries, confidence interval results, project limitations, and final business recommendations.

---

## 🔑 Key Findings

- **Prices are highly right-skewed**: a small number of premium products (gaming PCs, MacBooks, ultrabooks) pull the mean well above the median.
- **Platform matters**: Electroplanet shows significantly higher average and median prices than Jumia Morocco — but this is partly explained by differences in catalog composition (Jumia has a much larger, more accessory-heavy catalog).
- **Category is the dominant price driver**: adding product category to the regression model raises explained variance (R²) from **29% to 70%** — by far the strongest predictor of price.
- **Rating and review count have modest effects**: higher ratings are weakly associated with higher prices; higher review counts are moderately associated with lower prices.
- **Statistically sound methodology**: non-parametric tests were used throughout due to confirmed non-normality, with multiple-comparison correction (Benjamini-Hochberg) applied to post-hoc tests.

---

## ⚠️ Limitations

- **Sample imbalance**: Jumia Morocco contributes far more observations than Electroplanet, which can bias direct platform comparisons.
- **Non-identical catalogs**: the two platforms don't sell the exact same product mix, so part of the observed price gap reflects catalog differences rather than pure pricing strategy.
- **Missing data on engagement metrics**: `rating` and `review_count` have substantial missingness; correlation and regression analyses were restricted to complete cases.
- **Short observation window**: ~6 weeks of data is sufficient for short-term price monitoring but too short to detect seasonal effects.

---

## 🛠️ Statistical Methods Used

- **Descriptive**: mean, median, variance, standard deviation, quartiles, IQR
- **Normality testing**: Shapiro-Wilk
- **Group comparisons**: Mann-Whitney U (2 groups), Kruskal-Wallis (k groups)
- **Multiple comparisons**: Pairwise Mann-Whitney with Benjamini-Hochberg (FDR) correction
- **Correlation**: Spearman rank correlation
- **Regression**: OLS on log-transformed price, with and without categorical controls
- **Uncertainty estimation**: Bootstrap confidence intervals (5,000 resamples)
- **Power analysis**: Cohen's d and required sample size for 80% power

---

## ⚙️ How to Run

### 1. Environment Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### 3. Run the notebooks

Notebooks must be executed in order (01 → 05), either manually in Jupyter or via the automated pipeline below.

---

## 🔄 Automated Execution (Papermill + Airflow)

Notebooks 01–04 are executed automatically via **Papermill**, orchestrated by **Apache Airflow** as a post-transformation step in the dbt pipeline.

### Manual local run

```bash
python scripts/run_notebook.py \
  --project-id price-intel-prod \
  --dataset-id price_staging \
  --run-date 2026-06-11 \
  --output-dir reports
```

### Injected Parameters

| Parameter | Description | Default |
|---|---|---|
| `PROJECT_ID` | GCP Project ID | `price-intel-prod` |
| `DATASET_ID` | BigQuery dataset | `price_staging` |
| `RUN_DATE` | Execution date | today's date |
| `OUTPUT_DIR` | Output directory | `reports` |

### Outputs

- Executed notebooks → `reports/executed_notebooks/`
- CSV table exports → `reports/tables/`

> Generated report files are excluded from version control via `.gitignore` and are recreated automatically on each pipeline run.

---

##  CI/CD Pipeline

Defined in `.github/workflows/analytics-ci.yml`, triggered on every push/PR to `main` and `develop`.

| Job | Description |
|---|---|
| `lint` | Flake8 checks for syntax errors and undefined variables |
| `validate-imports` | Confirms core libraries import correctly (pandas, numpy, scipy, statsmodels, scikit-learn, pingouin, plotly, matplotlib, seaborn) |
| `validate-notebooks` | Ensures all notebooks are well-formed and parseable (nbformat) |
| `validate-streamlit` | Syntax check on `dashboard/streamlit_app.py` |
| `validate-runner` | Syntax check on `run_notebook.py` |

> Dependency versions in CI are pinned to match `requirements.txt`. Only direct dependencies are installed to keep pipeline runs fast and stable.

---

## 📁 Project Structure

```
analytics/
├── 01_data_loading_and_understanding.ipynb
├── 02_data_quality_validation.ipynb
├── 03_descriptive_statistics.ipynb
├── 04_inferential_statistics.ipynb
├── 05_final_insights.ipynb
├── scripts/
│   └── run_notebook.py
├── dashboard/
│   └── streamlit_app.py
├── reports/                  # generated, gitignored
│   ├── executed_notebooks/
│   └── tables/
├── requirements.txt
└── .github/workflows/analytics-ci.yml
```
