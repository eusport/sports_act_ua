#!/usr/bin/env python3
"""Generate a bar chart of yearly line changes from git history."""

import subprocess
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

def get_git_stats(repo_path="."):
    """Extract yearly additions/deletions from git log."""
    cmd = ["git", "-C", repo_path, "log", "--format=%ad", "--date=format:%Y", "--numstat", "--all"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    stats = defaultdict(lambda: {"additions": 0, "deletions": 0})
    current_year = None

    for line in result.stdout.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Year line (just 4 digits)
        if re.match(r'^\d{4}$', line):
            current_year = line
        # Numstat line: additions<tab>deletions<tab>filename
        elif current_year and '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 2:
                try:
                    additions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    # Only count sports_act.md changes
                    if 'sports_act' in parts[-1].lower() or parts[-1].endswith('.md'):
                        stats[current_year]["additions"] += additions
                        stats[current_year]["deletions"] += deletions
                except ValueError:
                    pass

    return dict(stats)

def create_chart(stats, output_path="changes.png"):
    """Create the bar chart matching the original style."""
    # Sort years
    years = sorted(stats.keys())
    additions = [stats[y]["additions"] for y in years]
    deletions = [-stats[y]["deletions"] for y in years]  # Negative for downward bars

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(years))
    width = 0.8

    # Colors with gradient effect
    green_colors = ['#90EE90', '#7CCD7C', '#66B266']  # Light to medium green
    red_colors = ['#FF6B6B', '#CD5C5C', '#B22222']    # Light to dark red

    # Draw bars
    for i, (year, add, dele) in enumerate(zip(years, additions, deletions)):
        # Addition bar (green)
        if add > 0:
            bar = ax.bar(i, add, width, color='#90EE90', edgecolor='#66B266', linewidth=0.5)
            # Add value label
            ax.text(i, add + 5, str(add), ha='center', va='bottom', fontsize=8, color='#333')

        # Deletion bar (red, going down)
        if dele < 0:
            bar = ax.bar(i, dele, width, color='#FF7F7F', edgecolor='#CD5C5C', linewidth=0.5)
            # Add value label
            ax.text(i, dele - 5, str(abs(dele)), ha='center', va='top', fontsize=8, color='#333')

    # Styling
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha='right', fontsize=9)
    ax.axhline(y=0, color='#888', linewidth=0.5)
    ax.set_ylabel('')
    ax.set_xlabel('')

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#888')
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#888')
    ax.spines['bottom'].set_color('#888')

    # Background
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    import os

    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Extracting git statistics...")
    stats = get_git_stats(script_dir)

    print(f"Found data for {len(stats)} years:")
    for year in sorted(stats.keys()):
        print(f"  {year}: +{stats[year]['additions']} -{stats[year]['deletions']}")

    output_path = os.path.join(script_dir, "changes.png")
    create_chart(stats, output_path)
