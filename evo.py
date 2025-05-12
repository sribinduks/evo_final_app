"""
@source: Prof. John Rachlin evo.py
"""

import random as rnd
import numpy as np
import copy
from functools import reduce
import pandas as pd
import pickle
import time
import os
import json


class Environment:

    def __init__(self):
        """ Population constructor """
        self.pop = {} # The solution population eval -> solution
        self.fitness = {} # Registered fitness functions: name -> objective function
        self.agents = {}  # Registered agents:  name -> (operator, num_solutions_input)

    def size(self):
        """ The size of the current population """
        return len(self.pop)

    def add_fitness_criteria(self, name, f):
        """ Register a fitness criterion (objective) with the
        environment. Any solution added to the environment is scored
        according to this objective """
        self.fitness[name] = f

    def add_agent(self, name, op, k=1):
        """ Register a named agent with the population.
        The operator (op) function defines what the agent does.
        k defines the number of solutions the agent operates on. """
        self.agents[name] = (op, k)

    def add_solution(self, sol):
        """ Add a solution to the population """
        eval = tuple([(name, f(sol)) for name, f in self.fitness.items()])
        self.pop[eval] = sol


    def run_agent(self, name):
        """ Invoke an agent against the population """
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        new_solution = op(picks)
        self.add_solution(new_solution)


    def evolve(self, n=1, dom=1, status=1, sync=1, reset=False, time_limit = 1200):
        """ Run n random agents (default=1)
        dom defines how often we remove dominated (unfit) solutions
        status defines how often we display the current population
        n = # of agent invocations
        dom = interval for removing dominated solutions
        viol = interval for removing solutions that violate user-defined upper limits
        status = interval for display the current population
        sync = interval for merging results with solutions.dat (for parallel invocation)
        time_limit = the evolution time limit (seconds).  Evolve function stops when limit reached
        """
        df_evo = pd.DataFrame()
        # Initialize solutions file
        if reset and os.path.exists('solutions.dat'):
            os.remove('solutions.dat')

        # Initialize user constraints
        if reset or not os.path.exists('constraints.json'):
            with open('constraints.json', 'w') as f:
                json.dump({name:99999 for name in self.fitness},
                          f, indent=4)

        if reset or not os.path.exists('time_limit.json'):
            with open('time_limit.json', 'w') as f:
                json.dump({'time':1200},
                          f, indent=4)

        with open('time_limit.json', 'r') as f:
            time_input = json.load(f)
        time_input = list(time_input.items())
        time_input = time_input[0][1]

        start = time.time_ns()
        elapsed = (time.time_ns() - start) / 10**9
        agent_names = list(self.agents.keys())

        i = 0

        if time_input != None:
            time_limit = time_input

        while i < n and self.size() > 0 and elapsed <= time_limit:

            pick = rnd.choice(agent_names)
            self.run_agent(pick)

            if i % sync == 0:
                try:
                    # Merge saved solutions into population
                    with open('solutions.dat', 'rb') as file:
                        loaded = pickle.load(file)
                        for eval, sol in loaded.items():
                            self.pop[eval] = sol

                except Exception as e:
                    print(e)

                #  Remove the dominated solutions and take the constraints the users set into account
                self.remove_dominated()
                self.remove_constraint_violators()

                # Resave the non-dominated solutions
                with open('solutions.dat', 'wb') as file:
                    print(len(self.pop))
                    pickle.dump(self.pop, file)


            if i % dom == 0:
                self.remove_dominated()

            if i % status == 0:
                self.remove_dominated()

                # To create a df for each solution print
                final = []
                for key in self.pop.keys():
                    cols = []
                    values = []
                    for x in key:
                        if x[0] not in cols:
                            cols.append(x[0])
                        values.append(x[1])
                    final.append(values)
                final.insert(0, cols)
                arr = np.array(list(self.pop.values()))
                df = pd.DataFrame(final[1:], columns=final[0])
                df_evo = pd.concat([df_evo,df])
                print(self)
                print("Elapsed Time (Sec) :", elapsed, "\n\n\n")

                with open('elapsed.json', 'w') as f:
                        json.dump({'elapsed': elapsed}, f)

            i += 1
            elapsed = (time.time_ns() - start) / 10 ** 9

            if reset or not os.path.exists('elapsed.json'):
                with open('elapsed.json', 'w') as f:
                    json.dump({'elapsed': elapsed}, f)

        # Clean up the population
        self.remove_dominated()

        return df_evo

    def get_random_solutions(self, k=1):
        """ Pick k random solutions from the population """
        if self.size() == 0: # No solutions in population
            return []
        else:
            popvals = tuple(self.pop.values())
            return [copy.deepcopy(rnd.choice(popvals)) for _ in range(k)]


    @staticmethod
    def _dominates(p, q):
        """ p = evaluation of solution: ((obj1, score1), (obj2, score2), ... )"""
        pscores = [score for _,score in p]
        qscores = [score for _,score in q]
        score_diffs = list(map(lambda x,y: y-x, pscores, qscores))
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)
        return min_diff >= 0.0 and max_diff > 0.0


    @staticmethod
    def _reduce_nds(S, p):
        return S - {q for q in S if Environment._dominates(p,q)}


    def remove_dominated(self):
        """ Remove dominated solutions """
        nds = reduce(Environment._reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k:self.pop[k] for k in nds}

    @staticmethod
    def _reduce_viol(S, T):
        objective, max_value = T
        return S - {q for q in S if dict(q)[objective]>max_value}


    def remove_constraint_violators(self):
        """ Remove solutions whose objective values exceed one or
        more user-defined constraints as listed in constraints.dat """

        # Read the latest constraints file into a dictionary
        with open('constraints.json', 'r') as f:
            limits = json.load(f)

        # Determine non-violators and update population
        nonviol = reduce(Environment._reduce_viol, limits.items(), self.pop.keys())
        self.pop = {k:self.pop[k] for k in nonviol}

    def __str__(self):
        """ Output the solutions in the population """
        rslt = ""
        for eval,sol in self.pop.items():
            rslt += str(dict(eval))+"\n" # +str(sol)+"\n"
        return rslt
