<div align="center">

# 🏆 LeetCode Profile Generator

**Generate beautiful SVG dashboards from your LeetCode profile for GitHub READMEs**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![GitHub Action](https://img.shields.io/badge/GitHub_Action-ready-brightgreen.svg)](action.yml)

[Features](#features) • [Quick Start](#quick-start) • [Cards](#cards) • [Themes](#themes) • [GitHub Action](#github-action) • [CLI](#cli) • [Contributing](CONTRIBUTING.md)

</div>

---

## ✨ Features

- 🎨 **8 beautiful SVG cards** — stats, rating graph, heatmap, difficulty, contests, badges, streak, dashboard
- 🎭 **9 built-in themes** — GitHub Dark/Light, Dracula, Nord, Catppuccin, Tokyo Night, Gruvbox, One Dark
- 🎯 **Pure SVG** — no screenshots, no browser automation, no raster images
- ⚡ **Fast** — parallel API calls, <8 second cold start
- 🤖 **GitHub Action ready** — automatic daily updates with one YAML file
- 🔧 **Highly customizable** — custom themes via JSON, toggle any card on/off
- 🆓 **Free & open source** — MIT license, self-hostable, zero dependencies beyond Python
- 📦 **Zero backend** — CLI tool, no server required

## 🚀 Quick Start

### Install

```bash
pip install leetcode-profile-generator
```

### Generate

```bash
leetcode-profile --username YourUsername --theme github_dark --output ./assets
```

### Embed in README

```markdown
![LeetCode Stats](./assets/leetcode_stats.svg)
![Rating History](./assets/rating_history.svg)
![Heatmap](./assets/heatmap.svg)
```

## 📊 Cards

### Stats Card (`leetcode_stats.svg`)
The primary profile overview — avatar, rating, rank, acceptance rate, and difficulty progress bars.

### Rating History (`rating_history.svg`)
Smooth Bézier curve showing contest rating progression with peak and latest highlights.

### Difficulty Distribution (`difficulty.svg`)
Horizontal bars showing easy/medium/hard solving progress with beats percentages.

### Submission Heatmap (`heatmap.svg`)
GitHub-style contribution heatmap showing daily submission activity over the past year.

### Contest History (`contest_history.svg`)
Table of recent 10 contests with ratings, ranks, and color-coded delta changes.

### Badges (`badges.svg`)
Grid of earned LeetCode badges with upcoming badge progress.

### Streak (`streak.svg`)
Current and longest streaks with monthly activity bar chart.

### Dashboard (`dashboard.svg`)
All-in-one combined card with compact stats, difficulty, streak, and recent contests.

## 🎨 Themes

| Theme | Name |
|-------|------|
| 🌑 | `github_dark` (default) |
| ☀️ | `github_light` |
| 🧛 | `dracula` |
| ❄️ | `nord` |
| 🐱 | `catppuccin_mocha` |
| ☕ | `catppuccin_latte` |
| 🌃 | `tokyo_night` |
| 🎨 | `gruvbox_dark` |
| ⚛️ | `one_dark` |

### Custom Themes

Create a JSON file with your color palette:

```json
{
  "name": "my_theme",
  "bg_color": "#1a1a2e",
  "title_color": "#e94560",
  "text_color": "#eaeaea",
  "easy_color": "#4ecca3",
  "medium_color": "#ffd369",
  "hard_color": "#e94560"
}
```

```bash
leetcode-profile --username YourUser --theme path/to/my_theme.json
```

See [`themes/custom_example.json`](themes/custom_example.json) for all available fields.

## 🤖 GitHub Action (Zero Setup Workflow)

Simply create `.github/workflows/leetcode.yml` in your profile repository:

```yaml
name: LeetCode Stats

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  leetcode:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: gufran21/leetcode-profile-generator@v1
        with:
          username: gufran21  # 👈 Replace with your LeetCode username
          theme: github_dark
```

### Embed in your GitHub Profile `README.md`:

```markdown
![LeetCode Stats](./assets/leetcode_stats.svg)
![Rating History](./assets/rating_history.svg)
![Submission Heatmap](./assets/heatmap.svg)
```

### Action Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `username` | *required* | Your LeetCode username |
| `theme` | `github_dark` | Color theme (`github_dark`, `dracula`, `nord`, `catppuccin_mocha`, etc.) |
| `output_dir` | `assets` | Directory where SVG files are saved |
| `auto_commit` | `true` | Automatically commit and push updated SVGs back to repository |
| `commit_message` | `chore: update LeetCode profile cards [skip ci]` | Git commit message |
| `generate_stats` | `true` | Generate `leetcode_stats.svg` |
| `generate_rating` | `true` | Generate `rating_history.svg` |
| `generate_difficulty` | `true` | Generate `difficulty.svg` |
| `generate_heatmap` | `true` | Generate `heatmap.svg` |
| `generate_streak` | `true` | Generate `streak.svg` |
| `generate_contest_history` | `true` | Generate `contest_history.svg` |
| `generate_badges` | `true` | Generate `badges.svg` |
| `generate_dashboard` | `false` | Generate `dashboard.svg` |

## 💻 CLI

```
Usage: leetcode-profile [OPTIONS]

Options:
  -u, --username TEXT        LeetCode username (required)
  -t, --theme TEXT           Theme name or path to custom JSON
  -o, --output TEXT          Output directory
  --stats / --no-stats       Generate stats card
  --rating / --no-rating     Generate rating history
  --difficulty / --no-difficulty
  --heatmap / --no-heatmap
  --streak / --no-streak
  --contest-history / --no-contest-history
  --badges / --no-badges
  --dashboard / --no-dashboard
  --no-cache                 Skip filesystem cache
  --cache-ttl INTEGER        Cache TTL in seconds (default: 86400)
  --no-avatar                Skip avatar fetch
  -v, --verbose              Debug logging
  --list-themes              List available themes
  --version                  Show version
  --help                     Show help
```

### Examples

```bash
# Generate all cards with Dracula theme
leetcode-profile -u gufran21 -t dracula -o ./assets

# Only stats and rating cards
leetcode-profile -u gufran21 --no-heatmap --no-streak --no-badges --no-contest-history

# Force fresh data (skip cache)
leetcode-profile -u gufran21 --no-cache

# List all available themes
leetcode-profile --list-themes
```

## 🏗️ Architecture

```
CLI / GitHub Action
      │
  GraphQL Client (httpx async)
      │
  ┌───┼───┐
  ▼   ▼   ▼
APIs (parallel fetch)
      │
  Data Models (dataclasses)
      │
  Data Service (orchestrator)
      │
  Card Generators (8 cards)
      │
  SVG Renderer + Theme Engine
      │
  Generated SVG Assets
```

## 🧪 Testing

```bash
pytest tests/ -v
```

The test suite includes:
- Model validation tests
- GraphQL client tests (mocked HTTP)
- Data service parsing tests
- Theme engine tests (all 9 themes)
- Card generator tests (XML validation, size limits)
- 8 cards × 9 themes = 72 parametrized card tests
- Streak calculator tests
- Cache tests (TTL, corruption recovery)
- CLI tests

## 📜 License

MIT — see [LICENSE](LICENSE)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, how to add themes/cards, and PR guidelines.

---

<div align="center">

**If this project helps you, give it a ⭐!**

Made with ❤️ for the competitive programming community

</div>
