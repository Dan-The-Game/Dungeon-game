SHOOTER = "#"
ARROW_UP = "↑"
ARROW_DOWN = "↓"
ARROW_RIGHT = "→"
ARROW_LEFT = "←"
TILE_SIZE = 2  # Each tile is TILE_SIZE x TILE_SIZE block
import os
import random
import math
from dataclasses import dataclass


GRID_SIZE = 24  # Change this to set map size (nxn)
WALL = "■"
FLOOR = "."
EXIT = "E"
PLAYER = "@"
MONSTER = "M"
INVULN_MONSTER = "X"
HEALTH = "+"
SPIKE_DANGEROUS = "▲"
SPIKE_SAFE = "_"

class Spike:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.period = random.choice([2, 3, 4])  # How many turns per cycle
        self.offset = random.randint(0, self.period-1)  # Phase offset
        self.turn = 0
    def is_dangerous(self):
        # Dangerous for half the period, safe for the other half
        phase = (self.turn + self.offset) % self.period
        return phase < self.period // 2
    def advance(self):
        self.turn += 1

def place_spikes(grid: list[list[str]], count: int, forbidden: set[tuple[int, int]]):
    spikes = []
    for _ in range(count):
        r, c = random_floor_tile(grid, forbidden)
        spikes.append(Spike(r, c))
        forbidden.add((r, c))
    return spikes

DIRECTIONS = {
    "w": (-1, 0),
    "a": (0, -1),
    "s": (1, 0),
    "d": (0, 1),
}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


@dataclass
class Actor:
    row: int
    col: int
    hp: int
    power_up: str = None  # Holds current power-up


def clamp_move(row: int, col: int, grid: list[list[str]]) -> tuple[int, int]:
    max_row = len(grid) - 1
    max_col = len(grid[0]) - 1
    row = max(0, min(max_row, row))
    col = max(0, min(max_col, col))
    return row, col


def build_grid(
    width: int,
    height: int,
    floor_chance: float,
    walkers: int,
    walk_steps: int,
) -> list[list[str]]:
    start = (1, 1)
    end = (height - 2, width - 2)

    while True:
        grid = [[WALL for _ in range(width)] for _ in range(height)]

        row, col = start
        grid[row][col] = FLOOR
        for r in range(start[0] - 1, start[0] + 2):
            for c in range(start[1] - 1, start[1] + 2):
                if 0 < r < height - 1 and 0 < c < width - 1:
                    grid[r][c] = FLOOR

        while (row, col) != end:
            if random.random() < 0.5:
                row += 1 if row < end[0] else 0
                row -= 1 if row > end[0] else 0
            else:
                col += 1 if col < end[1] else 0
                col -= 1 if col > end[1] else 0
            grid[row][col] = FLOOR

        for r in range(1, height - 1):
            for c in range(1, width - 1):
                if grid[r][c] == WALL and random.random() < floor_chance:
                    grid[r][c] = FLOOR
        for _ in range(walkers):
            row, col = random.randint(1, height - 2), random.randint(1, width - 2)
            for _ in range(walk_steps):
                grid[row][col] = FLOOR
                dr, dc = random.choice(list(DIRECTIONS.values()))
                row = max(1, min(height - 2, row + dr))
                col = max(1, min(width - 2, col + dc))
        grid[end[0]][end[1]] = EXIT

        # Place SHOOTER tiles after map is generated, based on difficulty
        shooter_count = 0
        if hasattr(build_grid, 'difficulty'):
            diff = build_grid.difficulty
            if diff == 'e':
                shooter_count = 1 if random.random() < 0.15 else 0
            elif diff == 'm':
                shooter_count = 1
            elif diff == 'h':
                shooter_count = random.choice([2, 3])
        # Place shooters on random wall tiles (not on border)
        wall_tiles = [(r, c) for r in range(2, height-2) for c in range(2, width-2) if grid[r][c] == WALL]
        random.shuffle(wall_tiles)
        for i in range(min(shooter_count, len(wall_tiles))):
            r, c = wall_tiles[i]
            grid[r][c] = SHOOTER

        if is_reachable(grid, start, end):
            return grid


