# na nossa aplicação de verdade o model seria todos os outros scripts (AG, WS)
# esse arquivo existe pra garantir a flexibilidade da interface
# edit: talvez a gente tenha que manter hein

from datetime import datetime
import time
from core.genetic_alg_functions import GeneticAlgorithm
from utils.database import data_provider, database_manipulation
from web.web_scraping_main import activate_web_scraping


def predict_score(view):
    view.lineedit_results.setText(
        f"Resultados: {view.selected_home_team} ou {view.selected_away_team}")


def activate_home_team_combobox(selected_team, view):
    print(f"combobox home ativada: {selected_team}")
    view.selected_home_team = selected_team


def activate_away_team_combobox(selected_team, view):
    print(f"combobox away ativada: {selected_team}")
    view.selected_away_team = selected_team


def run_gen_alg():
    gen_alg = GeneticAlgorithm(
        data_provider.glue, weight_range=(-100, 100), population_size=50, max_generations=10, fitness_input_size=300, mutation_weight=(-10, 10))

    start_time = time.time()

    gen_alg.population = gen_alg.random_population()

    for generation in range(gen_alg.max_generations):

        gen_alg.ranked_population = gen_alg.apply_fitness(
            gen_alg.population, gen_alg.fitness_input_gatherer)

        print(
            f"Geração {generation} | População: '{gen_alg.population[0]} | Fitness: {gen_alg.ranked_population[0][1]}%'")

        if(gen_alg.check_for_break(gen_alg.ranked_population)):
            break

        gen_alg.population = gen_alg.reproduce_population(
            gen_alg.ranked_population, gen_alg.population_size)

    end_time = time.time()

    gen_alg.log_data(timestamp=datetime.now(),
                     elapsed_time=end_time - start_time)

    gen_alg.dump_last_generation()
    gen_alg.retrieve_last_generation()

    return gen_alg


def run_web_scraping():
    activate_web_scraping()
