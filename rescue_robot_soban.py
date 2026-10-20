
import tkinter as tk
import heapq
import random

CELL = 30
COLS = 22
ROWS = 16

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

START = (1, 1)
VICTIM = (20, 14)

BACKGROUND = "#172033"
GRID = "#364258"
WALL = "#7F4545"
ROBOT = "#20B9FF"
VICTIM_COLOR = "#FFD43B"
PATH_COLOR = "#3978FF"
GREEN = "#2ECC71"
WHITE = "#FFFFFF"

root = tk.Tk()
root.title("AI Search-and-Rescue Robot Simulator")
root.configure(bg=BACKGROUND)
root.resizable(False, False)

robot = START
walls = set()
path = []
steps = 0
animation_job = None
mission_complete = False

title = tk.Label(
    root, text="AI SEARCH & RESCUE ROBOT",
    font=("Arial", 17, "bold"),
    bg=BACKGROUND, fg=WHITE
)
title.pack(pady=8)

status = tk.Label(
    root, text="Ready for rescue mission",
    font=("Arial", 10),
    bg=BACKGROUND, fg=GREEN
)
status.pack()

stats = tk.Label(
    root, text="Steps: 0 | Obstacles: 0 | Path: 0",
    font=("Arial", 10),
    bg=BACKGROUND, fg=WHITE
)
stats.pack(pady=5)

canvas = tk.Canvas(
    root, width=WIDTH, height=HEIGHT,
    bg="#202A3D", highlightthickness=0
)
canvas.pack(padx=10, pady=10)


def create_map():
    global walls
    walls = set()

    random.seed(10)

    for _ in range(55):
        cell = (random.randint(0, COLS - 1),
                random.randint(0, ROWS - 1))

        if cell != START and cell != VICTIM:
            walls.add(cell)

    # Keep the start and victim areas clear.
    for x in range(0, 4):
        for y in range(0, 4):
            walls.discard((x, y))

    for x in range(COLS - 4, COLS):
        for y in range(ROWS - 4, ROWS):
            walls.discard((x, y))


def draw_map():
    canvas.delete("all")

    for x in range(COLS):
        for y in range(ROWS):
            x1 = x * CELL
            y1 = y * CELL

            color = "#202A3D"

            if (x, y) in walls:
                color = WALL

            canvas.create_rectangle(
                x1, y1, x1 + CELL, y1 + CELL,
                fill=color, outline=GRID
            )

    # Draw planned route.
    for x, y in path:
        canvas.create_rectangle(
            x * CELL + 7, y * CELL + 7,
            x * CELL + CELL - 7, y * CELL + CELL - 7,
            fill=PATH_COLOR, outline=""
        )

    # Draw victim.
    vx, vy = VICTIM
    canvas.create_oval(
        vx * CELL + 5, vy * CELL + 5,
        vx * CELL + CELL - 5, vy * CELL + CELL - 5,
        fill=VICTIM_COLOR, outline=WHITE, width=2
    )
    canvas.create_text(
        vx * CELL + CELL / 2,
        vy * CELL + CELL / 2,
        text="V", fill="#172033",
        font=("Arial", 10, "bold")
    )

    # Draw robot.
    rx, ry = robot
    canvas.create_oval(
        rx * CELL + 4, ry * CELL + 4,
        rx * CELL + CELL - 4, ry * CELL + CELL - 4,
        fill=ROBOT, outline=WHITE, width=2
    )
    canvas.create_text(
        rx * CELL + CELL / 2,
        ry * CELL + CELL / 2,
        text="R", fill="#172033",
        font=("Arial", 10, "bold")
    )

    stats.config(
        text=f"Steps: {steps} | Obstacles: {len(walls)} | Path: {len(path)}"
    )


def find_path():
    # A* pathfinding algorithm.
    frontier = [(0, START)]
    came_from = {START: None}
    cost = {START: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == VICTIM:
            break

        x, y = current

        for nxt in (
            (x + 1, y), (x - 1, y),
            (x, y + 1), (x, y - 1)
        ):
            nx, ny = nxt

            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                continue

            if nxt in walls:
                continue

            new_cost = cost[current] + 1

            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                priority = new_cost + abs(VICTIM[0] - nx) + abs(VICTIM[1] - ny)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    if VICTIM not in came_from:
        return []

    result = []
    current = VICTIM

    while current is not None:
        result.append(current)
        current = came_from[current]

    result.reverse()
    return result


def start_mission():
    global robot, path, steps, mission_complete, animation_job

    if animation_job is not None:
        root.after_cancel(animation_job)
        animation_job = None

    robot = START
    steps = 0
    mission_complete = False
    path = find_path()

    if not path:
        status.config(text="No path found! Reset the map.", fg="#FF7777")
        draw_map()
        return

    status.config(text="Robot searching for the victim...", fg=GREEN)
    draw_map()
    move_robot(1)


def move_robot(index):
    global robot, steps, animation_job, mission_complete

    if index >= len(path):
        mission_complete = True
        animation_job = None
        status.config(text="RESCUE COMPLETE! Victim reached.", fg=VICTIM_COLOR)
        draw_map()
        return

    robot = path[index]
    steps += 1
    draw_map()
    animation_job = root.after(150, lambda: move_robot(index + 1))


def reset_simulator():
    global robot, path, steps, animation_job, mission_complete

    if animation_job is not None:
        root.after_cancel(animation_job)
        animation_job = None

    robot = START
    path = []
    steps = 0
    mission_complete = False

    create_map()
    status.config(text="Ready for rescue mission", fg=GREEN)
    draw_map()


buttons = tk.Frame(root, bg=BACKGROUND)
buttons.pack(pady=8)

tk.Button(
    buttons, text="Start Rescue",
    command=start_mission,
    bg=GREEN, fg="#172033",
    font=("Arial", 11, "bold"),
    padx=12, pady=5
).pack(side="left", padx=5)

tk.Button(
    buttons, text="Reset Map",
    command=reset_simulator,
    bg="#DCE6F1", fg="#172033",
    font=("Arial", 11, "bold"),
    padx=12, pady=5
).pack(side="left", padx=5)

create_map()
draw_map()

root.mainloop()
