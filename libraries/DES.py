import simpy
import random
import statistics
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from theoretical_results import *


class ServerRoom(object):
    """A server room has a limited number of servers (``num_servers``) to
    service jobs in parallel.
    Jobs have to request one of the servers. When they got one, they
    can start the service processes and wait for it to finish (which
    takes ``service_time`` minutes).

    """
    def __init__(self, env, num_servers, mu, policy="FIFO", queuetype="MM"):
        """
        Args:
            env (simpy.Environment): Simulation environment
            num_servers (int): Number of servers in the server room
            mu (float): Service rate of the server
            policy (str, optional): Scheduling policy. Defaults to "FIFO".
            queuetype (str, optional): Type of queue. Defaults to "MM".
        """
        self.env = env
        self.server = (
            simpy.PriorityResource(env, num_servers)
            if policy == "SJF"
            else simpy.Resource(env, num_servers)
        )
        self.mu = mu
        self.policy = policy
        self.queuetype = queuetype  # MM or MD or MC

    def service_time(self, job):
        """The service time of a job is the time it takes to process the job
        and the time it takes to transfer the job to the next server

        Args:
            job (int): Job number

        Yields:
            simpy.events.Timeout: [description]
        """
        if self.queuetype[1] == "M":
            yield self.env.timeout(random.expovariate(self.mu))
        if self.queuetype[1] == "D":
            yield self.env.timeout(1 / self.mu)
        if self.queuetype[1] == "C":
            if random.random() < 0.75:
                yield self.env.timeout(random.expovariate(1))
            else:
                yield self.env.timeout(random.expovariate(1 / 5))


def arrivals(env, job, servers, wait_times):
    """The job arrives, requests a server and starts the service process.

    Args:
        env (simpy.Environment): Simulation environment
        job (int): Job number
        servers (ServerRoom): Server room
        wait_times (list): List of wait times
    
    Yields:
        simpy.events.Timeout: [description]

    """
    arrival_time = env.now
    if servers.policy == "SJF":
        estimate = random.expovariate(servers.mu)
        with servers.server.request(priority=estimate) as request:
            yield request
            yield env.process(servers.service_time(job))
    else:
        with servers.server.request() as request:
            yield request
            yield env.process(servers.service_time(job))

    wait_times.append(env.now - arrival_time)


def run_server(env, num_servers, lamda, mu, wait_times, policy, queuetype="MM"):
    """Create a server, a number of initial jobs and keep creating jobs
    approx. every ``1 / lamda`` minutes.

    Args:
        env (simpy.Environment): Simulation environment
        num_servers (int): Number of servers in the server room
        lamda (float): Arrival rate
        mu (float): Service rate
        wait_times (list): List of wait times
        policy (str): Scheduling policy
    """
    servers = ServerRoom(env, num_servers, mu, policy, queuetype)
    job = 0

    while True:
        yield env.timeout(random.expovariate(lamda))
        job += 1
        env.process(arrivals(env, job, servers, wait_times))


def get_average_wait_time(wait_times):
    """Returns the average wait time of all jobs

    Args:
        wait_times (list): List of wait times

    Returns:
        float: Average wait time
    """
    average_wait = statistics.mean(wait_times)
    return average_wait





def run_simulations(steps, num_samples, num_servers, policy,queuetype="MM"):
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
            env.process(run_server(env, num_servers, lamda, mu, wait_times, policy,queuetype=queuetype))
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
    #policies = ["FIFO", "SJF"]
    queuetypes = ["MM", "MD", "MC"]
    num_workers = [1]#, 2, 4]
    plt.figure()

    for worker in num_workers:
        for queuetype in queuetypes:
            averages, std_devs, rhos, mus, lamdas = run_simulations(
                30, 30, worker, policy="FIFO", queuetype=queuetype
            )

            marker = "o" #if policy == "FIFO" else "s"
            plt.errorbar(rhos, averages, yerr=std_devs, fmt=marker, label=queuetype)

        plt.xlabel("System Load (ρ)")
        plt.ylabel("Average Wait Time")
        plt.title(f"Simulation Results : FIFO vs SJF Scheduling with {worker} workers ")
        plt.legend()
        plt.show()
