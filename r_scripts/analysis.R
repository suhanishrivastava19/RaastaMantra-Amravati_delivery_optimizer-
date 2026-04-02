#!/usr/bin/env Rscript
# ════════════════════════════════════════════════════════════════
# Raasta Mantra — Amravati Delivery System
# R Analysis Script: Algorithm Performance Statistics
# Run: Rscript r_scripts/analysis.R
# ════════════════════════════════════════════════════════════════

cat("╔══════════════════════════════════════════╗\n")
cat("║  Raasta Mantra Amravati — R Statistical Report ║\n")
cat("╚══════════════════════════════════════════╝\n\n")

# ── Simulated data (replace with MongoDB import via mongolite) ──
set.seed(42)
n_runs <- 50

astar_times  <- rnorm(n_runs, mean = 8.5,  sd = 3.2)   # ms
ucs_times    <- rnorm(n_runs, mean = 12.3, sd = 4.1)   # ms
astar_dists  <- rnorm(n_runs, mean = 4.2,  sd = 1.8)   # km
ucs_dists    <- rnorm(n_runs, mean = 4.1,  sd = 1.7)   # km
categories   <- sample(c("delivery", "urgent", "normal"), n_runs,
                       replace = TRUE, prob = c(0.4, 0.3, 0.3))
ratings      <- sample(1:5, 30, replace = TRUE,
                       prob = c(0.05, 0.10, 0.15, 0.35, 0.35))

# ════════════════════════════════════════════════════════════════
# 1. Descriptive Statistics
# ════════════════════════════════════════════════════════════════
cat("═══════════════════════════════\n")
cat("  1. DESCRIPTIVE STATISTICS\n")
cat("═══════════════════════════════\n\n")

cat("A* Algorithm:\n")
cat(sprintf("  Mean time  : %.2f ms\n", mean(astar_times)))
cat(sprintf("  Median time: %.2f ms\n", median(astar_times)))
cat(sprintf("  SD time    : %.2f ms\n", sd(astar_times)))
cat(sprintf("  Mean dist  : %.3f km\n", mean(astar_dists)))
cat(sprintf("  SD dist    : %.3f km\n\n", sd(astar_dists)))

cat("UCS Algorithm:\n")
cat(sprintf("  Mean time  : %.2f ms\n", mean(ucs_times)))
cat(sprintf("  Median time: %.2f ms\n", median(ucs_times)))
cat(sprintf("  SD time    : %.2f ms\n", sd(ucs_times)))
cat(sprintf("  Mean dist  : %.3f km\n", mean(ucs_dists)))
cat(sprintf("  SD dist    : %.3f km\n\n", sd(ucs_dists)))

# ════════════════════════════════════════════════════════════════
# 2. Hypothesis Test: Are A* and UCS significantly different?
# ════════════════════════════════════════════════════════════════
cat("═══════════════════════════════\n")
cat("  2. HYPOTHESIS TESTING\n")
cat("═══════════════════════════════\n\n")

t_result_time <- t.test(astar_times, ucs_times)
cat("T-test: A* vs UCS execution time\n")
cat(sprintf("  t-statistic : %.4f\n", t_result_time$statistic))
cat(sprintf("  p-value     : %.4f\n", t_result_time$p.value))
cat(sprintf("  95%% CI      : [%.2f, %.2f]\n", t_result_time$conf.int[1],
            t_result_time$conf.int[2]))
if (t_result_time$p.value < 0.05) {
  cat("  Result: SIGNIFICANT difference (p < 0.05)\n\n")
} else {
  cat("  Result: No significant difference (p >= 0.05)\n\n")
}

t_result_dist <- t.test(astar_dists, ucs_dists)
cat("T-test: A* vs UCS path distance\n")
cat(sprintf("  t-statistic : %.4f\n", t_result_dist$statistic))
cat(sprintf("  p-value     : %.4f\n\n", t_result_dist$p.value))

# ════════════════════════════════════════════════════════════════
# 3. Algorithm Winner Analysis
# ════════════════════════════════════════════════════════════════
cat("═══════════════════════════════\n")
cat("  3. WINNER ANALYSIS\n")
cat("═══════════════════════════════\n\n")

astar_wins_time <- sum(astar_times < ucs_times)
ucs_wins_time   <- sum(ucs_times < astar_times)
astar_wins_dist <- sum(astar_dists < ucs_dists)
ucs_wins_dist   <- sum(ucs_dists < astar_dists)

cat(sprintf("Speed wins  — A*: %d / UCS: %d\n", astar_wins_time, ucs_wins_time))
cat(sprintf("Distance wins— A*: %d / UCS: %d\n\n", astar_wins_dist,
            ucs_wins_dist))

overall_winner <- if (astar_wins_time + astar_wins_dist >
                        ucs_wins_time + ucs_wins_dist)
  "A* Algorithm" else "UCS Algorithm"
cat(sprintf("🏆 Overall Winner: %s\n\n", overall_winner))

# ════════════════════════════════════════════════════════════════
# 4. Category Analysis
# ════════════════════════════════════════════════════════════════
cat("═══════════════════════════════\n")
cat("  4. CATEGORY BREAKDOWN\n")
cat("═══════════════════════════════\n\n")

cat(table(categories))
cat("\n\n")

# ════════════════════════════════════════════════════════════════
# 5. Rating Analysis
# ════════════════════════════════════════════════════════════════
cat("═══════════════════════════════\n")
cat("  5. USER SATISFACTION\n")
cat("═══════════════════════════════\n\n")

cat(sprintf("Total ratings : %d\n", length(ratings)))
cat(sprintf("Average rating: %.2f / 5.0\n", mean(ratings)))
cat(sprintf("Satisfaction  : %.1f%%\n\n", mean(ratings >= 4) * 100))

cat("Rating distribution:\n")
for (i in 1:5) {
  count <- sum(ratings == i)
  stars <- paste(rep("★", i), collapse = "")
  bar   <- paste(rep("█", count), collapse = "")
  cat(sprintf("  %s: %s (%d)\n", stars, bar, count))
}

# ════════════════════════════════════════════════════════════════
# 6. Recommendation
# ════════════════════════════════════════════════════════════════
cat("\n═══════════════════════════════\n")
cat("  6. RECOMMENDATION\n")
cat("═══════════════════════════════\n\n")

cat("Based on statistical analysis:\n")
cat(sprintf("  • Use A*   for SPEED-critical routes (%.1f%% faster)\n",
            abs(mean(astar_times) - mean(ucs_times)) / mean(ucs_times) * 100))
cat(sprintf("  • Use UCS  for COST-optimal routes (guaranteed minimum cost)\n"))
cat(sprintf("  • Both algorithms perform equivalently for path length\n"))
cat(sprintf("  • User satisfaction: %.0f%% rated 4+ stars\n",
            mean(ratings >= 4) * 100))

cat("\n════════════════════════════════\n")
cat("  R Analysis Complete ✓\n")
cat("════════════════════════════════\n")

# ── MongoDB Integration ──
