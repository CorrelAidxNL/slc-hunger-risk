#Plot Employment in Agriculture from ILO modelled Estimates

#Required libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)


# Original data source: ILO 
# Indicator selected:
# Employment by sex and economic activity -- ILO modelled estimates, Nov. 2020 (thousands)
# Direct link: https://www.ilo.org/shinyapps/bulkexplorer16/?lang=en&segment=ref_area&id=SUR_A&indicator=EMP_2EMP_SEX_ECO_NB&sex=SEX_T+SEX_M+SEX_F&classif1=ECO_SECTOR_TOTAL+ECO_SECTOR_AGR+ECO_SECTOR_IND+ECO_SECTOR_SER+ECO_AGGREGATE_TOTAL+ECO_AGGREGATE_AGR+ECO_AGGREGATE_MAN+ECO_AGGREGATE_CON+ECO_AGGREGATE_MEL+ECO_AGGREGATE_MKT+ECO_AGGREGATE_PUB+ECO_DETAILS_TOTAL+ECO_DETAILS_A+ECO_DETAILS_B+ECO_DETAILS_C+ECO_DETAILS_DE+ECO_DETAILS_F+ECO_DETAILS_G+ECO_DETAILS_HJ+ECO_DETAILS_I+ECO_DETAILS_K+ECO_DETAILS_LMN+ECO_DETAILS_O+ECO_DETAILS_P+ECO_DETAILS_Q+ECO_DETAILS_RSTU&timefrom=2010&timeto=2019

# Read CSV ILO data employment in agriculture
ilo <- read.csv(file = "slc-hunger-risk/data/processed/ILO_data_sector_empl.csv",
         sep = ";",
         stringsAsFactors = F)

#Select all sexes
ilo <- ilo %>% filter(sex.label == "Sex: Total")

#Find row indices of agriculture and total sector
total.idx <- which(ilo$classif1.label == "Economic activity (Broad sector): Total")
agr.idx <- which(ilo$classif1.label == "Economic activity (Broad sector): Agriculture")

#create wide-data format dfs with counts of people working total and in agriculture
ilo_wide <- ilo[total.idx, c("time", "obs_value")]
colnames(ilo_wide)[2] <- "total"
ilo_wide2 <- ilo[agr.idx, c("time", "obs_value")]
colnames(ilo_wide2)[2] <- "agriculture"
ilo_wide <- merge(ilo_wide, ilo_wide2, by = "time")

#remove redundant vars and original data
rm(ilo_wide2, total.idx, agr.idx, ilo)

#Calculate percentage working in agriculture
ilo_wide$perc_agriculture <- ilo_wide$agriculture / ilo_wide$total
#Add year as date for easy plotting
ilo_wide$year <- as.Date(paste(ilo_wide$time, "01", "01", sep = "-"))

#plot
plot <- ilo_wide %>% 
  ggplot(aes(x = year, y = perc_agriculture*100)) +
  geom_line(color = "darkred") +
  geom_point(color = "darkred") +
  scale_x_date(date_labels = "%Y",
               date_breaks = "1 year",
               limits = c(as.Date("2010-01-01"), as.Date("2019-01-02"))) +
  labs(x = "Year", 
       y = "% employment in agriculture",
       title = "Share of Employment in Agriculture",
       subtitle = "Source: ILO - ILO Modelled Estimates, Nov. 2020") +
  ylim(0, 15)

plot
