# -*- coding: utf-8 -*-
import math
import sys
import numpy as np
import seaborn
import matplotlib
import matplotlib.pyplot as plt

from matplotlib import rc


def ztpd_probability(l, granularity):
    """Compute The probabilities of event k happening with λ = l.

    Arguments:
        l (float): λ parameter for the Zero Truncated Poisson Distribution.
        granularity (int): Number of values to be plotted. Has to be chosen depending
            on l, in order to show he complete behaviour of the distribution.

    Returns:
        list(float): The event probabilities from k = 1 to k = granularity-1
    """
    return [(math.pow(l, k))/ ((math.exp(l) - 1) * math.factorial(k)) for k in range(1, granularity)]


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


def ztpd_expected_value(l):
    """Compute expected value for λ = l."""
    return (l * math.exp(l)) / (math.exp(l) -1)

def pd_expected_value(l):
    """Compute expected value for λ = l."""
    return l


def plot_probabilities(parameters, colors, granularity):
    """Plot the first granularity values of the ZTPD for each given parameter, using the given colors."""
    figure, ax = plt.subplots()

    c1 = ["red"]
    c2 = ["blue"]
    # plot ztpd
    for l, color in zip(parameters, c1):
        # plot probabilities for this l
        data = [0.0] + ztpd_probability(l, granularity)
        plt.scatter(range(len(data)), data, color=color, s=45, alpha=0.7)

        # plot expected value for this l
        # exp_val = ztpd_expected_value(l)
        # plt.plot((exp_val, exp_val), (0, -0.1), color=color, ls="--", alpha=0.7)
        # ax.text(exp_val, -0.12, "$E={:.1f}$".format(exp_val), size=11, horizontalalignment="center")

    for l, color in zip(parameters, c2):
        # plot probabilities for this l
        data = pd_probability(l, granularity)
        plt.scatter(range(len(data)), data, color=color, marker="^", s=45, alpha=0.7)

        # plot expected value for this l
        # exp_val = pd_expected_value(l)
        # plt.plot((exp_val, exp_val), (0, -0.1), color=color, ls="--", alpha=0.7)
        # ax.text(exp_val, -0.12, "$E={:.1f}$".format(exp_val), size=11, horizontalalignment="center")

    # labels = ["λ = {:>5.1f}".format(l) for l in parameters] # use this to make it ugly
    labels = ["{}$(λ=1.0, k)$".format(func) for func in ["PD", "ZTPD"]]
    plt.legend(labels=labels, prop={'size':20})
    plt.xlabel("$k$", size=20)
    plt.ylabel("$f(k; λ)$", size=20)
    plt.title("ZTPD and PD Probability Mass Functions", size=20)

    plt.savefig("versus.svg")
    # show plot only if needed / specifically asked for
    if "-v" in sys.argv:
        plt.show()

if __name__ == "__main__":
    parameters = [1.0]
    colors = ["red", "blue", "green"]
    granularity = 10
    plot_probabilities(parameters, colors, granularity)

