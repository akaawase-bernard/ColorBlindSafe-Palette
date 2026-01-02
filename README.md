# ColorBlindSafe Figure Palette 🎨♿

**Automatically extract color palettes from images and scientific figures — and verify if they are color-blind safe.**

This tool removes the guesswork from choosing plot colors by simulating human color-blind vision and flagging unsafe color combinations.

---

## ✨ Features

- Extract dominant colors from images or figures
- Compute color usage frequency
- Simulate color-blind vision:
  - Protanopia (red-blind)
  - Deuteranopia (green-blind)
  - Tritanopia (blue-blind)
- Quantify perceptual color separation (ΔE)
- Automatically label colors as **safe / unsafe**
- Generate:
  - Publication-ready palette figure
  - Human-readable `.txt` summary
- Designed for **scientific plots, papers, and presentations**

---

## 📷 Example Output

<p align="center">
  <img src="data/flower_palette.png" width="700">
</p>

---

## 🎥 Video Walkthrough

A full explanation of the theory and code is available here:

👉 https://youtu.be/-E_L7enoNu0

---

## 🚀 Usage

```python
from colorblind_palette import extract_colorblind_safe_palette

extract_colorblind_safe_palette(
    "data/flower.jpg",
    n_colors=8
)

