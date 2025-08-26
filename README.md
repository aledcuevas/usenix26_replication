# Guide to Replicate Main Experiments

This repository contains scripts for reproducing the main results of the paper:
"Chameleon Channels: Measuring YouTube Accounts Repurposed for Deception and Profit."

## Overview

The project includes:
- **R Script** (`run_R_exps.R`): DSL experiment reproduction using the `dsl` R package
  - Note: `dsl` installation and details are found [here](https://dsl.software)
- **Python Scripts**: Data analysis pipeline with visualization and statistical analysis  
- **Bash Setup Script** (`run_python_exps.sh`): Automated Python environment setup and execution

## Prerequisites

### System Requirements
- **R** (version 4.0+ recommended)
- **Python** (version 3.8+ recommended) 
- **Bash** (Linux/macOS or WSL on Windows)
- **Git** (for cloning repository)

### Required R Packages
- `dsl` - Main package for running DSL experiments

### Required Python Packages
The `requirements.txt` file includes:
```
pandas
numpy
matplotlib
seaborn
plotly
lifelines
scipy
pyarrow
```

## Project Structure

```
project/
├── README.md
├── requirements.txt
├── run_python_exps.sh         # Bash Python setup script
├── run_R_exps.R               # R experiment script
├── data/                      # Input data directory
│   ├── socialblade_v_baseline.csv
│   ├── fameswap_v_baseline.csv
│   ├── control_event_study.parquet
│   ├── treatment_event_study.parquet
│   ├── kaplan_data.parquet
│   └── sankey_data.parquet
├── output/                    # Output directory
├── kaplan.py                  # Kaplan-Meier analysis
├── pre_post_change.py         # Pre/post analysis
└── sankey.py                  # Sankey diagram generation
```

## Required Data Files

### For R Script
Place these CSV files in the `./data/` directory:
- `socialblade_v_baseline.csv`
- `fameswap_v_baseline.csv`

### For Python Scripts
Place these files in the `./data/` directory:
- `control_event_study.parquet`
- `treatment_event_study.parquet`
- `kaplan_data.parquet`
- `sankey_data.parquet`
- The same CSV files as R script (may be used by Python scripts)

## Setup and Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Required Directories
```bash
mkdir -p data output
```

### 3. Install R Dependencies
The `reproduce_R_experiments.R` file will attempt to install the `dsl` package.
You may want to install this package separately to troubleshoot any issues you run into.
```r
# Open R or RStudio and run:
if (!require("dsl")) {
  install.packages("dsl")
}
```

## Execution Methods

### R Experiments
Run the R DSL experiments:

```bash
Rscript run_R_exps.R
```

This will:
- Load the required `dsl` R package
- Load both CSV datasets from `./data/`
- Run DSL experiments comparing Socialblade and Fameswap against baseline
- Generate descriptive statistics by data source
- Save results to `./output/dsl_experiment_results.RData`

### Python Analysis Pipeline
Run the automated Python setup and analysis:

```bash
chmod +x run_python_exps.sh
./run_python_exps.sh
```

This script will:
- Clean any existing virtual environment
- Create a new Python virtual environment
- Install all dependencies from `requirements.txt`
- Verify all required data files exist
- Run all Python analysis scripts (`kaplan.py`, `pre_post_change.py`, `sankey.py`)
- Generate all outputs in appropriate formats

## Expected Outputs

### R Script Outputs
- **Console Output**: Experiment configuration, results summaries, descriptive statistics
- **File Output**: `./output/dsl_experiment_results.RData` containing saved R objects
- **Analysis**: Comparison between Socialblade and Fameswap datasets against baseline

### Python Script Outputs  
- **Kaplan-Meier Analysis**: Survival curves and statistical comparisons
- **Pre/Post Analysis**: Before/after treatment effect analysis
- **Sankey Diagrams**: Flow visualizations of data relationships
- **Various Plot Files**: Generated in appropriate output formats

## Script Details

### R Script (`run_R_exps.R`)
- Loads two datasets for comparison against baseline
- Configures logistic regression model with comprehensive variable set
- Runs DSL experiments for both datasets
- Generates descriptive statistics by data source
- Saves results for further analysis

### Bash Script (`run_python_exps.sh`)
- Provides automated environment setup
- Includes comprehensive error checking
- Verifies all dependencies and data files
- Runs complete Python analysis pipeline
- Uses headless plotting to avoid GUI dependencies

### Python Scripts
- **kaplan.py**: Survival analysis using lifelines
- **pre_post_change.py**: Statistical comparison of pre/post repurposing effects
- **sankey.py**: Flow diagram generation using plotly

## Variable Mapping

The R script uses abbreviated variable names mapped from descriptive column names:

### Core Variables
- **Outcome**: `pred_Y` (whether the channel was repurposed) - Target prediction variable
- **Views**: `V3`, `V4` (view_count_mean, view_count_std)
- **Likes**: `L3`, `L4` (like_count_mean, like_count_std)  
- **Comments**: `C3`, `C4` (comment_count_mean, comment_count_std)
- **Duration**: `D3`, `D4` (duration_mean, duration_std)
- **Timing**: `R1`, `R2` (months_first_to_last_video, months_first_to_present)
- **Frequency**: `DB3`, `DB4` (days_between_videos_mean, days_between_videos_std)
- **Counts**: `N1`, `S1` (num_videos, subscriber_count)
- **Publishing Rate**: `VPW3`, `VPW4` (videos_per_week_mean, videos_per_week_std)

### Topic Classifications
Predicted topic variables (`pred_T1` through `pred_T14`):
- `pred_T1`: Non-YouTube monetization
- `pred_T2`: AI-generated videos  
- `pred_T3`: Political content
- `pred_T4`: Religious content
- `pred_T5`: News content
- `pred_T6`: Medical/health content
- `pred_T7`: Cryptocurrency content
- `pred_T8`: Gambling content
- `pred_T9`: Financial content
- `pred_T11`: Kids content
- `pred_T12`: Potential copyright infringement
- `pred_T13`: Manosphere/redpill content

Note: The formula excludes `pred_T14` (hateful/extremist content) due to low number of samples.

### Metadata
- `source`: indicates the group: Fameswap, Social Blade (repurposed), or Social Blade (baseline).
- `old_handle`: old channel handle.
- `new_handle`: new channel handle.
- `old_title`: old channel title.
- `new_title`: new channel title.

### Gold Standard Data
All variables that have a `pred_` prefix have been predicted with an LLM. All variables that
do not have the `pred_` prefix, have been manually annotated if they contain a value.

## Notes

- The R script includes built-in error handling for missing variables
- The bash script uses strict error handling (`set -euo pipefail`)
- All file paths use relative references from the project root
- The Python environment is isolated using virtual environments
- Output files are saved to the `./output/` directory
