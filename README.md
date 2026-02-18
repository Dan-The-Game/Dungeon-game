# ASCII Dungeon Game

A feature-rich ASCII art, turn-based dungeon crawler in Python.

## How to Run

From the project root:

```
python src/main.py
```

## Controls

- `W`, `A`, `S`, `D`: Move up, left, down, right
- `F`: Attack adjacent monster
- `E` + direction (`W`, `A`, `S`, `D`): Shoot an arrow in that direction (e.g., `EW` = shoot up)
- `U`: Use power-up (if you have one)
- `Q`: Quit the game
- `R`: Restart the game

You can enter up to 3 actions per turn (more if you chain monster kills with combos).

## Game Features

- **Procedurally generated dungeons** with increasing difficulty
- **Multiple tile types**:
	- `■`: Wall (impassable)
	- `.`: Floor (walkable)
	- `E`: Exit (advance to next room)
	- `@`: Player
	- `M`: Monster (1 HP)
	- `X`: Invulnerable Monster (cannot be killed by normal attacks)
	- `+`: Health pickup (+2 HP, also +2 ammo on Medium/Hard)
	- `P`: Power-up pickup (random effect)
	- `▲`: Dangerous spike trap (damages/kills if stepped on when active)
	- `_`: Safe spike trap (inactive)
	- `#`: Shooter tile (spawns arrows in 4 directions on a timer)
	- `→`: Arrows

- **Monsters**:
	- Move up to 2 times per turn, try to chase the player
	- Standing next to a monster at the end of a turn causes damage
	- Invulnerable monsters (`X`) cannot be killed by normal attacks

- **Spike Traps**:
	- Alternate between dangerous (`▲`) and safe (`_`)
	- Stepping on a dangerous spike kills the player unless invulnerable

- **Shooter Tiles**:
	- Appear as `#`, act as walls
	- Periodically fire arrows (`→`) in all 4 directions if the adjacent tile is floor
	- Each shooter has its own timer (2-5 turns)

- **Arrows**:
	- Move one tile per turn in their direction
	- Kill monsters or player instantly on contact or if paths cross
	- Player can shoot arrows using `E` + direction (costs 1 ammo, unless ammo is infinite)

- **Health and Power-ups**:
	- `+`: Grants +2 HP (and +2 ammo on Medium/Hard)
	- `P`: Grants a random power-up:
	- `time_stop`: Take 200 actions in one turn
	- `invulnerable/5hp`: Become invulnerable for next damage or gain +5 HP if used
	- `explosive`: Destroy a large area and kill monsters in a radius

- **Ammo System**:
	- Displayed next to HP
	- On Easy: infinite ammo (shows as "infinite")
	- On Medium: start with 10 ammo
	- On Hard: start with 5 ammo
	- Ammo only decreases if a shot is successful (arrow placed)

- **Combo System**:
	- Each monster killed in a turn grants +2 extra actions immediately in that turn (chain combos for huge turns!)

- **Cheat Codes**:
	- Enter `56840` followed by a power-up name (e.g., `56840time_stop`) or room number to instantly gain that power-up or go to that room -- used mostly for debugging

## Difficulty

- **Easy**: 5 HP, infinite ammo, more health pickups, fewer shooters
- **Medium**: 3 HP, 10 ammo, moderate health, more shooters and spikes
- **Hard**: 1 HP, 5 ammo, few health pickups, many shooters and spikes

## Tips

- Plan your moves ahead—combos let you chain many actions if you kill monsters in sequence
- Use arrows and power-ups strategically to clear tough rooms
- Watch out for shooters and spike traps!

## Trap Rooms & Progressive Difficulty

- Every 5th room is a trap room with no monsters, but many spikes and shooters.
- Trap rooms start with high spike and shooter counts, scaling up as you progress (room number increases).
- Trap room difficulty and spike/shooter counts are higher in harder difficulties.