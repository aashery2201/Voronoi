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

with open("games.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    games = []
    for row in reader:
        games.append(dict(zip(header, row)))

matchups = np.zeros((8, 8), dtype=int)
matchup_scores = np.zeros((8, 8), dtype=int)
for game in games:
    if int(game["Total Day"]) < 1000:
        continue

    p1 = int(game["Player 1"])
    p2 = int(game["Player 2"])
    p3 = int(game["Player 3"])
    p4 = int(game["Player 4"])
    s1 = int(game["Player 1 Final Score"])
    s2 = int(game["Player 2 Final Score"])
    s3 = int(game["Player 3 Final Score"])
    s4 = int(game["Player 4 Final Score"])

    ranked = sorted(
        [(p1, s1), (p2, s2), (p3, s3), (p4, s4)], key=lambda t: t[1], reverse=True
    )
    for ai in range(3):
        above_group, above_score = ranked[ai]
        above_group -= 1
        for bi in range(ai + 1, 4):
            below_group, below_score = ranked[bi]
            below_group -= 1

            matchups[above_group][below_group] += 1

            matchup_scores[above_group][below_group] += above_score
            matchup_scores[below_group][above_group] += below_score

matchup_win_ratios = np.zeros((8, 8), dtype=float)
for a in range(8):
    for b in range(8):
        total_games = matchups[a][b] + matchups[b][a]
        if a == b:
            matchup_win_ratios[a][b] = None
        elif total_games == 0:
            matchup_win_ratios[a][b] = 0
        else:
            matchup_win_ratios[a][b] = matchups[a][b] / total_games
# Matchup win ratios
plt.clf()
plt.imshow(matchup_win_ratios)
for a in range(8):
    for b in range(8):
        text = plt.gca().text(
            b,
            a,
            round(matchup_win_ratios[a][b], 2),
            ha="center",
            va="center",
            color="w",
        )
group_ticks = np.arange(8)
group_labels = [f"G{n + 1}" for n in range(8)]
plt.gca().set_xticks(group_ticks, group_labels)
plt.gca().set_yticks(group_ticks, group_labels)
plt.gca().set_title("Matchup Win Rates")
plt.xlabel("Loses")
plt.ylabel("Wins")
plt.savefig("plots/matchup_wins.png", dpi=300)

# Matchup score ratios
matchup_score_ratios = np.zeros((8, 8), dtype=float)
for a in range(8):
    for b in range(8):
        if a == b:
            matchup_scores[a][b] = 0
        a_score = matchup_scores[a][b]
        b_score = matchup_scores[b][a]
        matchup_score_ratios[a][b] = (
            (a_score / b_score) - 1
            if a_score > b_score
            else (-1 * (b_score / a_score)) + 1
        )
plt.clf()
plt.imshow(matchup_score_ratios, vmin=-1, vmax=1)
for a in range(8):
    for b in range(8):
        text = plt.gca().text(
            b,
            a,
            # round(matchup_score_ratios[a][b], 2),
            round(matchup_scores[a][b] / matchup_scores[b][a], 2),
            ha="center",
            va="center",
            color="w",
        )
group_ticks = np.arange(8)
group_labels = [f"G{n + 1}" for n in range(8)]
plt.gca().set_xticks(group_ticks, group_labels)
plt.gca().set_yticks(group_ticks, group_labels)
plt.gca().set_title("Matchup Score Ratios")
plt.xlabel("Loses")
plt.ylabel("Wins")
plt.savefig("plots/matchup_scores.png", dpi=300)
