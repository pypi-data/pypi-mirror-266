# -*- coding: utf-8 -*-
import math
import sys
import numpy as np
import seaborn
import matplotlib
import matplotlib.pyplot as plt

from matplotlib import rc


def pd_probability(l, granularity):
    """Compute The probabilities of event k happening with λ = l.

    Arguments:
        l (float): λ parameter for the Poisson Distribution.
        granularity (int): Number of values to be plotted. Has to be chosen depending
            on l, in order to show he complete behaviour of the distribution.

    Returns:
        list(float): The event probabilities from k = 1 to k = granularity-1
    """
    return [(math.pow(l, k)* math.exp(-1 * l))/ math.factorial(k) for k in range(0, granularity)]


def expected_value(l):
    """Compute expected value for λ = l."""
    return (l * math.exp(l)) / (math.exp(l) -1)


def plot_probabilities(parameters, colors, granularity):
    """Plot the first granularity values of the ZTPD for each given parameter, using the given colors."""
    figure, ax = plt.subplots()

    for l, color in zip(parameters, colors):
        # plot probabilities for this l
        data = pd_probability(l, granularity)
        
        # plt.scatter(range(len(data)), data, color=color, s=45, alpha=0.7)
        # plt.plot(list(zip(range(len(data)), data)), color=color)
        plt.plot(data, color=color)

        # plot expected value for this l
        # exp_val = expected_value(l)
        # plt.plot((exp_val, exp_val), (0, -0.1), color=color, ls="--", alpha=0.7)
        # ax.text(exp_val, -0.12, "$E={:.1f}$".format(exp_val), size=11, horizontalalignment="center")

    # labels = ["λ = {:>5.1f}".format(l) for l in parameters] # use this to make it ugly
    labels = ["$λ = {}$".format(l) for l in parameters]
    plt.legend(labels=labels, prop={'size':20})
    plt.xlabel("$k$", size=20)
    plt.ylabel("$g(k; λ)$", size=20)
    # plt.title("PD Probability Mass Function", size=20)

    plt.savefig("pd.svg")
    # show plot only if needed / specifically asked for
    if "-v" in sys.argv:
        plt.show()

if __name__ == "__main__":
    parameters = [1.0, 4.0, 10.0]
    colors = ["red", "blue", "green"]
    granularity = 25
    plot_probabilities(parameters, colors, granularity)

