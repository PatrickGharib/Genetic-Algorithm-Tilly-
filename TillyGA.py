import itertools
import random
import math
import sys
import operator

FOUNTAIN_SIZE = 12 * 12
MAX_GENERATIONS = 1000
POPULATION_SIZE = 1000
MUTATION_RATE = 70
# states will be (center, up, down, left, right)
STATES = []



def main():

    # pre compute possible situations that tilly can be in
    generate_states()
    pool = initialize_population()

    # out stdout to file
    # sys.stdout = open('output.txt', 'w')
    # initialize best tilly genome
    best_overall_tilly = {"fitness": 0}
    previous_best = -math.inf
    best_overall_fitness = -math.inf

    #  begin genetic algorithm
    for i in range(MAX_GENERATIONS):
        # keep track of the best generation tilly
        best_gen_tilly = {}
        generation_best = -math.inf
        # test each tilly in a generation
        for tilly in pool:
            tilly = evaluate_fitness(tilly)
            fitness = tilly["fitness"]
            # keep track of the best fitness score by any tilly
            if fitness >= previous_best:
                best_overall_fitness = fitness
                previous_best = best_overall_fitness
                best_overall_tilly.update(tilly)
            # update the best tilly in a generation
            if fitness >= generation_best:
                best_gen_tilly.update(tilly)
                generation_best = fitness
        # calculate the avg fitness for the current generation
        raw_fitness = [sub["fitness"] for sub in pool]
        sum_fitness = sum(raw_fitness) / POPULATION_SIZE
        #  best fitness value so far
        print("Current Generation:", i, ", Best Generational Fitness:", best_gen_tilly["fitness"],
              ", Generation AVG:", sum_fitness, ", Best Fitness yet :", best_overall_fitness)
        # returned pool is the next generation of tilly's
        pool = selection(pool)

    print(best_overall_tilly)
    # test the best genome against 5000 fountains and output result to file.
    test_best_tilly(best_overall_tilly)


def make_fountain():
    # fountain size is 10 x10 with boundries its 12 x 12
    fountain = [0] * FOUNTAIN_SIZE
    # in board 1 = good , 2 = bad, 3 = out of bounds
    for i in range(0, FOUNTAIN_SIZE):
        board_edge = i % 12
        # set out of bounds
        if i < 12\
                or board_edge == 0\
                or board_edge == 11\
                or i > 132:
            fountain[i] = 3
        else:
            fountain[i] = random.randrange(1, 3)
    return fountain


def generate_states():
    # create possible tilly neighbourhood states
    # (1 = good tile, 2 = bad tile, 3 = out of bounds tiles)
    for j in itertools.product([1, 2, 3], repeat=5):
        # filter out the case where there are out of bounds in 4 directions, it will never happen
        # that case will be if tilly goes to a board corner but tilly can't do that since tilly is
        # forced to return within bounds if it leave play area
        if j.count(3) > 2:
            continue
        # convert tuple to int to use as key in chromosome
        state_gen = list(j)
        state_key = int(''.join(map(str, state_gen)))
        STATES.append(state_key)


def initialize_population():
    pool = []*POPULATION_SIZE
    # generate initial population of tilly's
    for i in range(0, POPULATION_SIZE):
        generation = {}
        # generate situation action pairs
        for j in STATES:
            generation[j] = random.randint(0, 6)
        generation["fitness"] = 0
        pool.append(generation)
    return pool


def evaluate_fitness(current_tilly):
    # [top left, top right, bottom left, bottom right]
    current_fountain = make_fountain()
    tilly_position = random.choice([13, 22, 121, 130])
    # battery runs out in 200 moves
    for j in range(200):
        situation = get_tilly_von_neumann(current_fountain, tilly_position)
        action = current_tilly[situation]
        fitness, current_fountain, tilly_position = do_action_for_tilly(action, current_tilly["fitness"],
                                                                        current_fountain, tilly_position)
        current_tilly["fitness"] = fitness
    return current_tilly

