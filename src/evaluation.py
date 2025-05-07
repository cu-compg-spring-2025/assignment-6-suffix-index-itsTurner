import time
import tracemalloc
import utils
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
from suffix_trie import SuffixTrie
from suffix_tree import SuffixTree
from suffix_array import SuffixArray

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reference',
                        nargs='+',
                        help='Reference sequence files',
                        type=str,
                        required=True)
    parser.add_argument('--query_size',
                        type=int,
                        required=True,
                        nargs=3,
                        help='Query size range (start stop step)')
    parser.add_argument('--queries_per_size',
                        type=int,
                        default=5,
                        help='Unique queries per size (default: 5)')
    parser.add_argument('--rounds',
                        type=int,
                        default=5,
                        help='Number of rounds to run each algorithm ' \
                             + '(default: 5)')
    parser.add_argument('--out_file',
                        type=str,
                        required=True,
                        help='File to save plot to')
    parser.add_argument('--width',
                        type=float,
                        default=8,
                        help='Width of plot in inches (default: 8)')
    parser.add_argument('--height',
                        type=float,
                        default=5,
                        help='Height of plot in inches (default: 5)')
    return parser.parse_args()

def get_random_string(alphabet, length):
    return ''.join(random.choice(alphabet) for _ in range(length))

def get_random_substring(string, length):
    if length > len(string):
        raise ValueError("Length of substring is longer than the string.")

    start_index = random.randint(0, len(string) - length)
    return string[start_index:start_index + length]

def run_test(test_function):
    start = time.monotonic_ns()
    r = test_function()
    stop = time.monotonic_ns()

    tracemalloc.start()
    r = test_function()
    mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return stop - start, mem[1] - mem[0], r

def test_queryset_for_model(model, queries, rounds=1):
    run_times = []
    mem_usages = []

    print(f'\tQUERYSET FOR {model.__algorithm_name__}')
    for query_index, query in enumerate(queries):
        print(f'\t\tQUERY {query_index}')
        _run_times = []
        _mem_usages = []

        for i in range(rounds):
            run_time, mem_usage, _ = run_test(lambda: model.align(query))
            _run_times.append(run_time)
            _mem_usages.append(mem_usage)
            
        run_times.append(np.mean(_run_times))
        mem_usages.append(np.mean(_mem_usages))
        print(f'\t\t\tRUN TIME: {run_times[-1]}ns\tMEM USAGES: {mem_usages[-1]}b')
    
    return run_times, mem_usages

def test_setup(algorithms, datasets, rounds=1):
    run_times = [ [] for _ in range(len(algorithms)) ]
    mem_usages = [ [] for _ in range(len(algorithms)) ]
    models = [ [] for _ in range(len(algorithms))]

    for algorithm_index, algorithm in enumerate(algorithms):
        for dataset_index, dataset in enumerate(datasets):
            print(f'\tSETUP FOR {algorithm.__algorithm_name__} ON DATASET {dataset_index}')
            _run_times = []
            _mem_usages = []
            final_model = None

            for i in range(rounds):
                print(f'\t\tROUND {i}')
                run_time, mem_usage, model = run_test(lambda: algorithm(dataset))
                _run_times.append(run_time)
                _mem_usages.append(mem_usage)
                if i == 0:
                    final_model = model
                print(F'\t\t\tRUN TIME: {run_time}ns\tMEM USAGE: {mem_usage}b')
                
            run_times[algorithm_index].append(np.mean(_run_times))
            mem_usages[algorithm_index].append(np.mean(_mem_usages))
            models[algorithm_index].append(final_model)

            print(f'\t\tRUN TIME: {run_times[algorithm_index]}ns\tMEM USAGE: {mem_usages[algorithm_index]}')
    
    return run_times, mem_usages, models

def test_harness(algorithms, datasets, query_size_range, unique_queries_per_size, rounds=1):
    print(f'GENERATING QUERYSETS...')
    querysets = [[[get_random_substring(dataset, query_size)
                    for _ in range(unique_queries_per_size)]
                    for query_size in query_size_range]
                    for dataset in datasets]

    print(f'TESTING SETUP TIMES')
    setup_run_times, setup_mem_usages, models = test_setup(algorithms, datasets, rounds)
    print(f'SETUP TIMES COMPLETE')

    align_run_times = [[] for _ in range(len(algorithms))]
    align_mem_usages = [[] for _ in range(len(algorithms))]

    print(f'TESTING ALIGNMENT TIMES')
    for algorithm_index, algorithm in enumerate(models):
        for dataset_index, dataset_model in enumerate(algorithm):
            _run_times = []
            _mem_usages = []
            for queryset in querysets[dataset_index]:
                run_times, mem_usages = test_queryset_for_model(dataset_model, queryset, rounds)
                _run_times.append(np.mean(run_times))
                _mem_usages.append(np.mean(mem_usages))
            align_run_times[algorithm_index].append(_run_times)
            align_mem_usages[algorithm_index].append(_mem_usages)
    print(f'ALIGNMENT TIMES COMPLETE')

    return setup_run_times, setup_mem_usages, align_run_times, align_mem_usages

