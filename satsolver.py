#!/usr/bin/env python3
from typing import List
import numpy as np
from random import random
import pycosat

def solve(rows : List, cols : List, data : np.ndarray) -> bool:
    print(rows)
    print(cols)
    print(data.shape)
    # for i in range(int(random() * data.shape[0] * data.shape[1])):
    #     data[random() * data.shape[0], random() * data.shape[1]] = 1 if random() > 0.5 else -1
    cnf = [[1], [1, 3], [2, 3]]
    for solution in pycosat.itersolve(cnf):
        print(solution)