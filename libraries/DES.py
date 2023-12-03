import simpy
import random
import statistics
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from theoretical_results import *


class Theater(object):
    def __init__(self, env, num_cashiers, mu, policy='FIFO'):
        self.env = env
        self.cashier = simpy.PriorityResource(env, num_cashiers) if policy == 'SJF' else simpy.Resource(env,
                                                                                                        num_cashiers)
        self.mu = mu
        self.policy = policy

    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.expovariate(self.mu))


def go_to_movies(env, moviegoer, theater, wait_times):
    arrival_time = env.now
    if theater.policy == 'SJF':
        estimate = random.expovariate(theater.mu)
        with theater.cashier.request(priority=estimate) as request:
            yield request
            yield env.process(theater.purchase_ticket(moviegoer))
    else:
        with theater.cashier.request() as request:
            yield request
            yield env.process(theater.purchase_ticket(moviegoer))

    wait_times.append(env.now - arrival_time)


def run_theater(env, num_cashiers, lamda, mu, wait_times, policy):
    theater = Theater(env, num_cashiers, mu, policy)
    moviegoer = 0

    while True:
        yield env.timeout(random.expovariate(lamda))
        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater, wait_times))


def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    # Pretty print the results
    # minutes, frac_minutes = divmod(average_wait, 1)
    # seconds = frac_minutes * 60
    # return round(minutes), round(seconds)
    return average_wait


# def get_user_input():
#     num_cashiers = input("Input # of cashiers working: ")
#     params = int(num_cashiers)
#     return params
# random.seed(42)

def run_simulations(steps, num_samples, num_cashiers, policy):
    rho_list = []
    mu_list = []
    lamda_list = []
    averages_of_average_wait_times = []
    std_devs = []

    for rho in np.linspace(0.1, 1, steps):
        mu = 1
        lamda = rho * mu
        average_wait_times = []

        for _ in range(num_samples):
            wait_times = []
            env = simpy.Environment()
            env.process(run_theater(env, num_cashiers, lamda, mu, wait_times, policy))
            env.run(until=900)
            average_wait = get_average_wait_time(wait_times)
            average_wait_times.append(average_wait)

        rho_list.append(rho)
        mu_list.append(mu)
        lamda_list.append(lamda)
        averages_of_average_wait_times.append(statistics.mean(average_wait_times))
        std_devs.append(np.std(average_wait_times))
    return averages_of_average_wait_times, std_devs, rho_list, mu_list, lamda_list


if __name__ == "__main__":
    policies = ['FIFO', 'SJF']
    num_workers = [1, 2, 4]
    plt.figure()

    for worker in num_workers:
        for policy in policies:
            averages, std_devs, rhos, mus, lamdas = run_simulations(30, 30, worker, policy)

            marker = 'o' if policy == 'FIFO' else 's'
            plt.errorbar(rhos, averages, yerr=std_devs, fmt=marker, label=policy)

        plt.xlabel("System Load (ρ)")
        plt.ylabel("Average Wait Time")
        plt.title(f"Simulation Results : FIFO vs SJF Scheduling with {worker} workers ")
        plt.legend()
        plt.show()
