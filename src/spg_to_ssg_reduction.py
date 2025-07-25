from fractions import Fraction
from math import factorial

from error_handling import print_error
from stochasticparitygame import StochasticParityGame, read_spg_from_file
from simplestochasticgame import SimpleStochasticGame, SsgVertex, SsgTransition
from settings import USE_EXACT_ARITHMETIC, MAX_DENOMINATOR


def max_denom_and_min_prob(spg: StochasticParityGame, max_d: int=10_000) -> (float | Fraction, int):
    """
    Computes the minimum probability and the maximum denominator of the transition probabilities in a StochasticParityGame.
    This is used to compute the alphas for the conversion to a SimpleStochasticGame.
    :param spg: The StochasticParityGame to analyze
    :type spg: StochasticParityGame
    :param max_d: The maximum denominator to consider for the fractions, defaults to 10_000
    :type max_d: int
    :return: minimum probability and maximum denominator
    :rtype: (float | Fraction, int)
    """
    floats = set()
    for transition in spg.transitions.values():
        for prob, vert in transition.end_vertices:
            floats.add(prob)
    fractions = [Fraction(f).limit_denominator(max_d) for f in floats]
    return (min(floats), max(fr.denominator for fr in fractions))


def compute_alphas_for_spg(spg: StochasticParityGame, epsilon: float = None, max_d: int = 10_000) -> dict[int, Fraction | float]:
    """
    Computes the alphas for a StochasticParityGame to convert it to a SimpleStochasticGame.
    :param spg: StochasticParityGame to compute alphas for
    :type spg: StochasticParityGame
    :param epsilon: Precision parameter for the conversion, if None, alphas are computed such that the strategy is optimal for the game.
    :type epsilon: float
    :param max_d: Maximum denominator for the fractions, defaults to 10_000
    :type max_d: int
    :return: Dictionary mapping priorities to alphas where the alphas are either Fractions or floats depending on the USE_EXACT_ARITHMETIC setting.
    :rtype: dict[int, Fraction | float]
    """
    delta_min_float, max_denominator_M = max_denom_and_min_prob(spg, max_d)
    # if float(delta_min_float == 1.0):
        # print_error("The StochasticParity is not stochastic, therefore the reduction cannot be performed.")
    n_states = len(spg.vertices)
    used = sorted({v.priority for v in spg.vertices.values()})

    delta_min = Fraction(delta_min_float).limit_denominator(max_d)
    one_minus = Fraction(1, 1) - delta_min
    if epsilon is None:
        numerator   = delta_min ** n_states
        denominator = 8 * factorial(n_states) ** 2 * max_denominator_M ** (2 * n_states * n_states)
        alpha0 = numerator / denominator

        ratio_bound = (one_minus * (delta_min ** n_states)) / (denominator + 1)

        alphas = { used[0]: alpha0 }
        for prev_k, next_k in zip(used, used[1:]):
            gap = next_k - prev_k
            alphas[next_k] = alphas[prev_k] * ratio_bound
    else:
        numerator = Fraction(4) * Fraction(epsilon) * delta_min ** n_states
        denominator = (Fraction(4) - Fraction(epsilon)) * Fraction(8)
        alpha0 = numerator / denominator

        ratio_bound = (one_minus * (delta_min ** n_states)) / (((8 * (4 - Fraction(epsilon))) / (4 * Fraction(epsilon))) + 1)
        alphas = { used[0]: alpha0 }
        for prev_k, next_k in zip(used, used[1:]):
            gap = next_k - prev_k
            alphas[next_k] = alphas[prev_k] * ratio_bound
    if not USE_EXACT_ARITHMETIC:
        alphas = {k: float(v) for k, v in alphas.items()}
    return alphas


