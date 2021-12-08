#Plot Exchange Rates from Central Bank of Suriname data

#Required libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)


# Original data source: Exchange Rates Bank of Suriname 
# www.cbvs.sr --> National Summary Data Page
# Direct link: https://financien.sr/wp-content/uploads/xml/2020/Suriname_EXR_monthly.xml

#### Conversion from XML to CSV below commented out ####
# library(XML)
# 
# #Read XML
# exr <- xmlParse(file = "Suriname_EXR_monthly_xml.xml")
# exr <- xmlToList(exr)
# 
# #Data is in DataSet -> Series list
# exr$DataSet$Series %>% length()
# 
# #The last item of the list is the attributes. 
# attr <- exr$DataSet$Series$.attrs
# exr$DataSet$Series$.attrs <- NULL
# 
# #Each list item contains a time period and value
# #convert these to df
# series <- exr$DataSet$Series
# exr_df <- as.data.frame(matrix(nrow = length(series), ncol = 2))
# 
# for (i in 1:length(series)) {
#   exr_df[i, ] <- unlist(series[[i]])
# }
# rm(i)
# colnames(exr_df) <- c("Time_Period", "EXR_SDR_USD")
# 
# #We can remove everything but the DF
# rm(exr, series, attr)
# 
# # Store as csv
# write.csv(exr_df, file = "CBVS_exchange_rates.csv", row.names = FALSE)


# Load CSV exchange rates data from CBVS
exr <- read.csv(file = "slc-hunger-risk/data/processed/CBVS_exchange_rates.csv",
                sep = ";",
                stringsAsFactors = F)

#Convert formats
exr$EXR_SDR_USD <- as.numeric(exr$EXR_SDR_USD)
exr$Time_Period2 <- paste0(exr$Time_Period, "-01")
exr$Time_Period2 <- as.Date(exr$Time_Period2, format = "%Y-%m-%d")

#Remove anything before 2010
exr <- exr[exr$Time_Period2 > as.Date("2009-12-31"), ]

#Plot
plot <- ggplot(exr, aes(Time_Period2, EXR_SDR_USD)) +
  geom_line(color = "darkred") +
  geom_point(color = "darkred", size = 0.5) +
  scale_x_date(date_labels = "%Y %m",
               date_breaks = "6 months",
               limits = c(as.Date("2010-01-01"), as.Date("2021-11-22"))) +
  labs(x = NULL, 
       y = "Exchange Rate SRD/USD",
       title ="Exchange Rate SRD/USD 2010-2021",
       subtitle = "Source: Centrale Bank van Suriname/IMF") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
plot