def get_tilly_von_neumann(current_fountain, tilly_position):
    von_nuemann = ""
    von_nuemann += str(current_fountain[tilly_position])  # current tile you are on
    von_nuemann += str((current_fountain[(tilly_position - 12) % 144]))  # above
    von_nuemann += str((current_fountain[(tilly_position + 12) % 144]))  # below
    von_nuemann += str(current_fountain[tilly_position - 1])  # left
    von_nuemann += str(current_fountain[tilly_position + 1])  # right
    return int(von_nuemann)


def do_action_for_tilly(action, fitness, current_fountain, tilly_position):
    previous_tilly_position = tilly_position
    if action == 0:  # do nothing
        pass
    elif action == 1:
        tilly_position -= 12  # move up
    elif action == 2:
        tilly_position += 1  # move right
    elif action == 3:
        tilly_position += 12  # move down
    elif action == 4:
        tilly_position -= 1  # move left
    elif action == 5:
        tilly_position += random.choice([1, 12, -1, -12])  # move in a random direction
    else:
        if current_fountain[tilly_position] == 1: # good tile replacement
            fitness -= 1
        elif current_fountain[tilly_position] == 2: # bad tile replacement
            fitness += 10
        current_fountain[tilly_position] = 1 # replace the tile

    if current_fountain[tilly_position] == 3: # check if on boundry tile
        tilly_position = previous_tilly_position # move tilly back to board space
        fitness -= 5

    return fitness, current_fountain, tilly_position


def crossover(parent_1, parent_2):
    child = {}
    # go through parent genes pick one at rand
    # minus 1 to take into consideration that fitness is included in the dictionary
    for i in range(0, len(parent_1)-1):
        coin_flip = random.randrange(0, 100)
        if coin_flip < 50:
            key = STATES[i]
            child[key] = parent_1[key]
        else:
            key = STATES[i]
            child[key] = parent_2[key]
    child["fitness"] = 0
    return child


def mutate(tilly_to_mutate):
    # check to mutate
    # todo take this out and retest as i didnt realise that i check mutation rate twice
    if MUTATION_RATE < random.randrange(0, 100):
        # pick a random situation to mutate the action taken in that instance
        situation_to_mutate = random.randrange(0, len(STATES))
        tilly_to_mutate[STATES[situation_to_mutate]] = random.randrange(0, 7)
    return tilly_to_mutate


def selection(pool):
    new_pool = []
    #  sort tillys based on fitness increasing to decreasing
    sorted_pool = sorted(pool, key = lambda i: i["fitness"])
    raw_fitness = [sub["fitness"] for sub in sorted_pool]
    elite_tilly_index = raw_fitness.index(max(raw_fitness))
    sorted_pool[elite_tilly_index]["fitness"] = 0

    # create prob dist for roulette style selection
    # fitness is skewed so that there are no negative numbers in the distribution
    skew_factor = abs(min(raw_fitness))
    skewed_fitness = [skew_factor + i for i in raw_fitness]
    sum_fitness = sum(skewed_fitness)
    weight_dist = [i/sum_fitness for i in skewed_fitness]

    #  automatically throw the best gene into the next generation
    new_pool.append(sorted_pool[elite_tilly_index])
    #  pick parents to breed from top 15%
    for i in range(POPULATION_SIZE-1):

        # elite style selection, strong live, the weak perish
        # parent_1 = random.choice(sorted_pool[POPULATION_SIZE - (math.floor(POPULATION_SIZE*.15)):])

        parent_1, parent_2 = random.choices(sorted_pool[(math.floor(POPULATION_SIZE*.85)):],weights=weight_dist[(math.floor(POPULATION_SIZE*.85)):],k=2)

        # equal selection rate
        # parent_2 = weighted_choice(sorted_pool)

        # roulette selection for parent 2
        # parent_2 = weighted_choice(sorted_pool, weight_dist)

        child = crossover(parent_1, parent_2)
        #decide if you want to mutate
        if (MUTATION_RATE > random.randrange(0,100)):
            child = mutate(child)
        new_pool.append(child)

    return new_pool


