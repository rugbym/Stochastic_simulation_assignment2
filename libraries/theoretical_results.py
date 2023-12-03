import numpy as np

def average_number_of_people_in_system(lamda,mu):
    """Returns the average number of people in a M/M/1 queueing system
    with arrival rate lamda and service rate mu

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate

    Returns:
        float: Average number of people in system
    """
    rho = lamda/(mu)
    return rho/(1-rho)

def average_waiting_time(lamda,mu):
    """Returns the average waiting time of a M/M/1 queueing system
    with arrival rate lamda and service rate mu

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate

    Returns:
        float: Average waiting time
    """
    rho = lamda/(mu)
    return rho/mu/(1-rho)

# for m/m/n systems we define the following functions

def p_0(lamda,mu,n):
    """Returns the probability of having 0 people in a M/M/n queueing system
    with arrival rate lamda, service rate mu and n servers

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate
        n (int): Number of servers

    Returns:
        float: Probability of having 0 people in the system
    """
    if n==1:
        return 1 - lamda/mu
    else:
        rho = lamda/(mu*n)
        summation = (sum([(n * rho)**i/np.math.factorial(i) for i in range(n)]) + (n * rho)**n/(np.math.factorial(n)*(1-rho)))
        return 1/ summation

def p_k(lamda,mu,k,n=1):
    """Returns the probability of having k people in a M/M/n queueing system
    with arrival rate lamda, service rate mu and n servers

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate
        k (int): Number of people in the system
        n (int, optional): Number of servers. Defaults to 1.

    Returns:
        float: Probability of having k people in the system
    """
    rho = lamda/(mu*n)
    if n ==1:
        p_k = rho**k * p_0(lamda,mu,n)
    else:
        p_k = (n * rho)**k/np.math.factorial(k) * p_0(lamda,mu,n)
    return p_k

def waiting_probability(lamda,mu,n):
    """Returns the probability of waiting in a M/M/n queueing system
    with arrival rate lamda, service rate mu and n servers

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate
        n (int): Number of servers

    Returns:
        float: Probability of waiting
    """
    rho = lamda/(mu*n)
    P = p_k(lamda,mu,n,n)/(1-rho)
    return P

def average_waiting_time_mmn(lamda,mu,n):
    """Returns the average waiting time of a M/M/n queueing system
    with arrival rate lamda, service rate mu and n servers

    Args:
        lamda (float): Arrival rate
        mu (float): Service rate
        n (int): Number of servers

    Returns:
        float: Average waiting time
    """
    rho = lamda/(mu*n)
    return waiting_probability(lamda,mu,n)/(n*mu*(1-rho))