from tkinter import * 
import pandas as pd
from collections import namedtuple


class CaminoCritico:

    def algoritmoCPM(dataMatrix,nodes):
        visited = []    # List to keep track of visited nodes.
        queue = []  # Initialize a queue
        matrix = {}  # Initialize forward pass table structure
        matrix2 = {}  # Initialize backward pass table structure
        critic = []  # Initialize Critical Path array
        successors = {}  # Initialize successors table
        predecessors = {}  # Initialize predecessors table
        duraciones = {}

        # we fill the successors and predecessors' table
        for el in dataMatrix:
            matrix2[el[0]] = {'earlyStart': 0, 'earlyFinish': 0,
                            'lateStart': 0, 'lateFinish': 0, 'slack': 0}
            matrix[el[0]] = {'earlyStart': 0, 'earlyFinish': 0,
                            'lateStart': '-', 'lateFinish': '-', 'slack': '-'}
            duraciones[el[0]] = int(el[2])

            if(el[3] != ['']):
                predecessors[el[0]] = el[3]

            else:
                # we have to identify the origin node
                predecessors[el[0]] = []

            for item in el[3]:
                if item in successors:
                    if(item != ['']):
                        aux = successors[item]
                        aux.append(el[0])
                        successors[item] = aux
                else:
                    if(item != ""):
                        aux1 = []
                        aux1.append(el[0])
                        successors[item] = aux1

        # and the last activity, won't have a successor
        last = list(set(nodes)-set(successors.keys()))
        successors[last[0]] = []
        # the forward pass will be done with BFS
        def forward(visited, duraciones, graph, node):

            # each time we visit a node, we have to add it to the list and the queue
            visited.append(node)
            queue.append(node)

            # setting the initial values
            ES = 0
            EF = 0
            predecesor = []

            # as long the queue is not empty
            while queue:
                # get the next node that is waiting
                s = queue.pop(0)

                if len(predecesor) > 0:
                    if s in matrix:
                        # the EF of the predecessors have to be compared to select the bigger value, this will be the ES of the node that we are visiting
                        if matrix[predecesor[0]]['earlyFinish'] > matrix[s]['earlyStart']:
                            ES = matrix[predecesor[0]]['earlyFinish']
                        else:
                            ES = matrix[s]['earlyStart']
                    else:
                        ES = matrix[predecesor[0]]['earlyFinish']
                    element = {'earlyFinish': ES+duraciones[s], 'earlyStart': ES,
                            'lateStart': '-', 'lateFinish': '-', 'slack': '-'}
                else:
                    element = {'earlyFinish': EF+duraciones[s], 'earlyStart': ES,
                            'lateStart': '-', 'lateFinish': '-', 'slack': '-'}

                matrix[s] = (element)
                if(len(predecesor) > 0):
                    predecesor.pop(0)

                # we have to visit the neighbors
                for neighbor in graph[s]:
                    predecesor.append(s)
                    visited.append(neighbor)
                    queue.append(neighbor)

        # the backward pass will be done with BFS too
        def backward(visited, duraciones, graph, node):

            # this is pretty much the same as the forward pass but with some twists
            visited.append(node)
            queue.append(node)

            LF = 0
            LS = 0
            predecesor = []

            while queue:
                s = queue.pop(0)

                if len(predecesor) > 0:
                    if matrix2[s]['lateFinish'] != 0:

                        # the LS of the node is compared to select the smaller value to be the LF of the visited node
                        if matrix2[predecesor[0]]['lateStart'] < matrix2[s]['lateFinish']:
                            LF = matrix2[predecesor[0]]['lateStart']
                        else:
                            LF = matrix2[s]['lateFinish']
                    else:
                        LF = matrix2[predecesor[0]]['lateStart']
                    LS = LF-duraciones[s]
                    slack = LF-matrix[s]['earlyFinish']
                    element = {'earlyStart': matrix[s]['earlyStart'], 'earlyFinish': matrix[s]
                            ['earlyFinish'], 'lateStart': LS, 'lateFinish': LF, 'slack': slack}
                else:
                    LF = matrix[s]['earlyFinish']
                    LS = LF-duraciones[s]
                    slack = LF-matrix[s]['earlyFinish']
                    element = {'earlyStart': matrix[s]['earlyStart'], 'earlyFinish': matrix[s]
                            ['earlyFinish'], 'lateStart': LS, 'lateFinish': LF, 'slack': slack}

                if(slack == 0 and s not in critic):
                    # if the slack time is the same as 0, it means that it is part of the critical path
                    critic.insert(0, s)

                matrix2[s] = (element)

                if(len(predecesor) > 0):
                    predecesor.pop(0)

                for neighbor in graph[s]:
                    predecesor.append(s)
                    visited.append(neighbor)
                    queue.append(neighbor)

        forward(visited, duraciones, successors, dataMatrix[0][0])
        backward(visited, duraciones, predecessors,
                dataMatrix[len(dataMatrix)-1][0])

        forwardPass = pd.DataFrame.from_dict(matrix, orient="index")
        backwardPass = pd.DataFrame.from_dict(matrix2, orient="index")
        criticalPath = pd.DataFrame({'Critical Path': critic})
        rutaCritica = namedtuple("rutaCritica", ["forwardPass", "backwardPass", "criticalPath","criticalData"])
        return rutaCritica(
            forwardPass,
            backwardPass,
            str(critic),
            criticalPath
        )

#####################################################################

    def procesarInput(self,listaInput):
        # filling the matrix
        columns = 4
        matrix_data = []
        nodes = []

        for i in range(len(listaInput)):
            matrix_data.append([])
            for j in range(columns):
                matrix_data[i].append("")

        # Save the info in the matrix
        for i in range(len(listaInput)):
            tuplas = listaInput[i].split("-")
            for j in range(columns):
                if(j == 0):
                    matrix_data[i][j] = tuplas[j]
                    nodes.append(tuplas[j])
                if(j == 1):
                    matrix_data[i][j] = tuplas[j]
                if(j == 2):
                    matrix_data[i][j] = int(tuplas[j])
                if(j == 3):
                    # if it is a dot, it doesnt have predecessors
                    if(tuplas[j] == "."):
                        matrix_data[i][j] = [""]
                    else:
                        matrix_data[i][j] = str(tuplas[j]).split(sep=",")
        return self.algoritmoCPM(matrix_data,nodes)
        
        
#####################################################################

    def procesarArchivo(self,archivoProc):
            df = archivoProc.fillna("")
            # to know how many columns and rows, we will use shape
            rows = df.shape[0]
            columns = df.shape[1]
            matrix_data = []
            nodes = []

            # it's time to create the matrix mxn that will contain the data, it'll be a list of list
            for i in range(rows):
                matrix_data.append([])
                for j in range(columns):
                    matrix_data[i].append("")

            # next, we fill the matrix with the data
            for i in range(rows):
                for j in range(columns):
                    if(j == 0):
                        matrix_data[i][j] = df["identificacion"][i]
                        nodes.append(df["identificacion"][i])
                    if(j == 1):
                        matrix_data[i][j] = df["descripcion"][i]
                    if(j == 2):
                        matrix_data[i][j] = df["duracion"][i]
                    if(j == 3):
                        matrix_data[i][j] = str(df["predecessors"][i]).split(sep=",")
            return self.algoritmoCPM(matrix_data,nodes)

            