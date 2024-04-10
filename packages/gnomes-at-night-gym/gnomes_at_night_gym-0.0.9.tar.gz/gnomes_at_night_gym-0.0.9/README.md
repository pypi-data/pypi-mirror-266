# Gnomes at Night Gym Environment

This repo contains the custom Gym environment for the game of Gnomes at Night. Designed to test reinforcement learning algorithms on a cooperative task in imperfect-information environments.


## Installation

To install the environment locally, use the following command:
```sh
git clone https://github.com/vivianchen98/gnomes-at-night-gym.git
cd gnomes-at-night-gym
python -m venv .env
source .env/bin/activate
pip install -e .
```

To install from PyPI, use the following command:
```sh
pip install gnomes-at-night-gym
```

## Usage

To get started with the Gnomes at Night Gym Environment, simply import it into your project and instantiate it:

```python
import gymnasium as gym
import gnomes_at_night_gym

env = gym.make("gnomes_at_night_gym:Board9-v0-multistep", board_seed='A', round=1, render_mode="rgb_array")
```
When initializing the Gnomes at Night Gym Environment, you can customize its behavior using the following parameters:
| Parameter    | Options                           |
|--------------|-----------------------------------|
| `board_seed` | `'A'`, `'B'`, `'C'`, `'D'`         |
| `round`      | `1`, `2`, `3`, `4`, `5`            |
| `render_mode`| `'human'`, `'rgb_array'`, `'rgb_array_list'` |

## Scripts

To **play** in the environment with keyboard inputs, run
```sh
python play.py --board_seed A --round 1
```
which allows movements via the `arrow` keys, stay put with `/` key, and switch turn with the `space` key.

To **record** the video of gameplay (with dummay `horizon`-length random agents), run
```sh
python monitor.py --board_seed A --round 1 --horizon 5 --output_dir 'videos'
```
will save the videos of gameplay that terminates within 300 total steps to the `output_dir` path.