import itertools
import pandas as pd
import multiprocessing as mp
from brian2 import *  # Brian2 must be imported for the simulation
import pygad
import time
import sys
import os

import argparse
import matplotlib.pyplot as plt

# For keeping track of how much time each generation takes
start_time = time.time()
previous_gen_start_time = start_time

# For collecting stats, i.e. the errors of the best specimens in each generation,
# the means/standard deviations of the errors of the specimens that don't crash,
# and the variation within the population over time (mean of standard deviations of the genes).
best_errors = []
mean_errors_working_specimens = []
mean_first_errors_working_specimens = []
mean_second_errors_working_specimens = []
mean_third_errors_working_specimens = []
std_errors_working_specimens = []
std_first_errors_working_specimens = []
std_second_errors_working_specimens = []
std_third_errors_working_specimens = []
mean_gene_stddevs = []

# Import the simulation function from your model file
from optimization_model_multi import RingAttractorSim
# from optimization_model import opt_ring_attractor  # your simulation function
# Also import any utility functions if needed (e.g., for computing firing rates, etc.)
from utils import *

result_path = os.path.join('Optimization Models', 'multiGA_results')
GA_results_path = os.path.join(os.getcwd(), 'Optimization Models', 'GA_results')

# Check if directory 'GA_results' exists, if not create it
if not os.path.exists(GA_results_path):
    os.makedirs(GA_results_path)

# Create a unique directory for the current run based on the timestamp
current_results_dirname = f"GA_results/GA_run_{time.strftime('%Y%m%d_%H%M%S')}"
if not os.path.exists(current_results_dirname):
    os.makedirs(current_results_dirname)


# Set up argparse. Read in settings from command line, or use defaults.
parser = argparse.ArgumentParser(description='Run GA optimization for ring attractor model.')

parser.add_argument('--num_processes', type=int, default=1, help='Number of processes for parallel processing.')
parser.add_argument('--population_size', type=int, default=100, help='Population size for the genetic algorithm.')
parser.add_argument('--random_seed', type=int, default=24, help='Random seed for reproducibility.')
parser.add_argument('--num_generations', type=int, default=500, help='Number of generations for the genetic algorithm.')
parser.add_argument('--num_parents_mating', type=int, default=50, help='Number of parents mating in each generation.')
parser.add_argument('--mutation_type', type=str, default='adaptive', choices=['random', 'swap', 'inversion', 'scramble', 'adaptive', ], help='Type of mutation to use in the genetic algorithm.') # Options: "random", "swap", "inversion", "scramble", "adaptive", or a custom function
parser.add_argument('--mutation_probability', type=float, default=[0.5, 0.25], nargs=2, help='Probability of mutation for each gene. If using adaptive mutation, this should be a list of two values: the first for lower-than-average fitness solutions, the second for higher-than-average fitness solutions. If using random mutation, this should be a single value for all solutions.')
parser.add_argument('--parent_selection_type', type=str, default='tournament_nsga2', choices=['nsga2', 'tournament_nsga2'], help='Parent selection method for the genetic algorithm.')
parser.add_argument('--connectivity_profile', type=str, default='mexican_hat', choices=['mexican_hat', 'cosine'], help='Connectivity profile to optimize.')
parser.add_argument('--crossover_type', type=str, default='single_point', choices=['single_point', 'two_points', 'uniform', 'scattered'], help='Crossover type for the genetic algorithm.')
parser.add_argument('--keep_elitism', type=int, default=1, help='Number of best solutions to keep in the next generation.')
parser.add_argument('--rand_mut_min_val', type=float, default=-0.1, help='Minimum value for random mutation.')
parser.add_argument('--rand_mut_max_val', type=float, default=0.1, help='Maximum value for random mutation.')
parser.add_argument('--initial_ranges_mex', type=float, nargs=8, default=[0.05, 0.2, 0.1, 0.3, 0.5, 1.0, -1.0, -0.3], help='Initial ranges for Mexican hat connectivity profile: sigma_exc_min, sigma_exc_max, sigma_inh_min, sigma_inh_max, g_exc_min, g_exc_max, g_inh_min, g_inh_max.')
parser.add_argument('--stim_center', type=float, default=1.571, help='Center of the stimulus for the ring attractor model.')
parser.add_argument('--stim_width', type=float, default=0.5, help='Width of the stimulus for the ring attractor model.')
parser.add_argument('--tau', type=float, default=10.0, help='Time constant for the ring attractor model in ms.')
parser.add_argument('--sigma_noise', type=float, default=1.0)