def is_reachable(
    grid: list[list[str]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> bool:
    queue: list[tuple[int, int]] = [start]
    seen = {start}
    while queue:
        row, col = queue.pop(0)
        if (row, col) == end:
            return True
        for dr, dc in DIRECTIONS.values():
            nr, nc = row + dr, col + dc
            if (nr, nc) in seen:
                continue
            if grid[nr][nc] in (WALL, SHOOTER):
                continue
            seen.add((nr, nc))
            queue.append((nr, nc))
    return False


def find_char(grid: list[list[str]], char: str) -> list[tuple[int, int]]:
    results: list[tuple[int, int]] = []
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == char:
                results.append((r, c))
    return results


def random_floor_tile(grid: list[list[str]], forbidden: set[tuple[int, int]]) -> tuple[int, int]:
    floors = [
        (r, c)
        for r in range(1, len(grid) - 1)
        for c in range(1, len(grid[0]) - 1)
        if grid[r][c] == FLOOR and (r, c) not in forbidden
    ]
    return random.choice(floors)


def spawn_monsters(
    grid: list[list[str]],
    count: int,
    forbidden: set[tuple[int, int]],
    invuln_count: int = 0,
) -> list[Actor]:
    monsters: list[Actor] = []
    # Spawn invulnerable monsters first (hp = -1)
    for _ in range(invuln_count):
        row, col = random_floor_tile(grid, forbidden)
        forbidden.add((row, col))
        monsters.append(Actor(row=row, col=col, hp=-1))
    # Spawn regular monsters
    for _ in range(count):
        row, col = random_floor_tile(grid, forbidden)
        forbidden.add((row, col))
        monsters.append(Actor(row=row, col=col, hp=1))
    return monsters


def render(grid: list[list[str]], player: Actor, monsters: list[Actor], spikes: list) -> str:
    temp = [row[:] for row in grid]
    for monster in monsters:
        if monster.hp > 0 or monster.hp == -1:
            if monster.hp == -1:
                temp[monster.row][monster.col] = INVULN_MONSTER
            else:
                temp[monster.row][monster.col] = MONSTER
    # Place spikes (dangerous or safe)
    for s in spikes:
        temp[s.row][s.col] = SPIKE_DANGEROUS if s.is_dangerous() else SPIKE_SAFE
    temp[player.row][player.col] = PLAYER

    # Color mapping
    def colorize(char):
        if char == PLAYER:
            return "\033[32m@\033[0m"
        if char == MONSTER:
            return "\033[31mM\033[0m"
        if char == INVULN_MONSTER:
            return "\033[31;1mX\033[0m"
        if char == HEALTH:
            return "\033[32m+\033[0m"
        if char == SPIKE_DANGEROUS:
            return "\033[90m▲\033[0m"  # Gray
        if char == SPIKE_SAFE:
            return "\033[37m_\033[0m"  # White underscore
        if char == SHOOTER:
            return "\033[37m#\033[0m"  # White shooter
        if char == ARROW_UP:
            return "\033[37m↑\033[0m"
        if char == ARROW_DOWN:
            return "\033[37m↓\033[0m"
        if char == ARROW_RIGHT:
            return "\033[37m→\033[0m"
        if char == ARROW_LEFT:
            return "\033[37m←\033[0m"
        if char == EXIT:
            return "\033[34mE\033[0m"
        if char == 'P':
            return "\033[34mP\033[0m"
        if char == '.':
            return "\033[30;1m.\033[0m"
        return char

    expanded_rows = []
    for row in temp:
        block_rows = [[] for _ in range(TILE_SIZE)]
        for cell in row:
            colored = colorize(cell)
            cell_block = (colored + ' ') * TILE_SIZE
            for i in range(TILE_SIZE):
                block_rows[i].append(cell_block)
        for block_row in block_rows:
            expanded_rows.append(block_row)

    return "\n".join("".join(cell for cell in tile_row) for tile_row in expanded_rows)

# Move try_move above main
def try_move(actor: Actor, dr: int, dc: int, grid: list[list[str]]) -> None:
    new_row, new_col = clamp_move(actor.row + dr, actor.col + dc, grid)
    if grid[new_row][new_col] == WALL or grid[new_row][new_col] == SHOOTER:
        return
    # Prevent monsters from moving onto each other
    for other in getattr(actor, 'monster_list', []):
        if other is not actor and (other.row, other.col) == (new_row, new_col):
            return
    actor.row, actor.col = new_row, new_col


def remove_dead(monsters: list[Actor]) -> list[Actor]:
    # Only remove monsters with hp == 0 (dead regular monsters). Invulnerable (hp < 0) are never removed.
    return [m for m in monsters if m.hp != 0]


def find_adjacent_monster(player: Actor, monsters: list[Actor]) -> Actor | None:
    for dr, dc in DIRECTIONS.values():
        target_row = player.row + dr
        target_col = player.col + dc
        for monster in monsters:
            if (monster.hp > 0 or monster.hp == -1) and (monster.row, monster.col) == (target_row, target_col):
                return monster
    return None



def place_health_pickups(grid: list[list[str]], count: int, forbidden: set[tuple[int, int]]):
    for _ in range(count):
        r, c = random_floor_tile(grid, forbidden)
        grid[r][c] = HEALTH
        forbidden.add((r, c))

def generate_room(player: Actor, room: int, difficulty: str) -> tuple[list[list[str]], tuple[int, int], list[Actor]]:
    # Pass difficulty to build_grid for shooter placement
    build_grid.difficulty = difficulty
    grid = build_grid(width=GRID_SIZE, height=GRID_SIZE, floor_chance=0.65, walkers=6, walk_steps=80)
    exit_pos = find_char(grid, EXIT)[0]
    player.row, player.col = 1, 1
    if difficulty == "e":
        monster_count = 3 + room
        health_count = 1 + (room // 2)
        invuln_count = 0
    elif difficulty == "m":
        monster_count = 5 + 2 * room
        health_count = 1
        invuln_count = 1 if random.random() < 0.10 else 0
    else:
        monster_count = 10 + 4 * room
        health_count = 1 if room == 1 else 0
        roll = random.random()
        if roll < 0.80:
            invuln_count = 1
        elif roll < 0.90:
            invuln_count = 2
        else:
            invuln_count = 0
    monsters = spawn_monsters(grid, count=monster_count, forbidden={(1, 1), exit_pos}, invuln_count=invuln_count)
    forbidden = {(1, 1), exit_pos}
    forbidden.update((m.row, m.col) for m in monsters)
    if health_count > 0:
        place_health_pickups(grid, health_count, forbidden)
    if difficulty == "m":
        spike_count = monster_count
    elif difficulty == "h":
        spike_count = int(monster_count * 1.5)
    else:
        spike_count = max(2, monster_count // 2)
    spikes = place_spikes(grid, spike_count, forbidden)
    powerup_count = 0
    if difficulty in ("e", "m"):
        powerup_count = 1
    elif difficulty == "h" and room < 10:
        if random.random() < 0.10:
            powerup_count = 1
    if powerup_count > 0:
        for _ in range(powerup_count):
            while True:
                r = random.randint(1, len(grid) - 2)
                c = random.randint(1, len(grid[0]) - 2)
                if (r, c) not in forbidden and grid[r][c] == FLOOR:
                    grid[r][c] = 'P'
                    forbidden.add((r, c))
                    break
    return grid, exit_pos, monsters, spikes


def main() -> None:
    global TILE_SIZE
    while True:
        tile_input = input("Enter tile size (integer >= 1): ").strip()
        if tile_input.isdigit() and int(tile_input) >= 1:
            TILE_SIZE = int(tile_input)
            break
        print("Invalid input. Please enter a positive integer.")

    print("Select difficulty: (E)asy, (M)edium, (H)ard")
    while True:
        diff = input("Enter difficulty (e/m/h): ").strip().lower()
        if diff in ("e", "m", "h"):
            break
        print("Invalid input. Please enter 'e', 'm', or 'h'.")
    if diff == "e":
        start_hp = 5
    elif diff == "m":
        start_hp = 3
    else:
        start_hp = 1

    allowed_moves = 3

    player = Actor(row=1, col=1, hp=start_hp)
    room = 1
    score = 0
    grid, exit_pos, monsters, spikes = generate_room(player, room, diff)

    while True:
        # Move arrows before rendering
        arrow_dirs = {
            ARROW_UP: (-1, 0),
            ARROW_DOWN: (1, 0),
            ARROW_LEFT: (0, -1),
            ARROW_RIGHT: (0, 1),
        }
        arrows_to_move = []
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] in arrow_dirs:
                    arrows_to_move.append((r, c, grid[r][c]))
        for r, c, arrow in arrows_to_move:
            dr, dc = arrow_dirs[arrow]
            nr, nc = r + dr, c + dc
            # Only move if in bounds and next tile is FLOOR
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == FLOOR:
                grid[nr][nc] = arrow
                grid[r][c] = FLOOR
            else:
                grid[r][c] = FLOOR

        clear_screen()
        print(render(grid, player, monsters, spikes))
        print()
        def show_status():
            powerup_display = player.power_up if player.power_up else "None"
            print(
                f"Room: {room}  HP: {player.hp}  Power-up: {powerup_display}  Score: {score}  Monsters: {len(monsters)}  Exit: {exit_pos}"
            )
        show_status()



        # Health pickup
        if grid[player.row][player.col] == HEALTH:
            player.hp += 2
            grid[player.row][player.col] = FLOOR

            # (Old spike check removed; now handled in move loop with spike objects)

        if (player.row, player.col) == exit_pos:
            room += 1
            grid, exit_pos, monsters, spikes = generate_room(player, room, diff)
            continue

        if player.hp <= 0:
            show_status()
            print(f"Final Score: {score}")
            print("=================")
            while True:
                choice = input("Press R to restart or Q to quit: ").strip().lower()
                if choice == "q":
                    return
                if choice == "r":
                    main()
                    return


        move_seq = input(f"Enter up to {allowed_moves} actions (WASD to move, F to attack, U to use power-up, Q to quit, R to restart): ").strip().lower()
        # Cheat code: 56840(powerupname)
        if move_seq.startswith("56840"):
            cheat_power = move_seq[5:]
            valid_powers = {"time_stop", "invulnerable/5hp", "explosive"}
            if cheat_power in valid_powers:
                player.power_up = cheat_power
                print(f"Cheat activated: {cheat_power} power-up granted!")
                continue
        if "q" in move_seq:
            print("Goodbye.")
            break
        if "r" in move_seq:
            main()
            return
        move_limit = allowed_moves
        i = 0
        powerup_used_this_turn = False
        while i < len(move_seq) and i < move_limit:
            move = move_seq[i]
            # Health pickup
            if grid[player.row][player.col] == HEALTH:
                player.hp += 2
                grid[player.row][player.col] = FLOOR
            # Spike logic: skip check on first move (i == 0)
            if i > 0:
                spike_here = next((s for s in spikes if s.row == player.row and s.col == player.col), None)
                if spike_here:
                    if spike_here.is_dangerous():
                        if getattr(player, 'invulnerable', False) or player.power_up == 'invulnerable' or player.power_up == 'invulnerable/5hp':
                            # Remove spike and invulnerability
                            spikes.remove(spike_here)
                            if getattr(player, 'invulnerable', False):
                                player.invulnerable = False
                            if player.power_up == 'invulnerable/5hp':
                                player.power_up = None
                        else:
                            show_status()
                            print(f"Final Score: {score}")
                            print("=================")
                            while True:
                                choice = input("Press R to restart or Q to quit: ").strip().lower()
                                if choice == "q":
                                    return
                                if choice == "r":
                                    main()
                                    return
                    else:
                        # Safe spike, nothing happens
                        pass
            # Power-up pickup (placeholder: 'P' tile)
            if grid[player.row][player.col] == 'P':
                if player.power_up is None:
                    # Randomly choose between time stop, invulnerable, and explosive
                    roll = random.random()
                    if roll < 1/3:
                        player.power_up = 'time_stop'
                    elif roll < 2/3:
                        player.power_up = 'invulnerable/5hp'
                    else:
                        player.power_up = 'explosive'
                grid[player.row][player.col] = FLOOR
            show_status()
            if (player.row, player.col) == exit_pos:
                room += 1
                grid, exit_pos, monsters = generate_room(player, room, diff)
                break
            if player.hp <= 0:
                print("You were defeated.")
                return
            if move == "u":
                if player.power_up and not powerup_used_this_turn:
                    if player.power_up == 'time_stop':
                        move_limit += 200
                    elif player.power_up == 'invulnerable/5hp':
                        player.invulnerable = True
                        player.hp += 5
                    elif player.power_up == 'explosive':
                        # Set all tiles in a radius-4 circle to FLOOR, kill monsters, give points
                        radius = 4
                        killed = 0
                        for rr in range(max(1, player.row-radius), min(len(grid)-1, player.row+radius+1)):
                            for cc in range(max(1, player.col-radius), min(len(grid[0])-1, player.col+radius+1)):
                                if math.sqrt((rr-player.row)**2 + (cc-player.col)**2) <= radius:
                                    if grid[rr][cc] != EXIT:
                                        grid[rr][cc] = FLOOR
                        # Kill monsters in radius
                        for m in monsters:
                            if m.hp > 0 and math.sqrt((m.row-player.row)**2 + (m.col-player.col)**2) <= radius:
                                m.hp = 0
                                killed += 1
                        score += killed
                    player.power_up = None
                    powerup_used_this_turn = True
                    show_status()
                i += 1
                continue
            if move == "f":
                target = find_adjacent_monster(player, monsters)
                if target is not None:
                    if target.hp != -1:
                        target.hp -= 1
                        if target.hp == 0:
                            score += 1
                    player.predicted_attack = False
                else:
                    # Set prediction flag if no monster is adjacent
                    player.predicted_attack = True
                monsters = remove_dead(monsters)
                i += 1
                continue
            if move in DIRECTIONS:
                dr, dc = DIRECTIONS[move]
                try_move(player, dr, dc, grid)
                i += 1
                continue
            # Invalid input is ignored
            i += 1
        for monster in monsters:
            monster.is_monster = True
            monster.monster_list = monsters
            for _ in range(2):  # Up to 2 moves per turn
                # If already adjacent to player, stop moving
                if abs(monster.row - player.row) + abs(monster.col - player.col) == 1:
                    break
                # 80% chance to move toward player, 20% random
                if random.random() < 0.8:
                    dr = 0
                    dc = 0
                    if player.row > monster.row:
                        dr = 1
                    elif player.row < monster.row:
                        dr = -1
                    if player.col > monster.col:
                        dc = 1
                    elif player.col < monster.col:
                        dc = -1
                    # Prefer vertical or horizontal randomly if both are possible
                    if dr != 0 and dc != 0:
                        if random.random() < 0.5:
                            dc = 0
                        else:
                            dr = 0
                else:
                    dr, dc = random.choice(list(DIRECTIONS.values()))
                # Predict new position
                new_row, new_col = clamp_move(monster.row + dr, monster.col + dc, grid)
                spike_there = next((s for s in spikes if s.row == new_row and s.col == new_col), None)
                if spike_there and spike_there.is_dangerous():
                    monster.hp = 0
                    break
                try_move(monster, dr, dc, grid)
            del monster.is_monster
            del monster.monster_list
        # Advance all spike timers
        for s in spikes:
            s.advance()



        # Prediction attack: kill any monster that moves adjacent if player.predicted_attack is set

        monsters_to_kill = []
        if getattr(player, 'predicted_attack', False):
            for monster in monsters:
                if (monster.hp > 0 or monster.hp == -1) and abs(monster.row - player.row) + abs(monster.col - player.col) == 1:
                    if monster.hp != -1:
                        monsters_to_kill.append(monster)
            for monster in monsters_to_kill:
                if random.random() < 0.8:
                    monster.hp = 0
                    score += 1
            player.predicted_attack = False

        for monster in monsters:
            if monster.row == player.row and monster.col == player.col:
                if monster.hp != -1:
                    monster.hp = 0
                    score += 1
                # Auto-activate invulnerable if present
                if getattr(player, 'invulnerable', False):
                    pass
                elif player.power_up == 'invulnerable':
                    player.power_up = None
                    player.invulnerable = True
                else:
                    player.hp -= 1

        for monster in monsters:
            if monster.hp == 0:
                continue
            if abs(monster.row - player.row) + abs(monster.col - player.col) == 1:
                # Auto-activate invulnerable if present
                if getattr(player, 'invulnerable', False):
                    pass
                elif player.power_up == 'invulnerable':
                    player.power_up = None
                    player.invulnerable = True
                else:
                    player.hp -= 1
        # Reset invulnerable at end of turn
        if hasattr(player, 'invulnerable'):
            player.invulnerable = False

        monsters = remove_dead(monsters)


if __name__ == "__main__":
    main()
