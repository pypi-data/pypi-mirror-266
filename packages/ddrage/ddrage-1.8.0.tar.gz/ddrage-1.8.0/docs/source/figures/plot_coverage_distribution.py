# -*- coding: utf-8 -*-
import math
import sys
import numpy as np
import seaborn
import matplotlib
import matplotlib.pyplot as plt

from matplotlib import rc


def coverage(expected_coverage, min_cov=None, max_cov=None):
    """Pick a read coverage that can be assigned to a locus.

    The lambda parameter for the binomial distribution is calculated as::
    
        lambda_p = 2.0 if exp_cov <= 10 else exp_cov / 2.0
    
    This guarantees reasonable coverages for low coverage situations and
    also provides a lot of scatter for larger coverages.

    Note:
        The expected coverage is modified by a poisson distribution as follows::

            result = expected_coverage - poisson(lambda_p)
            if result < min_cov:
                return min_cov
            if result > max_cov:
                return max_cov
            return result

        The check against max_cov is not strictly necessary for this, but
        has been added to prevent results leaving the bounderies if other
        distributions are used.

    Arguments:
        expected_coverage (int): Expected number of reads.
        min_cov (int): Minimum result. If ``None``, a sensible value like 2 is assumed.
        max_cov (int): Maximum result. If ``None``, no truncation will take place.

    Returns:
        int: Coverage mondifed by a poisson distribution. Satisfies the in and max
        parameters.
    """
    if not min_cov:
        min_cov = 2

    if expected_coverage <= 10:
        lambda_p = 3.0
    else:
        lambda_p = expected_coverage / 2.0

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


def plot():
    results = []
    per_cov = 100
    max_cov = 101

    # plot expected coverage
    plt.plot(range(1, max_cov+1), color="red")

    # simulate read coverage
    for dₛ in range(1, max_cov+1):
        results.append([coverage(dₛ) for _ in range(per_cov)])

    
    by_expected_cov = [(dₛ, result) for dₛ, result in enumerate(results, start=1)]

    # create two x and y coordinate lists for the scatterplot
    # for each x value multiple y values (per_cov to be precise)
    # are plotted. Maybe this needs to be adapter later to use 
    # a better representation of events per expected coverage
    x = []
    y = []
    for dₛ, result in by_expected_cov:
        for count in result:
            x.append(dₛ)
            y.append(count)
    plt.scatter(x, y)
    
    plt.xlabel("expected coverage: d_s")
    plt.ylabel("generated coverage values")

    plt.show()

    

if __name__ == "__main__":
    plot()
