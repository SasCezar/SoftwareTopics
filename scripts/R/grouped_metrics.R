library(tidyverse)
library(ggplot2)
library(reshape2)
library(dplyr)
library(ggh4x)
library(paletteer)
library(forcats)
library(cowplot)
library(purrr)
library(ggpubr)
# library(patchwork)

targets <-
  c(
    "\\# Nodes",
    "\\# Edges",
    "\\# Leafs",
    "\\# Roots",
    "\\# Bridges",
    "\\# Intermediate",
    "\\# Self Loops",
    "\\# Cycles",
    'Pairs Acc'
  )

pp_mask <- c('0, 0, 0, 0',
             '1, 0, 0, 0',
             '0, 1, 0, 0',
             '0, 0, 1, 0',
             '0, 0, 0, 1')



for (t in targets) {
  target <- c(t)
  
  values <- c()
  
  df <-
    read.csv(
      '/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/cso_processed/melted_metrics.csv'
    )
  
  df <- df %>%
    mutate_at(c('Sim_Threshold', 'Value'), as.numeric) %>%
    filter(Metric %in% target) %>%
    mutate(LLM = replace(LLM, LLM == 'all-mpnet-base-v2', 'MP')) %>%
    mutate(LLM = replace(LLM, LLM == 'all-MiniLM-L6-v2', 'L6')) %>%
    unite(
      "processing",
      cycle:bridge:abstract:minimization,
      remove = FALSE,
      sep = ', '
    ) %>%
    mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
    mutate(
      processing = fct_relevel(
        processing,
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
        '1, 1, 1, 1'
      )
    ) %>%
    filter(processing %in% pp_mask)
  
  df$source <- rep('CSO', length(df$Value))
  values <- append(values, df$Value)
  cso <- ggplot(df, aes(LLM, Sim_Threshold, fill = Value)) +
    geom_tile() +
    facet_nested(~ source + processing)
  
  
  
  df <-
    read.csv(
      '/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/wikidata_processed/melted_metrics.csv'
    )
  
  df$Types_Threshold <- as.factor(df$Types_Threshold)
  df$Max_Depth <- as.factor(df$Max_Depth)
  
  
  df <- df %>%
    filter(Metric %in% target) %>%
    mutate_at(c('Value'), as.numeric) %>%
    unite(
      "processing",
      cycle:bridge:abstract:minimization,
      remove = FALSE,
      sep = ', '
    ) %>%
    mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
    mutate(
      processing = fct_relevel(
        processing,
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
        '1, 1, 1, 1'
      )
    ) %>%
    filter(processing %in% pp_mask)
  
  
  values <- append(values, df$Value)
  df$source <- rep('Wiki', length(df$Value))
  wiki <-
    ggplot(df, aes(Types_Threshold, Max_Depth, fill = Value)) +
    geom_tile() +
    facet_nested(~ source + processing)
  
  
  
  df <-
    read.csv(
      '/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/LLM_processed/melted_metrics.csv'
    )
  
  df <- df %>%
    filter(Metric %in% target) %>%
    unite(
      "processing",
      cycle:bridge:abstract:minimization,
      remove = FALSE,
      sep = ', '
    ) %>%
    mutate(LLM = replace(LLM, LLM == 'gpt-4-1106-preview', 'GPT-4')) %>%
    mutate(LLM = replace(LLM, LLM == 'gpt-3.5-turbo', 'GPT-3.5')) %>%
    mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
    mutate_at(c('Value'), as.numeric) %>%
    mutate(
      processing = fct_relevel(
        processing,
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
        '1, 1, 1, 1'
      )
    ) %>%
    filter(processing %in% pp_mask)
  
  
  values <- append(values, df$Value)
  
  df$source <- rep('LLM', length(df$Value))
  
  llm <- ggplot(df, aes(LLM, prompt_type, fill = Value)) +
    geom_tile() +
    facet_nested(~ source + processing)
  
  df <-
    read.csv(
      '/home/sasce/Downloads/SoftwareTopics/data/interim/taxonomy/LLM_Iter_processed/melted_metrics.csv'
    )
  
  df <- df %>%
    filter(Metric %in% target) %>%
    unite(
      "processing",
      cycle:bridge:abstract:minimization,
      remove = FALSE,
      sep = ', '
    ) %>%
    mutate(LLM = replace(LLM, LLM == 'gpt-4-1106-preview', 'GPT-4')) %>%
    mutate(LLM = replace(LLM, LLM == 'gpt-3.5-turbo', 'GPT-3.5')) %>%
    mutate(Metric = gsub(r"(\\)", "", Metric)) %>%
    mutate_at(c('Value'), as.numeric) %>%
    mutate(
      processing = fct_relevel(
        processing,
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
        '1, 1, 1, 1'
      )
    ) %>%
    filter(processing %in% pp_mask)
  
  
  
  values <- append(values, df$Value)
  df$source <- rep('LLM-Iter', length(df$Value))
  llm_iter <- ggplot(df, aes(LLM, prompt_type, fill = Value)) +
    geom_tile() +
    facet_nested(~  source + processing)
  
  p1 <- ggplot(df, aes(LLM, prompt_type, fill = Value)) +
    geom_tile() +
    facet_nested(~ processing)
  
  legend_b <- get_legend(
    p1 +
      guides(color = guide_legend(nrow = 1)) +
      theme(legend.position = "right") +
      theme(legend.key.height = unit(3, 'cm'))
  )
  
  
  #grid.arrange(cso, wiki, llm, llm_iter,ncol=1, top=t, sca)
  a <- plot_grid(
    cso + theme(legend.position = "none"),
    wiki + theme(legend.position = "none"),
    llm + theme(legend.position = "none"),
    llm_iter + theme(legend.position = "none"),
    align = 'vh',
    hjust = -1,
    ncol = 1
  )
  b <- plot_grid(
    a,
    legend_b,
    ncol = 2,
    align = "h",
    rel_widths = c(1, .1)
  )
  
  plot(b)
  
  ggsave(
    sprintf(
      '/home/sasce/Downloads/SoftwareTopics/report/plots/models_%s.pdf',
      t
    ),
    width = 9,
    height = 10
  )
  
  
  #g <- ggarrange(cso, wiki, llm, llm_iter,ncol=1, common.legend = TRUE, legend="right")
  
  #  g <- annotate_figure(g, top = text_grob(t))
  
  # plot(g)
  
  #combined <-
  #  cso + wiki + llm + llm_iter & theme(legend.position = "bottom")
  #combined + plot_layout(guides = "collect")
  #plot(combined)
}
