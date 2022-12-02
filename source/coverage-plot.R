library(tidyverse)
library(ggplot2)
library(ggsci)

args      <- commandArgs(trailingOnly = TRUE)
data_file <- args[1]
pdf_file  <- args[2]

tests <- list(
  "cms-npi" = "Healthcare Providers (CMS NPI Directory)",
  "epa-frs" = "EPA-Registered Facilities (EPA FRS)",
  "hud-phb" = "Public Housing Buildings (HUD)",
  "uspto-pat" = "US Patent Assignees (USPTO)"
)

lookups <- list(
  "point" = "Address Points",
  "line" = "TIGER Street Lines",
  "all" = "Both"
)

decades <- c("2020", "2010", "2000")

# Group by decade
data <- read_csv(data_file) %>%
  mutate(
    decade = paste0(as.integer(year / 10), "0")
  ) %>%
  filter(
    decade %in% decades,
    test %in% names(tests)
  ) %>%
  group_by(decade, test, lookup) %>%
  summarize(
    n = sum(n),
    blkgrp = sum(blkgrp)
  ) %>%
  mutate(
    coverage = 100.0 * blkgrp / n,
    test = factor(test, levels = rev(names(tests)), labels = rev(tests)),
    lookup = factor(lookup, levels = rev(names(lookups)), labels = rev(lookups))
  )

print(head(data))

g <- ggplot(data, aes(lookup, coverage, fill = lookup)) +
  geom_col(width = 0.75) +
  coord_flip() +
  scale_y_continuous(
    limits = c(0, 100),
    breaks = seq(0, 100, 10),
    labels = sapply(seq(0, 100, 10), function(y) { paste0(y, "%") })
  ) +
  scale_fill_npg() +
  theme_minimal() +
  theme(
    axis.title = element_blank(),
    axis.text.x = element_text(size = 6, angle = 90),
    axis.text.y = element_text(size = 6),
    axis.ticks.y = element_blank(),
    legend.position = "none",
    panel.grid = element_blank(),
    panel.grid.major.x = element_line(color = "gray70", size = 0.125, linetype = 1),
    strip.text.x = element_text(size = 10, hjust = 0),
    strip.text.y = element_text(size = 7, hjust = 0, angle = 0)
  ) +
  facet_grid(test ~ decade)

ggsave(
  filename = pdf_file,
  plot = g,
  width = 7.5,
  height = 4
)
