cat("=== Section 0: Configuration & Setup ===\n")

USE_REDUCED_DATA   <- TRUE
SELECTED_LOCATIONS <- c(1, 2, 5, 8, 15)
OUTPUT_DIR         <- "output"
TRAINING_ROW_LIMIT <- 5000

required_packages <- c("data.table", "lubridate", "lightgbm", "xgboost", "Metrics")
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg, repos = "https://cran.r-project.org")
}
library(data.table); library(lubridate)
catboost_available <- requireNamespace("catboost", quietly = TRUE)
if (catboost_available) library(catboost)
library(lightgbm); library(xgboost); library(Metrics)
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)
cat(paste0("  TRAINING_ROW_LIMIT = ", TRAINING_ROW_LIMIT, "\n"))
cat(paste0("  CatBoost available = ", catboost_available, "\n\n"))


cat("=== Section 1: Merge Training CSVs ===\n")
merge_csv <- function(input_folders, output_folder) {
  all_data <- list(); idx <- 1
  for (folder in input_folders) {
    for (f in sort(list.files(folder, pattern = "\\.csv$", full.names = TRUE))) {
      cat(paste0("  Reading: ", f, "\n"))
      all_data[[idx]] <- fread(f, encoding = "UTF-8"); idx <- idx + 1
    }
  }
  combined <- rbindlist(all_data, use.names = TRUE, fill = TRUE)
  combined[, DateTime := as.POSIXct(DateTime, format = "%Y-%m-%d %H:%M:%OS", tz = "UTC")]
  setorder(combined, LocationCode, DateTime)
  fwrite(combined, file.path(output_folder, "training_data.csv"))
  cat(paste0("  Combined: ", nrow(combined), " rows\n"))
  combined
}
training_data <- merge_csv(c("TrainingData", "TrainingData_Additional"), OUTPUT_DIR)
if (USE_REDUCED_DATA) {
  training_data <- training_data[LocationCode %in% SELECTED_LOCATIONS]
  cat(paste0("  After filter: ", nrow(training_data), " rows\n"))
}
cat("\n")


cat("=== Section 2: Prepare External Data ===\n")
prepare_external_data <- function(input_folder, output_folder) {
  external_data <- NULL
  for (f in sort(list.files(input_folder, pattern = "\\.csv$", full.names = TRUE))) {
    cat(paste0("  Processing: ", basename(f), "\n"))
    df <- fread(f, encoding = "UTF-8")
    df[, datetime := as.POSIXct(datetime, format = "%Y-%m-%d %H:%M:%OS", tz = "UTC")]
    numeric_cols <- setdiff(names(df), "datetime")
    for (col in numeric_cols) df[, (col) := as.numeric(get(col))]
    df[, datetime_bin := as.POSIXct(floor_date(datetime, unit = "10 minutes"), tz = "UTC")]
    resampled <- df[, lapply(.SD, mean, na.rm = TRUE), by = datetime_bin, .SDcols = numeric_cols]
    setnames(resampled, "datetime_bin", "datetime")
    setorder(resampled, datetime)
    for (col in numeric_cols) {
      vals <- resampled[[col]]
      if (any(is.na(vals))) {
        non_na <- which(!is.na(vals))
        if (length(non_na) >= 2) vals <- approx(non_na, vals[non_na], seq_along(vals), rule = 2)$y
        vals[is.na(vals)] <- 0
        resampled[, (col) := vals]
      }
    }
    external_data <- if (is.null(external_data)) resampled else merge(external_data, resampled, by = "datetime", all = FALSE)
  }
  setorder(external_data, datetime)
  fwrite(external_data, file.path(output_folder, "external_data.csv"))
  cat(paste0("  External data: ", nrow(external_data), " rows, ", ncol(external_data), " cols\n"))
  external_data
}
external_data <- prepare_external_data("ExternalData", OUTPUT_DIR)
cat("\n")


