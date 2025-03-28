from json.decoder import JSONDecodeError
from core.utils.last_generation_manager import Last_Generation
import random
import json
from pathlib import Path
from os.path import join


class GeneticAlgorithm:
    """Classe Base para a execução do algoritmo genetico

        Args:
            fitness_input_gatherer (function): Uma função que retorna o conjunto de dados usados para avaliar o fitness
            good_generations (int, optional): Quantidade necessária de gerações boas para o algoritmo parar por conta própria. Defaults to 3.
            weight_range (tuple, optional): Valores mínimos e máximos que um gene poderá ter quando for gerado aleatoriamente. Defaults to (-10, 10).
            mutation_chance (int, optional): Chance, em porcentagem, de uma mutação acontecer em um gene na hora da reprodução. Defaults to 1.
            mutation_magnitude (tuple, optional): Define o valor mínimo e máximo para ser somado em um gene na hora da mutação. Defaults to (-1, 1).
            chromosome_size (int, optional): Quantidade de genes presentes em um cromossomo. Defaults to 9.
            population_size (int, optional): Quantidade de indivíduos por geração. Defaults to 50.
            max_generations (int, optional): Quantidade de gerações pela qual o algoritmo vai passar antes de ser interrompido. Defaults to 100.
            fitness_input_size (int, optional): Quantidade de valores que serão usados para avaliar cada cromossomo cada vez. Defaults to 100.
    """

    def __init__(self,
                 fitness_input,
                 good_generations=3,
                 weight_range=(-10, 10),
                 mutation_chance=1,
                 mutation_magnitude=(-1, 1),
                 chromosome_size=11,
                 population_size=50,
                 max_generations=100,
                 persistent_individuals=5,
                 random_individuals=5,
                 timestamp=-1,
                 generate_new_population=False
                 ):
        try:
            self.fitness_input = fitness_input
            self.persistent_individuals = persistent_individuals + \
                1 if persistent_individuals % 2 != 0 else persistent_individuals
            self.random_individuals = random_individuals + \
                1 if random_individuals % 2 != 0 else random_individuals
            self.last_generation = Last_Generation()
        except Exception as e:
            raise(e)
        else:
            self.target_good_generations = good_generations

            # Define o quanto os pesos vão influenciar nos atributos
            self.weight_range = weight_range
            self.mutation_chance = mutation_chance
            self.mutation_magnitude = mutation_magnitude
            self.chromosome_size = chromosome_size

            # x na primeira geração, nas outras vira 2x
            self.population_size = population_size
            self.max_generations = max_generations
            self.generate_new_population = generate_new_population
            self.fitness_input_size = len(self.fitness_input)
            self.consecutive_good_generations = 0
            self.ranked_population = []
            self.population = []
            self.highest_fitness = -1
            self.current_generation = 0

            # Coisas para o json
            self.timestamp = str(timestamp).replace(
                " ", "--").replace(":", "-").split(".")[0]

    def get_first_generation(self):
        """Inicializa a população do algoritmo genético. Vê se existem dados de uma população já guardados,
        se não existir ou se a população for menor do que o necessário, gera indivíduos aleatórios para preencher
        o que precisa.

        Returns:
            list: Primeira geração para o algoritmo genético
        """
        previous_generation = []
        try:
            # Solução rápida pro problema dos cromossomos de uma geração anterior serem de tamanhos diferentes
            # do que o tamanho que a gente quer.
            if(len(self.last_generation.previous_generation[0]) == self.chromosome_size and not self.generate_new_population):
                previous_generation = self.last_generation.previous_generation
        except Exception:
            pass
        finally:
            if(len(previous_generation) < self.population_size):
                # Population less than the expected, solving...
                for _ in range(self.population_size - len(previous_generation)):
                    chromosome = self.generate_random_chromosome()
                    previous_generation.append(chromosome)
        return previous_generation

    def random_population(self):
        """Preenche uma população com indivíduos gerados aleatoriamente

        Returns:
            (list): População preenchida com os indivíduos lindinhos

        Complexidade: O(p*c)
            p = Tamanho desejado da população
            c = Tamanho de cada cromossomo
        """
        return [self.generate_random_chromosome() for _ in range(self.population_size)]

    def generate_random_chromosome(self) -> list:
        """Preenche um cromossomo com valores, cujos mínimos e máximos são definidos por weight_range

        Returns:
            list: Cromossomo preenchido
        """
        return [random.uniform(self.weight_range[0], self.weight_range[1]) for _ in range(self.chromosome_size)]

    def check_for_break(self, population: list):
        """Parece meio inútil porque só chama outra função mas o propósito dela é
        ser extendida caso quisermos fazer com que o algoritmo pare com condições mais elaboradas.

        Args:
            population (list): A população a ser avaliada

        Returns:
            bool: True se o algoritmo genético estiver pronto para ser parado
        """

        return self.evaluate_population(population)

    def evaluate_population(self, population: list) -> bool:
        """Julga se uma lista de indivíduos é boa ou não segundo os critérios
        definidos dentro dela. Por enquanto o critério é 1/10 da população ter
        uma pontuação de 0, ou seja, 10 conjuntos de pesos acertarem todas as
        partidas (talvez seja meio exigente).

        Args:
            population (list): A lista a ser avaliada;

        Returns:
            bool: True se a população for boa segundo os critérios;

        Complexidade: O(p)
            p = Quantidade de indivíduos na população
        """

        # TODO pensar num jeito melhor de avaliar a população

        good_individuals = 0
        for individual in population:
            good_individuals += individual[1] > 70

        is_population_good = good_individuals >= int(len(population)/10)

        if(is_population_good):
            self.consecutive_good_generations += 1
        else:
            self.consecutive_good_generations = 0

        return is_population_good

    def apply_fitness(self, population: list, fitness_input):
        """Recebe uma população de cromossomos e calcula o fitness para cada um deles

        Args:
            population (list): A população com cromossomos
            fitness_input_gatherer (function): A função usada para gerar os dados com os quais
            cada cromossomo será avaliado

        Returns:
            list: Uma população ordenada, contendo (indivíduo, fitness)
        """

        ranked_population = []

        for individual in population:
            fitness_value = self.calculate_fitness(
                individual, fitness_input)

            scored_individual = (individual, fitness_value)

            ranked_population.append(scored_individual)

        ranked_population.sort(key=lambda element: element[1], reverse=True)

        return ranked_population

    def calculate_fitness(self, chromosome: list, match_data: dict):
        """Calcula o valor de fitness de um cromossomo.
        Obs.: Por enquanto tá extremamente mal otimizado
        Sugestão: Registrar um erro do vetor de pesos apenas se tiver
        uma diferença considerável entre as pontuações dos 2 times

        Args:
            chromosome (list): O cromossomo a ser avaliado;
            match_data (dict): Os dados verdadeiros dos jogos para comparar com o cromossomo;

        Returns:
            fitness (int): O fitness do cromossomo, equivalente à porcentagem de partidas acertadas;

        Complexidade: O(m):
            m: Quantidade de partidas presentes em match_data
        """

        wrong_predictions = 0
        for current_match in match_data:
            predicted_1q_winner = self.predict_match(chromosome, current_match)[
                "predicted_1q_winner"]
            real_1q_winner = "team_home" if current_match["home_won"] else "team_away"

            # 1 se for True, 0 se for False
            wrong_predictions += int(real_1q_winner != predicted_1q_winner)

        fitness_value = ((self.fitness_input_size -
                          wrong_predictions) * 100)/self.fitness_input_size

        return fitness_value

    def predict_match(self, chromosome, current_match):
        home_team_stats = current_match["team_home"]
        home_team_parsed_stats = []
        for gene_index, stats in enumerate(home_team_stats):
            try:
                home_team_parsed_stats.append(
                    home_team_stats[stats] * chromosome[gene_index])

            except TypeError:
                home_team_parsed_stats.append(chromosome[gene_index])

        away_team_stats = current_match["team_away"]
        away_team_parsed_stats = []
        for gene_index, stats in enumerate(away_team_stats):
            try:
                away_team_parsed_stats.append(
                    away_team_stats[stats] * chromosome[gene_index])
            except TypeError:
                away_team_parsed_stats.append(chromosome[gene_index])

        home_team_score = sum(home_team_parsed_stats)
        away_team_score = sum(away_team_parsed_stats)
        score_difference = abs(home_team_score - away_team_score)

        predicted_1q_winner = "team_home" if home_team_score > away_team_score else "team_away"

        higher_score = home_team_score if predicted_1q_winner == "team_home" else away_team_score
        score_difference_percentage = (100 * score_difference)/higher_score

        prediction_results = {
            "predicted_1q_winner": predicted_1q_winner,
            "home_team_score": home_team_score,
            "away_team_score": away_team_score,
            "score_difference": score_difference,
            "score_difference_percentage": score_difference_percentage,
        }

        return prediction_results

    def reproduce_population(self, ranked_population: list, population_size: int):
        """Função responsável por delegar a reprodução de uma geração a outras
        funções mais específicas

        Args:
            ranked_population (list): Uma lista de indivíduos com seus pesos
            population_size (int): O tamanho desejado para a população.

        Returns:
            [list]: Uma lista com novos indivíduos após a reprodução ter acontecido.
        """

        reproduced_population = []

        for _ in range(int((population_size - self.persistent_individuals - self.random_individuals)/2)):
            parent1 = self.weighted_choice(ranked_population)
            parent2 = self.weighted_choice(ranked_population)

            child1, child2 = self.crossover(parent1, parent2)

            reproduced_population.append(self.mutation(child1))
            reproduced_population.append(self.mutation(child2))

        for i in range(self.persistent_individuals):
            reproduced_population.append(ranked_population[i][0])
        for i in range(self.random_individuals):
            reproduced_population.append(self.generate_random_chromosome())

        return reproduced_population

    @staticmethod
    def weighted_choice(weighted_items):
        """Escolhe um item dentro de uma lista com os itens e seus pesos,
        dando prioridade para itens com peso maior

        Args:
            weighted_items ([list]): Uma lista contendo itens no formato (item, peso)

        Returns:
            item: O item escolhido a partir do peso
        """

        total_weight = sum((item[1] for item in weighted_items))
        element = random.uniform(0, total_weight)
        for item, weight in weighted_items:
            if element < weight:
                return item
            element = element - weight
        return item

    def crossover(self, parent1: list, parent2: list):
        """Recebe os genes de dois pais, realiza o crossing-over e
        retorna dois filhos

        Args:
            parent1 (list): Um dos indivíduos cujos genes serão repassados
            parent2 (list): O outro indivíduo cujos genes serão repassados

        Returns:
            ([list],[list]): Os dois filhos gerados a partir dos pais
        """

        split_point = int(random.random() * self.chromosome_size)

        return (parent1[:split_point] + parent2[split_point:],
                parent2[:split_point] + parent1[split_point:])

    def mutation(self, chromosome: list):
        """Percorre por todos os genes de um cromossomo recebido, e,
        dada uma chance definida por GeneticAlgorithm.mutation_chance,
        vai adicionar um valor aleatório entre os valores de self.mutation_magnitude
        ao gene do cromossomo original

        Args:
            chromosome (list): O cromossomo a ser percorrido

        Returns:
            [list]: O cromossomo após ter passado pelo processo de mutação
        """

        mutated_chromosome = []
        for i in range(self.chromosome_size):

            mutation_happening = random.random() * 100

            if int(mutation_happening < self.mutation_chance):
                mutation = random.uniform(
                    self.mutation_magnitude[0], self.mutation_magnitude[1])

                # Mutação vira 0 se o cromossomo tiver atingido o limite de peso
                mutation *= self.weight_range[0] <= chromosome[i] + \
                    mutation <= self.weight_range[1]

                mutated_chromosome.append(chromosome[i] + mutation)
            else:
                mutated_chromosome.append(chromosome[i])

        return mutated_chromosome

    def log_and_dump_data(self, timestamp=-1, elapsed_time=-1):
        """Salva os dados do algoritmo genético no arquivo genetic_algorithm.log
        e guarda a última geração do algoritmo no arquivo last_generation.txt

        Args:
            timestamp (int, optional): Momento em que os dados foram salvos. Defaults to -1.
            elapsed_time (int, optional): Tempo que o algoritmo genético demorou para ser concluído. Defaults to -1.
        """

        print("Algorithm Stopped!")

        log_file = open(join(Path(__file__).resolve().parent.parent.parent.parent,
                             'data', 'logs', 'genetic_algorithm.log'), "a")

        log_file.write(f"\n\nTimestamp: {timestamp}")
        log_file.write(
            f"\nGenetic Algorithm exited in {elapsed_time} seconds.")
        log_file.write(f"\n{self.current_generation} generations passed.")
        log_file.write(f"\n\tGenetic Algorithm Parameters:")
        log_file.write(f"\n\t\tfitness_input_size: {self.fitness_input_size}")
        log_file.write(
            f"\n\t\tgood_generations: {self.target_good_generations}")
        log_file.write(f"\n\t\tnew_weight_range: {self.weight_range}")
        log_file.write(f"\n\t\tmutation_chance: {self.mutation_chance}")
        log_file.write(f"\n\t\tmutation_magnitude: {self.mutation_magnitude}")
        log_file.write(f"\n\t\tchromosome_size: {self.chromosome_size}")
        log_file.write(f"\n\t\tpopulation_size: {self.population_size}")
        log_file.write(f"\n\t\tmax_generations: {self.max_generations}")
        log_file.write(
            f"\n\t\tconsecutive_good_generations: {self.consecutive_good_generations}")
        log_file.write(
            f"\n\tGenetic Algorithm Output:\n\tFinal Score: {self.ranked_population[0][1]}%")
        log_file.write(f"\n\tHighest Fitness: {self.highest_fitness}")
        match_data = self.fitness_input[0]
        for index, stat in enumerate(match_data["team_home"]):
            try:
                log_file.write(
                    f"\n\t\t{stat}: {self.ranked_population[0][0][index]}")
            except IndexError:
                pass
        log_file.close()
        self.last_generation.dump(self.population)

    def add_gen_info_to_json(self):
        try:
            json_file = open(
                join(Path(__file__).resolve().parent.parent.parent.parent, "data", "json", "gen", "genetic_algorithm.json"), "r")
            data = json.load(json_file)

            current_generation_data = {
                "best_fitness": self.ranked_population[0][1],
                "current_generation": self.current_generation
            }

            data.append(current_generation_data)
        except FileNotFoundError:
            data = []
        json_file = open(
            join(Path(__file__).resolve().parent.parent.parent.parent, "data", "json", "gen", "genetic_algorithm.json"), "w+")

        json.dump(data, json_file, indent=4)
        json_file.close()
