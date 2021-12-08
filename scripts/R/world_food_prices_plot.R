#Plot World Food Prices from FAO Data FAO Food Price Index

#Required libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)

# Original data source: FAO 
# Direct link data used here: https://www.fao.org/fileadmin/templates/worldfood/Reports_and_docs/Food_price_indices_data_nov815.csv
# Update on latest data: https://www.fao.org/worldfoodsituation/foodpricesindex/en/

# Read CSV FAO data Food Price Index
wfpi <- read.csv(file = "slc-hunger-risk/data/processed/Food_price_indices_data_nov815.csv",
                sep = ";",
                stringsAsFactors = F)

#WFPI Reference year: 2014-2016=100

#Colnames formatting and deleting non-data rows
colnames(wfpi) <- wfpi[2,]
wfpi <- wfpi[-c(1:3),]

#Create Date for easy plotting
wfpi$Date <- as.Date(paste(wfpi$Date, "01", sep = "-"),
                    format = "%Y-%m-%d")

#Filter data from 2010 onwards
wfpi <- wfpi[wfpi$Date > as.Date("2009-12-31"), ]
colnames(wfpi)[2] <- "FPI"

#To long format
wfpi <- gather(wfpi, "Indicator", "Value", "FPI":"Sugar")
wfpi$Value <- as.numeric(wfpi$Value)

#Plot, only indicator "FPI" - the general food price index
plot <- wfpi %>% filter(Indicator == "FPI") %>%
  ggplot(aes(x = Date, y = Value)) +
  geom_line(color = "steelblue") +
  geom_point(color = "steelblue") +
  scale_x_date(date_labels = "%Y",
               date_breaks = "1 year",
               limits = c(as.Date("2010-01-01"), as.Date("2021-12-31"))) +
  labs(x = "Year", 
       y = "FPI (2014-2016 = 100)",
       title = "FPI - World Food Price Index 2010-2021",
       subtitle = "Source: FAO. 2014-2016=100") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
plot


