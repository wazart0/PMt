# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time




class Graph():
    pass


class MonteCarlo():
    def __init__(self, edges):
        self.edges = edges
        self.vertices = {i: np.random.RandomState() for i in pd.concat([frame.source, frame.target]).unique()}


    def choose_next_vertex(self, vertex):
        return self.vertices[vertex].choice(list(self.edges[self.edges.source == vertex].target), p=list(self.edges[self.edges.source == vertex].probability))


    def run(self, starting_vertex, goalFunction):
        vertex = starting_vertex
        result = 0
        while True:
            if len(list(self.edges[self.edges.source == vertex].target)) == 0:
                return [vertex, result]
            next_vertex = self.choose_next_vertex(vertex)
            result = goalFunction(vertex, next_vertex, result)
            vertex = next_vertex


    def sumResults(self, vertex, next_vertex, result):
        return result + list(self.edges[(self.edges.source == vertex) & (self.edges.target == next_vertex)].value)[0]



frame = pd.DataFrame(data=[
[1, 2, 0.7],
[1, 4, 0.3],
[2, 3, 0.8],
[2, 5, 0.1],
[2, 4, 0.1],
[3, 4, 1.0],
[4, 6, 0.7],
[4, 1, 0.1],
[4, 6, 0.2],
[5, 8, 0.9],
[5, 9, 0.1],
[6, 7, 1.0],
[7, 8, 0.9],
[7, 9, 0.1]
], columns=['source', 'target', 'probability'])
frame['value'] = frame.probability*10.


sim = MonteCarlo(frame)
results = []
for i in range(10000):
    results.append(sim.run(1, sim.sumResults))


fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
# We can set the number of bins with the `bins` kwarg
axs[0].hist([i[0] for i in results], bins=10)
axs[1].hist([i[1] for i in results], bins=30)


# %%
