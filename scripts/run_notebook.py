import papermill as pm
import argparse
from datetime import date
from pathlib import Path

NOTEBOOKS = [
    "01_data_loading_and_understanding",
    "02_data_quality_validation",
    "03_descriptive_statistics",
    "04_inferential_statistics"
]

parser = argparse.ArgumentParser()
parser.add_argument("--project-id", default="price-intel-prod")
parser.add_argument("--dataset-id", default="price_staging")
parser.add_argument("--run-date", default=str(date.today()))
parser.add_argument("--output-dir", default="reports")
args = parser.parse_args()

for notebook in NOTEBOOKS:
    input_path = f"notebooks/{notebook}.ipynb"
    output_path = f"reports/executed_notebooks/{notebook}_{args.run_date}.ipynb"
    
    print(f"Exécution de {notebook}...")
    
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
    print(f" {notebook} terminé !")

print("Tous les notebooks exécutés avec succès !")