cat("=== Section 3: Generate Full Data (08:00-16:59) ===\n")
generate_full_data <- function(data) {
  data <- copy(data)
  data[, DateTime := as.POSIXct(floor_date(DateTime, "1 minute"), tz = "UTC")]
  filled_list <- list()
  for (loc in unique(data$LocationCode)) {
    cat(paste0("  Location ", loc, "...\n"))
    grp <- data[LocationCode == loc]
    grp[, Date := as.IDate(DateTime)]; grp[, tod := as.ITime(DateTime)]
    dates_ok <- unique(grp[tod >= as.ITime("08:00:00") & tod <= as.ITime("16:59:00"), Date])
    if (!length(dates_ok)) next
    full_times <- do.call(c, lapply(dates_ok, function(d)
      seq(as.POSIXct(paste(d, "08:00:00"), tz="UTC"), as.POSIXct(paste(d, "16:59:00"), tz="UTC"), by="1 min")))
    g2 <- grp[!duplicated(DateTime)]; g2[, c("Date","tod") := NULL]
    m  <- merge(data.table(DateTime = full_times), g2, by = "DateTime", all.x = TRUE)
    m[, LocationCode := loc]
    filled_list[[length(filled_list)+1]] <- m
  }
  result <- rbindlist(filled_list, use.names = TRUE, fill = TRUE)
  cat(paste0("  Full data: ", nrow(result), " rows\n"))
  result
}
data <- generate_full_data(training_data); cat("\n")


cat("=== Section 4: Resample to 10-Minute Intervals ===\n")
data[, DateTime := as.POSIXct(DateTime, tz = "UTC")]
data[, DateTime_bin := as.POSIXct(floor_date(DateTime, "10 minutes"), tz = "UTC")]
num_cols <- setdiff(names(data), c("LocationCode","DateTime","DateTime_bin"))
data <- data[, c(list(DateTime = DateTime_bin[1]), lapply(.SD, mean, na.rm=TRUE)),
             by = .(LocationCode, DateTime_bin), .SDcols = num_cols]
data[, DateTime_bin := NULL]
setorder(data, LocationCode, DateTime)
cat(paste0("  Resampled: ", nrow(data), " rows\n\n"))


cat("=== Section 5: Clean, Merge External, Encode DateTime, Add Location Details ===\n")
before <- nrow(data); data <- na.omit(data)
cat(paste0("  NA drop: ", before, " -> ", nrow(data), "\n"))
data[, DateTime := as.POSIXct(DateTime, tz = "UTC")]
external_data[, datetime := as.POSIXct(datetime, tz = "UTC")]
ext_cols <- setdiff(names(external_data), "datetime")
data <- merge(data, external_data[, c("datetime", ext_cols), with=FALSE], by.x="DateTime", by.y="datetime", all.x=TRUE)
data[, timestamp := as.integer(DateTime)]; data[, month := month(DateTime)]
data[, day := mday(DateTime)]; data[, hour := hour(DateTime)]; data[, minute := minute(DateTime)]
location_details <- data.table(
  LocationCode = 1:17,
  latitude  = c(23.899444,23.899722,23.899722,23.899444,23.899444,23.899444,23.899444,23.899722,23.899444,23.899444,23.899722,23.899722,23.897778,23.897778,24.009167,24.008889,23.97512778),
  longitude = c(121.544444,121.544722,121.545000,121.544444,121.544722,121.544444,121.544444,121.545000,121.544444,121.544444,121.544722,121.544722,121.539444,121.539444,121.617222,121.617222,121.613275),
  orientation = c(181,175,180,161,208,208,172,219,151,223,131,298,249,197,127,82,0),
  altitude    = c(5,5,5,5,5,5,5,3,3,1,1,1,5,5,1,1,0)
)
data <- merge(data, location_details, by = "LocationCode", all.x = TRUE)
cat(paste0("  Final: ", nrow(data), " rows, ", ncol(data), " cols\n"))
reference_data <- copy(data); cat("\n")


cat("=== Section 6: Create Samples (Vectorized) ===\n")
excluded_cols   <- c("DateTime","WindSpeed(m/s)","Pressure(hpa)","Temperature(\u00b0C)","Humidity(%)","Sunlight(Lux)","Power(mW)")
feature_columns <- setdiff(names(data), excluded_cols)
cat(paste0("  Feature columns: ", length(feature_columns), "\n"))

