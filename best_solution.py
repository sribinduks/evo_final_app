"""
When run, this .py file will output the best chosen solution and outputs the exact assignments as a dataframe
AND creates a .xlsx file with the assignments as a more appealing visual aid.
*Mimics Professor Rachlin's Excel lab TA Spreadsheet!*
"""

import pandas as pd
import pickle
import numpy as np

# Global Variables
TAS, SECTIONS = pd.read_csv('data/tas.csv'), pd.read_csv('data/sections.csv')
MAX_COL = TAS['max_assigned']
NAMES = TAS['name']
TIME_COL = SECTIONS.daytime
MIN_COL = SECTIONS['min_ta']
TAS = TAS.iloc[:, 3:]

result = []
with (open("solutions.dat", "rb")) as openfile:
    while True:
        try:
            result.append(pickle.load(openfile))
        except EOFError:
            break

# creates a list of all the objective names
objectives = [obj_tup[0] for obj_tup in list(result[0].keys())[0]]

# takes array of solutions and formats it into a list
arr = list(result[0].values())


def return_df(idx):
    """
    :param idx: integer index given to one solution
    :return: a data frame with the TA assignments for that solution
    """
    best_sol = np.array(arr[idx])
    df_final = pd.DataFrame([['*A*' if best_sol[i, j] == 1 else TAS.iloc[i, j] for j in range(len(TAS.columns))]
                             for i in range(len(TAS))])
    df_final.insert(0, "TAS", NAMES.values.tolist(), True)

    secs = list(range(0, len(SECTIONS)))
    secs.insert(0, "Lab #:")
    times = TIME_COL.values.tolist()
    times.insert(0, "Time:")
    header = pd.MultiIndex.from_arrays([secs,times])
    df_final.columns = header
    return df_final