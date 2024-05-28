library(tidyverse)
library(ggplot2)
library(reshape2)
library(dplyr)
library(ggh4x)
library(paletteer)
library(forcats)
library(cowplot)
library(purrr)

df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/cso_processed/melted_metrics.csv')


target <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc", '\\# New Terms')

df <- df %>% 
  filter(Metric %in% target) %>%
  mutate_at(c('Sim_Threshold', 'Value'), as.numeric)%>%
  mutate(LLM = replace(LLM, LLM == 'all-mpnet-base-v2', 'MP')) %>%
  mutate(LLM = replace(LLM, LLM == 'all-MiniLM-L6-v2', 'L6')) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate(processing = fct_relevel(processing, 
                                  '0, 0, 0, 0', 
                                  '1, 0, 0, 0', 
                                  '0, 1, 0, 0',
                                  '0, 0, 1, 0',
                                  '0, 0, 0, 1',
                                  '0, 1, 1, 0',
                                  '1, 1, 0, 0',
                                  '1, 0, 1, 0',
                                  '1, 0, 0, 1',
                                  '1, 1, 0, 1',
                                  '1, 0, 1, 1',
                                  '1, 1, 1, 1'))


# ggplot(df, aes(x = Sim_Threshold, y = Value, colour=Metric)) + 
#   geom_point() +
#   facet_nested(LLM ~cycle + bridge + abstract + minimization, scales = "free_y")

df %>%
  group_split(Metric) %>% 
  map(
    ~ggplot(., aes(LLM, Sim_Threshold, fill = Value)) + 
      geom_tile() +
      scale_fill_gradient2(
        low = "#3366CC",
        mid = "white",
        high = "#FF3300",
        midpoint = min(.$Value) + ((max(.$Value) - min(.$Value))/2)
      ) +
      facet_nested(~ Metric + processing)
  ) %>% 
  plot_grid(plotlist = ., align = 'hv', ncol=1)


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/cso_metrics_heatmap.pdf', width=9, height=14)



df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/wikidata_processed/melted_metrics.csv')

df$Types_Threshold <- as.factor(df$Types_Threshold)
df$Max_Depth <- as.factor(df$Max_Depth)

df <- df %>% 
  filter(Metric %in% target) %>%
  mutate_at(c('Value'), as.numeric) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc", '\\# New Terms', "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate(processing = fct_relevel(processing, 
                                  '0, 0, 0, 0', 
                                  '1, 0, 0, 0', 
                                  '0, 1, 0, 0',
                                  '0, 0, 1, 0',
                                  '0, 0, 0, 1',
                                  '0, 1, 1, 0',
                                  '1, 1, 0, 0',
                                  '1, 0, 1, 0',
                                  '1, 0, 0, 1',
                                  '1, 1, 0, 1',
                                  '1, 0, 1, 1',
                                  '1, 1, 1, 1'))

df %>%
  group_split(Metric) %>% 
  map(
    ~ggplot(., aes(Types_Threshold, Max_Depth, fill = Value)) + 
      geom_tile() +
      scale_fill_gradient2(
        low = "#3366CC",
        mid = "white",
        high = "#FF3300",
        midpoint = min(.$Value) + ((max(.$Value) - min(.$Value))/2)
      ) +
      facet_nested(~ Metric + processing)
  ) %>% 
  plot_grid(plotlist = ., align = 'hv', ncol=1)


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/wiki_metrics_heatmap.pdf', width=9, height=14)



df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_processed/melted_metrics.csv')


df <- df %>% 
  filter(Metric %in% target) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc", '\\# New Terms', "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate_at(c('Value'), as.numeric) %>%
  mutate(processing = fct_relevel(processing, 
                                  '0, 0, 0, 0', 
                                  '1, 0, 0, 0', 
                                  '0, 1, 0, 0',
                                  '0, 0, 1, 0',
                                  '0, 0, 0, 1',
                                  '0, 1, 1, 0',
                                  '1, 1, 0, 0',
                                  '1, 0, 1, 0',
                                  '1, 0, 0, 1',
                                  '1, 1, 0, 1',
                                  '1, 0, 1, 1',
                                  '1, 1, 1, 1'))

df %>%
  group_split(Metric) %>% 
  map(
    ~ggplot(., aes(LLM, prompt_type, fill = Value)) + 
      geom_tile() +
      scale_fill_gradient2(
        low = "#3366CC",
        mid = "white",
        high = "#FF3300",
        midpoint = min(.$Value) + ((max(.$Value) - min(.$Value))/2)
      ) +
      facet_nested(~ Metric + processing)
  ) %>% 
  plot_grid(plotlist = ., align = 'hv', ncol=1)


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/llm_metrics_heatmap.pdf', width=9, height=14)


df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_Iter_processed/melted_metrics.csv')


df <- df %>% 
  filter(Metric %in% target) %>%
  unite("processing", cycle:bridge:abstract:minimization, remove = FALSE, sep=', ') %>%
  mutate(Metric = fct_relevel(Metric, "\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc", '\\# New Terms', "Missing")) %>%
  mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
  mutate_at(c('Value'), as.numeric) %>%
  mutate(processing = fct_relevel(processing, 
                                  '0, 0, 0, 0', 
                                  '1, 0, 0, 0', 
                                  '0, 1, 0, 0',
                                  '0, 0, 1, 0',
                                  '0, 0, 0, 1',
                                  '0, 1, 1, 0',
                                  '1, 1, 0, 0',
                                  '1, 0, 1, 0',
                                  '1, 0, 0, 1',
                                  '1, 1, 0, 1',
                                  '1, 0, 1, 1',
                                  '1, 1, 1, 1'))

df %>%
  group_split(Metric) %>% 
  map(
    ~ggplot(., aes(LLM, prompt_type, fill = Value)) + 
      geom_tile() +
      scale_fill_gradient2(
        low = "#3366CC",
        mid = "white",
        high = "#FF3300",
        midpoint = min(.$Value) + ((max(.$Value) - min(.$Value))/2)
      ) +
      facet_nested(~ Metric + processing)
  ) %>% 
  plot_grid(plotlist = ., align = 'hv', ncol=1)


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/llm_iter_metrics_heatmap.pdf', width=9, height=14)


