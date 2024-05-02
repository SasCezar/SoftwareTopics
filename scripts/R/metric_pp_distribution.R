library(tidyverse)
library(ggplot2)
library(reshape2)
library(dplyr)
library(ggh4x)
library(paletteer)
library(forcats)
library(cowplot)
library(purrr)
library(stringr)

normalit<-function(m){
  m = as.numeric(m)
  (m - min(m))/(max(m)-min(m))
}

x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")

ds <- c('wikidata', 'cso', 'LLM')
dir <- '~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/' 
dir_plot <- '/home/sasce/PycharmProjects/SoftwareTopics/report/plots/' 

for(x in ds){
  df_og <- read.csv(paste(dir, x, '_processed/extra_melted_metrics.csv', sep = ""))
  df_corr <- read.csv(paste(dir, x, '_processed/metrics_correlation_postprocessing.csv', sep = ""))
  
  df_corr <- df_corr %>%
    mutate(across(where(is.numeric), round, 2)) %>%
    mutate(pp_name, pp_name=str_to_title(pp_name))
  
  df <- df_og %>%
    filter(Metric %in% x_vars) %>%
    filter(if_any(everything(), ~ !is.na(.))) %>%
    group_by(Metric) %>%
    mutate(Value = normalit(Value)) %>%
    mutate_at(c('Value'), as.numeric) %>%
    mutate(pp_name, pp_name=str_to_title(pp_name))
  
  df_mean = df_og %>%
    filter(Metric %in% x_vars) %>%
    filter(if_any(everything(), ~ !is.na(.))) %>%
    group_by(Metric, pp_name, is_pp) %>%
    mutate_at(c('Value'), as.numeric) %>%
    mutate(pp_name, pp_name=str_to_title(pp_name)) %>%
    summarize(Mean = mean(Value, na.rm=TRUE)) %>%
    mutate(across(where(is.numeric), round, 2)) 
  
  df <- select(df,-any_of(c('Take_All', 'Types_Threshold', 'Max_Depth', 'Sim_Threshold', 'LLM')))
  
  ggplot() +
    geom_boxplot(data=df, aes(y=Value, x=is_pp, fill=is_pp), alpha=0.4) + 
    geom_label(data=df_corr, aes(label=correlation), x=1.5, y=.9, size=2) +
    geom_label(data=df_mean, aes(x=is_pp, label=Mean, fill=is_pp), y=.1, size=1.5, alpha=.4) +
    facet_grid(pp_name ~ Metric, scales = "free") + 
    guides(fill="none") +
    labs(x='Postprocessing', y='Normalized Values')
  
  fname <- paste(dir_plot, x ,'_pp_dist_corr.pdf', sep = "")
  
  ggsave(fname,  width=9, height=4)
  
}

