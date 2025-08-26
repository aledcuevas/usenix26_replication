#!/usr/bin/env bash
set -euo pipefail

# 0) Clean start
if [ -d .venv ]; then rm -rf .venv; fi

# 1) Create & activate env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# ensure output directory exists
mkdir -p output

# 2) Install deps
pip install -r requirements.txt

# 3) Headless plotting (avoid GUI issues)
export MPLBACKEND=Agg

# 4) Quick import check
python - <<'PY'
import pandas, numpy, matplotlib, seaborn, plotly, lifelines, pyarrow, scipy
print("Imports OK")
PY

# 5) Sanity check that data files exist in ./data
for f in \
  socialblade_v_baseline.csv \
  fameswap_v_baseline.csv \
  control_event_study.parquet \
  treatment_event_study.parquet \
  kaplan_data.parquet \
  sankey_data.parquet
do
  path="data/$f"
  [ -f "$path" ] || { echo "❌ Missing file: $path" >&2; exit 1; }
done
echo "✅ All input files present."

# 6) Check output directory
[ -d output ] || { echo "❌ Missing output/ directory" >&2; exit 1; }
echo "✅ output/ directory exists."

# 7) Run your Python scripts
for s in kaplan.py pre_post_change.py sankey.py; do
  echo "Running $s ..."
  python "$s"
done

echo "✅ All scripts ran successfully."
