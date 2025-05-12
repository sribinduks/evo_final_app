"""
sorting.py
A demonstration of using evocomp to sort a list of numbers
"""
# Import libraries
import random as rnd
import pandas as pd
import numpy as np
import evo

# Global Variables
TAS, SECTIONS = pd.read_csv('data/tas.csv'), pd.read_csv('data/sections.csv')
MAX_COL = TAS['max_assigned']
TIME_COL = SECTIONS.daytime
MIN_COL = SECTIONS['min_ta']
TAS = TAS.iloc[:, 3:]


"""5 OBJECTIVE FUNCTIONS"""


def overallocation(sol):
    """Objective function: Identifies overallocation penalty"""
    return sum([np.sum(sol[i, :]) - np.array(MAX_COL)[i] for i in range(len(np.array(MAX_COL)))
                if np.sum(sol[i, :]) > np.array(MAX_COL)[i]])


def conflicts(sol):
    """Objective function: Identifies conflicts penalty"""
    return sum([1 for ta in range(len(pd.DataFrame(sol.tolist(), columns=TIME_COL.values.tolist())))
                if len(list(TIME_COL[sol[ta] == 1])) > len(set(TIME_COL[sol[ta] == 1]))])


def undersupport(sol):
    """Objective function: Identifies undersupport penalty"""
    sums = [pd.DataFrame(sol, columns=[MIN_COL.values.tolist()]).iloc[:, i].sum() for i in range(len(MIN_COL))]
    return sum([MIN_COL[i] - sums[i] for i in range(len(MIN_COL)) if MIN_COL[i] > sums[i]])


def unwilling(sol):
    """Objective function: Identifies unwilling penalty"""
    return len([1 for i in range(len(TAS)) for j in range(len(TAS.columns))
                if TAS.iloc[i, j] == "U" and sol[i, j] == 1])


def unpreferred(sol):
    """Objective function: Identifies unpreferred penalty"""
    return len([1 for i in range(len(TAS)) for j in range(len(TAS.columns))
                if TAS.iloc[i, j] == "W" and sol[i, j] == 1])


"""AGENT FUNCTIONS"""


def minimize_unwilling(solutions):
    """ AGENT: replaces letter preferences with appropriate assignments (i.e. U = 0)"""
    return np.array([[0 if TAS.iloc[i, j] == "U" and solutions[0][i, j] == 1 else solutions[0][i, j]
                      for j in range(len(TAS.columns))] for i in range(len(TAS))])


def toggle(solutions):
    """AGENT: switches 0s and 1s for a random value in solution"""
    sol = solutions[0]
    i = rnd.randrange(0, sol.shape[0])
    j = rnd.randrange(0, sol.shape[1])
    sol[i, j] = 1 - sol[i, j]
    return sol


def switch_rows(solutions):
    """AGENT: switches assignments of random TAs"""
    sol = solutions[0]
    tas = np.random.choice(len(sol), 2)
    sol[[tas[0], tas[1]]] = sol[[tas[1], tas[0]]]
    return sol


def fix_undersupport(solutions):
    """AGENT: randomly assigns TAs to undersupported labs"""
    sol = solutions[0]
    for lab in np.where(MIN_COL - np.sum(sol, axis=0) > 0)[0]:
        if True:
            sol[np.random.choice(np.where(sol[lab] == 0)[0])][lab] = 1
    return sol


def fix_overallocated_tas(solutions):
    """AGENT: randomly unassigns TAs to overallocated labs"""
    sol = solutions[0]
    for ta in np.where(np.sum(sol, axis=1) > MAX_COL)[0]:
        sol[ta][np.random.choice(np.where(sol[ta] == 1)[0])] = 0
    return sol


def merge(solutions):
    """AGENT: concatenates rows from 2 solutions"""
    sol1 = solutions[0]
    sol2 = solutions[1]
    i = rnd.randrange(0, sol1.shape[0])
    new_sol = np.concatenate((sol1[0:i, :], sol2[i:, :]), axis=0)
    return new_sol


def main():
    # create population
    E = evo.Environment()

    # register the fitness criteria (objects)
    E.add_fitness_criteria("overallocation", overallocation)
    E.add_fitness_criteria("conflicts", conflicts)
    E.add_fitness_criteria("undersupport", undersupport)
    E.add_fitness_criteria("unwilling", unwilling)
    E.add_fitness_criteria("unpreferred", unpreferred)

    # register all agents
    E.add_agent("minimize_unwilling", minimize_unwilling, 1)
    E.add_agent("toggle", toggle, 1)
    E.add_agent("switch_rows", switch_rows, 1)
    E.add_agent("fix_undersupport", fix_undersupport, 1)
    E.add_agent("fix_overallocated_tas", fix_overallocated_tas, 1)
    E.add_agent("merge", merge, 2)

    # seed the population with an initial solution
    sol = np.random.choice([0, 1], size=(len(TAS), len(SECTIONS)))
    E.add_solution(sol)

    # run the evolver
    E.evolve(5000000, dom=1, sync=1, status=1,reset =True)


main()