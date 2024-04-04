'''
Genetic Alogrithm for determinine the best fuzzylogic
threshold values
'''

import json
from random import randint
from random import random
from fuzzywuzzy import fuzz

class MissingArgumentException(Exception):
    def __init__(self, message="Argument is missing"):
        self.message = message
        super().__init__(self.message)

class GA:
    def __init__(self, objectives=None):
        
        if objectives is None:
            message = """

            objectives have not been supplied.
            Please Supply objectives as a list of lists
            With the first 2 values as the strings to compare and the third a boolean
            representing if the values should or shouldn't match.
            ie
            [
                ["Jane Doe", "Jane A. Doe", True],
                ["Kenny Loggins", "Jane A. Doe", False],
            ]
            It is also suggested to provide as many values as possible with the examples reflecting as close to 
            real circumstances as possible.
            """
            raise MissingArgumentException(message)

        self.objectives = objectives
        self.bounds = [[-0, -100]]


    def objective(self, x):

        count = len(self.objectives)
        for match in self.objectives:
            r = fuzz.WRatio(match[0], match[1])
            if r > -x[0] and match[2]:
                count -= 1
            elif r < -x[0] and not match[2]:
                count -= 1

        return count

    
    def decode(self, bounds, n_bits, bitstring):
        decoded = list()
        largest = 2**n_bits
        for i in range(len(bounds)):
            start, end = i * n_bits, (i * n_bits) + n_bits
            try:
                substring = bitstring[start:end]
                chars = "".join([str(s) for s in substring])
                integer = int(chars, 2)
                value = bounds[i][0] + (integer / largest) * (bounds[i][1] - bounds[i][0])
                decoded.append(value)
            except:
                pass
        return decoded
    

    def selection(self, pop, scores, k=3):
        selection_ix = randint(0, len(pop)-1)
        iterator = [randint(0, len(pop)-1) for _ in range(k-1)]
        for ix in iterator:
            if scores[ix] < scores[selection_ix]:
                selection_ix = ix
        return pop[selection_ix]


    def crossover(self, p1, p2, r_cross):
        c1, c2 = p1.copy(), p2.copy()
        if random() < r_cross:
            pt = randint(1, len(p1) - 2)
            c1 = p1[:pt] + p2[pt:]
            c2 = p2[:pt] + p1[pt:]
        return [c1, c2]


    def mutation(self, bitstring, r_mut):
        for i in range(len(bitstring)):
            if random() < r_mut:
                bitstring[i] = 1 - bitstring[i]


    def genetic_algorithm(self, objective, bounds, n_bits, n_iter, n_pop, r_cross, r_mut):
        x_range = n_bits * len(bounds)
        pop = []
        for _ in range(n_pop):
            x_v = [randint(0, 1) for _ in range(x_range)]
            pop.append(x_v)



        # pop = [randint(0, 2, x_range).tolist() for _ in range(n_pop)]
        best, best_eval = 0, objective(self.decode(bounds, n_bits, pop[0]))

        for gen in range(n_iter):
            decoded = [self.decode(bounds, n_bits, p) for p in pop if p != 0]
            scores = [objective(d) for d in decoded]

            for i in range(n_pop):
                if scores[i] < best_eval:
                    best, best_eval = pop[i], scores[i]
                    print("%d, found new best f(%s) = %f" % (gen, decoded[i], scores[i]))

            selected = [self.selection(pop, scores) for _ in range(n_pop)]

            children = list()

            for i in range(0, n_pop, 2):
                p1, p2 = selected[i], selected[i + 1]
                for c in self.crossover(p1, p2, r_cross):
                    self.mutation(c, r_mut)
                    children.append(c)
            pop = children
        return [best, best_eval, scores]
    

    def run(self, n_iter=300, n_pop=10, r_cross=0.8):

        bounds = [[-0, -100]]

        n_bits = 16

        r_mut = 1.0 / (float(n_bits) * len(bounds))

        best, score, scores = self.genetic_algorithm(
            self.objective, bounds, n_bits, n_iter, n_pop, r_cross, r_mut
        )

        print("Done!")

        decoded = self.decode(bounds, n_bits, best)

        print("Ideal Threshold Value is: %s" % (decoded))
        print(f"Objectives which do can't be resolved by this score: {score}")



class Example:
    def fuzzy():
        matches = [
                ["Jane Doe", "Jane A. Doe", True],
                ["Yang-yu Chen", "Yang Yu Chen", True],
                ["Kumar, khruv", "khruv Kumar", True],
                ["Liz Z. Erd", "Liz Zed Erd", True],
                ["A. Mused", "Andrew b Mused", False],
                ["Lois Di Nominator", "Lois D. Nominator", True],
                ["P. Ann O'Recital", "Patty Ann O'Recital", False],
                ["Lee A. Sun", "Pete A. Sun", False],
                ["Ray Sin", "Ray Sin", True],
                ["Isabelle Ringing", "Isabelle Ringing", True],
                ["Eileen Sideways", "Eileen Sideways", True],
                ["Rita Book", "Rita Book", True],
                ["Paige Turner", "Paige Turner", True],
                ["Rhoda Report", "Rhoda Report", True],
                ["Augusta Wind", "Augusta Wind", True],
                ["Chris Anthemum", "Chris Anthemum", True],
                ["Anne Teak", "Anne Teak", True],
                ["Willie Makit", "Willie B'Here", False],
                ["Gene Eva Convenshun", "Gene E Convenshun", True],
                ["Hugh N. Cry", "Hugh G Head", False],
                ["Dr Jimmy L Buffet", "Jimmy Buffet", True],
                ["Ching Yu Chan", "Chingyu Chan", True],
                ["Jane Doe", "Jane Anne Doe", True],
                ["Victor Von Victor", "Richard R Richard", False],
                ["Peggy Sue", "Betty White", False],
                ["Rodger Rabbit", "Rodger Bunny", False],
                ["Peter Lowenbrau Griffin", "Lois Patrice Griffin", False],
                ["Peter Lowenbrau Griffin", "Peter L Griffin", True],
                ["Lois P Griffin", "Lois Patrice Griffin", True],
                ["Peta Griffin", "Peter Griffin", False],
                ["Victor Griffin", "Lois Griffin", False],
                ["Natalie Portman", "Nathan Portman", False],
                ["Natasha Romanoff", "Tash Romanoff", True],
                ["Andi Warhog", "ANDY WARHOL", False],
                ["Mr Donald Duck", "DUCK DONALD", True],
                ["Jim Jones", "Mr Jim Jones", True]
            ]
        with open("example.json", "w+") as jsonfile:
            json.dump(matches, jsonfile, indent=4)

