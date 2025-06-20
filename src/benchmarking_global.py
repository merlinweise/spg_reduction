# Imports
import random
import os

from src.ssg_to_smg import check_target_reachability
from stochasticparitygame import SpgVertex, SpgTransition, StochasticParityGame, read_spg_from_file
from error_handling import print_error
from spg_to_ssg_reduction import spg_to_ssg
from ssg_to_smg import ssg_to_smgspec, save_smg_file
from settings import GLOBAL_DEBUG


def create_chain_spg(length: int, min_prob: float) -> StochasticParityGame:
    vertices = {}
    for i in range(length + 1):
        vertices["v" + str(i)] = SpgVertex(name="v" + str(i), is_eve=True, priority=0)
    transitions = {}
    for i in range(length):
        transitions[(vertices["v" + str(i)], "next")] = SpgTransition(start_vertex=vertices["v" + str(i)], end_vertices={(min_prob, vertices["v" + str(i + 1)]), (1 - min_prob, vertices["v" + "0"])}, action="next")
    transitions[(vertices["v" + str(length)], "end")] = SpgTransition(start_vertex=vertices["v" + str(length)], end_vertices={(1.0, vertices["v" + str(length)])}, action="end")
    initial_vertex = vertices["v0"]
    return StochasticParityGame(vertices=vertices, transitions=transitions, init_vertex=initial_vertex)


