library(xts)
library(TTR)
library(magrittr)
library(dplyr)
library(readr)
library(data.table)
library(AlphaVantageClient)

setAPIKey("RG5RUC1X8147FK1D")
example_prices <- fetchSeries(function_nm = "time_series_daily", symbol = "msft")
example_sma <- fetchSeries(function_nm = "sma", symbol = "msft", interval = "daily",
                           time_period = 10, series_type = "open")

example_sma

update.packages()

devtools::install_github("jbkunst/highcharter")
#Reading in the data
input.raw <- read_csv("input.csv", na = '', col_types = "cdd")

#Reformatting the date_value column to a date format
input.raw$date_value <- as.Date(input.raw$date_value, "%m/%d/%Y")

#make the raw data usable by geting rid of NAs
input.data <- input.raw[!is.na(input.raw$price_local),]

#The TTR packages work best with xts time series
price <- xts(input.data$price_local, order.by = input.data$date_value,)
volume <- xts(input.data$volume, order.by = input.data$date_value)

#############TTR Package Calculations & Assignment############

#Relative Strength
wb_RSI <- RSI(price, n = 14)

#Simple Moving Average n = 50
wb_SMA50 <- SMA(price, 50)

#Simple Moving Average n = 200
wb_SMA200 <- SMA(price, 200)

#Rate of Change
wb_ROC <- ROC(price, 25)

#Moving Average Convergence Divergence
wb_MACD <- MACD(price, nFast = 12, nSlow = 26, nSig = 9)

#On Balance Value
wb_OBV <- OBV(price = price, volume = volume)

#Bollinger Bands
bbSMA = BBands(price, sd = 2.0, n = 26, maType = SMA)

#Merging as a DataFrame
output.data <- data.frame(input.data, wb_RSI, wb_SMA50, wb_SMA200, wb_OBV, wb_ROC, wb_MACD, bbSMA)

setnames(output.data, old = c('EMA', 'wb_ROC', 'SMA', 'SMA.1', 'macd', 'obv'), new = c('RSI (14)', 'ROC', 'SMA (50)', 'SMA (200)', 'MACD', 'OBV'))

MACD1 <- xts(output.data$MACD, order.by = output.data$date_value)

RSI.SellLevel <- xts(rep(70, NROW(wb_RSI)), index(wb_RSI))
RSI.BuyLevel <- xts(rep(30, NROW(wb_RSI)), index(wb_RSI))

write.csv(output.data, file = "output_data.csv", row.names = FALSE)
write.table(output.data, file = "output_text.txt", row.names = FALSE)
