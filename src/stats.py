import pstats
stats = pstats.Stats("profile_results")
stats.sort_stats("tottime")
stats.print_stats(20)

