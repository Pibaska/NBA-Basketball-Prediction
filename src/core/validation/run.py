from core.validation.validation import Validation


def validacao():
    print("Rodando Validação")
    validation = Validation(test_cycles=1)
    validation.start_time = time.time()

    print("Generating Genetic Algorithm Score")
    gen_alg_stats = validation.calculate_performance(
        validation.gen_alg_score_generator)
    print("Generating Random Score")
    random_stats = validation.calculate_performance(
        validation.random_score_generator)
    print("Generating Constant Score")
    constant_stats = validation.calculate_performance(
        validation.constant_score_generator)

    validation.end_time = time.time()
    validation.dump_json(gen_alg_stats=gen_alg_stats,
                        random_stats=random_stats, constant_stats=constant_stats)
