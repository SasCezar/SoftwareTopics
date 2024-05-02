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
library(wesanderson)

df <- read.csv('~/PycharmProjects/SoftwareTopics/data/interim/taxonomy/intersections.csv')

df <- df %>% 
    mutate(Model1 = fct_relevel(Model1, 'CSO', 'Wiki', 'LLM', 'All')) %>%
    mutate(Model2 = fct_relevel(Model2, 'CSO', 'Wiki', 'LLM', 'All')) %>%
    mutate(Metric= fct_relevel(Metric, 'Gitranking', 'New Terms', 'Unmatched', 'Pairs'))


ggplot(df, aes(Model1, Model2, fill= Intersection)) + 
  geom_tile(aes(fill = Intersection), 
            color = "white",
            lwd = 1.5,
            linetype = 1) +
  labs(x ="Model", y = "Model") +
  geom_text(aes(label = round(Intersection, 2)), size=6, colour = "white")+ 
  theme(text = element_text(size = 20),
        legend.position="none")  +
  facet_grid(~ Metric, scales = "free")


ggsave('~/PycharmProjects/SoftwareTopics/report/plots/intra_intersections.pdf', width=9, height=4)



