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

df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/wikidata_processed/metrics_correlation.csv')

x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")
hyper <- c("Take All", 'Max Depth', "LLM", 'Sim Threshold', 'Types Threshold')

df <- df %>%
  filter(!X %in% hyper)%>%
  filter(Y %in% hyper)%>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(X = gsub(r"(\\)", "", X))


ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2)), size=4, colour = "white")+ 
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20),
        legend.position="none")  +
  guides(x =  guide_axis(angle = 45)) 

ggsave('~/PycharmProjects/SoftwareTopics/report/plots/wiki_hyper_correlation_heatmap.pdf', width=9, height=4)


df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/cso_processed/metrics_correlation.csv')
x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")
hyper <- c("Take All", 'Max Depth', "LLM", 'Sim Threshold', 'Types Threshold')

df <- df %>%
  filter(!X %in% hyper)%>%
  filter(Y %in% hyper)%>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(X = gsub(r"(\\)", "", X))

ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2)), size=4, colour = "white")+ 
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20), 
        legend.position="none") +
  guides(x =  guide_axis(angle = 45)) 
#rotate_x_text(angle = -90, align = 0, valign = 0.25)
#scale_x_discrete(guide = guide_axis(n.dodge = 2))



ggsave('~/PycharmProjects/SoftwareTopics/report/plots/cso_hyper_correlation_heatmap.pdf', width=9, height=4)




df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_processed/metrics_correlation.csv')
x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")
hyper <- c("Take All", 'Max Depth', "LLM", 'Sim Threshold', 'Types Threshold', 'prompt_type')

df <- df %>%
  filter(!X %in% hyper)%>%
  filter(Y %in% hyper)%>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(X = gsub(r"(\\)", "", X))

ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2)), size=4, colour = "white")+ 
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20), 
        legend.position="none") +
  guides(x =  guide_axis(angle = 45)) 
#rotate_x_text(angle = -90, align = 0, valign = 0.25)
#scale_x_discrete(guide = guide_axis(n.dodge = 2))



ggsave('~/PycharmProjects/SoftwareTopics/report/plots/LLM_hyper_correlation_heatmap.pdf', width=9, height=4)



df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/LLM_Iter_processed/metrics_correlation.csv')
x_vars <- c("\\# Nodes", "\\# Edges", "\\# Leafs", "\\# Roots", "\\# Bridges",  "\\# Intermediate", "\\# Self Loops", "\\# Cycles", "\\#  CC", "Pairs Acc")
hyper <- c("Take All", 'Max Depth', "LLM", 'Sim Threshold', 'Types Threshold', 'prompt_type')

df <- df %>%
  filter(!X %in% hyper)%>%
  filter(Y %in% hyper)%>%
  mutate(Y = str_to_title(Y, locale = "en")) %>%
  mutate(X = gsub(r"(\\)", "", X))

ggplot(df, aes(X, Y, fill= correlation)) + 
  geom_tile(aes(fill = correlation), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  geom_text(aes(label = round(correlation, 2)), size=4, colour = "white")+ 
  labs(x ="Metric", y = "Postprocessing") +
  theme(text = element_text(size = 20), 
        legend.position="none") +
  guides(x =  guide_axis(angle = 45)) 
#rotate_x_text(angle = -90, align = 0, valign = 0.25)
#scale_x_discrete(guide = guide_axis(n.dodge = 2))


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/LLM_Iter_hyper_correlation_heatmap.pdf', width=9, height=4)


