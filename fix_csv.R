library(data.table)

files <- c(
  "output/catboost_pred.csv",
  "output/lightgbm_pred.csv",
  "output/xgboost_pred.csv",
  "output/submission.csv"
)

for (f in files) {
  dt <- fread(f, colClasses = "character")
  setnames(dt, names(dt), c("serial_no", "power_mw"))
  fwrite(dt, f)
  cat("Fixed:", basename(f), "\n")
}

# Fix predictions_all.csv using correct column names
tmpl <- fread("TestSet_SubmissionTemplate/upload(no answer).csv", colClasses = "character")
serials   <- tmpl[[1]]
datetimes <- format(as.POSIXct(substr(serials,1,12), format="%Y%m%d%H%M", tz="UTC"), "%Y-%m-%d %H:%M")
locations <- as.integer(substr(serials,13,14))

cat_p <- fread("output/catboost_pred.csv",  colClasses="character")
lgb_p <- fread("output/lightgbm_pred.csv",  colClasses="character")
xgb_p <- fread("output/xgboost_pred.csv",   colClasses="character")
sub_p <- fread("output/submission.csv",      colClasses="character")

out <- data.table(
  serial_no = serials,
  datetime  = datetimes,
  location  = locations,
  catboost  = as.numeric(cat_p$power_mw),
  lightgbm  = as.numeric(lgb_p$power_mw),
  xgboost   = as.numeric(xgb_p$power_mw),
  ensemble  = as.numeric(sub_p$power_mw)
)
fwrite(out, "output/predictions_all.csv")
cat("Fixed: predictions_all.csv\n")
cat("Sample:\n"); print(head(out, 2))
cat("\nAll files now use English headers.\n")
