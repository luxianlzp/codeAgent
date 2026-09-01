# Project Memory

- This workspace is used to demonstrate Code Agent building a small frontend game project.
- Prefer plain HTML, CSS, and JavaScript without external network dependencies.
- For browser games, create a small folder with index.html, style.css, and script.js.
- Prefer write_file with nested paths to create project files; avoid Unix-only commands such as mkdir -p on Windows.
- Keep the game playable by opening index.html directly in a browser.
- Use clear UI states such as idle, running, ended, and restart.
- Include visible score, timer, high score, and simple animations when useful.
- After generating files, run a simple verification command such as listing the project directory.
