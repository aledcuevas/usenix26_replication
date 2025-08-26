# DSL Experiment Reproduction Script
# Authors of "Chameleon Channels: Repurposing YouTube Channels for Deception and Profit"
# Date: 08/15/2025

# Install and load required packages
if (!require("dsl")) {
  install.packages("dsl")
}
library(dsl)

# Load datasets
cat("Loading datasets...\n")
df_socialblade <- read.csv("./data/socialblade_v_baseline.csv")
df_fswap <- read.csv("./data/fameswap_v_baseline.csv")

cat("Socialblade dataset dimensions:", dim(df_socialblade), "\n")
cat("Fameswap dataset dimensions:", dim(df_fswap), "\n")

# Define experiment parameters
model_type <- "logit"

# Define formula
experiment_formula <- pred_Y ~ V3 + V4 + L3 + L4 + C3 + C4 + D3 + D4 + R1 + R2 + DB3 + DB4 +
  N1 + S1 + VPW3 + VPW4 + pred_T2 + pred_T7 +
  pred_T9 + pred_T8 + pred_T11 + pred_T13 + pred_T6 +
  pred_T5 + pred_T1 + pred_T3 + pred_T12 + pred_T4

# Define predicted variables
predicted_variables <- c("T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T11", "T12", "T13")

# Define prediction variables
prediction_variables <- c("pred_T1", "pred_T2", "pred_T3", "pred_T4", "pred_T5", "pred_T6",
                         "pred_T7", "pred_T8", "pred_T9", "pred_T11", "pred_T12", "pred_T13")

# Print experiment configuration
cat("\n=== EXPERIMENT CONFIGURATION ===\n")
cat("Model type:", model_type, "\n")
cat("Formula:", deparse(experiment_formula), "\n")
cat("Predicted variables:", paste(predicted_variables, collapse = ", "), "\n")
cat("Prediction variables:", paste(prediction_variables, collapse = ", "), "\n")

# Run experiments
cat("\n=== RUNNING EXPERIMENTS ===\n")

# Experiment 1: Socialblade vs Baseline
cat("\n--- Experiment 1: Socialblade vs Baseline ---\n")
result_socialblade <- dsl(
  model = model_type,
  formula = experiment_formula,
  predicted_var = predicted_variables,
  prediction = prediction_variables,
  data = df_socialblade
)

cat("Socialblade experiment completed.\n")
#print(summary(result_socialblade))

# Experiment 2: Fameswap vs Baseline  
cat("\n--- Experiment 2: Fameswap vs Baseline ---\n")
result_fswap <- dsl(
  model = model_type,
  formula = experiment_formula,
  predicted_var = predicted_variables,
  prediction = prediction_variables,
  data = df_fswap
)

cat("Fameswap experiment completed.\n")
#print(summary(result_fswap))

# Store results for further analysis if needed
cat("\n=== EXPERIMENTS COMPLETED ===\n")
cat("Results stored in:\n")
cat("- result_socialblade\n")
cat("- result_fswap\n")

# Extract variables from formula for descriptive statistics
formula_vars <- all.vars(experiment_formula)
# Remove the dependent variable to get only predictors
predictor_vars <- setdiff(formula_vars, "pred_Y")

cat("\n=== DESCRIPTIVE STATISTICS ===\n")
cat("Variables in formula:", paste(formula_vars, collapse = ", "), "\n\n")

rename_map <- c(
  pred_Y = "signif_change",

  V3 = "view_count_mean",
  V4 = "view_count_std",

  L3 = "like_count_mean",
  L4 = "like_count_std",

  C3 = "comment_count_mean",
  C4 = "comment_count_std",

  D3 = "duration_mean",
  D4 = "duration_std",

  R1 = "months_first_to_last",
  R2 = "months_first_to_present",

  DB3 = "days_between_videos_mean",
  DB4 = "days_between_videos_std",

  N1 = "num_videos",
  S1 = "subscriber_count",

  VPW3 = "videos_per_week_mean",
  VPW4 = "videos_per_week_std",

  pred_T1 = "non_youtube_monetization",
  pred_T2 = "ai_generated_videos",
  pred_T3 = "political_content",
  pred_T4 = "religious_content",
  pred_T5 = "news_content",
  pred_T6 = "medical_health_content",
  pred_T7 = "cryptocurrency_content",
  pred_T8 = "gambling_content",
  pred_T9 = "financial_content",
  pred_T11 = "kids_content",
  pred_T12 = "potential_copyright_infringement",
  pred_T13 = "manosphere_redpill_content"
)

# Helper to pretty-print stats with renamed vars
print_descriptives_mapped <- function(data, vars, dataset_name) {
  mapped_vars <- ifelse(vars %in% names(rename_map), rename_map[vars], vars)
  names(mapped_vars) <- vars
  
  cat("--- Descriptive Statistics for", dataset_name, "---\n")
  
  available_vars <- intersect(vars, names(data))
  desc_stats <- data.frame()
  
  for (var in available_vars) {
    if (is.numeric(data[[var]])) {
      valid_data <- data[[var]][!is.na(data[[var]])]
      desc_stats <- rbind(desc_stats, data.frame(
        Variable = mapped_vars[[var]],
        N = length(valid_data),
        Mean = round(mean(valid_data), 4),
        SD = round(sd(valid_data), 4),
        Min = round(min(valid_data), 4),
        Max = round(max(valid_data), 4)
      ))
    }
  }
  if (nrow(desc_stats) > 0) {
    print(desc_stats, row.names = FALSE)
  }
  cat("\n")
}

# Print descriptive statistics by source
cat("--- Splitting datasets by source ---\n")

# Extract unique sources from each dataset
sources_socialblade <- unique(df_socialblade$source)
sources_fswap <- unique(df_fswap$source)

cat("Sources in Socialblade dataset:", paste(sources_socialblade, collapse = ", "), "\n")
cat("Sources in Fameswap dataset:", paste(sources_fswap, collapse = ", "), "\n\n")

# Print descriptives for each source
# 1. Fameswap source (from fswap dataset)
if ("fameswap" %in% sources_fswap) {
  fameswap_data <- df_fswap[df_fswap$source == "fameswap", ]
  print_descriptives_mapped(fameswap_data, predictor_vars, "Fameswap Source")
}

# 2. Socialblade source (from socialblade dataset)  
if ("socialblade" %in% sources_socialblade) {
  socialblade_data <- df_socialblade[df_socialblade$source == "socialblade", ]
  print_descriptives_mapped(socialblade_data, predictor_vars, "Socialblade Source")
}

# 3. Socialblade_baseline source (use from fswap dataset to avoid duplication)
if ("socialblade_baseline" %in% sources_fswap) {
  baseline_data <- df_fswap[df_fswap$source == "socialblade_baseline", ]
  print_descriptives_mapped(baseline_data, predictor_vars, "Socialblade_Baseline Source")
} else if ("socialblade_baseline" %in% sources_socialblade) {
  baseline_data <- df_socialblade[df_socialblade$source == "socialblade_baseline", ]
  print_descriptives_mapped(baseline_data, predictor_vars, "Socialblade_Baseline Source")
}

# Optional: Save results to file
save(result_socialblade, result_fswap, file = "./output/dsl_experiment_results.RData")