def test_best_tilly(tilly):
    score = []
    count = {}
# sys.stdout = open('bestTillyTesting.txt', 'w')
    # for i in range(500):
    print("NOW TESTING SOLUTION AGAINST 5000 RANDOM FOUNTAINS...")
    for i in range(5000):
        tilly["fitness"] = 0
        score.append(evaluate_fitness(tilly)["fitness"])
    score.sort()
        # for i in score:
        #     count[i] = score.count(i)
        # print("avg score during test:", sum(score)/len(score))
        # count_sort = sorted(count.items(), key=operator.itemgetter(1))
        # print("number of times score achieved(SCORE ACHIEVED, # OF TIMES ACHIEVED):\n", count_sort)
        # print("unsorted count:\n", count)
        # print("-----------------------------------------------------------------------------------------------------------------"
        #       "-----------------------------------------------------------------------------------------------------------------"
        #       "-----------------------------------------------------------------------------------------------------------------")
        # count.clear()
        # score.clear()
    sys.stdout = open(('average_score' + str(sum(score)/len(score)) + 'num_generations'+ str(MAX_GENERATIONS) +'.txt'), 'w')
    del tilly["fitness"]
    print(tilly)

# 1000 generations
# test_best_tilly({'fitness': 720, 11111: 1, 11112: 2, 11113: 4, 11121: 4, 11122: 2, 11123: 4, 11131: 3, 11132: 2, 11133: 4, 11211: 3, 11212: 3, 11213: 3, 11221: 3, 11222: 1, 11223: 4, 11231: 3, 11232: 3, 11233: 5, 11311: 2, 11312: 2, 11313: 1, 11321: 1, 11322: 4, 11323: 1, 11331: 2, 11332: 2, 12111: 1, 12112: 2, 12113: 1, 12121: 1, 12122: 1, 12123: 1, 12131: 2, 12132: 2, 12133: 4, 12211: 3, 12212: 2, 12213: 1, 12221: 4, 12222: 4, 12223: 5, 12231: 3, 12232: 5, 12233: 0, 12311: 1, 12312: 2, 12313: 1, 12321: 4, 12322: 2, 12323: 1, 12331: 1, 12332: 5, 13111: 4, 13112: 2, 13113: 4, 13121: 4, 13122: 4, 13123: 4, 13131: 3, 13132: 2, 13211: 3, 13212: 2, 13213: 3, 13221: 3, 13222: 3, 13223: 3, 13231: 3, 13232: 2, 13311: 1, 13312: 6, 13321: 3, 13322: 1, 21111: 6, 21112: 6, 21113: 6, 21121: 6, 21122: 6, 21123: 6, 21131: 6, 21132: 6, 21133: 6, 21211: 6, 21212: 6, 21213: 6, 21221: 6, 21222: 2, 21223: 6, 21231: 6, 21232: 2, 21233: 4, 21311: 6, 21312: 6, 21313: 6, 21321: 6, 21322: 4, 21323: 6, 21331: 6, 21332: 6, 22111: 6, 22112: 2, 22113: 6, 22121: 6, 22122: 5, 22123: 6, 22131: 6, 22132: 2, 22133: 2, 22211: 6, 22212: 1, 22213: 5, 22221: 1, 22222: 6, 22223: 5, 22231: 6, 22232: 3, 22233: 5, 22311: 6, 22312: 6, 22313: 6, 22321: 1, 22322: 6, 22323: 6, 22331: 1, 22332: 6, 23111: 6, 23112: 6, 23113: 6, 23121: 6, 23122: 6, 23123: 6, 23131: 6, 23132: 6, 23211: 6, 23212: 6, 23213: 6, 23221: 6, 23222: 6, 23223: 4, 23231: 6, 23232: 6, 23311: 6, 23312: 0, 23321: 6, 23322: 0, 31111: 3, 31112: 2, 31113: 1, 31121: 3, 31122: 4, 31123: 0, 31131: 0, 31132: 1, 31211: 2, 31212: 2, 31213: 0, 31221: 3, 31222: 3, 31223: 6, 31231: 0, 31232: 0, 31311: 6, 31312: 0, 31321: 6, 31322: 5, 32111: 3, 32112: 5, 32113: 3, 32121: 6, 32122: 4, 32123: 1, 32131: 3, 32132: 6, 32211: 1, 32212: 6, 32213: 1, 32221: 0, 32222: 4, 32223: 5, 32231: 0, 32232: 3, 32311: 2, 32312: 1, 32321: 0, 32322: 5, 33111: 2, 33112: 1, 33121: 5, 33122: 5, 33211: 1, 33212: 1, 33221: 0, 33222: 4}
#  )

