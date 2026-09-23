"""
Correlation heatmap for the BRFSS2021 diabetes dataset.
Diverging palette: teal (negative) -- white (0) -- coral (positive),
matching the project deck. Outputs correlation_heatmap.png.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

df = pd.read_csv("diabetes_clean.csv")

# put the target first so its row/column is easy to read
cols = ["Diabetes_012"] + [c for c in df.columns if c != "Diabetes_012"]
corr = df[cols].corr()
n = len(cols)

# diverging colormap: teal -> white -> coral
cmap = LinearSegmentedColormap.from_list(
    "teal_coral", ["#0E8080", "#7FB8B8", "#F4F7F6", "#EFA98F", "#E06D4F"]
)

fig, ax = plt.subplots(figsize=(13.5, 12), dpi=150)
im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect="equal")

ax.set_xticks(range(n)); ax.set_yticks(range(n))
ax.set_xticklabels(cols, rotation=90, fontsize=8, color="#1E2A2A")
ax.set_yticklabels(cols, fontsize=8, color="#1E2A2A")
ax.tick_params(length=0)

# thin grid between cells (2px surface gap feel)
ax.set_xticks(np.arange(-.5, n, 1), minor=True)
ax.set_yticks(np.arange(-.5, n, 1), minor=True)
ax.grid(which="minor", color="white", linewidth=1.5)
for s in ax.spines.values():
    s.set_visible(False)

# annotate each cell; white text on strong colors, ink on light
for i in range(n):
    for j in range(n):
        v = corr.values[i, j]
        txt_color = "white" if abs(v) > 0.55 else "#1E2A2A"
        ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                fontsize=6.3, color=txt_color)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02, ticks=[-1, -0.5, 0, 0.5, 1])
cbar.ax.tick_params(labelsize=8, color="#6E8383", labelcolor="#1E2A2A")
cbar.outline.set_visible(False)
cbar.set_label("Correlation (Pearson r)", fontsize=9, color="#1E2A2A")

ax.set_title("Diabetes Health Indicators — Correlation Heatmap",
             fontsize=15, fontweight="bold", color="#0C3B3B", pad=14)

plt.tight_layout()
plt.savefig("correlation_heatmap.png", bbox_inches="tight", facecolor="white")
print("saved correlation_heatmap.png")
