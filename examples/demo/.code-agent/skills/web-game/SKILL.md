---
name: web-game
description: Build a small browser game as a frontend mini project using HTML, CSS, and JavaScript.
---

# Web Game Mini Project

Use this skill when the user asks to create a small browser game, especially for a demo-friendly frontend project.

## Project Shape

Prefer a small folder with three files:

```text
game-name/
├─ index.html
├─ style.css
└─ script.js
```

Use plain HTML, CSS, and JavaScript. Do not depend on external network assets or package installs unless the user explicitly requests them.

## Implementation Guidance

- Make the game playable immediately by opening `index.html` in a browser.
- Keep HTML responsible for structure, CSS for layout/visuals/animation, and JavaScript for game state and interactions.
- Include clear game states: idle, running, ended, and restart.
- Add visible score, timer or moves, and a start/restart control when appropriate.
- Use simple, polished visuals that show well in a short demo: clear buttons, readable text, responsive layout, and lightweight animations.
- Prefer deterministic, easy-to-explain logic over complex game engines.
- Store small persistent values such as high score with `localStorage` when it makes the demo better.
- After writing files, run a simple verification command such as listing the created project directory.

## Whack-A-Mole Defaults

For a whack-a-mole game, use these defaults unless the user asks otherwise:

- A 3x3 hole grid.
- Random mole appearances.
- Click mole to add score; empty holes do not add score.
- 30 second round timer.
- Current score, high score, and start/restart button.
- Short pop or scale animation when the mole appears or is hit.

Finish with a concise summary of created files, how to open the game, and any verification command that was run.
