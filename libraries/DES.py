import simpy
import random
import statistics


wait_times = []


class Theater(object):
    def __init__(self, env, num_cashiers,mu):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.mu = mu


    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.expovariate(self.mu))


def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the theater
    arrival_time = env.now

    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))


    # Moviegoer heads into the theater
    wait_times.append(env.now - arrival_time)


def run_theater(env, num_cashiers, lamda, mu):
    theater = Theater(env, num_cashiers, lamda)

    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater))

    while True:
        yield env.timeout(random.expovariate(lamda))  # Wait a bit before generating a new person

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))


def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


def get_user_input():
    num_cashiers = input("Input # of cashiers working: ")
    params = int(num_cashiers)
    return params


if __name__ == "__main__":
    random.seed(42)
    num_server = [1,2,4]
    for cashiers in num_server:
        # Setup
        num_cashiers = cashiers
        lamda=1
        mu =1


        # Run the simulation
        env = simpy.Environment()
        env.process(run_theater(env, num_cashiers, lamda, mu))
        env.run(until=90)

        # View the results
        mins, secs = get_average_wait_time(wait_times)
        print(
            "Running simulation...",
            f"\nThe average wait time for {cashiers} cashier(s) is {mins} minutes and {secs} seconds.",
        )
