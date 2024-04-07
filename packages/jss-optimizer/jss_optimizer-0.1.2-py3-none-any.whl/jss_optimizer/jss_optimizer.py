import random
import numpy as np
from tqdm import tqdm
import warnings
warnings.simplefilter("ignore", UserWarning)

class HyperparameterOptimizer:
    def __init__(self, model, params):
        self.model = model
        self.params = params

    def cal_pop_fitness(self, pop, X_train, y_train, X_test, y_test):
        fitness = []
        for i in range(len(pop)):
            if pop[i][1] >= 1:
                classifier = self.model(random_state=42, **{self.params[j]: pop[i][j] for j in range(len(pop[i]))}, oob_score=True)
                classifier.fit(X_train, y_train)
                fitness.append(classifier.score(X_train, y_train))
            else:
                fitness.append(0)
        return fitness

    def select_mating_pool(self, pop, fitness, num_parents):
        parents = np.empty((num_parents, pop.shape[1]))
        for parent_num in range(num_parents):
            max_fitness_idx = np.argmax(fitness)
            parents[parent_num, :] = pop[max_fitness_idx, :]
            fitness[max_fitness_idx] = -99999
        return parents

    def crossover(self, parents, offspring_size):
        offspring = np.empty(offspring_size)
        crossover_point = np.uint8(offspring_size[1] / 2)

        for k in range(offspring_size[0]):
            parent1_idx = k % parents.shape[0]
            parent2_idx = (k + 1) % parents.shape[0]
            offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
            offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
        return offspring

    def mutation(self, offspring_crossover, num_mutations=1):
        mutations_counter = np.uint8(offspring_crossover.shape[1] / num_mutations)

        for idx in range(offspring_crossover.shape[0]):
            gene_idx = mutations_counter - 1
            for mutation_num in range(num_mutations):
                random_value = np.random.randint(1, 6)
                offspring_crossover[idx, gene_idx] = offspring_crossover[idx, gene_idx] + random_value
                gene_idx = gene_idx + mutations_counter
        return offspring_crossover

    def optimize(self, X_train, y_train, X_test, y_test, sol_per_pop=5, num_parents_mating=3, num_generations=100):
        pop_size = (sol_per_pop, len(self.params))
        new_population = np.random.randint(low=1, high=(20 - 4), size=pop_size)

        best_solution = None
        best_fitness = float('-inf')
        print("\n")
        for generation in tqdm(range(num_generations)):
            fitness = self.cal_pop_fitness(new_population, X_train, y_train, X_test, y_test)
            best_fitness_in_gen = max(fitness)
            if best_fitness_in_gen > best_fitness:
                best_fitness = best_fitness_in_gen
                best_solution = new_population[np.argmax(fitness)]

            parents = self.select_mating_pool(new_population, fitness, num_parents_mating)
            offspring_crossover = self.crossover(parents, offspring_size=(pop_size[0] - parents.shape[0], len(self.params)))
            offspring_mutation = self.mutation(offspring_crossover, num_mutations=2)
            new_population[0:parents.shape[0], :] = parents
            new_population[parents.shape[0]:, :] = offspring_mutation
        print("\nFinished applying genetic algorithm.")
        print("Score of the best candidates after parameter optimizing with genetic algorithm: ", best_fitness)
        return best_solution

    def objective_function(self, combination, X_train, y_train, X_test, y_test):
        classifier = self.model(random_state=42, **{self.params[j]: combination[j] for j in range(len(combination))}, oob_score=True)
        classifier.fit(X_train, y_train)
        return classifier.score(X_test, y_test)

    def simulate_annealing(self, start_solution, X_train, y_train, X_test, y_test, T=10, T_min=0.001, alpha=0.99):
        print("Appplying Simulated Annealing to optimize by escaping local optimas ... \n")
        combination = start_solution.copy()
        with tqdm(total=int((T-T_min)/alpha)) as pbar:
            while T > T_min:
                new_combination = combination.copy()
                i = random.randint(0, len(combination) - 1)
                new_combination[i] = random.randint(1, 20)
                delta_E = self.objective_function(new_combination, X_train, y_train, X_test, y_test) - self.objective_function(combination, X_train, y_train, X_test, y_test)
                if delta_E > 0:
                    combination = new_combination
                else:
                    p = np.exp(delta_E / T)
                    if random.uniform(0, 1) < p:
                        combination = new_combination
                T *= alpha
                pbar.update(1)
        print("\nScore of the best candidates after parameter optimizing with GA-SA algorithm:  ", self.objective_function(combination, X_train, y_train, X_test, y_test))
        return combination


