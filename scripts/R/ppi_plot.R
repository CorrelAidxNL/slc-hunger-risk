#Plot Producer Price Index Suriname from FAO data

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

#Select from FAO Bulk data: Producer price index == Element 'Producer Price Index (2014-2016 = 100)'
fao_ppi <- fao %>% filter(Element == "Producer Price Index (2014-2016 = 100)")

#Select common goods
common <- c("Bananas", "Oranges", "Sugar cane", "Rice, paddy")
fao_ppi <- fao_ppi[fao_ppi$Item %in% common, ]

#Select data from 2010 onwards
fao_ppi <- fao_ppi[fao_ppi$Year.Code > 2009, ]

#Factorize Items and change date to year-format for plotting
fao_ppi$Item <- as.factor(fao_ppi$Item)
fao_ppi$Year.Date <- as.Date(paste(fao_ppi$Year.Code, "01", "01", sep = "-"))

#Plot producer price index
plot <- ggplot(fao_ppi, aes(x = Year.Date, y = Value)) +
  geom_line(aes(color = Item)) + 
  geom_point(aes(color = Item), size = 0.5) +
  scale_color_manual(values = c("green", "orange", "dark gray", "brown")) +
  scale_x_date(date_labels = "%Y",
               date_breaks = "1 year",
               limits = c(as.Date("2010-01-01"), as.Date("2019-01-02"))) +
  labs(x = "Year", 
       y = "Producer Price Index",
       title ="Producer Price Index common products 2000-2019",
       subtitle = "Source: FAO. (2014-2016 = 100)") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
plot