def spg_to_ssg(spg: StochasticParityGame, epsilon: float = None, print_alphas: bool = False) -> SimpleStochasticGame:
    """
    Converts a StochasticParityGame to a SimpleStochasticGame.
    :param spg: The StochasticParityGame to convert
    :type spg: StochasticParityGame
    :param epsilon: The epsilon value for the conversion, if None, it will be computed based on the game
    :type epsilon: float, optional
    :param print_alphas: Whether to print the computed alphas, defaults to False
    :type print_alphas: bool, optional
    :return: The converted SimpleStochasticGame
    :rtype: SimpleStochasticGame
    """
    alphas = compute_alphas_for_spg(spg, epsilon=epsilon)
    if print_alphas:
        print("Computed alphas:")
        for k, v in alphas.items():
            print(f"Priority {k}: {float(v)}" + (f" | Optimized to {v.limit_denominator(MAX_DENOMINATOR)}" if USE_EXACT_ARITHMETIC else ""))
    vertices: dict[str, SsgVertex] = dict()
    transitions: dict[tuple[SsgVertex, str], SsgTransition] = dict()
    respective_spg_ssg_vertixes: dict[SpgVertex, SsgVertex] = dict()
    initial_vertex: SsgVertex = None

    for v in spg.vertices.values():
        vertices[v.name] = SsgVertex(name=v.name, is_eve=v.is_eve, is_target=False)
        respective_spg_ssg_vertixes[v] = vertices[v.name]
    new_vertices: dict[str, SsgVertex] = dict()
    initial_vertex = vertices[spg.init_vertex.name]
    respective_intermediate_vertices: dict[SsgVertex, SsgVertex] = dict()
    for v in spg.vertices.values():
        if not vertices.keys().__contains__(v.name+"\'"):
            new_vertices[v.name+"\'"] = SsgVertex(name=v.name + "\'", is_eve=not v.is_eve, is_target=False)
            respective_intermediate_vertices[vertices[v.name]] = new_vertices[v.name+"\'"]
        else:
            i = 0
            while vertices.keys().__contains__(v.name+"\'"+str(i)):
                i += 1
            new_vertices[v.name+"\'"+str(i)] = SsgVertex(name=v.name + "\'" + str(i), is_eve=not v.is_eve, is_target=False)
            respective_intermediate_vertices[vertices[v.name]] = new_vertices[v.name+"\'"+str(i)]
    vertices |= new_vertices
    if not vertices.keys().__contains__("v_win"):
        vertices["v_win"] = SsgVertex(name="v_win", is_eve=True, is_target=True)
    else:
        i=0
        while vertices.keys().__contains__("v_win"+str(i)):
            i += 1
        vertices["v_win"+str(i)] = SsgVertex(name="v_win" + str(i), is_eve=True, is_target=True)
    if not vertices.keys().__contains__("v_lose"):
        vertices["v_lose"] = SsgVertex(name="v_lose", is_eve=False, is_target=False)
    else:
        i=0
        while vertices.keys().__contains__("v_lose"+str(i)):
            i += 1
        vertices["v_lose"+str(i)] = SsgVertex(name="v_lose" + str(i), is_eve=False, is_target=False)

    for transition in spg.transitions.values():
        start_v = vertices[transition.start_vertex.name]
        action = transition.action
        end_vs = set()
        for prob, end_v in transition.end_vertices:
            end_vs.add((prob, respective_intermediate_vertices[vertices[end_v.name]]))
        transitions[(start_v, action)] = SsgTransition(start_v, end_vs, action)

    for vertex in spg.vertices.values():
        if vertex.priority % 2 == 0:
            transitions[(respective_intermediate_vertices[respective_spg_ssg_vertixes[vertex]], "alpha")] = SsgTransition(respective_intermediate_vertices[respective_spg_ssg_vertixes[vertex]], {(alphas[vertex.priority], vertices["v_win"]), (1 - alphas[vertex.priority], vertices[respective_spg_ssg_vertixes[vertex].name])}, "alpha")
        else:
            transitions[(respective_intermediate_vertices[respective_spg_ssg_vertixes[vertex]], "alpha")] = SsgTransition(respective_intermediate_vertices[respective_spg_ssg_vertixes[vertex]], {(alphas[vertex.priority], vertices["v_lose"]), (1 - alphas[vertex.priority], vertices[respective_spg_ssg_vertixes[vertex].name])}, "alpha")
    return SimpleStochasticGame(vertices, transitions, initial_vertex)
