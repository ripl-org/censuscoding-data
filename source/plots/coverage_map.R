library(tidyverse)
library(ggplot2)
library(urbnmapr)
library(gridExtra)

args        <- commandArgs(trailingOnly = TRUE)
county_file <- args[1]
data_file   <- args[2]
png_file    <- args[3]

# Group by zip code and join county
data <- read_csv(data_file) %>%
  group_by(zipcode, lookup) %>%
  summarize(
    n = sum(n),
    blkgrp = sum(blkgrp)
  ) %>%
  left_join(
    read_csv(county_file),
    by = "zipcode",
    multiple = "all"
  )

print(head(data))
cat("Missing county for", sum(data[is.na(data$county), "n"]), "of", sum(data$n), "\n")

# Group by county
data <- data %>%
  group_by(county, lookup) %>%
  summarize(
    n = sum(n),
    blkgrp = sum(blkgrp)
  ) %>%
  mutate(
    coverage = 100.0 * blkgrp / n
  ) %>%
  pivot_wider(
    id_cols = county,
    names_from = lookup,
    values_from = coverage
  )

print(head(data))

sf_state  <- get_urbn_map(map = "states",   sf = TRUE)
sf_county <- get_urbn_map(map = "counties", sf = TRUE)

data <- inner_join(sf_county, data, by = c("county_fips"="county"))

data <- list(
  mutate(data, coverage = line),
  mutate(data, coverage = point)
)
titles <- c(
  "Line Coverage",
  "Point Coverage"
)

plot <- do.call(grid.arrange, 
  lapply(
    seq(1, 2),
    function(i) {
      ggplot(data[[i]]) +
        geom_sf(mapping = aes(fill = coverage), color = NA) +
        geom_sf(data = sf_state, fill = NA, color = "black", size = 0.25) +
        coord_sf(datum = NA) +
        scale_fill_gradient(
          name = "Coverage (%)",
          low = "pink",
          high = "navyblue", 
          na.value = "white",
          limits = c(0, 100),
          breaks = c(0, 100)
        ) +
        ggtitle(titles[[i]]) +
        theme_bw() +
        theme(
          legend.position="right",
          panel.border = element_blank()
        )
    }
  )
)

ggsave(
  filename = png_file,
  plot = plot,
  width = 7.5,
  height = 8
)
