library(tidyverse)
library(ggplot2)
library(ggsci)
library(gridExtra)

args      <- commandArgs(trailingOnly = TRUE)
data_file <- args[1]
pdf_file  <- args[2]

tests <- list(
  "epa-frs" = "EPA-Registered Facilities (EPA FRS)",
  "hud-phb" = "Public Housing Buildings (HUD)"
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
    blkgrp_true = sum(blkgrp_true),
    tract_true = sum(tract_true),
    county_true = sum(county_true)
  ) %>%
  mutate(
    blkgrp_accuracy = 100.0 * blkgrp_true / n,
    tract_accuracy = 100.0 * tract_true / n,
    county_accuracy = 100.0 * county_true / n,
    test = factor(test, levels = rev(names(tests)), labels = rev(tests)),
    lookup = factor(lookup, levels = rev(names(lookups)), labels = rev(lookups))
  )

print(head(data))

data <- list(
  mutate(data, accuracy = blkgrp_accuracy),
  mutate(data, accuracy = tract_accuracy),
  mutate(data, accuracy = county_accuracy)
)
titles <- c(
  "Block Group (12-digit GEOID) Accuracy",
  "Tract (11-digit GEOID) Accuracy",
  "County (5-digit GEOID) Accuracy"
)

plot <- do.call(grid.arrange, 
  lapply(
    seq(1, 3),
    function(i) {
      ggplot(data[[i]], aes(lookup, accuracy, fill = lookup)) +
        geom_col(width = 0.75) +
        coord_flip() +
        scale_y_continuous(
          limits = c(0, 100),
          breaks = seq(0, 100, 10),
          labels = sapply(seq(0, 100, 10), function(y) { paste0(y, "%") })
        ) +
        scale_fill_npg() +
        ggtitle(titles[[i]]) +
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
    }
  )
)

ggsave(
  filename = pdf_file,
  plot = plot,
  width = 7.5,
  height = 6.5
)