def create_mutex_spg() -> StochasticParityGame:
    vertices = {
        "start":    SpgVertex(name="start",     is_eve=True,    priority=0),
        "(N,N,0)":  SpgVertex(name="(N,N,0)",   is_eve=True,    priority=3),
        "(N,N,1)":  SpgVertex(name="(N,N,1)",   is_eve=False,   priority=3),
        "(N,T,0)":  SpgVertex(name="(N,T,0)",   is_eve=True,    priority=3),
        "(N,T,1)":  SpgVertex(name="(N,T,1)",   is_eve=False,   priority=3),
        "(N,C,0)":  SpgVertex(name="(N,C,0)",   is_eve=True,    priority=3),
        "(N,C,1)":  SpgVertex(name="(N,C,1)",   is_eve=False,   priority=3),
        "(T,N,0)":  SpgVertex(name="(T,N,0)",   is_eve=True,    priority=3),
        "(T,N,1)":  SpgVertex(name="(T,N,1)",   is_eve=False,   priority=3),
        "(T,T,0)":  SpgVertex(name="(T,T,0)",   is_eve=True,    priority=3),
        "(T,T,1)":  SpgVertex(name="(T,T,1)",   is_eve=False,   priority=3),
        "(T,C,0)":  SpgVertex(name="(T,C,0)",   is_eve=True,    priority=3),
        "(T,C,1)":  SpgVertex(name="(T,C,1)",   is_eve=False,   priority=3),
        "(C,N,0)":  SpgVertex(name="(C,N,0)",   is_eve=True,    priority=2),
        "(C,N,1)":  SpgVertex(name="(C,N,1)",   is_eve=False,   priority=2),
        "(C,T,0)":  SpgVertex(name="(C,T,0)",   is_eve=True,    priority=2),
        "(C,T,1)":  SpgVertex(name="(C,T,1)",   is_eve=False,   priority=2),
        "(C,C,0)":  SpgVertex(name="(C,C,0)",   is_eve=True,    priority=1),
        "(C,C,1)":  SpgVertex(name="(C,C,1)",   is_eve=False,   priority=1)
    }
    transitions = {
        (vertices["start"], "start"):   SpgTransition(start_vertex=vertices["start"], end_vertices={(0.5, vertices["(N,N,0)"]), (0.5, vertices["(N,N,1)"])}, action="enter"),
        (vertices["(N,N,0)"], "stay"):  SpgTransition(start_vertex=vertices["(N,N,0)"], end_vertices={(0.5, vertices["(N,N,0)"]), (0.5, vertices["(N,N,1)"])}, action="stay"),
        (vertices["(N,N,0)"], "try"):   SpgTransition(start_vertex=vertices["(N,N,0)"], end_vertices={(0.5, vertices["(T,N,0)"]), (0.5, vertices["(T,N,1)"])}, action="try"),
        (vertices["(N,N,1)"], "stay"):  SpgTransition(start_vertex=vertices["(N,N,1)"], end_vertices={(0.5, vertices["(N,N,0)"]), (0.5, vertices["(N,N,1)"])}, action="try"),
        (vertices["(N,N,1)"], "try"):   SpgTransition(start_vertex=vertices["(N,N,1)"], end_vertices={(0.5, vertices["(N,T,0)"]), (0.5, vertices["(N,T,1)"])}, action="try"),
        (vertices["(N,T,0)"], "stay"):  SpgTransition(start_vertex=vertices["(N,T,0)"], end_vertices={(0.5, vertices["(N,T,0)"]), (0.5, vertices["(N,T,1)"])}, action="try"),
        (vertices["(N,T,0)"], "try"):   SpgTransition(start_vertex=vertices["(N,T,0)"], end_vertices={(0.5, vertices["(T,T,0)"]), (0.5, vertices["(T,T,1)"])}, action="try"),
        (vertices["(N,T,1)"], "enter"): SpgTransition(start_vertex=vertices["(N,T,1)"], end_vertices={(0.5, vertices["(N,C,0)"]), (0.5, vertices["(N,C,1)"])}, action="try"),
        (vertices["(N,C,0)"], "stay"):  SpgTransition(start_vertex=vertices["(N,C,0)"], end_vertices={(0.5, vertices["(N,C,0)"]), (0.5, vertices["(N,C,1)"])}, action="try"),
        (vertices["(N,C,0)"], "try"):   SpgTransition(start_vertex=vertices["(N,C,0)"], end_vertices={(0.5, vertices["(T,C,0)"]), (0.5, vertices["(T,C,1)"])}, action="try"),
        (vertices["(N,C,1)"], "exit"):  SpgTransition(start_vertex=vertices["(N,C,0)"], end_vertices={(0.5, vertices["(N,N,0)"]), (0.5, vertices["(N,N,1)"])}, action="try"),
        (vertices["(T,N,0)"], "enter"): SpgTransition(start_vertex=vertices["(T,N,0)"], end_vertices={(0.5, vertices["(C,N,0)"]), (0.5, vertices["(C,N,1)"])}, action="try"),
        (vertices["(T,N,1)"], "stay"):  SpgTransition(start_vertex=vertices["(T,N,1)"], end_vertices={(0.5, vertices["(T,N,0)"]), (0.5, vertices["(T,N,1)"])}, action="try"),
        (vertices["(T,N,1)"], "try"):   SpgTransition(start_vertex=vertices["(T,N,1)"], end_vertices={(0.5, vertices["(T,T,0)"]), (0.5, vertices["(T,T,1)"])}, action="try"),
        (vertices["(T,T,0)"], "enter"): SpgTransition(start_vertex=vertices["(T,T,0)"], end_vertices={(0.5, vertices["(C,T,0)"]), (0.5, vertices["(C,T,1)"])}, action="try"),
        (vertices["(T,T,1)"], "enter"): SpgTransition(start_vertex=vertices["(T,T,1)"], end_vertices={(0.5, vertices["(T,C,0)"]), (0.5, vertices["(T,C,1)"])}, action="try"),
        (vertices["(T,C,0)"], "enter"): SpgTransition(start_vertex=vertices["(T,C,0)"], end_vertices={(0.5, vertices["(C,C,0)"]), (0.5, vertices["(C,C,1)"])}, action="try"),
        (vertices["(T,C,1)"], "exit"):  SpgTransition(start_vertex=vertices["(T,C,1)"], end_vertices={(0.5, vertices["(T,N,0)"]), (0.5, vertices["(T,N,1)"])}, action="try"),
        (vertices["(C,N,0)"], "exit"):  SpgTransition(start_vertex=vertices["(C,N,0)"], end_vertices={(0.5, vertices["(N,N,0)"]), (0.5, vertices["(N,N,1)"])}, action="try"),
        (vertices["(C,N,1)"], "stay"):  SpgTransition(start_vertex=vertices["(C,N,1)"], end_vertices={(0.5, vertices["(C,N,0)"]), (0.5, vertices["(C,N,1)"])}, action="try"),
        (vertices["(C,N,1)"], "try"):   SpgTransition(start_vertex=vertices["(C,N,1)"], end_vertices={(0.5, vertices["(C,T,0)"]), (0.5, vertices["(C,T,1)"])}, action="try"),
        (vertices["(C,T,0)"], "exit"):  SpgTransition(start_vertex=vertices["(C,T,0)"], end_vertices={(0.5, vertices["(N,T,0)"]), (0.5, vertices["(N,T,1)"])}, action="try"),
        (vertices["(C,T,1)"], "enter"): SpgTransition(start_vertex=vertices["(C,T,1)"], end_vertices={(0.5, vertices["(C,C,0)"]), (0.5, vertices["(C,C,1)"])}, action="try"),
        (vertices["(C,C,0)"], "exit"):  SpgTransition(start_vertex=vertices["(C,C,0)"], end_vertices={(0.5, vertices["(N,C,0)"]), (0.5, vertices["(N,C,1)"])}, action="try"),
        (vertices["(C,C,1)"], "exit"):  SpgTransition(start_vertex=vertices["(C,C,1)"], end_vertices={(0.5, vertices["(C,N,0)"]), (0.5, vertices["(C,N,1)"])}, action="try")
    }
    initial_vertex = vertices["start"]
    return StochasticParityGame(vertices=vertices, transitions=transitions, init_vertex=initial_vertex)


