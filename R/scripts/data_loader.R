# Install the packages
packages <- c("tidyquant", "dplyr", "lubridate", "readr", "PerformanceAnalytics", "tidyr")

installed <- packages %in% rownames(installed.packages())
if (any(!installed)) {
  install.packages(packages[!installed])
}

#Loading the packages
lapply(packages, library, character.only = TRUE)

#Analysis Period
start_10y <- as.Date(Sys.Date()) - years(10)
start_5y  <- as.Date(Sys.Date()) - years(5)
start_3y  <- as.Date(Sys.Date()) - years(3)
end_date <- as.Date("2024-12-30")

#Importing datas from Yahoo Finance for ETFs
get_etf_data <- function(ticker, start_date, end_date) {
	tq_get(ticker, from = start_date, to = end_date) %>%
		select(date, adjusted) %>%
		rename(!!ticker := adjusted)
}

#Importing ETF datas and IBOVESPA
bova11 <- get_etf_data("BOVA11.SA", start_10y, end_date)
ivvb11 <- get_etf_data("IVVB11.SA", start_10y, end_date)
xfix11 <- get_etf_data("XFIX11.SA", start_date = as.Date("2021-01-12"), end_date)
ibov <- get_etf_data("^BVSP", start_10y, end_date)

#Importing IFIX from .csv file
ifix_path <- "../data_sources/ifix_snapshot.csv"

#Importing IFIX
ifix <- read_csv(ifix_path) %>%
	rename(Data = 1) %>%
	mutate(date = dmy(Data)) %>%
	select(date, ifix_value = `Último`)

#Merging IFIX and XFIX11
ifix_extended <- ifix %>%
	rename(`XFIX11.SA` = ifix_value)

xfix11_extended <- bind_rows(
	filter(ifix_extended, date < as.Date("2021-01-12")),
	xfix11
)

#Adjusting XFIX scale
ifix_last <- ifix_extended %>% filter(date == as.Date("2021-01-11")) %>% pull (`XFIX11.SA`)
xfix11 <- xfix11 %>%
	mutate(`XFIX11.SA` = `XFIX11.SA` * (ifix_last / first(`XFIX11.SA`)))

#Recreating series
xfix11_extended <- bind_rows(
	ifix_extended %>% filter(date <= as.Date("2021-01-11")),
	xfix11 %>% filter(date >= as.Date("2021-01-12"))
)

#Importing SELIC rate
selic <- read_csv("../data_sources/selic_snapshot.csv") %>%
	mutate(date = dmy(data)) %>%
	select(date, selic_rate = SELIC)

#Changing for decimal
selic_returns <- selic %>%
	mutate(LFT.SIM = selic_rate / 100) 

#Filter all assets for 10 years
bova11 <- filter(bova11, date >= start_10y & date <= end_date)
ivvb11 <- filter(ivvb11, date >= start_10y & date <= end_date)
ibov <- filter(ibov, date >= start_10y & date <= end_date)
xfix11_extended <- filter(xfix11_extended, date >= start_10y & date <= end_date)
selic_returns <- filter(selic_returns, date >= start_10y & date <= end_date)

#Unit datas per date
merged_data <- bova11 %>%
	inner_join(ivvb11, by = "date") %>%
	inner_join(xfix11_extended, by = "date") %>%
	inner_join(ibov, by = "date") %>%
	inner_join(selic_returns, by = "date")

#Calculating Daily Returns
returns_data <- merged_data %>%
	arrange(date) %>%
	mutate(across(c(BOVA11.SA, IVVB11.SA, XFIX11.SA, `^BVSP`), ~ (./lag(.)) - 1)) %>%
	drop_na()

#Salving as .csv
write_csv(returns_data, "dashboard/full_returns.csv")
