# midterm-2026-python
Midterm project for numerical methods in python 2026 fall - Grant Adamson

This is a cellular automata simulation using the states 0, 1, and 2 with adjustable dimensions, simulation length, and rules determined by an accompanying rules.json file.

The dimensions and number of rounds are freely adjustable in the json.
The starting seed is the initial grid to start the simulation, which must match the dimensions for the program to run successfully. 

The json file also contains the list of rules with a choice of rule type / specifications. 
There can be 6 rules, one for each state transition (0 to 1, 0 to 2, 1 to 0, 1 to 2, 2 to 0, 2 to 1). There are two rule types, 0 and 1

Rule type 0 changes the state of a cell based on specific values adjacent to the cell by direction, with -1 as a wildcard. 
The formatting for this rule is as follows: initial state, state if rule is met, rule type (0), left state, right state, up state, down state
If a rule is met, the cell will change to the highest value state that it can (if it meets both rules for becoming 1 and 2 it becomes a 2.)

Rule type 1 changes the state of a cell based on the amount of each value adjacent to the cell, with -1 being a wildcard (any amount of that state is fine).
The formatting for this rule is as follows: initial state, state if rule is met, rule type (1), number of adjacent 0's, number of adjacent 1's, number of adjacent 2's
If a rule is met, the cell will change to the highest value state that it can (if it meets both rules for becoming 1 and 2 it becomes a 2.)

Once the json is updated and in the same folder as the python file, simply run the python file and hit the start button on the plot.
It will run until the requested amount of rounds in the json, and can be paused/resumed at any point with the button. 