def create_frozen_lake_spg(columns: int, rows: int, point0: tuple[int, int] | None = None, point1: tuple[int, int] | None = None, share_of_holes: float = 0.5, wind_probability: float = 0.5, slide_probability: float = 0.5) -> StochasticParityGame:
    field = [[2 for _ in range(rows)] for _ in range(columns)]
    if point0 is not None and point1 is not None:
        if point0 == point1:
            print_error(f"point1 and point2 must be different, but they are both {point0}.")
    if point0 is not None:
        if not (0 <= point0[0] < columns and 0 <= point0[1] < rows):
            print_error(f"point1 {point0} is out of bounds for a {columns}x{rows} grid.")
    if point1 is not None:
        if not (0 <= point1[0] < columns and 0 <= point1[1] < rows):
            print_error(f"point2 {point1} is out of bounds for a {columns}x{rows} grid.")
    if share_of_holes < 0 or share_of_holes > 1:
        print_error(f"share_of_holes must be between 0 and 1, but it is {share_of_holes}.")
    if point0 is None:
        point0 = (random.randint(0, columns - 1), random.randint(0, rows - 1))
        if point1 is not None:
            while point0 == point1:
                point0 = (random.randint(0, columns - 1), random.randint(0, rows - 1))
    if point1 is None:
        point1 = (random.randint(0, columns - 1), random.randint(0, rows - 1))
        if point0 == point1:
            while point1 == point0:
                point1 = (random.randint(0, columns - 1), random.randint(0, rows - 1))
    field[point0[0]][point0[1]] = 0
    field[point1[0]][point1[1]] = 1
    number_of_holes = int(columns * rows * share_of_holes)
    holes = set()
    while number_of_holes > 0:
        x = random.randint(0, columns - 1)
        y = random.randint(0, rows - 1)
        if field[x][y] == 2:
            field[x][y] = 3
            holes.add((x, y))
            number_of_holes -= 1
        else:
            while field[x][y] != 2:
                x = random.randint(0, columns - 1)
                y = random.randint(0, rows - 1)
            field[x][y] = 3
            holes.add((x, y))
            number_of_holes -= 1
    vertices = dict()
    for x in range(columns):
        for y in range(rows):
            if field[x][y] == 0:
                vertices[f"v_{x}_{y}_0_0"] = SpgVertex(name=f"v_{x}_{y}_0_0", is_eve=True, priority=2)
                vertices[f"v_{x}_{y}_0_1"] = SpgVertex(name=f"v_{x}_{y}_0_1", is_eve=True, priority=3)
                vertices[f"v_{x}_{y}_1_1"] = SpgVertex(name=f"v_{x}_{y}_1_1", is_eve=False, priority=3)
            elif field[x][y] == 1:
                vertices[f"v_{x}_{y}_0_0"] = SpgVertex(name=f"v_{x}_{y}_0_0", is_eve=True, priority=3)
                vertices[f"v_{x}_{y}_1_0"] = SpgVertex(name=f"v_{x}_{y}_1_0", is_eve=False, priority=3)
                vertices[f"v_{x}_{y}_0_1"] = SpgVertex(name=f"v_{x}_{y}_0_1", is_eve=True, priority=2)
            elif field[x][y] == 2:
                vertices[f"v_{x}_{y}_0_0"] = SpgVertex(name=f"v_{x}_{y}_0_0", is_eve=True, priority=3)
                vertices[f"v_{x}_{y}_1_0"] = SpgVertex(name=f"v_{x}_{y}_1_0", is_eve=False, priority=3)
                vertices[f"v_{x}_{y}_0_1"] = SpgVertex(name=f"v_{x}_{y}_0_1", is_eve=True, priority=3)
                vertices[f"v_{x}_{y}_1_1"] = SpgVertex(name=f"v_{x}_{y}_1_1", is_eve=False, priority=3)
            elif field[x][y] == 3:
                vertices[f"v_{x}_{y}_0_0"] = SpgVertex(name=f"v_{x}_{y}_0_0", is_eve=True, priority=1)
                vertices[f"v_{x}_{y}_0_1"] = SpgVertex(name=f"v_{x}_{y}_0_1", is_eve=True, priority=1)

    transitions = dict()
    for x in range(columns):
        for y in range(rows):
            match field[x][y]:
                case 0:
                    # change the current target to the other target field
                    transitions[(vertices[f"v_{x}_{y}_0_0"], "change_target")] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x}_{y}_0_1"])}, action="change_target")
                    for direction in ["left", "right", "up", "down"]:
                        match direction:
                            case "left":
                                next_field = field[x - 1][y] if x > 0 else None
                                second_next_field = field[x - 2][y] if x > 1 else None
                                move = (-1, 0)
                            case "right":
                                next_field = field[x + 1][y] if x < columns - 1 else None
                                second_next_field = field[x + 2][y] if x < columns - 2 else None
                                move = (1, 0)
                            case "up":
                                next_field = field[x][y - 1] if y > 0 else None
                                second_next_field = field[x][y - 2] if y > 1 else None
                                move = (0, -1)
                            case "down":
                                next_field = field[x][y + 1] if y < rows - 1 else None
                                second_next_field = field[x][y + 2] if y < rows - 2 else None
                                move = (0, 1)
                        match (next_field, second_next_field):
                            case (None, _):
                                pass
                            case (1, _):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, None):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1-wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 1):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 2):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 3):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (3, _):
                                transitions[(vertices[f"v_{x}_{y}_0_1"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_1"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)

                case 1:
                    # change the current target to the other target field
                    transitions[(vertices[f"v_{x}_{y}_0_1"], "change_target")] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x}_{y}_0_0"])}, action="change_target")
                    for direction in ["left", "right", "up", "down"]:
                        match direction:
                            case "left":
                                next_field = field[x - 1][y] if x > 0 else None
                                second_next_field = field[x - 2][y] if x > 1 else None
                                move = (-1, 0)
                            case "right":
                                next_field = field[x + 1][y] if x < columns - 1 else None
                                second_next_field = field[x + 2][y] if x < columns - 2 else None
                                move = (1, 0)
                            case "up":
                                next_field = field[x][y - 1] if y > 0 else None
                                second_next_field = field[x][y - 2] if y > 1 else None
                                move = (0, -1)
                            case "down":
                                next_field = field[x][y + 1] if y < rows - 1 else None
                                second_next_field = field[x][y + 2] if y < rows - 2 else None
                                move = (0, 1)
                        match (next_field, second_next_field):
                            case (None, _):
                                pass
                            case (0, _):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                            case (2, None):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1-wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                            case (2, 0):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                            case (2, 2):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                            case (2, 3):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                            case (3, _):
                                transitions[(vertices[f"v_{x}_{y}_0_0"], direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[(vertices[f"v_{x}_{y}_1_0"], "blow_" + direction)] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                case 2:
                    for direction in ["left", "right", "up", "down"]:
                        match direction:
                            case "left":
                                next_field = field[x - 1][y] if x > 0 else None
                                second_next_field = field[x - 2][y] if x > 1 else None
                                move = (-1, 0)
                            case "right":
                                next_field = field[x + 1][y] if x < columns - 1 else None
                                second_next_field = field[x + 2][y] if x < columns - 2 else None
                                move = (1, 0)
                            case "up":
                                next_field = field[x][y - 1] if y > 0 else None
                                second_next_field = field[x][y - 2] if y > 1 else None
                                move = (0, -1)
                            case "down":
                                next_field = field[x][y + 1] if y < rows - 1 else None
                                second_next_field = field[x][y + 2] if y < rows - 2 else None
                                move = (0, 1)
                        match (next_field, second_next_field):
                            case (None, _):
                                pass
                            case (0, None):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1 - wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (0, 1):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (0, 2):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (0, 3):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (1, None):
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1 - wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (1, 0):
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (1, 2):
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (1, 3):
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, None):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1 - wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1 - wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 0):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 1):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 2):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability * (1 - wind_probability), vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"]), (slide_probability * wind_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (2, 3):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_0"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={((1 - slide_probability) * (1 - wind_probability), vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"]), (slide_probability, vertices[f"v_{x + 2 * move[0]}_{y + 2 * move[1]}_0_1"]), ((1 - slide_probability) * wind_probability, vertices[f"v_{x + move[0]}_{y + move[1]}_1_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                            case (3, _):
                                transitions[vertices[f"v_{x}_{y}_0_0"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_0_1"], direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action=direction)
                                transitions[vertices[f"v_{x}_{y}_1_0"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_0"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_0"])}, action="blow_" + direction)
                                transitions[vertices[f"v_{x}_{y}_1_1"], "blow_" + direction] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_1_1"], end_vertices={(1.0, vertices[f"v_{x + move[0]}_{y + move[1]}_0_1"])}, action="blow_" + direction)
                case 3:
                    # if fallen into a hole, go back to the current start field
                    transitions[(vertices[f"v_{x}_{y}_0_0"], "go_back")] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_0"], end_vertices={(1.0, vertices[f"v_{point1[0]}_{point1[1]}_0_0"])}, action="go_back")
                    transitions[(vertices[f"v_{x}_{y}_0_1"], "go_back")] = SpgTransition(start_vertex=vertices[f"v_{x}_{y}_0_1"], end_vertices={(1.0, vertices[f"v_{point0[0]}_{point0[1]}_0_0"])}, action="go_back")
    initial_vertex = vertices[f"v_{point0[0]}_{point0[1]}_0_0"]
    return StochasticParityGame(vertices=vertices, transitions=transitions, init_vertex=initial_vertex)


def create_random_spg(number_of_vertices: int, number_of_outgoing_transitions: int, number_of_priorities: int) -> StochasticParityGame:
    vertices = {f"v_{i}": SpgVertex(name=f"v_{i}", is_eve=True if random.randint(0, 1) == 1 else False, priority=random.randint(0, number_of_priorities - 1)) for i in range(number_of_vertices)}
    transitions = {}
    i = 0
    for vertex in vertices.values():
        for i in range(number_of_outgoing_transitions):
            if random.randint(0, 1) == 1:
                transitions[(vertex, f"action_{i}")] = SpgTransition(start_vertex=vertex, end_vertices={(1.0, random.choice(list(vertices.values())))}, action=f"action_{i}")
            else:
                transitions[(vertex, f"action_{i}")] = SpgTransition(start_vertex=vertex, end_vertices={(0.5, random.choice(list(vertices.values()))), (0.5, random.choice(list(vertices.values())))}, action=f"action_{i}")
            i += 1
    initial_vertex = random.choice(list(vertices.values()))
    return StochasticParityGame(vertices, transitions, initial_vertex)


def benchmark_own_examples_for_correctness(filenames_of_benchmarks: list[str], expected_values: list[tuple[float, float]], use_global_path=False, debug: bool = False) -> None:
    if len(filenames_of_benchmarks) != len(expected_values):
        raise ValueError("The number of benchmark files must match the number of expected values.")
    i = 0
    for filename in filenames_of_benchmarks:
        spg = read_spg_from_file(filename, use_global_path=use_global_path)
        ssg = spg_to_ssg(spg=spg, epsilon=1e-6, print_alphas=debug)
        smg_spec = ssg_to_smgspec(ssg=ssg, version1=True, debug=False, print_correspondingvertices=debug)
        save_smg_file(smg_spec, file_name="temp.smg", use_global_path=use_global_path, force=True)
        result = check_target_reachability(smg_file="temp.smg", print_probabilities=False, use_global_path=use_global_path)
        print("####################################################################################")
        print()
        print(f"Expected minimum probability of Eve winning with even parity for {filename}: {expected_values[i][0]}")
        print(f"Computed minimum probability of Eve winning with even parity for {filename}: {result[0]}")
        print("---------------------------------------------------------------------------------------")
        print(f"Expected maximum probability of Eve winning with even parity for {filename}: {expected_values[i][1]}")
        print(f"Computed maximum probability of Eve winning with even parity for {filename}: {result[1]}")
        print()
        i += 1


def benchmark_chain_spgs_for_correctness(use_global_path: bool = False, debug: bool = GLOBAL_DEBUG) -> None:
    for i in range(1, 20):
        spg = create_chain_spg(length=2 ** i, min_prob=0.5)
        ssg = spg_to_ssg(spg=spg, epsilon=1e-6, print_alphas=debug)
        smg_spec = ssg_to_smgspec(ssg=ssg, version1=True, debug=False, print_correspondingvertices=False)
        save_smg_file(smg_spec, file_name="temp.smg", use_global_path=use_global_path, force=True)
        result = check_target_reachability(smg_file="temp.smg", print_probabilities=False, use_global_path=use_global_path)
        print("####################################################################################")
        print()
        print(f"Expected minimum probability of Eve winning with even parity for chain of length {2 ** i}: 1.0")
        print(f"Computed minimum probability of Eve winning with even parity for chain of length {2 ** i}: {result[0]}")
        print("---------------------------------------------------------------------------------------")
        print(f"Expected maximum probability of Eve winning with even parity for chain of length {2 ** i}: 1.0")
        print(f"Computed maximum probability of Eve winning with even parity for chain of length {2 ** i}: {result[1]}")
        print()


def benchmark_mutex_spg_for_correctness(use_global_path: bool = False, debug: bool = GLOBAL_DEBUG) -> None:
    spg = create_mutex_spg()
    ssg = spg_to_ssg(spg=spg, epsilon=1e-6, print_alphas=debug)
    smg_spec = ssg_to_smgspec(ssg=ssg, version1=True, debug=False, print_correspondingvertices=False)
    save_smg_file(smg_spec, file_name="temp.smg", use_global_path=use_global_path, force=True)
    result = check_target_reachability(smg_file="temp.smg", print_probabilities=False, use_global_path=use_global_path)
    print("####################################################################################")
    print()
    print(f"Expected minimum probability of Eve winning with even parity for mutex game: 0.0")
    print(f"Computed minimum probability of Eve winning with even parity for mutex game: {result[0]}")
    print("---------------------------------------------------------------------------------------")
    print(f"Expected maximum probability of Eve winning with even parity for mutex game: 0.0")
    print(f"Computed maximum probability of Eve winning with even parity for mutex game: {result[1]}")
    print()

