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

#TICKER ACCEPTS VALID STOCK TICKERS (AMZN, AAPL, etc)
getAlphaData <- function(ticker) {
    x <- TRUE
    setAPIKey("RG5RUC1X8147FK1D")

    time_series_daily_prices <- fetchSeries(function_nm = "time_series_daily", symbol = ticker, outputsize = "full", datatype = 'json')
    time_series_intraday_prices <- fetchSeries(function_nm = "time_series_intraday", symbol = ticker, outputsize = "full", datatype = 'json', interval = '15min')
    time_series_daily_adjusted <- fetchSeries(function_nm = "time_series_daily_adjusted", symbol = ticker, outputsize = "full", datatype = 'json')
    time_series_weekly <- fetchSeries(function_nm = "time_series_weekly", symbol = ticker, outputsize = "full", datatype = 'json')
    time_series_monthly <- fetchSeries(function_nm = "time_series_monthly", symbol = ticker, outputsize = "full", datatype = 'json')

    #Technical Indicators
    daily_sma <- fetchSeries(function_nm = "sma", symbol = ticker, interval = "daily", time_period = 60, series_type = "close")

    weekly_sma <- fetchSeries(function_nm = "sma", symbol = ticker, interval = "weekly",
                            time_period = 50, series_type = "close", datatype = 'json')

    monthly_sma <- fetchSeries(function_nm = "sma", symbol = ticker, interval = "monthly",
                             time_period = 15, series_type = "close", datatype = 'json')


    #Reformatting to a date format
    time_series_daily_prices <- time_series_daily_prices$xts_object
    time_series_intraday_prices <- time_series_intraday_prices$xts_object
    time_series_daily_adjusted <- time_series_daily_adjusted$xts_object
    time_series_weekly <- time_series_weekly$xts_object
    time_series_monthly <- time_series_monthly$xts_object

    daily_sma <- daily_sma$xts_object
    weekly_sma <- weekly_sma$xts_object
    monthly_sma <- monthly_sma$xts_object

    #HERE IS WHERE I WILL COMPARE THE DATA AGAINST ITSELF TO GENERATE A TREND JUDGEMENT

    #Merging as a DataFrame
    #output.data <- data.frame()

    if (x) {
        return("buy")
    } else {
        return("sell")
    }
}
getAlphaData("AMZN")