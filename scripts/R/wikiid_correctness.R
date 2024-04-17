library(ggplot2)
library(dplyr)
library(forcats)

df <- read.csv('~/PycharmProjects/SoftwareTopics/scripts/R/cso_wikiid_correctness.csv')

df <- df %>% 
  mutate(Percent=Value,Percent=scales::percent(Value, accuracy = 1L))  %>%
  mutate(Metric = fct_relevel(Metric, 'Incorrect', 'Correct')) 

ggplot(df, aes(x = Threshold, y = Value, fill = Metric, label=Value)) + 
  geom_bar(stat = 'identity', position = "dodge") +
  labs(y = "Percentage", x = "Similarity Threshold") +
  theme(legend.title=element_blank(), text = element_text(size = 20)) +
  scale_x_continuous(breaks = scales::pretty_breaks(n = 10)) +
  theme(legend.position = "top")
  

ggsave('~/PycharmProjects/SoftwareTopics/report/plots/wikiid_correctness.pdf', 
       width = 10, height = 5)