import json
from pathlib import Path

import matplotlib.pyplot as plt 
from matplotlib.colors import ListedColormap # for the 3 states
from matplotlib.widgets import Button # for the ability to pause


RULES_PATH = Path(__file__).with_name("rules.json") # reads rules.json for the initialization and rules
with RULES_PATH.open(encoding="utf-8") as rules_file:
    rules = json.load(rules_file)


def create_grid(rows, cols): # creates a 2d list to represent the grid of cells given dimensions
    return [[0 for _ in range(cols)] for _ in range(rows)]


dimensions = rules["dimensions"]
rows = dimensions["rows"]
cols = dimensions["columns"]
round_limit = rules["rounds"]
seed = rules["seed"]

if not isinstance(round_limit, int) or isinstance(round_limit, bool) or round_limit < 0: # Initialization error handling for invalid json files
    raise ValueError("The configured number of rounds must be a non-negative integer.")
if len(seed) != rows or any(len(seed_row) != cols for seed_row in seed):
    raise ValueError("The seed dimensions must match the configured rows and columns.")
if any(state not in (0, 1, 2) for seed_row in seed for state in seed_row):
    raise ValueError("Seed cells must have a state of 0, 1, or 2.")

state_rules = rules["rules"] 
for rule in state_rules: # Rule error handling for invalid json files
    if len(rule) < 3 or rule[0] not in (0, 1, 2) or rule[1] not in (0, 1, 2): 
        raise ValueError(f"Invalid rule header: {rule}")
    if rule[2] == 0:
        if len(rule) != 7 or any(value not in (-1, 0, 1, 2) for value in rule[3:]):
            raise ValueError(f"Invalid directional rule: {rule}")
    elif rule[2] == 1:
        if len(rule) != 6 or any(value < -1 or value > 4 for value in rule[3:]):
            raise ValueError(f"Invalid neighbor-count rule: {rule}")
    else:
        raise ValueError(f"Unknown rule type: {rule[2]}")

# It creates the grid with 2 extra rows and columns, one on each side of the board. 
# This is so that they can be initialized to 0 and never changed, to ease implementation of the edge/corner cells as anything not on the board is treated as 0.
grid = create_grid(rows + 2, cols + 2)
for row_index, seed_row in enumerate(seed, start=1): # initialize the grid to the seed from the json
    grid[row_index][1:cols + 1] = seed_row

# print("Initial seed:") # used for testing before the plot was done, to see the grid in the terminal un-comment these 2 lines and the 2 others below that say used for testing
# print(*grid, sep="\n")

cmap = ListedColormap(["white", "gray", "black"]) # set colors and create the visual grid on the plot, labeling it in the process
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.18)
image = ax.imshow(
    [row[1:cols + 1] for row in grid[1:rows + 1]],
    cmap=cmap,
    vmin=0,
    vmax=2,
    interpolation="nearest",
)
ax.set_xticks([index - 0.5 for index in range(cols + 1)], minor=True)
ax.set_yticks([index - 0.5 for index in range(rows + 1)], minor=True)
ax.grid(which="minor", color="lightgray", linewidth=0.8)
ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
ax.set_aspect("equal")
ax.set_title("Initial seed (Round 0)")

button_ax = fig.add_axes([0.4, 0.04, 0.2, 0.08]) # button for starting and pausing the simulation
start_pause_button = Button(button_ax, "Start" if round_limit else "Finished") # after the simulation is finished the button changes
simulation_state = {"grid": grid, "round": 0, "running": False}
simulation_timer = fig.canvas.new_timer(interval=1000) # used a 1 second timer between rounds


def advance_simulation(): # does a round of simulation with the rules from the json
    if simulation_state["round"] >= round_limit: # ends after given amount of rounds
        return True

    current_grid = simulation_state["grid"] 
    next_grid = create_grid(rows + 2, cols + 2) # makes a new grid for the next round

    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            current_state = current_grid[row][col]
            neighbors = ( # gets the neighbors states for that type of rule
                current_grid[row][col - 1], 
                current_grid[row][col + 1],
                current_grid[row - 1][col],
                current_grid[row + 1][col],
            )
            neighbor_counts = tuple(neighbors.count(state) for state in (0, 1, 2)) # gets the quantity of each neighbor state for that type of rule
            matching_next_states = []

            for rule in state_rules: # The rules prioritize whatever rule is met that would result in a higher number state, for example if the rules
                                     # are that a 0 becomes 1 with one neighboring 1 and 0 becomes 2 with one neighboring 2, a 0 between a 1 and 2 will become a 2.
                                     # The program loops through each applicable rule for each cell in the working grid, ignoring the filler 0 ring.
                                     # Because of the 0 ring, I can use consistant rules for every cell without having to add edge cases for edges/corners
                if rule[0] != current_state:
                    continue

                if rule[2] == 0:
                    matches = all(
                        required == -1 or required == actual
                        for required, actual in zip(rule[3:], neighbors)
                    )
                else:
                    matches = all(
                        required == -1 or neighbor_counts[state] >= required
                        for state, required in enumerate(rule[3:])
                    )

                if matches:
                    matching_next_states.append(rule[1])

            next_grid[row][col] = ( 
                max(matching_next_states) if matching_next_states else current_state
            )

    simulation_state["grid"] = next_grid # updates the grid and round 
    simulation_state["round"] += 1 
    round_number = simulation_state["round"] 
    # print(f"Round {round_number}:") # used these two lines to test before adding the plot
    # print(*next_grid, sep="\n")
    image.set_data([row[1:cols + 1] for row in next_grid[1:rows + 1]])
    ax.set_title(f"Round {round_number}")
    fig.canvas.draw_idle()

    if round_number == round_limit: # stop when enough rounds are done
        simulation_state["running"] = False
        start_pause_button.label.set_text("Finished")
        simulation_timer.stop()
    return True


def toggle_simulation(_event): # start and pause functionality
    del _event
    if simulation_state["round"] >= round_limit:
        return

    if simulation_state["running"]:
        simulation_state["running"] = False
        simulation_timer.stop()
        start_pause_button.label.set_text("Start")
    else:
        simulation_state["running"] = True
        simulation_timer.start()
        start_pause_button.label.set_text("Pause")


simulation_timer.add_callback(advance_simulation)
start_pause_button.on_clicked(toggle_simulation)
plt.show()
