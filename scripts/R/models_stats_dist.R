library(tidyverse)
library(ggplot2)
library(reshape2)
library(dplyr)
library(ggh4x)
library(paletteer)
library(forcats)
library(cowplot)
library(purrr)

df_cso <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/cso_processed/melted_metrics.csv')


target <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", 'Pairs Acc', 'Missing')

df_cso <- df_cso %>% 
  filter(Metric %in% target) %>%
  mutate_at(c('Sim_Threshold', 'Value'), as.numeric)%>%
  mutate(LLM = replace(LLM, LLM == 'all-mpnet-base-v2', 'MP')) %>%
  mutate(LLM = replace(LLM, LLM == 'all-MiniLM-L6-v2', 'L6')) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  filter(processing %in% c('0, 0, 0, 0')) %>%
  select(-c('processing', 'cycle', 'bridge', 'abstract', 'minimization')) %>%
  distinct()

df_cso$src <- 'CSO'


df_wiki <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/wikidata_processed/melted_metrics.csv')

df_wiki$Types_Threshold <- as.factor(df_wiki$Types_Threshold)
df_wiki$Max_Depth <- as.factor(df_wiki$Max_Depth)

df_wiki <- df_wiki %>% 
  filter(Metric %in% target) %>%
  mutate_at(c('Value'), as.numeric) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  filter(processing %in% c('0, 0, 0, 0')) %>%
  select(-c('processing', 'cycle', 'bridge', 'abstract', 'minimization')) %>%
  distinct()

df_wiki$src <- 'Wiki'


df_llm <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_processed/melted_metrics.csv')


df_llm <- df_llm %>% 
  filter(Metric %in% target) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate_at(c('Value'), as.numeric) %>%
  filter(processing %in% c('0, 0, 0, 0')) %>%
  select(-c('processing', 'cycle', 'bridge', 'abstract', 'minimization')) %>%
  distinct()

df_llm$src <- 'LLM'

df_llm_iter <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_Iter_processed/melted_metrics.csv')


df_llm_iter <- df_llm_iter %>% 
  filter(Metric %in% target) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate_at(c('Value'), as.numeric) %>%
  filter(processing %in% c('0, 0, 0, 0')) %>%
  select(-c('processing', 'cycle', 'bridge', 'abstract', 'minimization')) %>%
  distinct()

df_llm_iter$src <- 'LLM_Iter'

df_cso <- select(df_cso,-any_of(c('Take_All', 'Types_Threshold', 'Max_Depth', 'Sim_Threshold', 'LLM', 'prompt_type')))
df_wiki <- select(df_wiki,-any_of(c('Take_All', 'Types_Threshold', 'Max_Depth', 'Sim_Threshold', 'LLM', 'prompt_type')))
df_llm <- select(df_llm,-any_of(c('Take_All', 'Types_Threshold', 'Max_Depth', 'Sim_Threshold', 'LLM', 'prompt_type')))
df_llm_iter <- select(df_llm_iter,-any_of(c('Take_All', 'Types_Threshold', 'Max_Depth', 'Sim_Threshold', 'LLM', 'prompt_type')))

df <-  rbind(df_cso, df_wiki)
df <- rbind(df, df_llm)
df <- rbind(df, df_llm_iter)

df <- df %>%
  mutate(src = fct_relevel(src, 'CSO', 'Wiki', 'LLM', 'LLM_Iter'))

df_corr <- read.csv(paste(dir, x, '_processed/metrics_correlation.csv', sep = ""))
  
df_corr <- df_corr %>%
    rename(
      Metric = X,
      Hyper = Y     
      ) %>%
    filter(Metric %in% x_vars) %>%
    filter(! Hyper %in% x_vars) %>%
    mutate(across(where(is.numeric), round, 2))

df_mean = df %>%
    group_by(Metric, src) %>%
    summarize(Mean = mean(Value, na.rm=TRUE)) %>%
    mutate(across(where(is.numeric), round, 2)) 

ggplot() +
    geom_boxplot(data=df, aes(y=Value, x=src, fill=src), alpha=0.4, outliers = FALSE) + 
    facet_wrap(~Metric, scale="free") +
    guides(fill="none") +
    labs(x=element_blank(), y='Values')
  

ggsave('~/PycharmProjects/SoftwareTopics/report/plots/models_metrics_distr.pdf', width=9, height=4)


