# Source in each Ubuntu terminal; not a PowerShell script.
export CLUB_COURSE=/mnt/d/projects/data-engineering-lab/docs/data-engineering
export CLUB_LAB_ROOT=/mnt/d/projects/data-engineering-lab/.learning-runtime
export AIRFLOW_HOME="$CLUB_LAB_ROOT/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$CLUB_COURSE/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DEFAULT_TIMEZONE=Asia/Hong_Kong
export AIRFLOW__API__HOST=127.0.0.1
export PIP_CACHE_DIR="$CLUB_LAB_ROOT/cache/pip"
export TMPDIR="$CLUB_LAB_ROOT/tmp"
export SPARK_LOCAL_DIRS="$CLUB_LAB_ROOT/tmp/spark"
export SPARK_LOCAL_IP=127.0.0.1
export PYTHONDONTWRITEBYTECODE=1
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
mkdir -p "$AIRFLOW_HOME" "$PIP_CACHE_DIR" "$TMPDIR" "$SPARK_LOCAL_DIRS"
