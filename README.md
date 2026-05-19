# Meteor Blast

A pixel art space shooter built in Python using pygame-ce.

Survive an endless meteor storm, shoot down meteors for bonus score, and collect power-ups to stay alive. Difficulty escalates through levels as meteor speed and spawn rate increase. Compete for a place on the local high score leaderboard.

---

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move ship |
| Space | Fire laser |
| ESC | Pause / unpause |
| R | Restart (game over screen) |

---

## Power-ups

Power-ups drop randomly from destroyed meteors.

| Power-up | Effect |
|----------|--------|
| Shield | Absorbs one meteor hit |
| Nuke | Destroys all meteors on screen |
| Fast Fire | Reduces laser cooldown for 10 seconds |

---

## Requirements

- Python 3.10+
- pygame-ce

---

## Setup

```bash
git clone https://github.com/JimmiWazEre/meteor_blast.git
cd meteor_blast
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, replace the `source` line with:

```bash
.venv\Scripts\activate
```

---

## Running the game

```bash
python main.py
```

Or if installed as a system command:

```bash
meteorblast
```

---

## Project structure

```
meteor_blast/
├── main.py
├── requirements.txt
├── scores.json
├── images/
│   ├── player.png
│   ├── meteor.png
│   ├── laser.png
│   ├── star.png
│   ├── splash.png
│   ├── shield.png
│   ├── shield_powerup.png
│   ├── nuke_powerup.png
│   ├── laser_powerup.png
│   ├── PressStart2P-Regular.ttf
│   └── explosion/
│       └── 0-16.png
└── audio/
    ├── laser.wav
    ├── explosion.wav
    ├── damage.ogg
    └── game_music.wav
```

---

## Built with

- [pygame-ce](https://pyga.me/) — community edition of pygame
- [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) — pixel art font by CodeMan38

---

## Acknowledgements

Based on the [Space Shooter tutorial](https://youtu.be/8OMghdHP-zs) by [Clear Code](https://www.youtube.com/@ClearCode) on YouTube. Meteor Blast is a heavily modified and extended version of that project, used as the foundation for learning Python and pygame through hands-on development.

All audio assets (sound effects and music) are sourced from Clear Code's tutorial project.

---

## About

Built as a learning project to develop Python and pygame skills through hands-on game development.