# Author: Akhil Krishna Mohan

import random


class DNA(object):
    alphabet_pool = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST ,.?!'  # All characters in use

    def __init__(self, first_parent=None, second_parent=None, max_length=5):
        self.code = []  # Sequence of "genes"
        self.str_len = 0
        if first_parent is None and second_parent is None:
            self.generate_randomly(max_length=max_length)
        else:
            self.generate_from_parents(first_parent, second_parent)

    def generate_randomly(self, max_length=5):
        self.str_len = max_length
        for counter in range(self.str_len):
            self.code.append(self.random_char())

    def generate_from_parents(self, first_parent, second_parent, max_length=5):
        assert type(first_parent) == Individual
        assert type(second_parent) == Individual

        first_strand = first_parent.DNA
        second_strand = second_parent.DNA

        if len(second_strand) < len(first_strand):  # Ensures that the longer one comes second
            first_strand, second_strand = second_strand, first_strand

        # The following code was meant for variable length strings
        # TODO implement variable length strings
        self.str_len = max_length
        pivot = random.randint(0, len(first_strand) - 1)

        last_index = min(max_length, len(second_strand))

        for index in range(last_index):
            if index <= pivot:
                self.code.append(first_strand[index])

            else:
                self.code.append(second_strand[index])

        for index in range(last_index, self.str_len):
            self.code.append(self.random_char())

    def mutate(self, mutation_rate=0.15):
        index = 0
        # While loop because the mutations are supposed to include deletions
        # TODO support for variable length strings
        while index < len(self.code):
            decider = random.random()
            if decider < mutation_rate:
                self.code[index] = self.random_char()
            index += 1

    @staticmethod
    def random_char():
        return DNA.alphabet_pool[random.randint(0, len(DNA.alphabet_pool) - 1)]

    def __len__(self):
        return len(self.code)

    def __getitem__(self, item):
        return self.code[item]

    def __str__(self):
        return ''.join(self.code)


class Individual(object):
    def __init__(self, target, first_parent=None, second_parent=None, max_length=5):
        # Ignore the hard-coded max_length (for variable length strings)
        self.target = target
        if first_parent is None and second_parent is None:
            self.DNA = DNA(max_length=len(self.target))
        else:
            self.DNA = DNA(first_parent=first_parent, second_parent=second_parent, max_length=len(self.target))

        self.cached_fitness = None  # To avoid unnecessary computation

    @property
    def fitness(self):
        # Counts number of characters in target that were matched, divides by length of word
        # Fitness = characters matched / length of word
        if self.cached_fitness:
            return self.cached_fitness

        counter = 0
        # Has to deal with variable length strings
        # TODO
        min_len = min(len(self.target), len(self.DNA))
        for index in range(min_len):
            char = self.target[index]
            if char == self.DNA[index]:
                counter += 1

        self.cached_fitness = float(counter) / len(self.DNA)
        return self.cached_fitness

    def mutate(self):
        self.DNA.mutate()

    def __str__(self):
        return str(self.DNA)


class Population(object):
    def __init__(self, size, target, past_population=None):
        self.size = size
        self.target = target
        self.individuals = []
        if not past_population:  # If there isn't a past population to generate from, generate at random
            self.generate_random()
        else:
            self.generate_from_past(past_population)

        self.cached_max_fitness = None  # Save computation
        self.cached_repr = None  # Save computation

    @property
    def max_fitness(self):
        if self.cached_max_fitness:
            return self.cached_max_fitness

        self.cached_max_fitness = max([individual.fitness for individual in self.individuals])
        return self.cached_max_fitness

    def generate_random(self):
        for index in range(self.size):
            self.individuals.append(Individual(self.target, max_length=len(self.target)))

    def generate_from_past(self, past_population):
        assert type(past_population) == Population
        past_individuals = past_population.individuals
        max_fitness = past_population.max_fitness

        parents_list = []  # Weighted (based on fitness) list of parents

        for individual in past_individuals:
            # Add a weighted number of copies of an individual to the parents list
            temp = [individual for count in range(int(individual.fitness / (max(max_fitness, 0.1))))]
            parents_list.extend(temp)

        # If all the fitnesses were 0, just use the past individuals list and hope that mutation saves your ass

        if not parents_list:
            parents_list = list(past_individuals)

        # Pick the parents, generate the children
        for counter in range(self.size):
            first_parent = parents_list[random.randint(0, len(parents_list) - 1)]
            second_parent = parents_list[random.randint(0, len(parents_list) - 1)]
            self.individuals.append(
                Individual(target=self.target, first_parent=first_parent, second_parent=second_parent,
                           max_length=len(self.target)))
            self.individuals[-1].mutate()

    def evaluate(self, min_fitness=0.99):
        # Check if all members of population are sufficiently close to target
        # for individual in self.individuals:
        #     if individual.fitness < min_fitness:
        #         return False
        # return True
        # Use below code to stop at the first good match
        if self.max_fitness >= min_fitness:
            return True
        return False

    def __str__(self):
        if self.cached_repr:
            return self.cached_repr
        self.cached_repr = ''
        for individual in self.individuals:
            self.cached_repr += str(individual) + '\n'
        return self.cached_repr


def reach_target(target, size=5):
    # Rudimentary function to actually test things
    pop = Population(size, target)
    print pop, '\n'
    i = 1
    while True:
        pop = Population(size, target, past_population=pop)
        if pop.evaluate():
            print pop
            print 'Generation: ', i + 1
            break
        i = i + 1
        print pop, '\n'


if __name__ == '__main__':
    reach_target("logos", size=15)
