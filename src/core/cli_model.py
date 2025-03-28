
from datetime import datetime
import time
import json
from os.path import join
from pathlib import Path
from core.gen.classes.genetic_algorithm import GeneticAlgorithm
from data.utils import data_provider
from core.web.control import activate_web_scraping
from core.validation.validation import Validation


def predict_score(team_home_name, team_away_name, date, view=None, manual_chromosome=None):
    gen_alg = GeneticAlgorithm([])
    if(manual_chromosome is not None):
        weight_list = manual_chromosome
        for i in range(len(weight_list)):
            weight_list[i] = float(weight_list[i])
    else:
        weight_list = gen_alg.get_first_generation()[0]

    predicted_match = data_provider.get_specific_match_averages(
        team_home_name, team_away_name, date)

    try:
        print(
            f"Trying to predict match between {team_home_name} (Home) and {team_away_name} (Away) set in {date[1]}/{date[2]}/{date[0]}")
        prediction_results = gen_alg.predict_match(
            weight_list, predicted_match)
        prediction_results["predicted_1q_winner"] = team_home_name if prediction_results[
            "predicted_1q_winner"] == "team_home" else team_away_name
        print(f"Home Team Score: {prediction_results['home_team_score']}")
        print(f"Away Team Score: {prediction_results['away_team_score']}")
        print(
            f"Winner: {prediction_results['predicted_1q_winner']}\nScore Difference Percentage: {prediction_results['score_difference_percentage']}")
    except Exception as e:
        raise e

    # view.lineedit_results.setText(
    #     f"Resultados: {view.selected_home_team} ou {view.selected_away_team}")


def run_gen_alg(date=[2018, 6, 20],
                good_generations=3,
                weight_range=(-10, 10),
                mutation_chance=1,
                mutation_magnitude=(-1, 1),
                chromosome_size=100,
                population_size=50,
                max_generations=100,
                persistent_individuals=5,
                random_individuals=5,
                timestamp=-1,
                generate_new_population=False):

    input_matches = data_provider.get_matches_averages_by_season(date)

    gen_alg = GeneticAlgorithm(
        input_matches, good_generations=good_generations, weight_range=weight_range, mutation_chance=mutation_chance,
        mutation_magnitude=mutation_magnitude, chromosome_size=chromosome_size, population_size=population_size,
        max_generations=max_generations, persistent_individuals=persistent_individuals, timestamp=timestamp,
        generate_new_population=generate_new_population)

    start_time = time.time()

    gen_alg.population = gen_alg.get_first_generation()

    for generation in range(gen_alg.max_generations):
        try:
            gen_alg.current_generation = generation

            gen_alg.ranked_population = gen_alg.apply_fitness(
                gen_alg.population, gen_alg.fitness_input)

            print(
                f"Generation {generation} | Best Chromosome: '{gen_alg.population[0]} | Fitness: {gen_alg.ranked_population[0][1]}%'")

            if(gen_alg.ranked_population[0][1] > gen_alg.highest_fitness):
                gen_alg.highest_fitness = gen_alg.ranked_population[0][1]
                print(f"New highest fitness: {gen_alg.highest_fitness}")

            if(gen_alg.check_for_break(gen_alg.ranked_population)):
                print("Population is good; Finish Algoritm")
                break

            gen_alg.population = gen_alg.reproduce_population(
                gen_alg.ranked_population, gen_alg.population_size)

            if(gen_alg.current_generation % 5 == 0):
                gen_alg.add_gen_info_to_json()
        except KeyboardInterrupt:
            break

    end_time = time.time()

    gen_alg.log_and_dump_data(timestamp=datetime.now(),
                              elapsed_time=end_time - start_time)

    return gen_alg


def run_web_scraping():
    activate_web_scraping()


def run_validation(test_cycles=5):
    with open(join(Path(__file__).resolve().parent, 'validation', 'config.json'), "r") as config_file:
        generator_data = json.load(config_file)

        print("Running Validation")
        validation = Validation(test_cycles=test_cycles)
        validation.start_time = time.time()

        for generator in generator_data:
            if(generator["function"] == "genetic"):
                generator["result"] = validation.calculate_performance(
                    lambda: validation.gen_alg_score_generator(
                        good_generations=generator["params"]["good_generations"],
                        weight_range=generator["params"]["weight_range"],
                        mutation_chance=generator["params"]["mutation_chance"],
                        mutation_magnitude=generator["params"]["mutation_magnitude"],
                        chromosome_size=generator["params"]["chromosome_size"],
                        population_size=generator["params"]["population_size"],
                        max_generations=generator["params"]["max_generations"],
                        persistent_individuals=generator["params"]["persistent_individuals"],
                        random_individuals=generator["params"]["random_individuals"]
                    ))
            elif(generator["function"] == "random"):
                generator["result"] = validation.calculate_performance(
                    validation.random_score_generator)
            elif(generator["function"] == "constant"):
                generator["result"] = validation.calculate_performance(
                    lambda: validation.constant_score_generator(generator["chromosome"]))
            else:
                raise Exception
            pass

        print(generator_data)

    validation.end_time = time.time()
    validation.dump_json(validation_results=generator_data)

# def activate_home_team_combobox(selected_team, view):
#   print(f"combobox home ativada: {selected_team}")
#   view.selected_home_team = selected_team
#
# def activate_away_team_combobox(selected_team, view):
#   print(f"combobox away ativada: {selected_team}")
#   view.selected_away_team = selected_team
#
