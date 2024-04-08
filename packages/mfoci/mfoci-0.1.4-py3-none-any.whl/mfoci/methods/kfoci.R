library("pacman")
p_load(KPC, proxy, kernlab)

args <- commandArgs(trailingOnly = TRUE)
path <- args[1]
setwd(path)

num_features <- NULL
stop <- TRUE
x <- read.csv("x.csv")
y <- read.csv("y.csv")

result <- KFOCI(y, x,  kernlab::vanilladot(), num_features = num_features, stop = stop, numCores = 1)
selected_cols <- colnames(x)[result]
write.csv(selected_cols, paste0(path, "/selected_cols_linear.csv"), row.names = FALSE)

result <- KFOCI(y, x, kernlab::rbfdot(1), num_features = num_features, stop = stop, numCores = 1)
selected_cols <- colnames(x)[result]
write.csv(selected_cols, paste0(path, "/selected_cols_gaussian.csv"), row.names = FALSE)
