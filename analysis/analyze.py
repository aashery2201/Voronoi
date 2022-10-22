import csv
import re
from glob import glob
from itertools import product
from os import makedirs, remove

import matplotlib.pyplot as plt
import numpy as np

NS = [1, 2, 5, 10, 20]
LENGTHS = [50, 100, 500, 1000, 2000]
GROUPS = list(range(1, 9))

pattern = re.compile(r"(?P<length>\d+), (?P<n>\d+) - (?P<dimension>.+)")

for existing in glob("plots/**/*.png"):
    remove(existing)

makedirs("plots", exist_ok=True)

with open("results.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    # [(n, length, dimension)]
    game_dims = [
        (int(match.group("n")), int(match.group("length")), match.group("dimension"))
        for col in header[1:-2]
        if (match := pattern.match(col))
    ]
    # spawn -> length -> group -> score
    game_results = {n: {length: {} for length in LENGTHS} for n in NS}
    for (group, data) in enumerate(reader):
        group = group + 1
        results = zip(game_dims, data[1:-2])
        for ((n, length, dimension), result) in results:
            if dimension == "Total Score":
                game_results[n][length][group] = int(result)

makedirs("plots/raw", exist_ok=True)
for n in NS:
    plt.clf()
    for group in range(8):
        num_bar_groups = len(LENGTHS)
        num_bars = 8
        x = np.arange(num_bar_groups)
        width = 0.1
        group_name = group + 1
        bars = plt.bar(
            x - (width * num_bars) / 2 + (group * width),
            [game_results[n][length][group_name] for length in LENGTHS],
            width,
            label=f"G{group_name}",
        )
    plt.title(f"n={n}")
    plt.gca().set_ylabel("Score")
    plt.gca().set_xticks(x, LENGTHS)
    plt.gca().legend()
    plt.savefig(f"plots/raw/{n}.png", dpi=300)

makedirs("plots/scaled", exist_ok=True)
scaled_results = {n: {length: {} for length in LENGTHS} for n in NS}
for n in NS:
    for length in LENGTHS:
        highest_score = max(game_results[n][length][group] for group in GROUPS)
        for group in GROUPS:
            scaled_results[n][length][group] = (
                game_results[n][length][group] / highest_score
            )

for n in NS:
    plt.clf()
    for group in range(8):
        num_bar_groups = len(LENGTHS)
        num_bars = 8
        x = np.arange(num_bar_groups)
        width = 0.1
        group_name = group + 1
        bars = plt.bar(
            x - (width * num_bars) / 2 + (group * width),
            [scaled_results[n][length][group_name] for length in LENGTHS],
            width,
            label=f"G{group_name}",
        )
    plt.title(f"n={n}")
    plt.gca().set_ylabel("% of max score")
    plt.gca().set_xticks(x, LENGTHS)
    plt.gca().legend()
    plt.savefig(f"plots/scaled/{n}.png", dpi=300)