args = parser.parse_args()

rand_seed = args.random_seed
num_processes = args.num_processes
population_size = args.population_size
num_generations = args.num_generations
num_parents_mating = args.num_parents_mating
mutation_type = args.mutation_type
mutation_probability = args.mutation_probability
connectivity_profile = args.connectivity_profile
parent_selection_type = args.parent_selection_type
crossover_type = args.crossover_type
keep_elitism = args.keep_elitism
rand_mut_min_val = args.rand_mut_min_val
rand_mut_max_val = args.rand_mut_max_val

initial_ranges_mex = args.initial_ranges_mex

stim_center = args.stim_center
stim_width = args.stim_width

tau = args.tau 
sigma_noise = args.sigma_noise

# Write the parameters to a file
with open(f"{current_results_dirname}/exp_params.txt", "w") as f:
    f.write(f"Random seed: {rand_seed}\n")
    f.write(f"Number of processes: {num_processes}\n")
    f.write(f"Population size: {population_size}\n")
    f.write(f"Number of generations: {num_generations}\n")
    f.write(f"Number of parents mating: {num_parents_mating}\n")
    f.write(f"Mutation type: {mutation_type}\n")
    f.write(f"Mutation probability: {mutation_probability}\n")
    f.write(f"Parent selection type: {parent_selection_type}\n")
    f.write(f"Connectivity profile: {connectivity_profile}\n")
    f.write(f"Crossover type: {crossover_type}\n")
    f.write(f"Keep elitism: {keep_elitism}\n")
    f.write(f"Random mutation min value: {rand_mut_min_val}\n")
    f.write(f"Random mutation max value: {rand_mut_max_val}\n")
    f.write(f"Initial ranges for Mexican hat connectivity profile: {initial_ranges_mex}\n")


# If adaptive mutation is used, there is a probability for lower-than-average fitness solutions 
# and a probability for higher-than-average fitness solutions.
if not (mutation_type in ['adaptive']):
    mutation_probability = mutation_probability[0]  # Use the first value for all solutions

# Set seed for reproducibility
np.random.seed(rand_seed)
seed(rand_seed)



# Fixed parameters for the simulation (not searched over)
fixed_params = {
    'tau': tau,           # in our simulation, run_ring_attractor converts this to ms.
    'sigma_noise': sigma_noise,   # similarly converted to mV inside run_ring_attractor.
    'syn_profile': connectivity_profile,  # Set the connectivity profile
}


# Set the ranges to sample the initial values from
# Note: during optimization, the values can go outside these ranges,
# but it is possible to set limits for that as well.
if connectivity_profile == 'mexican_hat':
    sigma_exc_range = initial_ranges_mex[:2]  # Use the first two values for sigma_exc
    sigma_inh_range = initial_ranges_mex[2:4]  # Use the next two values for sigma_inh
    g_exc_range   = initial_ranges_mex[4:6]    # Use the next two values for g_exc
    g_inh_range   = initial_ranges_mex[6:8]    # Use the last two values for g_inh
    gene_0_stddevs = []
    gene_1_stddevs = []
    gene_2_stddevs = []
    gene_3_stddevs = []
elif connectivity_profile == 'cosine':
    g_cosine_range = [0.01, 0.1]    # cosine gain
    glob_inh_range = [True, False]  # global inhibition flag
    w_inh_range = [-2.0, -0.5]      # global inhibition weight
else:
    raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")




# Number of genes based on the connectivity profile
if connectivity_profile == 'mexican_hat':
    num_genes = 4  # sigma_exc, sigma_inh, g_exc, g_inh
elif connectivity_profile == 'cosine':
    num_genes = 3 # g_cosine, glob_inh, w_inh
else:  
    raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")