def main():
    args = get_args()

    # Define parameters
    query_size_range = range(args.query_size[0],
                             args.query_size[1],
                             args.query_size[2])

    algorithms = [SuffixTrie, SuffixTree, SuffixArray]

    print(f'READING DATASETS')
    datasets = [utils.read_fasta(dataset)[0] for dataset in args.reference]
    datasets_name = [dataset[0] for dataset in datasets]
    datasets_content = [dataset[1] for dataset in datasets]
    print(f'DATASETS READ')

    unique_queries_per_size = args.queries_per_size
    rounds = args.rounds

    # Run experiment
    print(f'RUNNING EXPERIMENT NOW\n————————————')
    setup_run_times, setup_mem_usages, align_run_times, align_mem_usages = test_harness(
        algorithms=algorithms,
        datasets=datasets_content,
        query_size_range=query_size_range,
        unique_queries_per_size=unique_queries_per_size,
        rounds=rounds)
    
    # Present results
    # Generation performance
    fig, axs = plt.subplots(2, 1, figsize=(args.width, args.height))
    fig.tight_layout(pad=3.0)

    # Generation runtime
    algorithm_names = list(map(lambda a: a.__algorithm_name__, algorithms))
    number_of_datasets = len(datasets_name)
    width_of_bar = 0.4/number_of_datasets
    center_axes = np.arange(len(algorithm_names))

    for dataset_index, dataset_name in enumerate(datasets_name):
        srt_per_dataset = [setup_run_times[algorithm_index][dataset_index] for algorithm_index in range(len(algorithms))]
        smu_per_dataset = [setup_mem_usages[algorithm_index][dataset_index] for algorithm_index in range(len(algorithms))]
        axs[0].bar(center_axes + width_of_bar*dataset_index + width_of_bar / 2, srt_per_dataset, width=width_of_bar, label=dataset_name)
        axs[1].bar(center_axes + width_of_bar*dataset_index + width_of_bar / 2, smu_per_dataset, width=width_of_bar, label=dataset_name)

    axs[0].set_title(f'Data Structure Generation Performance')
    axs[0].set_xlabel('Database')
    axs[0].set_ylabel('Run time (ns)')
    axs[0].legend(loc='best', frameon=False, ncol=3)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].set_xticks(center_axes + 0.2)
    axs[0].set_xticklabels(algorithm_names)

    axs[1].set_xlabel('Query size')
    axs[1].set_ylabel('Memory (bytes)')
    axs[1].legend(loc='best', frameon=False, ncol=3)
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].set_xticks(center_axes + 0.2)
    axs[1].set_xticklabels(algorithm_names)

    fig.savefig(f'{args.out_file.split(".png")[0]}_generation.png')

    # Alignment performance
    fig, axs = plt.subplots(2, 1, figsize=(args.width, args.height))

    # Alignment runtime
    for algorithm_index, algorithm in enumerate(algorithms):
        for dataset_index, dataset_name in enumerate(datasets_name):
            label = f'{algorithm.__algorithm_name__} on {dataset_name}'
            axs[0].plot(query_size_range, align_run_times[algorithm_index][dataset_index], label=label)
            axs[1].plot(query_size_range, align_mem_usages[algorithm_index][dataset_index], label=label)

    axs[0].set_title(f'String Alignment Performance')
    axs[0].set_xlabel('Query size')
    axs[0].set_ylabel('Run time (ns)')
    axs[0].legend(loc='best', frameon=False, ncol=3)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)

    axs[1].set_xlabel('Query size')
    axs[1].set_ylabel('Memory (bytes)')
    axs[1].legend(loc='best', frameon=False, ncol=3)
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)

    fig.savefig(f'{args.out_file.split(".png")[0]}_alignment.png')

if __name__ == '__main__':
    main()