create_samples <- function(data, ext_data, ref_data, feat_cols, is_train = TRUE) {
  data     <- copy(data); data[, DateTime := as.POSIXct(DateTime, tz = "UTC")]
  ref      <- copy(ref_data); ref[, DateTime := as.POSIXct(DateTime, tz = "UTC")]
  ext      <- copy(ext_data); ext[, datetime := as.POSIXct(datetime, tz = "UTC")]

  data[, tod := as.ITime(DateTime)]
  data <- data[tod >= as.ITime("09:00:00") & tod <= as.ITime("16:59:00")]
  data[, tod := NULL]

  if (is_train && nrow(data) > TRAINING_ROW_LIMIT) {
    dates_all <- sort(unique(as.Date(data$DateTime)))
    n_keep    <- min(ceiling(length(dates_all) * TRAINING_ROW_LIMIT / nrow(data)), length(dates_all))
    data      <- data[as.Date(DateTime) %in% tail(dates_all, n_keep)]
    cat(paste0("  Trimmed to ", n_keep, " dates: ", nrow(data), " rows\n"))
  }
  cat(paste0("  Processing ", nrow(data), " rows (vectorized joins)...\n"))

  # Columns to retrieve
  ref_pull <- intersect(c(feat_cols, "Power(mW)"), names(ref))
  ref_sub  <- ref[, c("LocationCode", "DateTime", ref_pull), with = FALSE]

  # Build enriched ext fallback: expand ext across all 17 locations
  cat("  Building lookup table (ext fallback)...\n")
  ext_enriched <- rbindlist(lapply(seq_len(nrow(location_details)), function(li) {
    info <- location_details[li]
    tmp  <- copy(ext)
    tmp[, LocationCode := info$LocationCode]
    tmp[, timestamp   := as.integer(datetime)]
    tmp[, month       := month(datetime)]; tmp[, day  := mday(datetime)]
    tmp[, hour        := hour(datetime)];  tmp[, minute := minute(datetime)]
    tmp[, latitude    := info$latitude];   tmp[, longitude   := info$longitude]
    tmp[, orientation := info$orientation];tmp[, altitude    := info$altitude]
    tmp[, `Power(mW)` := NA_real_]
    setnames(tmp, "datetime", "DateTime")
    cols_keep <- intersect(c("LocationCode","DateTime",ref_pull), names(tmp))
    tmp[, cols_keep, with = FALSE]
  }))

  # Combined lookup: ref first (authoritative), then ext fallback
  lookup <- rbindlist(list(ref_sub, ext_enriched), fill = TRUE)
  setkey(lookup, LocationCode, DateTime)
  lookup <- unique(lookup, by = c("LocationCode","DateTime"))
  cat(paste0("  Lookup table: ", nrow(lookup), " rows\n"))

  data[, .row := .I]

  # Vectorized yesterday join
  query_y  <- data[, .(LocationCode, DateTime = DateTime - 86400, .row)]
  joined_y <- lookup[query_y, on = .(LocationCode, DateTime), nomatch = NA]
  setorder(joined_y, .row)
  valid_y  <- !is.na(joined_y[[ref_pull[1]]])
  cat(paste0("  Skipped (no yesterday): ", sum(!valid_y), "\n"))
  data     <- data[.row %in% joined_y[valid_y, .row]]
  joined_y <- joined_y[valid_y]
  setorder(data, .row)

  # Vectorized morning join
  query_m  <- data[, .(LocationCode, DateTime = as.POSIXct(paste(as.Date(DateTime), "08:50:00"), tz="UTC"), .row)]
  joined_m <- lookup[query_m, on = .(LocationCode, DateTime), nomatch = NA]
  setorder(joined_m, .row)

  # Build feature matrices
  get_mat <- function(jt, cols) {
    m <- matrix(NA_real_, nrow(jt), length(cols)); colnames(m) <- cols
    for (col in intersect(cols, names(jt))) m[, col] <- as.numeric(jt[[col]])
    m
  }
  y_mat <- get_mat(joined_y, ref_pull)
  m_mat <- get_mat(joined_m, ref_pull)
  c_mat <- get_mat(data,     feat_cols)

  x_dt  <- as.data.table(cbind(y_mat, m_mat, c_mat))
  setnames(x_dt, gsub("[^A-Za-z0-9_]", "_",
    c(paste0("yesterday_", ref_pull), paste0("morning_", ref_pull), paste0("current_", feat_cols))))

  cat(paste0("  Done: ", nrow(x_dt), " samples, ", ncol(x_dt), " features\n"))
  list(X = x_dt, y = if (is_train) as.numeric(data[["Power(mW)"]]) else c())
}

