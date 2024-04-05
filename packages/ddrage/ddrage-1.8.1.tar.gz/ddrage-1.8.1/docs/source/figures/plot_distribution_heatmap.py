# -*- coding: utf-8 -*-
import math
import sys

from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import rc


# TODO: http://opisthokonta.net/?p=1157

def plot_versus():

    dim = 51
    data = np.zeros((2,dim,dim))

    # experimental data
    # for i in range(2, dim):
    #     precision = 10000
    #     all_values = Counter([dist_cov_exp(i) for _ in range(precision)])
        
    #     for j in range(2, dim):
    #         data[j,i] = all_values[j] / precision
    

    # analytical data
    # TODO: Not sure if this checks out. Test this.
    for target_cov in range(2, dim):
        lambda_p = get_lambda(target_cov)
        for k in range(2, dim):
            # data[target_cov, observed_cov] = target_cov - pd_prob(lambda_p, observed_cov) + lambda_p
            data[0, k, target_cov] = pd_prob(lambda_p, k)
            data[1, k, target_cov] = pd_prob(lambda_p, k)


    f, (ax1, ax2) = plt.subplots(1,2)
    axa = sns.heatmap(data[0], cmap="bone_r", ax=ax1)
    axb = sns.heatmap(data[1], cmap="bone_r", ax=ax2)

    axa.set_title("current", fontsize=20)
    axb.set_title("only poisson", fontsize=20)

    axes = [ax1, axb]
    line_offset = 2
    for ax in axes:
        ax.invert_yaxis()
        # plot diagonal for expected coverage
        ax.plot((line_offset, dim), (dim-line_offset,0))
        # plot lowered diagonal for half of the sequencing depth
        ax.plot(((dim/2)+line_offset, dim), (dim-line_offset, dim-(dim/2)), color="r")
    
        # Axes labels
        ax.set_xlabel("target coverage: $d_{s}$")
        ax.set_ylabel("expected coverages")
        
        # make sure only every fifth ticklabel is shown
        interval = 5
        x_labels = [item.get_text() if int(item.get_text()) % interval == 0 else "" for item in ax.get_xticklabels()]
        ax.set_xticklabels(x_labels)
        y_labels = [item.get_text() if int(item.get_text()) % interval == 0 else "" for item in ax.get_yticklabels()]
        ax.set_yticklabels(y_labels)
    
        # Add labels to diagonal lines
        label_fontsize = 20
        # ax.text(dim-2, -1, "target coverage", ha='right', fontsize=label_fontsize, color=sns.color_palette()[0])
        ax.text(dim, (dim*0.65), "$\\frac{d_{s}}{2}$", ha='right', fontsize=label_fontsize, color=sns.color_palette()[2])
    

    # sns.regplot(x, y, )
    # sns.kdeplot(x, ax=ax2)
    plt.show()


def plot():
    """Plot a heatmap for the distribution of coverage values.
    """
    dim = 51
    data = np.zeros((dim,dim))

    # experimental data
    # for i in range(2, dim):
    #     precision = 10000
    #     all_values = Counter([dist_cov_exp(i) for _ in range(precision)])
        
    #     for j in range(2, dim):
    #         data[j,i] = all_values[j] / precision
    

    # analytical data
    # TODO: Not sure if this checks out. Test this.
    for target_cov in range(2, dim):
        lambda_p = get_lambda(target_cov)
        for k in range(2, dim):
            # data[target_cov, observed_cov] = target_cov - pd_prob(lambda_p, observed_cov) + lambda_p
            data[k, target_cov] = pd_prob(lambda_p, k)

    ax = sns.heatmap(data, cmap="bone_r")

    # flip y axis to make sure 0,0 exists
    ax.invert_yaxis()
    
    line_offset = 2
    # plot diagonal for expected coverage
    ax.plot((line_offset, dim), (dim-line_offset,0))
    # plot lowered diagonal for half of the sequencing depth
    ax.plot(((dim/2)+line_offset, dim), (dim-line_offset, dim-(dim/2)), color="r")

    # Axes labels
    ax.set_xlabel("target coverage: $d_{s}$")
    ax.set_ylabel("expected coverages")
    
    # make sure only every fifth ticklabel is shown
    interval = 5
    x_labels = [item.get_text() if int(item.get_text()) % interval == 0 else "" for item in ax.get_xticklabels()]
    ax.set_xticklabels(x_labels)
    y_labels = [item.get_text() if int(item.get_text()) % interval == 0 else "" for item in ax.get_yticklabels()]
    ax.set_yticklabels(y_labels)

    # Add labels to diagonal lines
    label_fontsize = 20
    ax.text(dim-2, -1, "target coverage", ha='right', fontsize=label_fontsize, color=sns.color_palette()[0])
    ax.text(dim, (dim*0.65), "$\\frac{d_{s}}{2}$", ha='right', fontsize=label_fontsize, color=sns.color_palette()[2])

    # plot the figure to pdf
    plt.savefig("cov_dist_heatmap.pdf")

    # show plot only if needed / specifically asked for
    if "-v" in sys.argv:
        plt.show()




def pd_probabilities(lamb, granularity):
    """Probability of PD."""
    return [(math.pow(lamb, k)* math.exp(-1 * lamb))/ math.factorial(k) for k in range(0, granularity)]


def pd_prob(lambda_p, k):
    """P(λ, k)"""
    return (math.pow(lambda_p, k)* math.exp(-1 * lambda_p))/ math.factorial(k)



def get_lambda(expected_coverage):
    """Compute lambda values."""
    if expected_coverage <= 10:
        # lambda_p = expected_coverage # bad results for low values
        # lambda_p = 2.0 # harsh breaking point
        # lambda_p = 2 + (expected_coverage) # linear approximation
        lambda_p = 2*(1 - (expected_coverage/10)) + (expected_coverage) # for a smoother transition
    else:
        # lambda_p = expected_coverage / 2.0
        lambda_p = expected_coverage
    return lambda_p


def distributed_coverage_centered_experimental(expected_coverage, min_cov=None, max_cov=None):
    """Taken from ddrage/distributions.py
    """
    if not min_cov:
        min_cov = 2

    lambda_p = get_lambda(expected_coverage)

    # lambda_p = expected_coverage
    # Move the mode of the poisson distribution (which is lambda)
    # to the expected coverage. Values below E(PD(lambda)) = lambda 
    # will be subtracted from d_s, values above will be added.
    cov = expected_coverage - (np.random.poisson(lambda_p) - int(lambda_p))

    # Make sure the bounds are respected.
    if cov < min_cov:
        return min_cov
    elif max_cov and (cov > max_cov):
        return max_cov
    else:
        return cov

dist_cov_exp = distributed_coverage_centered_experimental


if __name__ == "__main__":
    # plot()
    plot_versus()
