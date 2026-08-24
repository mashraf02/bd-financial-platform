from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/bd_platform"
PYTHON_BIN = "python3"

# Inside Docker, 'localhost' means the container itself, not the Windows host
# running PostgreSQL. host.docker.internal is Docker Desktop's special hostname
# that resolves to the actual host machine. We override DB_HOST just for these
# tasks so direct-from-Windows runs (outside Docker) are unaffected.
ENV_OVERRIDE = "DB_HOST=host.docker.internal"

default_args = {
    "owner": "mashraful",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="bd_financial_pipeline",
    description="Daily ingestion + load for Bangladesh Financial Data Platform",
    default_args=default_args,
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    tags=["bd-financial-platform"],
) as dag:

    install_deps = BashOperator(
        task_id="install_dependencies",
        bash_command=f"pip install -q -r {PROJECT_DIR}/requirements.txt",
    )

    run_ingestion = BashOperator(
        task_id="run_ingestion",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON_BIN} -m src.run_ingestion",
    )

    load_exchange_rates = BashOperator(
        task_id="load_exchange_rates",
        bash_command=f"cd {PROJECT_DIR} && export {ENV_OVERRIDE} && {PYTHON_BIN} -m src.loaders.load_exchange_rates",
    )

    load_world_bank = BashOperator(
        task_id="load_world_bank",
        bash_command=f"cd {PROJECT_DIR} && export {ENV_OVERRIDE} && {PYTHON_BIN} -m src.loaders.load_world_bank",
    )

    load_bb_trade = BashOperator(
        task_id="load_bb_trade",
        bash_command=f"cd {PROJECT_DIR} && export {ENV_OVERRIDE} && {PYTHON_BIN} -m src.loaders.load_bb_trade",
    )

    install_deps >> run_ingestion >> [load_exchange_rates, load_world_bank, load_bb_trade]
