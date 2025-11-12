library(ggplot2)
library(readr)
library(dplyr)
library(lubridate)
library(knitr)
library(purrr)
library(gridExtra)

#Loading Data
load("dashboard/metrics_all.RData")

#Function to prepare benchmark and portfolios
preparar_dados_plot <- function(janela) {
    #Loading Simulations
    risk <- read_csv(paste0("dashboard/rebalance_", janela, "_risk.csv")) %>% mutate(carteira = "Risk")
    mixed <- read_csv(paste0("dashboard/rebalance_", janela, "_mixed.csv")) %>% mutate(carteira = "Mixed")

    #Benchmark
    returns_data <- read_csv("dashboard/full_returns.csv") %>%
        rename(benchmark_ibov = `^BVSP`)
    end_date <- max(returns_data$date)

    anos <- as.numeric(gsub("y","",janela))

    benchmark <- returns_data %>%
        filter(date >= end_date %m-% years(anos)) %>%
        mutate(valor = 100 * cumprod(1 + benchmark_ibov) / first(cumprod(1 + benchmark_ibov)),
                carteira = "Benchmark") %>%
        select(date, valor, carteira)
    
    bind_rows(risk, mixed, benchmark)
}

#Function to change métrics in table
preparar_tabela_metricas <- function(janela) {
    map_df(c("risk","mixed","benchmark"), function(tipo) {
        if (tipo == "benchmark") {
            m <- metricas[[janela]][["risk"]]$benchmark
            tibble(
                carteira = "Benchmark",
                annualized = m$annualized,
                drawdown = m$drawdown,
                sharpe = m$sharpe,
                sortino = m$sortino,
                alpha = NA,
                beta = NA,
                tracking_error = NA
            )
        }   else {
            m <- metricas[[janela]][[tipo]]
            tibble(
                carteira = tipo,
                annualized = m$carteira$annualized,
                drawdown = m$carteira$drawdown,
                sharpe = m$carteira$sharpe,
                sortino = m$carteira$sortino,
                alpha = m$carteira$alpha,
                beta = m$carteira$beta,
                tracking_error = m$carteira$tracking_error
            )
        }
    })
}

#Function to generate graphs and table
plotar_janela <- function(janela) {
    dados_plot <- preparar_dados_plot(janela)
    tabela <- preparar_tabela_metricas(janela)

    #graphic
    g <- ggplot(dados_plot, aes(x = date, y = valor, color = carteira)) +
        geom_line(size = 1) +
        labs(title = paste(janela, "Evolution"),
            x = "Data", y = "Valor da carteira") +
        theme_minimal()

    t <- tableGrob(tabela, rows = NULL)


    grid.arrange(g, t, nrow = 2, heights = c(3, 1))
    print(g)
    print(kable(tabela, caption = paste("Métricas -", janela)))
}

plotar_janela("10y")
plotar_janela("5y")
plotar_janela("3y")
