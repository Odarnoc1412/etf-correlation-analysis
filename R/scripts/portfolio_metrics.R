library(PerformanceAnalytics)
library(dplyr)
library(readr)
library(xts)
library(lubridate)
library(purrr)
library(tibble)

returns_data <- read_csv("dashboard/full_returns.csv")
end_date <- max(returns_data$date)

returns_data <- returns_data %>%
    rename(benchmark_ibov = `^BVSP`)
    
# Defining Time Date
janelas <- list(
    "10y" = returns_data %>% filter(date >= end_date %m-% years(10)) %>% select(date, benchmark_ibov, LFT.SIM),
    "5y" = returns_data %>% filter(date >= end_date %m-% years(5)) %>% select(date, benchmark_ibov, LFT.SIM),
    "3y" = returns_data %>% filter(date >= end_date %m-% years(3)) %>% select(date, benchmark_ibov, LFT.SIM)
)

#Metrics Calculation
calcular_metricas <- function(nome_arquivo, benchmark_df) {
    carteira_df <- read_csv(nome_arquivo)

    #Verifying if "valor" exists
    if (!"valor" %in% names(carteira_df)) {
        stop("Coluna 'valor' não encontrada em ", nome_arquivo)
    }

    #Convert to xts and calculate returns
    carteira_xts <- xts(carteira_df$valor, order.by = as.Date(carteira_df$date))
    returns <- na.omit(Return.calculate(carteira_xts))

    benchmark_xts <- xts(benchmark_df$benchmark_ibov, order.by = as.Date(benchmark_df$date))
    benchmark_returns <- na.omit(benchmark_xts) #Doesn't need to use Return.calculate because benchmark is already a daily return

    rf_returns <- xts(benchmark_df$`LFT.SIM`, order.by = as.Date(benchmark_df$date))
    rf_returns <- na.omit(rf_returns)

    #Series Alignment
    dados_alinhados <- merge(returns, benchmark_returns, join = "inner")
    dados_alinhados <- merge(dados_alinhados, rf_returns, join = "inner")
    colnames(dados_alinhados) <- c("carteira", "benchmark", "rf")

    #Check if there is sufficient returns
    if (nrow(returns) < 2 || sd(returns) == 0) {
        return(list(
            annualized = NA,
            drawdown = NA,
            sharpe = NA,
            sortino = NA,
            alpha = NA,
            beta = NA,
            tracking_error = NA
        ))
    }

    #Annualized Alpha
    alpha_diario <- CAPM.alpha(Ra = dados_alinhados[,"carteira"],
                                Rb = dados_alinhados[,"benchmark"],
                                Rf = dados_alinhados[,"rf"])
    alpha_anual <- (1 + alpha_diario)^252 - 1

    list(
        carteira = list(
            annualized = round(Return.annualized(dados_alinhados[,"carteira"]) * 100, 2),
            drawdown = round(maxDrawdown(dados_alinhados[,"carteira"]) * 100, 2),
            sharpe = round(SharpeRatio(dados_alinhados[,"carteira"], Rf = dados_alinhados[,"rf"])[1, 1] * sqrt(252), 2),
            sortino = round(SortinoRatio(dados_alinhados[,"carteira"], Rf = dados_alinhados[,"rf"])[1, 1] * sqrt(252), 2),
            alpha = round(alpha_anual * 100, 2),   # em %
            beta = round(CAPM.beta(Ra = dados_alinhados[,"carteira"],
                                   Rb = dados_alinhados[,"benchmark"]), 2),
            tracking_error = round(TrackingError(Ra = dados_alinhados[,"carteira"],
                                                 Rb = dados_alinhados[,"benchmark"]) * sqrt(252), 2)
        ),
        benchmark = list(
            annualized = round(Return.annualized(dados_alinhados[,"benchmark"]) * 100, 2),
            drawdown = round(maxDrawdown(dados_alinhados[,"benchmark"]) * 100, 2),
            sharpe = round(SharpeRatio(dados_alinhados[,"benchmark"], Rf = dados_alinhados[,"rf"])[1, 1] * sqrt(252), 2),
            sortino = round(SortinoRatio(dados_alinhados[,"benchmark"], Rf = dados_alinhados[,"rf"])[1, 1] * sqrt(252), 2)
        )
    )
}

#Defining Portfolio
carteiras <- c("risk", "mixed")

#Looping to calculate windown and portfolio
metricas <- list()

for (janela in names(janelas)) {
    benchmark_df <- janelas[[janela]]

    metricas[[janela]] <- map(carteiras, function(tipo) {
        nome_arquivo <- paste0("dashboard/rebalance_", janela, "_", tipo, ".csv")
        calcular_metricas(nome_arquivo, benchmark_df)
    })

    names(metricas[[janela]]) <- carteiras
}

#Salving all metrics in one file
save(metricas, file = "dashboard/metrics_all.RData")