# 500 generations
# test_best_tilly({'fitness': 620, 11111: 5, 11112: 5, 11113: 3, 11121: 4, 11122: 5, 11123: 4, 11131: 1, 11132: 2, 11133: 2, 11211: 3, 11212: 3, 11213: 5, 11221: 3, 11222: 5, 11223: 4, 11231: 1, 11232: 1, 11233: 2, 11311: 1, 11312: 2, 11313: 5, 11321: 1, 11322: 2, 11323: 5, 11331: 2, 11332: 2, 12111: 1, 12112: 1, 12113: 1, 12121: 1, 12122: 1, 12123: 1, 12131: 1, 12132: 1, 12133: 2, 12211: 1, 12212: 1, 12213: 5, 12221: 4, 12222: 1, 12223: 3, 12231: 5, 12232: 2, 12233: 4, 12311: 1, 12312: 2, 12313: 1, 12321: 5, 12322: 5, 12323: 4, 12331: 2, 12332: 2, 13111: 2, 13112: 2, 13113: 3, 13121: 4, 13122: 5, 13123: 4, 13131: 2, 13132: 2, 13211: 3, 13212: 3, 13213: 3, 13221: 4, 13222: 4, 13223: 4, 13231: 5, 13232: 2, 13311: 6, 13312: 6, 13321: 4, 13322: 6, 21111: 6, 21112: 6, 21113: 6, 21121: 6, 21122: 2, 21123: 6, 21131: 6, 21132: 3, 21133: 1, 21211: 6, 21212: 6, 21213: 3, 21221: 6, 21222: 6, 21223: 6, 21231: 3, 21232: 5, 21233: 0, 21311: 6, 21312: 6, 21313: 6, 21321: 6, 21322: 6, 21323: 6, 21331: 6, 21332: 6, 22111: 6, 22112: 1, 22113: 6, 22121: 6, 22122: 6, 22123: 6, 22131: 6, 22132: 6, 22133: 4, 22211: 6, 22212: 6, 22213: 6, 22221: 1, 22222: 6, 22223: 3, 22231: 6, 22232: 6, 22233: 2, 22311: 1, 22312: 1, 22313: 6, 22321: 5, 22322: 1, 22323: 6, 22331: 6, 22332: 6, 23111: 6, 23112: 6, 23113: 6, 23121: 6, 23122: 5, 23123: 6, 23131: 6, 23132: 6, 23211: 6, 23212: 6, 23213: 6, 23221: 6, 23222: 4, 23223: 6, 23231: 6, 23232: 3, 23311: 0, 23312: 5, 23321: 1, 23322: 0, 31111: 0, 31112: 3, 31113: 0, 31121: 4, 31122: 2, 31123: 3, 31131: 3, 31132: 5, 31211: 4, 31212: 1, 31213: 2, 31221: 4, 31222: 5, 31223: 0, 31231: 4, 31232: 3, 31311: 3, 31312: 3, 31321: 6, 31322: 2, 32111: 3, 32112: 1, 32113: 2, 32121: 5, 32122: 2, 32123: 5, 32131: 4, 32132: 4, 32211: 5, 32212: 5, 32213: 5, 32221: 1, 32222: 0, 32223: 0, 32231: 3, 32232: 6, 32311: 4, 32312: 2, 32321: 5, 32322: 0, 33111: 3, 33112: 2, 33121: 6, 33122: 5, 33211: 0, 33212: 4, 33221: 5, 33222: 6}
# )

