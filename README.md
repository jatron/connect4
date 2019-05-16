<p align="center">
  <h1 align="center"> Connect Four </h1>
</p>

<p align="center">
  <b>Play connect four in the comfort</b> of your <i>terminal</i>!
</p>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Description](#description)
- [Requirements](#requirements)
- [Environment Configuration](#environment-configuration)
- [Usage](#usage)
- [Advanced Usage](#advanced-usage)
- [Additional Info](#additional-info)

---

## Description

Connect Four is a two-player connection game in which the players first choose a color and then take turns dropping one colored disc from the top into a seven-column, six-row vertically suspended grid. The pieces fall straight down, occupying the lowest available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs.
<br>

## Requirements

- Git
- Python 3
- Python `pip`
- Python module `colorama`
- Python module `docopt`
- Python module `gevent`
- Python module `loguru`
- Python module `numpy`
- Python module `prompt_toolkit`
- Python module `pyinstaller`
- Python module `tinydb`
- Python module `ujson`
<br>

## Environment Configuration

  ```bash
  git clone https://github.com/BoulaZa5/connect4.git
  cd connect4
  bash ./scripts/configure_connect4.sh
  ```
<br>

## Usage

1. Try two players in the same terminal

  > If you're playing as HUMANPLAYER, you can save the game or forfeit it every time you are asked for input
  >> Test it by writing `save savefile.c4`, `forfeit`, `end`, or `exit`

  ```bash
  python3 ./src/play.py HUMANPLAYER vs HUMANPLAYER
  ```

2. Try to load a saved game

  ```bash
  python3 ./src/play.py load savefile.c4
  ```

3. Try two players on the same network(or pc)

  > The instance with firstplayer=NETWORKPLAYER must be opened first.
  >> [peterrateb/Intelligent-connect-4](https://github.com/peterrateb/Intelligent-connect-4) uses the same networking protocol, so you can even play across clients.

  ```bash
  python3 ./src/play.py NETWORKPLAYER vs HUMANPLAYER --local-port=3501 --peer-address=127.0.0.1 --peer-port=3500
  ```
  ```bash
  python3 ./src/play.py HUMANPLAYER vs NETWORKPLAYER --local-port=3500 --peer-address=127.0.0.1 --peer-port=3501
  ```

4. Try to beat the hard AI

  ```bash
  python3 ./src/play.py HUMANPLAYER vs MINIMAXPLAYER --p2-difficulty=HARD
  ```
<br>

## Advanced Usage

```
Play connect four in the comfort of your terminal.

Player types are HUMANPLAYER, NETWORKPLAYER, and MINIMAXPLAYER.
Player difficulties are HARD, NORMAL, and EASY.
Ports and address are only used in network games.
Player difficulties are only used in case of using an AI.
When playing as a HUMANPLAYER, you can input `save <savefile>` to save the game and exit your client or `exit` to exit your client.

Usage:
  play.py [--debugging] [--verbose] load <savefile>
  play.py [--time-limit=TIMEINSECONDS]
          [--local-port=PORT] [--peer-address=ADDRESS] [--peer-port=PORT]
          [--debugging] [--verbose]
          [--p1-difficulty=DIFFICULTY] [--p2-difficulty=DIFFICULTY]
          <playertype> vs <playertype>
  play.py (-h | --help)

Options:
  -h --help                   Show this screen.
  --time-limit=TIMEINSECONDS  Maximum allowed time per player move in seconds [default: 180].
  --local-port=PORT           Local port [default: 3500].
  --peer-address=ADDRESS      Peer player's IP address.
  --peer-port=PORT            Peer player's port [default: 3500].
  --p1-difficulty=DIFFICULTY  First player difficulty [default: NORMAL].
  --p2-difficulty=DIFFICULTY  Second player difficulty [default: NORMAL].
  -d --debugging              Save debugging log.
  -v --verbose                Turn on verbose output mode.
```
<br>

## Additional Info

Used util function is:
![](http://latex.codecogs.com/svg.latex?1024^2*Streak_4+1024*Streak_3+Streak_2-1024^3*OpponentStreak_4)
<br>

<br>