cat("  Creating training samples...\n")
train_result <- create_samples(data, external_data, reference_data, feature_columns, is_train = TRUE)

cat("  Parsing test set...\n")
upload_template <- fread("TestSet_SubmissionTemplate/upload(no answer).csv", encoding = "UTF-8", colClasses = "character")
serial_col <- names(upload_template)[1]
upload_template[, serial_str  := as.character(get(serial_col))]
upload_template[, DateTime    := as.POSIXct(substr(serial_str,1,12), format="%Y%m%d%H%M", tz="UTC")]
upload_template[, LocationCode := as.integer(substr(serial_str,13,14))]
upload_parsed <- upload_template[, .(serial_str, DateTime, LocationCode)]
setnames(upload_parsed, "serial_str", serial_col)
upload_parsed <- merge(upload_parsed, external_data, by.x="DateTime", by.y="datetime", all.x=TRUE)
upload_parsed[, timestamp := as.integer(DateTime)]; upload_parsed[, month := month(DateTime)]
upload_parsed[, day := mday(DateTime)]; upload_parsed[, hour := hour(DateTime)]; upload_parsed[, minute := minute(DateTime)]
upload_parsed <- merge(upload_parsed, location_details, by = "LocationCode", all.x = TRUE)

cat("  Creating test samples...\n")
test_result <- create_samples(upload_parsed, external_data, reference_data, feature_columns, is_train = FALSE)
cat("\n")


cat("=== Section 7: Model Training ===\n")
train_x <- train_result$X; train_y <- train_result$y; test_x <- test_result$X
for (col in names(train_x)) set(train_x, which(is.na(train_x[[col]])), col, 0)
for (col in names(test_x))  set(test_x,  which(is.na(test_x[[col]])),  col, 0)
cat(paste0("  Train: ", nrow(train_x), " x ", ncol(train_x), " | Test: ", nrow(test_x), " x ", ncol(test_x), "\n\n"))

post_process <- function(p) round(pmax(p, 0), 2)
submission_template <- fread("TestSet_SubmissionTemplate/upload(no answer).csv", encoding = "UTF-8")
serial_col_name <- names(submission_template)[1]; answer_col_name <- names(submission_template)[2]
model_preds <- list(); model_pred_files <- c()

if (catboost_available) {
  cat("--- Training CatBoost ---\n")
  tryCatch({
    cat_model <- catboost.train(
      catboost.load_pool(as.data.frame(train_x), label = train_y),
      params = list(iterations=1500, learning_rate=0.05, depth=6, loss_function="RMSE", verbose=100))
    cat_preds <- post_process(catboost.predict(cat_model, catboost.load_pool(as.data.frame(test_x))))
    model_preds$catboost <- cat_preds
    pred_df <- copy(submission_template); pred_df[, (answer_col_name) := cat_preds]
    fwrite(pred_df, file.path(OUTPUT_DIR, "catboost_pred.csv"))
    catboost.save_model(cat_model, file.path(OUTPUT_DIR, "catboost_model.bin"))
    model_pred_files <- c(model_pred_files, file.path(OUTPUT_DIR, "catboost_pred.csv"))
    cat("  CatBoost done.\n\n")
  }, error = function(e) cat(paste0("  CatBoost failed: ", conditionMessage(e), "\n\n")))
} else cat("--- Skipping CatBoost ---\n\n")