# below is the test for the best tilly we've made after 10000 generations
# #test_best_tilly({'fitness': 730,     11111: 1, 11112: 2, 11113: 4, 11121: 4, 11122: 2, 11123: 4, 11131: 3, 11132: 2,
#                  11133: 6, 11211: 3, 11212: 3, 11213: 0, 11221: 3, 11222: 5, 11223: 5, 11231: 3, 11232: 3, 11233: 5,
#                  11311: 2, 11312: 2, 11313: 1, 11321: 0, 11322: 4, 11323: 1, 11331: 2, 11332: 2, 12111: 1, 12112: 2,
#                  12113: 1, 12121: 4, 12122: 2, 12123: 1, 12131: 2, 12132: 3, 12133: 2, 12211: 3, 12212: 3, 12213: 1,
#                  12221: 5, 12222: 4, 12223: 5, 12231: 0, 12232: 1, 12233: 4, 12311: 1, 12312: 2, 12313: 1, 12321: 0,
#                  12322: 5, 12323: 4, 12331: 5, 12332: 2, 13111: 4, 13112: 2, 13113: 4, 13121: 4, 13122: 2, 13123: 4,
#                  13131: 3, 13132: 2, 13211: 3, 13212: 4, 13213: 4, 13221: 4, 13222: 4, 13223: 4, 13231: 3, 13232: 3,
#                  13311: 5, 13312: 0, 13321: 6, 13322: 1, 21111: 6, 21112: 6, 21113: 6, 21121: 6, 21122: 6, 21123: 6,
#                  21131: 6, 21132: 6, 21133: 2, 21211: 6, 21212: 6, 21213: 3, 21221: 6, 21222: 5, 21223: 5, 21231: 6,
#                  21232: 6, 21233: 5, 21311: 6, 21312: 6, 21313: 6, 21321: 4, 21322: 6, 21323: 6, 21331: 6, 21332: 6,
#                  22111: 6, 22112: 6, 22113: 6, 22121: 6, 22122: 6, 22123: 4, 22131: 1, 22132: 5, 22133: 1, 22211: 6,
#                  22212: 6, 22213: 3, 22221: 5, 22222: 5, 22223: 3, 22231: 1, 22232: 1, 22233: 3, 22311: 6, 22312: 6,
#                  22313: 6, 22321: 4, 22322: 4, 22323: 4, 22331: 6, 22332: 6, 23111: 6, 23112: 6, 23113: 6, 23121: 6,
#                  23122: 2, 23123: 6, 23131: 6, 23132: 2, 23211: 6, 23212: 6, 23213: 6, 23221: 6, 23222: 5, 23223: 3,
#                  23231: 6, 23232: 6, 23311: 1, 23312: 3, 23321: 0, 23322: 2, 31111: 4, 31112: 0, 31113: 4, 31121: 6,
#                  31122: 3, 31123: 2, 31131: 1, 31132: 1, 31211: 6, 31212: 3, 31213: 1, 31221: 3, 31222: 2, 31223: 3,
#                  31231: 0, 31232: 5, 31311: 4, 31312: 2, 31321: 6, 31322: 5, 32111: 4, 32112: 5, 32113: 1, 32121: 1,
#                  32122: 4, 32123: 3, 32131: 2, 32132: 5, 32211: 1, 32212: 6, 32213: 3, 32221: 0, 32222: 0, 32223: 4,
#                  32231: 5, 32232: 0, 32311: 6, 32312: 3, 32321: 2, 32322: 3, 33111: 5, 33112: 3, 33121: 3, 33122: 6,
#                  33211: 2, 33212: 5, 33221: 4, 33222: 5})

main()