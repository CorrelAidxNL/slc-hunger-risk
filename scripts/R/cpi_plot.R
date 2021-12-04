#Plot Consumer Price Index Suriname from FAO data

#Required libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)

#Load FAO Bulk Data
fao <- read.csv(file = "slc-hunger-risk/data/processed/fao-data-Suriname.csv",
                sep = ",",
                stringsAsFactors = F)

#Make sure value is numeric
fao$Value <- as.numeric(fao$Value)
#Create date-format column for easy plotting
fao$Year.Date <- as.Date(paste(fao$Year.Code, (fao$Months.Code-7000), 01, sep = "-"))

#Select from FAO Bulk data: Consumer Prices, General Indices (2015 = 100)	== Item.Code 23012
fao_cpi <- fao %>% filter(Item.Code == 23012)

#Plot CPI
plot <- ggplot(fao_cpi, aes(x = Year.Date, y = Value)) + 
  geom_line(color = "darkred") + 
  geom_point(color = "darkred", size = 0.5) +
  labs(x = "Year", 
       y = "Consumer Price Index",
       title ="Consumer Price Index General 2000-2021",
       subtitle = "Source: FAO. 2015 == 100")
plot

