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
  filter(lookup == "all") %>%
  group_by(zipcode) %>%
  summarize(
    n = sum(n),
    blkgrp_true = sum(blkgrp_true),
    tract_true = sum(tract_true),
    county_true = sum(county_true)
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
  group_by(county) %>%
  summarize(
    n = sum(n),
    blkgrp_true = sum(blkgrp_true),
    tract_true = sum(tract_true),
    county_true = sum(county_true)
  ) %>%
  mutate(
    blkgrp_accuracy = 100.0 * blkgrp_true / n,
    tract_accuracy = 100.0 * tract_true / n,
    county_accuracy = 100.0 * county_true / n
  )

print(head(data))

sf_state  <- get_urbn_map(map = "states",   sf = TRUE)
sf_county <- get_urbn_map(map = "counties", sf = TRUE)

data <- inner_join(sf_county, data, by = c("county_fips"="county"))

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
      ggplot(data[[i]]) +
        geom_sf(mapping = aes(fill = accuracy), color = NA) +
        geom_sf(data = sf_state, fill = NA, color = "black", size = 0.25) +
        coord_sf(datum = NA) +
        scale_fill_gradient(
          name = "Accuracy (%)",
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
  height = 12
)
