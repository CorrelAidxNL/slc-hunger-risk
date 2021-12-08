#Plot Transport Price Index Suriname from Bureau of Statistics Data

#Required libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)

# Original data source two pdfs: Price Indices September 2021 & January 2020
# https://statistics-suriname.org/wp-content/uploads/2020/02/WEP-CPI-0120.pdf
# https://statistics-suriname.org/wp-content/uploads/2021/10/CPI-0921.pdf
# Converted to CSV

# Load CSV data retrieved from CPI pdfs of Statistics bureau suriname (ABS)
tpi <- read.csv(file = "slc-hunger-risk/data/processed/ABS_Sur_TransportPriceIndex_data.csv",
                  sep = ",",
                  stringsAsFactors = F)

#Create Date format for easy plotting of time
tpi$Time_Period <- str_c(tpi$Year, tpi$Month, "01", sep = "-")
tpi$Time_Period2 <- as.Date(tpi$Time_Period, format = "%Y-%m-%d")

colnames(tpi)[2] <- "Indicator"

#Change Indicator name to shorten
tpi$Indicator[tpi$Indicator == "PriceIndexTotal"] <- "Total"
tpi$Indicator[tpi$Indicator == "PriceIndexTransport"] <- "Transport"

#Plot
plot <- ggplot(tpi, aes(x = Time_Period2, y = Value)) + 
  geom_line(aes(color = Indicator)) + 
  geom_point(aes(color = Indicator)) +
  scale_color_manual(values = c("darkred", "steelblue")) +
  scale_x_date(date_labels = "%Y %m",
               date_breaks = "3 months",
               limits = c(as.Date("2018-01-01"), as.Date("2022-01-01"))) +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  labs(x = NULL, 
       y = "Consumer Price Index",
       title ="Transport Price Index 2018-2021",
       subtitle = "Source: General Bureau of Statistics Suriname")
plot
