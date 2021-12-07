#Plot Food Price Index Suriname from FAO data

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

#Select from FAO Bulk data: Consumer Prices, Food Indices (2015 = 100) == Item.Code 23013
fao_fpi <- fao %>% filter(Item.Code == 23013)

#Plot fpi
plot <- ggplot(fao_fpi, aes(x = Year.Date, y = Value)) + 
  geom_line(color = "steelblue") + 
  geom_point(color = "steelblue", size = 0.5) +
  labs(x = "Year", 
       y = "Consumer Price Index",
       title ="Consumer Price Index Food 2000-2021",
       subtitle = "Source: FAO. 2015 == 100")
plot