cat("--- Training LightGBM ---\n")
tryCatch({
  lgb_model <- lgb.train(
    params  = list(objective="regression", metric="rmse", num_leaves=63, learning_rate=0.05, verbose=-1),
    data    = lgb.Dataset(as.matrix(train_x), label=train_y), nrounds=1000, verbose=1)
  lgb_preds <- post_process(predict(lgb_model, as.matrix(test_x)))
  model_preds$lightgbm <- lgb_preds
  pred_df <- copy(submission_template); pred_df[, (answer_col_name) := lgb_preds]
  fwrite(pred_df, file.path(OUTPUT_DIR, "lightgbm_pred.csv"))
  lgb.save(lgb_model, file.path(OUTPUT_DIR, "lightgbm_model.rds"))
  model_pred_files <- c(model_pred_files, file.path(OUTPUT_DIR, "lightgbm_pred.csv"))
  cat("  LightGBM done.\n\n")
}, error = function(e) cat(paste0("  LightGBM failed: ", conditionMessage(e), "\n\n")))

cat("--- Training XGBoost ---\n")
tryCatch({
  xgb_model <- xgb.train(
    params  = list(objective="reg:squarederror", eval_metric="rmse", eta=0.05, max_depth=6, tree_method="hist"),
    data    = xgb.DMatrix(as.matrix(train_x), label=train_y), nrounds=1000, verbose=1)
  xgb_preds <- post_process(predict(xgb_model, xgb.DMatrix(as.matrix(test_x))))
  model_preds$xgboost <- xgb_preds
  pred_df <- copy(submission_template); pred_df[, (answer_col_name) := xgb_preds]
  fwrite(pred_df, file.path(OUTPUT_DIR, "xgboost_pred.csv"))
  xgb.save(xgb_model, file.path(OUTPUT_DIR, "xgboost_model.rds"))
  model_pred_files <- c(model_pred_files, file.path(OUTPUT_DIR, "xgboost_pred.csv"))
  cat("  XGBoost done.\n\n")
}, error = function(e) cat(paste0("  XGBoost failed: ", conditionMessage(e), "\n\n")))


cat("=== Section 8: Ensemble & Output ===\n")
if (length(model_pred_files) == 0) {
  cat("  ERROR: No model predictions.\n")
} else {
  pred_list      <- lapply(model_pred_files, function(f) fread(f, encoding="UTF-8")[[answer_col_name]])
  ensemble_preds <- post_process(Reduce(`+`, pred_list) / length(pred_list))

  sub <- copy(submission_template); sub[, (answer_col_name) := ensemble_preds]
  fwrite(sub, file.path(OUTPUT_DIR, "submission.csv"))
  cat(paste0("  submission.csv: ", length(ensemble_preds), " rows\n"))

  all_preds <- copy(submission_template)
  all_preds[, serial_str := as.character(get(serial_col_name))]
  all_preds[, datetime   := format(as.POSIXct(substr(serial_str,1,12), format="%Y%m%d%H%M", tz="UTC"), "%Y-%m-%d %H:%M")]
  all_preds[, location   := as.integer(substr(serial_str,13,14))]
  all_preds[, serial_str := NULL]; all_preds[, (answer_col_name) := NULL]
  if (!is.null(model_preds$catboost))  all_preds[, catboost := model_preds$catboost]
  if (!is.null(model_preds$lightgbm))  all_preds[, lightgbm := model_preds$lightgbm]
  if (!is.null(model_preds$xgboost))   all_preds[, xgboost  := model_preds$xgboost]
  all_preds[, ensemble := ensemble_preds]
  fwrite(all_preds, file.path(OUTPUT_DIR, "predictions_all.csv"))
  cat(paste0("  predictions_all.csv: columns = ", paste(names(all_preds), collapse=", "), "\n"))
  cat(paste0("  Range: [", min(ensemble_preds), ", ", max(ensemble_preds), "]\n"))
}

cat("\n=== Pipeline Complete ===\n")