# Function that is called after each generation to collect statistics and print results
def on_generation(ga_instance):
    global previous_gen_start_time
    global best_errors
    global mean_errors_working_specimens
    global std_errors_working_specimens
    global mean_first_errors_working_specimens
    global mean_second_errors_working_specimens
    global mean_third_errors_working_specimens
    global std_first_errors_working_specimens
    global std_second_errors_working_specimens
    global std_third_errors_working_specimens
    global current_results_dirname
    global gene_0_stddevs, gene_1_stddevs, gene_2_stddevs, gene_3_stddevs
    global mean_gene_stddevs
    

    # Calculate the population standard deviation for each gene
    # This gives a measure of the variation within the population
    all_genomes = ga_instance.population
    gene_std_devs = np.std(all_genomes, axis=0)
    mean_gene_stddevs.append(np.mean(gene_std_devs))
    if connectivity_profile == 'mexican_hat':
        gene_0_stddevs.append(gene_std_devs[0])
        gene_1_stddevs.append(gene_std_devs[1])
        gene_2_stddevs.append(gene_std_devs[2])
        gene_3_stddevs.append(gene_std_devs[3])
        np.savetxt(f"{current_results_dirname}/gene_0_stddevs.txt", np.array(gene_0_stddevs))
        np.savetxt(f"{current_results_dirname}/gene_1_stddevs.txt", np.array(gene_1_stddevs))
        np.savetxt(f"{current_results_dirname}/gene_2_stddevs.txt", np.array(gene_2_stddevs))
        np.savetxt(f"{current_results_dirname}/gene_3_stddevs.txt", np.array(gene_3_stddevs))
    elif connectivity_profile == 'cosine':
        gene_0_stddevs.append(gene_std_devs[0])
        gene_1_stddevs.append(gene_std_devs[1])
        gene_2_stddevs.append(gene_std_devs[2])
        np.savetxt(f"{current_results_dirname}/gene_0_stddevs.txt", np.array(gene_0_stddevs))
        np.savetxt(f"{current_results_dirname}/gene_1_stddevs.txt", np.array(gene_1_stddevs))
        np.savetxt(f"{current_results_dirname}/gene_2_stddevs.txt", np.array(gene_2_stddevs))
    else:
        raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")
    
    np.savetxt(f"{current_results_dirname}/mean_gene_stddevs.txt", np.array(mean_gene_stddevs))



    # Retrieve the fitnesses of working and failed specimens
    # The fitness function is set up such that a negative fitness is given
    # to specimens that fail the simulation for some reason (e.g., NaN values). 
    pop_fitnesses = np.array(ga_instance.last_generation_fitness)
    positive_fitnesses = pop_fitnesses[pop_fitnesses[:, 0] >= 0]
    negative_fitnesses = pop_fitnesses[pop_fitnesses[:, 0] < 0]

    # Calculate the errors for working specimens
    # Simply the inverse of the fitness value calculation as can be seen in the fitness_func.
    first_fitness_vals = positive_fitnesses[:, 0]
    first_errors = (1.0 / first_fitness_vals) - 1e-8
    mean_first_errors = np.mean(first_errors)
    std_first_errors = np.std(first_errors)
    mean_first_errors_working_specimens.append(mean_first_errors)
    std_first_errors_working_specimens.append(std_first_errors)
    second_fitness_vals = positive_fitnesses[:, 1]
    second_errors = (1.0 / second_fitness_vals) - 1e-8
    mean_second_errors = np.mean(second_errors)
    std_second_errors = np.std(second_errors)
    mean_second_errors_working_specimens.append(mean_second_errors)
    std_second_errors_working_specimens.append(std_second_errors)
    third_fitness_vals = positive_fitnesses[:, 2]
    third_errors = (1.0 / third_fitness_vals) - 1e-8
    mean_third_errors = np.mean(third_errors)
    std_third_errors = np.std(third_errors)
    mean_third_errors_working_specimens.append(mean_third_errors)
    std_third_errors_working_specimens.append(std_third_errors)


    mean_specimen_fitnesses = np.mean(np.stack([first_fitness_vals, second_fitness_vals, third_fitness_vals]), axis=0)


    mean_specimen_errors = np.mean(np.stack([first_errors, second_errors, third_errors]), axis=0)
    mean_errors = np.mean(mean_specimen_errors)
    std_errors = np.std(mean_specimen_errors)
    mean_errors_working_specimens.append(mean_errors)
    std_errors_working_specimens.append(std_errors)

    # mean_fitness_vals = np.mean(np.stack([first_fitness_vals, second_fitness_vals, third_fitness_vals]), axis=0)
    # errors = (1.0 / mean_fitness_vals) - 1e-8
    # mean_errors = np.mean(errors)
    # std_errors = np.std(errors)
    # mean_errors_working_specimens.append(mean_errors)
    # std_errors_working_specimens.append(std_errors)
    

    np.savetxt(f"{current_results_dirname}/mean_errors_working_specimens.txt", np.array(mean_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/std_errors_working_specimens.txt", np.array(std_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/mean_first_errors_working_specimens.txt", np.array(mean_first_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/std_first_errors_working_specimens.txt", np.array(std_first_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/mean_second_errors_working_specimens.txt", np.array(mean_second_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/std_second_errors_working_specimens.txt", np.array(std_second_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/mean_third_errors_working_specimens.txt", np.array(mean_third_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/std_third_errors_working_specimens.txt", np.array(std_third_errors_working_specimens))


    print(f"Generation mean FITNESS (working solutions): {np.mean(mean_specimen_fitnesses):.4f} +/- {np.std(mean_specimen_fitnesses):.4f} | {len(positive_fitnesses)} working, {len(negative_fitnesses)} failed solutions")
    print(f"Generation mean ERROR (working solutions): {mean_errors:.4f} +/- {std_errors:.4f}")
    print(f"      mean cwce: {mean_first_errors:.4f} +/- {std_first_errors:.4f}")
    print(f"      mean angular Z-score: {mean_second_errors:.4f} +/- {std_second_errors:.4f}")
    print(f"      mean NMSE: {mean_third_errors:.4f} +/- {std_third_errors:.4f}")
    print(f"Generation mean gene standard deviations: {np.mean(gene_std_devs):.4f}")

    solution, solution_fitness, solution_idx = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)
    best_errors.append(1/(solution_fitness) - 1e-8)
    np.savetxt(f"{current_results_dirname}/best_errors.txt", np.array(best_errors))
    
    gens_completed = ga_instance.generations_completed
    with open(f"{current_results_dirname}/exp_results.txt", "a") as f:
        f.write(f"Generation {gens_completed} - Best specimen's errors: {1/(solution_fitness) - 1e-8} (sigma_exc: {solution[0]}, sigma_inh: {solution[1]}, g_exc: {solution[2]} mV, g_inh: {solution[3]} mV)\n")
        f.write(f"Generation mean FITNESS: {np.mean(positive_fitnesses):.4f} +/- {np.std(positive_fitnesses):.4f} | {len(positive_fitnesses)} working, {len(negative_fitnesses)} failed solutions\n")
        f.write(f"Generation mean ERROR (working solutions): {mean_errors:.4f} +/- {std_errors:.4f}\n")
        f.write(f"      mean cwce: {mean_first_errors:.4f} +/- {std_first_errors:.4f}\n")
        f.write(f"      mean angular Z-score: {mean_second_errors:.4f} +/- {std_second_errors:.4f}\n")
        f.write(f"      mean NMSE: {mean_third_errors:.4f} +/- {std_third_errors:.4f}\n")
        f.write(f"Generation mean gene standard deviations: {np.mean(gene_std_devs):.4f}\n")
        f.write(f"Generation time: {time.time() - previous_gen_start_time:.2f} seconds\n")
    print(f"Generation {gens_completed} - Best specimen's errors: {1/(solution_fitness) - 1e-8} (sigma_exc: {solution[0]}, sigma_inh: {solution[1]}, g_exc: {solution[2]} mV, g_inh: {solution[3]} mV)")
    print(f"Generation time: {time.time() - previous_gen_start_time:.2f} seconds\n")

    previous_gen_start_time = time.time()


# Function that takes the parameter values given by a specimen, runs a simulation
# with those values, calculates the composite error, and returns the fitness value.
# Basically the same as in the grid search code.
# Specimens for which the simulation fails are given a composite error of -1,
# so that they can easily be identified and excluded from the statistics.
def fitness_func(ga_instance, solution, solution_idx):
    np.random.seed(rand_seed)
    seed(rand_seed)

    params = fixed_params.copy()

    if connectivity_profile == 'mexican_hat':
        params.update({
            'sigma_exc': solution[0],
            'sigma_inh': solution[1],
            'g_exc': solution[2]*mV,
            'g_inh': solution[3]*mV
        })
    elif connectivity_profile == 'cosine':
        raise NotImplementedError("Cosine profile optimization not yet implemented in GA fitness function.")
    else:
        raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")
    
    try:
        # Run the simulation.        
        GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude = sim.do_run(result_path)
        # opt_ring_attractor returns: (GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude)
        # GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude = opt_ring_attractor(params, stim_center=stim_center, stim_width=stim_width)
        
        # Compute the circular standard deviation (spread) from the PVA magnitude.
        circular_std = np.sqrt(-2 * np.log(out_pva_magnitude + 1e-8))
        
        # Compute the center error and the confidence weighted center error (CWCE).
        center_err, cwce = conf_weighted_CE(out_pva_angle, GT_center, out_pva_magnitude)
        
        # Compute the angular Z-score:
        # This expresses the misalignment (center_err) in units of the circular standard deviation,
        # analogous to a z-score in linear statistics.
        angular_Zscore = center_err / circular_std
        
        # Compute the NMSE between the observed firing rates and the ideal Gaussian profile.
        nmse = compute_nmse_normalized(out_rates, GT_input, norm_type='max')
        
        # Combine the errors into one composite score, just to be able to
        # quickly check NaN or infinite values.
        composite_error = cwce + angular_Zscore + nmse

        # Check if the composite error is NaN or infinite. In that case, set all errors to -1
        if np.isnan(composite_error) or np.isinf(composite_error):
            cwce = -1
            angular_Zscore = -1
            nmse = -1
            print(f"Composite error is NaN or infinite for solution {solution_idx}. Setting all errors to -1.")
            

    # For now, if there is any exception raised, just give very low fitness value to this solution.
    except Exception as e:
        cwce = -1
        angular_Zscore = -1
        nmse = -1
        print(f"Exception occurred for solution {solution_idx}: {e}. Setting all errors to -1.")


    fitness_cwce = 1 / (cwce + 1e-8)
    fitness_angular_Zscore = 1 / (angular_Zscore + 1e-8)
    fitness_nmse = 1 / (nmse + 1e-8)

    return [fitness_cwce, fitness_angular_Zscore, fitness_nmse]


# Create the GA instance with the specified parameters
ga_instance = pygad.GA(num_generations=num_generations,
                       sol_per_pop=population_size,
                       fitness_func=fitness_func,
                       num_genes=num_genes,
                       num_parents_mating=num_parents_mating,
                       mutation_type=mutation_type,
                       mutation_probability=mutation_probability,
                       on_generation=on_generation,
                       parent_selection_type=parent_selection_type,
                       crossover_type=crossover_type,
                       parallel_processing=["process", num_processes],
                       keep_elitism=keep_elitism,
                       random_seed=rand_seed,
                       random_mutation_min_val= rand_mut_min_val,
                       random_mutation_max_val= rand_mut_max_val)



# Initialize the population with random values within the specified ranges
if connectivity_profile == 'mexican_hat':
    ga_instance.initialize_population(low = [sigma_exc_range[0], sigma_inh_range[0], g_exc_range[0], g_inh_range[0]],
                                      high = [sigma_exc_range[1], sigma_inh_range[1], g_exc_range[1], g_inh_range[1]],
                                      allow_duplicate_genes=True,
                                      mutation_by_replacement=False,
                                      gene_type=[float, float, float, float])
elif connectivity_profile == 'cosine':
    raise NotImplementedError("Cosine profile optimization not yet implemented in GA initialization.")
else:
    raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")





if __name__ == '__main__':

    # Run the GA optimization. At the end, save all statistics once again, and create plots.
    
    set_device('cpp_standalone', build_on_run=False)

    print(f"Starting optimization for {connectivity_profile} connectivity profile")
    
    default_params = {
    'tau'        : 10,
    'sigma_noise': 1.0,
    'sigma_exc'  : 0.125,
    'sigma_inh'  : 0.1,
    'g_exc'      : 1.0*mV,
    'g_inh'      : -1.0*mV,
    'syn_profile': 'mexican_hat',
    'autapse'    : True,
    'glob_inh'   : False
    }
    
    stim_center = 0.0
    stim_width  = 0.5
    sim = RingAttractorSim(default_params,
                           stim_center=stim_center,
                           stim_width=stim_width)
    
    ga_instance.run()

     
    solution, solution_fitness, solution_idx = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)
    
    print(f"""Best solution found:
    errors: {1/solution_fitness}
    sigma_exc: {solution[0]}
    sigma_inh: {solution[1]}
    g_exc: {solution[2]} mV
    g_inh: {solution[3]} mV
""")
    
    ga_instance.save(f"{current_results_dirname}/ga_instance_final")

    print(f"Total time taken for optimization: {time.time() - start_time:.2f} seconds")

    np.savetxt(f"{current_results_dirname}/mean_errors_working_specimens.txt", np.array(mean_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/std_errors_working_specimens.txt", np.array(std_errors_working_specimens))
    np.savetxt(f"{current_results_dirname}/best_errors.txt", np.array(best_errors))
    np.savetxt(f"{current_results_dirname}/mean_gene_stddevs.txt", np.array(mean_gene_stddevs))
    np.savetxt(f"{current_results_dirname}/gene_0_stddevs.txt", np.array(gene_0_stddevs))
    np.savetxt(f"{current_results_dirname}/gene_1_stddevs.txt", np.array(gene_1_stddevs))
    np.savetxt(f"{current_results_dirname}/gene_2_stddevs.txt", np.array(gene_2_stddevs))
    if connectivity_profile == 'mexican_hat':
        np.savetxt(f"{current_results_dirname}/gene_3_stddevs.txt", np.array(gene_3_stddevs))


    plt.figure()
    plt.plot(best_errors, label='Best Errors')
    plt.xlabel('Generation')
    plt.ylabel('Error')
    plt.title('Best Errors Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/best_errors.png")


    plt.figure()
    plt.plot(mean_errors_working_specimens, label='Mean Errors (Working Specimens)')
    plt.fill_between(range(len(mean_errors_working_specimens)), 
                     np.array(mean_errors_working_specimens) - np.array(std_errors_working_specimens), 
                     np.array(mean_errors_working_specimens) + np.array(std_errors_working_specimens), 
                     alpha=0.2)
    plt.xlabel('Generation')
    plt.ylabel('Mean Error')
    plt.title('Mean Errors Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/mean_errors.png")

    plt.figure()
    plt.plot(mean_first_errors_working_specimens, label='Mean CWCE (Working Specimens)')
    plt.fill_between(range(len(mean_first_errors_working_specimens)), 
                     np.array(mean_first_errors_working_specimens) - np.array(std_first_errors_working_specimens), 
                     np.array(mean_first_errors_working_specimens) + np.array(std_first_errors_working_specimens), 
                     alpha=0.2)
    plt.xlabel('Generation')
    plt.ylabel('Mean CWCE')
    plt.title('Mean CWCE Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/mean_first_errors.png")

    plt.figure()
    plt.plot(mean_second_errors_working_specimens, label='Mean Angular Z-score (Working Specimens)')
    plt.fill_between(range(len(mean_second_errors_working_specimens)), 
                     np.array(mean_second_errors_working_specimens) - np.array(std_second_errors_working_specimens), 
                     np.array(mean_second_errors_working_specimens) + np.array(std_second_errors_working_specimens), 
                     alpha=0.2)
    plt.xlabel('Generation')
    plt.ylabel('Mean Angular Z-score')
    plt.title('Mean Angular Z-score Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/mean_second_errors.png")

    plt.figure()
    plt.plot(mean_third_errors_working_specimens, label='Mean NMSE (Working Specimens)')
    plt.fill_between(range(len(mean_third_errors_working_specimens)), 
                     np.array(mean_third_errors_working_specimens) - np.array(std_third_errors_working_specimens), 
                     np.array(mean_third_errors_working_specimens) + np.array(std_third_errors_working_specimens), 
                     alpha=0.2)
    plt.xlabel('Generation')
    plt.ylabel('Mean NMSE')
    plt.title('Mean NMSE Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/mean_third_errors.png")

    plt.figure()
    plt.plot(mean_gene_stddevs, label='Mean Gene Standard Deviations')
    plt.xlabel('Generation')
    plt.ylabel('Mean Gene Std Dev')
    plt.title('Mean Gene Standard Deviations Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/mean_gene_stddevs.png")

    plt.figure()
    plt.plot(gene_0_stddevs, label='Gene 0 Std Dev')
    plt.xlabel('Generation')
    plt.ylabel('Gene 0 Std Dev')
    plt.title('Gene 0 Standard Deviations Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/gene_0_stddevs.png")

    plt.figure()
    plt.plot(gene_1_stddevs, label='Gene 1 Std Dev')
    plt.xlabel('Generation')
    plt.ylabel('Gene 1 Std Dev')
    plt.title('Gene 1 Standard Deviations Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/gene_1_stddevs.png")

    plt.figure()
    plt.plot(gene_2_stddevs, label='Gene 2 Std Dev')
    plt.xlabel('Generation')
    plt.ylabel('Gene 2 Std Dev')
    plt.title('Gene 2 Standard Deviations Over Generations')
    plt.legend()
    plt.savefig(f"{current_results_dirname}/gene_2_stddevs.png")

    if connectivity_profile == 'mexican_hat':
        plt.figure()
        plt.plot(gene_3_stddevs, label='Gene 3 Std Dev')
        plt.xlabel('Generation')
        plt.ylabel('Gene 3 Std Dev')
        plt.title('Gene 3 Standard Deviations Over Generations')
        plt.legend()
        plt.savefig(f"{current_results_dirname}/gene_3_stddevs.png")
