#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 13:16:08 2026

@author: bernard akaawase
"""


def extract_colorblind_safe_palette(
    image_path,
    n_colors=5,
    deltaE_thresh=10,
    resize=400,
    plot=True,
    save=True,
    outdir=None
):
    """
    Extract dominant colors from an image and evaluate color-blind safety.
    Saves figure and summary text if save=True.
    """

    import os
    import numpy as np
    from PIL import Image
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    from skimage.color import rgb2lab
    from collections import Counter

    # -----------------------------
    # Output paths
    # -----------------------------
    base = os.path.splitext(os.path.basename(image_path))[0]
    if outdir is None:
        outdir = os.path.dirname(image_path)

    fig_path = os.path.join(outdir, f"{base}_palette.png")
    txt_path = os.path.join(outdir, f"{base}_palette.txt")

    # -----------------------------
    # Color-blind simulation matrices
    # -----------------------------
    
    # Protanopia (Red-blind)
    # Red perception is weakened
    # Reds and greens become harder to distinguish
    # Common failure mode: red vs green lines look identical
    
    #Deuteranopia (Green-blind)
    # Green channel is altered
    # Most common type of color blindness
    # Causes orange / green / yellow confusion
    
    # Tritanopia (Blue-blind)
    # Rare, but important
    # Blue–yellow confusion
    # Can break heatmaps and colormaps
    
    CB_MATRICES = {
        "protanopia": np.array([
            [0.56667, 0.43333, 0.0],
            [0.55833, 0.44167, 0.0],
            [0.0,     0.24167, 0.75833]
        ]),
        "deuteranopia": np.array([
            [0.625, 0.375, 0.0],
            [0.70,  0.30,  0.0],
            [0.0,   0.30,  0.70]
        ]),
        "tritanopia": np.array([
            [0.95,  0.05,  0.0],
            [0.0,   0.43333, 0.56667],
            [0.0,   0.475,   0.525]
        ])
    }

    # -----------------------------
    # Load & preprocess image
    # -----------------------------
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    scale = resize / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)))

    img_np = np.asarray(img)
    pixels = img_np.reshape(-1, 3) / 255.0

    # -----------------------------
    # KMeans color extraction
    # -----------------------------
    kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    labels = kmeans.fit_predict(pixels)
    colors = kmeans.cluster_centers_

    counts = Counter(labels)
    freqs = np.array([counts[i] for i in range(n_colors)])
    freqs = freqs / freqs.sum() * 100

    # -----------------------------
    # Color-blind safety test
    # -----------------------------
    def simulate_cb(rgb, matrix):
        return np.clip(rgb @ matrix.T, 0, 1)

    safe_flags = []

    for i in range(len(colors)):
        is_safe = True
        for mat in CB_MATRICES.values():
            sim_colors = np.array([simulate_cb(c, mat) for c in colors])
            sim_lab = rgb2lab(sim_colors.reshape(-1, 1, 3)).reshape(-1, 3)

            for j in range(len(sim_lab)):
                if i != j:
                    dE = np.linalg.norm(sim_lab[i] - sim_lab[j])
                    if dE < deltaE_thresh:
                        is_safe = False
                        break
            if not is_safe:
                break

        safe_flags.append(is_safe)

    # -----------------------------
    # Format results
    # -----------------------------
    results = []
    for rgb, f, safe in zip(colors, freqs, safe_flags):
        rgb255 = tuple((rgb * 255).astype(int))
        hexcol = "#{:02X}{:02X}{:02X}".format(*rgb255)
        results.append({
            "hex": hexcol,
            "rgb": rgb255,
            "frequency": round(f, 1),
            "colorblind_safe": safe
        })

    results.sort(key=lambda x: -x["frequency"])


    # -----------------------------
    # Print + write text summary
    # -----------------------------
    lines = []
    header = f" Extracted {n_colors} colors from {image_path}\n"
    table_head = (
        "┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃ Hex      ┃ RGB             ┃ Freq (%) ┃ Color-Blind Safe?  ┃\n"
        "┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩\n"
    )

    lines.append(header)
    lines.append(table_head)

    for r in results:
        flag = "YES" if r["colorblind_safe"] else "NO"
        lines.append(
            f"│ {r['hex']:<8} │ {str(r['rgb']):<15} │ "
            f"{r['frequency']:>6}% │ {flag:<18} │\n"
        )

    lines.append("└──────────┴─────────────────┴──────────┴────────────────────┘\n")

    # ---- PRINT to console ----
    print("\n".join(lines))

    # ---- SAVE to file ----
    if save:
        with open(txt_path, "w") as f:
            f.writelines(lines)


    # -----------------------------
    # Plot image + palette
    # -----------------------------
    if plot:
        fig, axes = plt.subplots(
            1, 2, figsize=(8, 5),
            gridspec_kw={"width_ratios": [3, 1]}
        )

        axes[0].imshow(img_np)
        axes[0].set_title("Input Image", fontsize = 30)
        axes[0].axis("off")

        ax = axes[1]
        for i, r in enumerate(results):
            ax.barh(i, 1, color=r["hex"], edgecolor="black")
            label = f"{r['hex']} {'✓' if r['colorblind_safe'] else '✗'}"
            ax.text(0.5, i, label, ha="center", va="center",
                    fontsize=9, color="white")

        ax.set_title("Extracted Palette", fontsize = 15)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.invert_yaxis()

        plt.tight_layout()

        if save:
            plt.savefig(fig_path, dpi=300, bbox_inches="tight")

        plt.show()

    return results




## Run the function
extract_colorblind_safe_palette(
    "data/flower.jpg",
    n_colors=8
)
