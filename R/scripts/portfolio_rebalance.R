library(dplyr)
library(lubridate)
library(readr)

#Loading datas and weights
source("scripts/data_loader.R")
load("dashboard/portfolio_weights.RData")

#Defining Time
end_date <- max(returns_data$date)

ret_10y <- returns_data %>% filter(date >= end_date %m-% years(10))
ret_5y <- returns_data %>% filter(date >= end_date %m-% years(5))
ret_3y <- returns_data %>% filter(date >= end_date %m-% years(3))

#Tax with compensation function
calcular_imposto_com_compensacao <- function(lucro, prejuizo_acumulado, taxa = 0.15) {
    if (lucro > 0) {
        if (prejuizo_acumulado >= lucro) {
            return(list(imposto = 0, novo_prejuizo = prejuizo_acumulado - lucro))
        }   else {
            lucro_liquido <- lucro - prejuizo_acumulado
            imposto <- lucro_liquido * taxa
            return(list(imposto = imposto, novo_prejuizo = 0))
        }
    }   else {
        return(list(imposto = 0, novo_prejuizo = prejuizo_acumulado + abs(lucro)))
    }
}

#IR for LFT
calcular_ir_lft <- function(ganho, dias_corridos) {
    if (is.na(ganho) || ganho <= 0) return(0)
    if (dias_corridos <= 180) {
        taxa <- 0.225
    } else if (dias_corridos <= 360) {
        taxa <- 0.20
    } else if (dias_corridos <= 720) {
        taxa <- 0.175
    } else {
        taxa <- 0.15
    }
    return(ganho * taxa)
}


#Rebalancing with taxes
simulate_rebalanced_portfolio <- function(data, weights, rebalance_freq = "quarter", tax_rate = 0.15) {
    ativos <- names(weights)
    carteira <- rep(100 * weights, each = 1)
    prejuizo_acumulado <- 0
    valores <- numeric(nrow(data))
    valores[1] <- sum(carteira)

    ultima_data_rebalance <- data$date[1]

    for (i in 2:nrow(data)) {
        retornos <- as.numeric(data[i, ativos])
        carteira <- carteira * (1 + retornos)
        valores[i] <- sum(carteira)

        #Rebalancing
        if (month(data$date[i]) %% 3 == 0 && day(data$date[i]) == max(day(data$date))) {
            valor_total <- sum(carteira)
            valor_alvo <- valor_total * weights
            
            ativos_risco <- setdiff(ativos, "LFT.SIM")

            lucro_risco <- if (length(ativos_risco) > 0) {
                sum(pmax(carteira[ativos_risco] - valor_alvo[ativos_risco], 0))
            } else 0

            imposto_info <- calcular_imposto_com_compensacao(lucro_risco, prejuizo_acumulado, tax_rate)
            imposto_risco <- imposto_info$imposto 
            prejuizo_acumulado <- imposto_info$novo_prejuizo

            #Taxes on LFT
            imposto_lft <- 0
            if ("LFT.SIM" %in% ativos) {
                dias_corridos <- as.numeric(data$date[i] - ultima_data_rebalance)
                ganho_lft <- max(carteira["LFT.SIM"] - valor_alvo["LFT.SIM"], 0, na.rm = TRUE)
                imposto_lft <- calcular_ir_lft(ganho_lft, dias_corridos)
            }
            

            ultima_data_rebalance <- data$date[i]

            valor_liquido <- valor_total - imposto_risco - imposto_lft
            carteira <- valor_liquido * weights
        }
    }

    return(data.frame(date = data$date, valor = valores))
}

#Simulation windowns
rebalance_10y_risk <- simulate_rebalanced_portfolio(ret_10y, weights_risk)
rebalance_10y_mixed <- simulate_rebalanced_portfolio(ret_10y, weights_mixed)

rebalance_5y_risk    <- simulate_rebalanced_portfolio(ret_5y, weights_risk)
rebalance_5y_mixed   <- simulate_rebalanced_portfolio(ret_5y, weights_mixed)

rebalance_3y_risk    <- simulate_rebalanced_portfolio(ret_3y, weights_risk)
rebalance_3y_mixed   <- simulate_rebalanced_portfolio(ret_3y, weights_mixed)

#Exporting results
write_csv(rebalance_10y_risk, "dashboard/rebalance_10y_risk.csv")
write_csv(rebalance_10y_mixed, "dashboard/rebalance_10y_mixed.csv")
write_csv(rebalance_5y_risk, "dashboard/rebalance_5y_risk.csv")
write_csv(rebalance_5y_mixed, "dashboard/rebalance_5y_mixed.csv")
write_csv(rebalance_3y_risk, "dashboard/rebalance_3y_risk.csv")
write_csv(rebalance_3y_mixed, "dashboard/rebalance_3y_mixed.csv")
