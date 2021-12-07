#Plot Food Inflation Suriname from FAO data

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

#Select from FAO Bulk data: Food price inflation == Item.Code 23014
fao_infl <- fao %>% filter(Item.Code == 23014)

#plot food inflation
plot <- ggplot(fao_infl, aes(x = Year.Date, y = Value)) + 
  geom_line(color = "darkgreen") + 
  geom_point(color = "darkgreen") +
  labs(x = "Year", 
       y = "Food price inflation (%)",
       title ="Food Price Inflation 2000-2021",
       subtitle = "Source: FAO.")
plot
