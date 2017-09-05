require(reshape2)
suppressPackageStartupMessages(
    require(googleVis)
    )
library(xts)
library(TTR)
library(magrittr)
library(dplyr)
library(readr)
library(testthat)
library(data.table)
library(ggplot2)
library(rCharts)
library(highcharter)
library(tidyr)
library(magrittr)
library(highcharter)
library(quantmod)
library(stringr)
library(purrr)
library(devtools)

require(crosstalk)
devtools::install_github("jbkunst/highcharter")

source("https://install-github.me/jbkunst/highcharter")

install.packages("highcharter")
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

################################### CHART CREATION #####################################
colors <- c("#d35400", "#2980b9", "#2ecc71", "#f1c40f", "#2c3e50", "#7f8c8d")
colors2 <- c("#000004", "#3B0F70", "#8C2981", "#DE4968", "#FE9F6D", "#FCFDBF")

hc <- highchart(type = "stock") %>%
  hc_title(text = "Momentum Indicators") %>%
  hc_add_theme(hc_theme_darkunica()) %>%
  hc_add_series_xts(price, name = "PRICE", color = hex_to_rgba("white", 1)) %>%
  hc_rangeSelector(inputEnabled = FALSE) %>%
  hc_scrollbar(enabled = FALSE) %>%
  hc_yAxis_multiples(create_yaxis(naxis = 3, heights = c(3, 1, 1), title = list(text = "Price (Local Cur.)"))) %>%
  hc_add_series_xts(wb_SMA50, name = "SMA50", yAxis = 0, color = hex_to_rgba("purple", 0.6)) %>%
  hc_add_series_xts(wb_SMA200, name = "SMA200", yAxis = 0, color = hex_to_rgba("pink", 0.6)) %>%
  hc_add_series_xts(wb_RSI, name = "RSI", yAxis = 1, color = hex_to_rgba("white", 1)) %>%
  hc_add_series_xts(RSI.SellLevel, color = hex_to_rgba("red", 0.4),
                yAxis = 1, name = "Sell level") %>%
  hc_add_series_xts(RSI.BuyLevel, color = hex_to_rgba("green", 0.4),
                yAxis = 1, name = "Buy level") %>%
  hc_add_series_xts(wb_OBV, name = "OBV", yAxis = 2) %>%
  hc_xAxis(
      list(
      title = list(text = "Time"))) %>%
  mutate(color = rep(colors, length.out = 5),
      segmentColor = rep(colors2)
hc #This is the object to pass as JSON.
#########################################################################################

?? colorize_vector
cols <- viridis(3)
cols <- substr(cols, 0, 7)

highcharts_demo() %>%
  colorize(3, colors = c("440154","#21908C","#FDE725"))
?? coloredline


series:[{
    type:'coloredline',
            data:[{
        y:200,
                    segmentColor:'red'
    }, {
        y:210,
                    segmentColor:'red'
    }, {
        y:210,
                    segmentColor:'red'
    }, {
        y:100,
                    segmentColor:'green'
    }, {
        y:100,
                    segmentColor:'red'
    }]
}]






nyears <- 5

df <- expand.grid(seq(12) - 1, seq(nyears) - 1)
df$value <- abs(seq(nrow(df)) + 10 * rnorm(nrow(df))) + 10
df$value <- round(df$value, 2)
ds <- list_parse2(df)


ha <- highchart() %>%
  hc_chart(type = "heatmap") %>%
  hc_title(text = "Simulated values by years and months") %>%
  hc_xAxis(categories = month.abb) %>%
  hc_yAxis(categories = 2016 - nyears + seq(nyears)) %>%
  hc_add_series(name = "value", data = ds)

hc_colorAxis(ha, minColor = "#FFFFFF", maxColor = "#434348")

hc_colorAxis(ha, minColor = "#FFFFFF", maxColor = "#434348",
             type = "logarithmic")


require("viridisLite")

n <- 4
stops <- data.frame(q = 0:n / n,
                    c = substring(viridis(n + 1), 0, 7),
                    stringsAsFactors = FALSE)
stops <- list_parse2(stops)

hc_colorAxis(ha, stops = stops, max = 75)
