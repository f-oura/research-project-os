---
name: research-plot
description: Create, restyle, export, or review research figures using this project's pinned custom-plot styles and visual QA. Use when making plots for analysis, papers, or slides.
---

# Shared research plotting

Resolve paths from the Git project root, then read `@DEPENDENCY@/.agents/skills/research-plot/SKILL.md` and its referenced checklist before plotting. That pinned submodule is the canonical workflow; do not copy or edit its source into this project.

If absent, run `git submodule update --init -- @DEPENDENCY@` from the project root. This checks out the committed pin; do not use `--remote`. If access or the existing Python environment is unavailable, report the missing dependency rather than silently falling back to a different style or installing a new environment.

Use `@DEPENDENCY@/python/plotstyle.py`: `apply_selected(preset='paper'|'slides')`, `semantic(...)`, and `selected_palette(kind='density'|'signed')`. Add that Python directory using a path derived from the project root. Read `config/selection.json`, `config/color_options.json`, and `config/styles.json` inside the submodule for the adopted policy. Center signed differences explicitly at zero.

Keep the project's existing calculation backend, input/provenance records, output locations, and scientific conventions. Python/Matplotlib is the rendering default; record why ROOT rendering is needed if Python is unavailable or calculation integration makes ROOT appropriate. Figure styling does not authorize data production, hardware operations, or publication. Follow journal/collaboration overrides and inspect the actual rendered figure at its intended size.
