import random
import matplotlib.pyplot as plt
from deap import base, creator, tools, algorithms

# Define the problem
CITIES = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(10)]

# Create the fitness and individual classes
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialize the toolbox
toolbox = base.Toolbox()
toolbox.register("indices", random.sample, range(len(CITIES)), len(CITIES))
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Define the fitness function
def evalTSP(individual):
    distance = 0
    for i in range(len(individual)):
        city1 = CITIES[individual[i-1]]
        city2 = CITIES[individual[i]]
        distance += ((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)**0.5
    return distance,

toolbox.register("evaluate", evalTSP)
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# Genetic Algorithm parameters
POPULATION_SIZE = 300
P_CROSSOVER = 0.7
P_MUTATION = 0.2
MAX_GENERATIONS = 50

# Run the Genetic Algorithm
population = toolbox.population(n=POPULATION_SIZE)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("min", np.min)
stats.register("avg", np.mean)

population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION, ngen=MAX_GENERATIONS, stats=stats, verbose=True)

# Plot the convergence
min_fitness_values = logbook.select("min")
avg_fitness_values = logbook.select("avg")

plt.plot(min_fitness_values, label='Minimum Fitness')
plt.plot(avg_fitness_values, label='Average Fitness')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Convergence of Genetic Algorithm')
plt.legend()
plt.show()