import papermill as pm
import argparse
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument("--notebook", required=True)
parser.add_argument("--project-id", default="price-intel-prod")
parser.add_argument("--dataset-id", default="price_staging")
parser.add_argument("--run-date", default=str(date.today()))
parser.add_argument("--output-dir", default="reports")
args = parser.parse_args()

input_path = f"notebooks/{args.notebook}.ipynb"
output_path = f"reports/executed_notebooks/{args.notebook}_{args.run_date}.ipynb"

pm.execute_notebook(
    input_path=input_path,
    output_path=output_path,
    parameters={
        "PROJECT_ID": args.project_id,
        "DATASET_ID": args.dataset_id,
        "RUN_DATE": args.run_date,
        "OUTPUT_DIR": args.output_dir
    }
)

print(f" {args.notebook} exécuté avec succès")