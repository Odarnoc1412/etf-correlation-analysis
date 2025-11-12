#portfolio_simulation.R

library(dplyr)
library(readr)
library(lubridate)
library(PerformanceAnalytics)
library(tibble)
library(xts)
library(ggplot2)
source("scripts/data_loader.R")

#Loading return .csv
returns_data <- read_csv("dashboard/full_returns.csv")

#Defining weights
weights_risk <- c(BOVA11.SA = 1/3, IVVB11.SA = 1/3, XFIX11.SA = 1/3)
weights_mixed <- c(BOVA11.SA = 0.2, IVVB11.SA = 0.2, XFIX11.SA = 0.2, LFT.SIM = 0.4)

#Saving weights
save(weights_risk, weights_mixed, file = "dashboard/portfolio_weights.RData")


# Building Risk Assets: 100% risk assets and Building Mixed Assets: 60% risk assets / 40% risk-free asset
returns_data <- returns_data %>%
    mutate(
        carteira_risk = as.numeric(as.matrix(select(., all_of(names(weights_risk)))) %*% weights_risk),
        carteira_mixed = as.numeric(as.matrix(select(., all_of(names(weights_mixed)))) %*% weights_mixed)
    )

colnames(returns_data)

#Benchmark
returns_data <- returns_data %>%
    rename(benchmark_ibov = `^BVSP`)

#Converting to xts for metrics and graphics
ret_xts <- returns_data %>%
    select(date, carteira_risk, carteira_mixed, benchmark_ibov) %>%
    column_to_rownames("date") %>%
    as.xts()

#Quickly Visualization
#charts.PerformanceSummary(ret_xts)

#Basic Metrics
#table.AnnualizedReturns(ret_xts)
#table.Stats(ret_xts)
