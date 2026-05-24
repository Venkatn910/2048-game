"""
2048 Game Logic
Core engine: grid management, moves, merging, scoring, win/loss detection.
"""

import random
import copy


GRID_SIZE = 4


def new_grid():
    """Return a fresh 4x4 grid of zeros."""
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


def empty_cells(grid):
    """Return list of (row, col) tuples for all empty cells."""
    return [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]


def add_random_tile(grid):
    """
    Place a 2 (90%) or 4 (10%) in a random empty cell.
    Returns True if a tile was placed, False if the grid is full.
    """
    cells = empty_cells(grid)
    if not cells:
        return False
    r, c = random.choice(cells)
    grid[r][c] = 4 if random.random() < 0.1 else 2
    return True


def compress_row(row):
    """Slide all non-zero values to the left, preserving order."""
    return [v for v in row if v != 0]


def merge_row(row):
    """
    Merge equal adjacent tiles in a left-compressed row.
    Returns (new_row, score_gained).
    """
    score = 0
    i = 0
    merged = []
    while i < len(row):
        if i + 1 < len(row) and row[i] == row[i + 1]:
            val = row[i] * 2
            merged.append(val)
            score += val
            i += 2
        else:
            merged.append(row[i])
            i += 1
    return merged, score


def slide_row_left(row):
    """Full slide-left on one row: compress → merge → pad. Returns (row, score)."""
    compressed = compress_row(row)
    merged, score = merge_row(compressed)
    padded = merged + [0] * (GRID_SIZE - len(merged))
    return padded, score


def transpose(grid):
    return [list(row) for row in zip(*grid)]


def reverse_rows(grid):
    return [row[::-1] for row in grid]


def move_left(grid):
    new_grid = []
    total_score = 0
    for row in grid:
        new_row, score = slide_row_left(row)
        new_grid.append(new_row)
        total_score += score
    return new_grid, total_score


def move_right(grid):
    reversed_grid = reverse_rows(grid)
    moved, score = move_left(reversed_grid)
    return reverse_rows(moved), score


def move_up(grid):
    transposed = transpose(grid)
    moved, score = move_left(transposed)
    return transpose(moved), score


def move_down(grid):
    transposed = transpose(grid)
    moved, score = move_right(transposed)
    return transpose(moved), score


MOVES = {
    'left':  move_left,
    'right': move_right,
    'up':    move_up,
    'down':  move_down,
}


def apply_move(grid, direction):
    """
    Apply a move to the grid.
    Returns (new_grid, score_gained, moved) where moved=True if anything changed.
    """
    fn = MOVES[direction]
    new, score = fn(grid)
    moved = new != grid
    return new, score, moved


def has_won(grid):
    """True if any cell contains 2048."""
    return any(grid[r][c] == 2048 for r in range(GRID_SIZE) for c in range(GRID_SIZE))


def has_moves(grid):
    """True if at least one valid move remains."""
    if empty_cells(grid):
        return True
    for direction in MOVES:
        new, _ = MOVES[direction](grid)
        if new != grid:
            return True
    return False


def is_game_over(grid):
    """True when the player has no moves left."""
    return not has_moves(grid)


def new_game():
    """Initialise a fresh game state dict."""
    grid = new_grid()
    add_random_tile(grid)
    add_random_tile(grid)
    return {
        'grid': grid,
        'score': 0,
        'best': 0,
        'won': False,
        'over': False,
        'keep_playing': False,   # set True when player continues after winning
    }


def step(state, direction):
    """
    Advance the game by one move.
    Mutates *state* in-place and returns it.
    """
    if state['over']:
        return state
    if state['won'] and not state['keep_playing']:
        return state

    grid, score_gained, moved = apply_move(state['grid'], direction)

    if not moved:
        return state

    state['grid'] = grid
    state['score'] += score_gained
    if state['score'] > state['best']:
        state['best'] = state['score']

    if not state['won'] and has_won(grid):
        state['won'] = True

    add_random_tile(state['grid'])

    if is_game_over(state['grid']):
        state['over'] = True

    return state
