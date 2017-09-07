library(xts)
library(TTR)
require(httr)
library(rmarkdown)
library(testthat)
library(magrittr)
library(dplyr)
library(readr)
library(data.table)
require(AlphaVantageClient)



getAlphaData <- function(ticker) {
    setAPIKey("RG5RUC1X8147FK1D")

    time_series_daily_prices <- fetchSeries(function_nm = "time_series_daily", symbol = ticker, outputsize = "full", datatype = 'json')
    daily_sma <- fetchSeries(function_nm = "sma", symbol = "msft", interval = "daily",
                           time_period = 10, series_type = "open", datatype = 'json')

    #Reformatting to a date format
    stockprice <- time_series_daily_prices$xts_object
    sma1 <- daily_sma$xts_object


    #Stockprice becomes input.raw
    input.raw <- stockprice

    #make the raw data usable by geting rid of NAs
    #input.data <- input.raw[!is.na(input.raw$price_local),]

    #The TTR packages work best with xts time series
    price <- xts(input.raw$"4. close")
    volume <- xts(input.raw$"5. volume")

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
    output.data <- data.frame(input.raw, wb_RSI, wb_SMA50, wb_SMA200, wb_OBV, wb_ROC, wb_MACD, bbSMA)

    write.csv(output.data, file = "output_data.csv", row.names = FALSE)
    info <- output.data
    return(info)
}
getAlphaData("AMZN")
