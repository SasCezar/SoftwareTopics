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

df <- read.csv('/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/wikidata_processed/metrics_correlation_postprocessing.csv')

x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")
remove <- c("Max Children", "\\# Parents", "\\# Children", "Is DAG", 'Types Threshold', "Take All", 'Max Depth', "LLM", 'Sim Threshold', "Max Parents")

df <- df %>%
  filter(!X %in% remove)%>%
  filter(!Y %in% remove)%>%
  filter(X %in% x_vars) %>%
  filter(!Y %in% x_vars) %>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(Y = fct_relevel(Y, 'Minimization', 'Abstract', 'Bridge', 'Cycle')) %>%
  mutate(X = gsub(r"(\\)", "", X))



ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2)))+ 
  scale_fill_distiller(palette = "Spectral", direction=-1) +
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20),
        legend.position="none")  +
  guides(x =  guide_axis(angle = 45)) 

ggsave('/home/sasce/Downloads/SoftwareTopics/report/plots/wiki_pp_correlation_heatmap.pdf', width=9, height=4)


df <- read.csv('/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/cso_processed/metrics_correlation_postprocessing.csv')

x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", 'Pairs Acc')
remove <- c("Max Children", "\\# Parents", "\\# Children", "Is DAG", 'Types Threshold', "Take All", 'Max Depth', "LLM", 'Sim Threshold', "Max Parents")

df <- df %>%
  filter(!X %in% remove)%>%
  filter(!Y %in% remove)%>%
  filter(X %in% x_vars) %>%
  filter(!Y %in% x_vars) %>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(Y = fct_relevel(Y, 'Minimization', 'Abstract', 'Bridge', 'Cycle')) %>%
  mutate(X = gsub(r"(\\)", "", X))

ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2))) +
  scale_fill_distiller(palette = "Spectral", direction=-1) +
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20), 
        legend.position="none") +
  guides(x =  guide_axis(angle = 45)) 
  #rotate_x_text(angle = -90, align = 0, valign = 0.25)
  #scale_x_discrete(guide = guide_axis(n.dodge = 2))



ggsave('/home/sasce/Downloads/SoftwareTopics/report/plots/cso_pp_correlation_heatmap.pdf', width=9, height=4)
