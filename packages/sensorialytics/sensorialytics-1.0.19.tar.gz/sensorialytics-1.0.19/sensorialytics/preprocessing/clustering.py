#  clustering.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

from itertools import groupby

import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn
from sklearn.cluster import SpectralClustering, DBSCAN

from .manipulations import norm_cov_matrix

__all__ = ['cluster_variables']


def cluster_variables(df: pandas.DataFrame, n_clusters: int, sigma: float,
                      clustering_variables: set = None, target: set = None,
                      return_results: bool = False,
                      plot_results: bool = False,
                      **kwargs):
    """
    :param df: pandas dataframe
    :param n_clusters: number of cluster to create
    :param sigma: decay constant for affinity matrix
    :param clustering_variables: variables to use in clustering
    :param target: optional target variable to spot correlations
    :param return_results: return full clusters description
    :param plot_results: plot the covariance and affinity matrices
    :param kwargs: kwargs for seaborn heatmap
    :return: full clusters description
    """
    # Affinity -----------------------------------------------------------------
    clustering_variables, matrix_variables, target = __get_variables(
        clustering_variables=clustering_variables,
        df=df,
        target=target
    )

    clustering_matrix_full, clustering_matrix, cov_matrix = __get_matrices(
        clustering_variables=clustering_variables,
        df=df,
        matrix_variables=matrix_variables,
        sigma=sigma,
        n_clusters=n_clusters
    )

    # Clusters -----------------------------------------------------------------
    clusters, clusters_dim, ordered_variables = __get_clusters(
        clustering_matrix=clustering_matrix,
        clustering_variables=clustering_variables,
        n_clusters=n_clusters,
        sigma=sigma,
        target=target)

    sorted_cov_matrix = cov_matrix.loc[ordered_variables, ordered_variables]
    sorted_clustering_matrix_full = clustering_matrix_full.loc[
        ordered_variables, ordered_variables]

    # Plots --------------------------------------------------------------------
    if plot_results:
        __plot_results(
            sorted_cov_matrix=sorted_cov_matrix,
            sorted_clustering_matrix_full=sorted_clustering_matrix_full,
            clusters_dim=clusters_dim,
            target=target,
            **kwargs)

    if return_results:
        return {
            'clusters': clusters,
            'cov_matrix': cov_matrix,
            'clustering_matrix': clustering_matrix,
            'sorted_cov_matrix': sorted_cov_matrix,
            'sorted_clustering_matrix_full': sorted_clustering_matrix_full
        }


def __get_matrices(clustering_variables, df, matrix_variables, sigma,
                   n_clusters):
    cov_matrix = numpy.abs(norm_cov_matrix(df[matrix_variables]))
    dist_matrix = numpy.maximum(1. - cov_matrix, 0.0)

    clustering_matrix_full = __get_clustering_matrix_full(
        n_clusters=n_clusters,
        dist_matrix=dist_matrix,
        sigma=sigma
    )

    clustering_matrix = \
        clustering_matrix_full.loc[clustering_variables, clustering_variables]

    return clustering_matrix_full, clustering_matrix, cov_matrix


def __get_clustering_matrix_full(n_clusters, dist_matrix, sigma):
    if n_clusters is None:
        return dist_matrix
    else:
        return numpy.exp(- dist_matrix ** 2 / (2. * sigma ** 2))


def __get_variables(clustering_variables, df, target):
    if target is None:
        target = set()

    if clustering_variables is None:
        matrix_variables = set(df.columns)
    else:
        matrix_variables = clustering_variables.copy()

    matrix_variables.update(target)
    clustering_variables = matrix_variables.copy()
    clustering_variables.difference_update(target)

    return clustering_variables, matrix_variables, target


def __get_clusters(clustering_matrix, clustering_variables, n_clusters, sigma,
                   target):
    if n_clusters is None:
        cluster = DBSCAN(metric='precomputed', eps=sigma, min_samples=1)
    else:
        cluster = SpectralClustering(affinity='precomputed',
                                     n_clusters=n_clusters)

    clusters_tags = cluster.fit_predict(X=clustering_matrix)

    clusters = {}
    for k, v in sorted(zip(clustering_variables, clusters_tags)):
        clusters.setdefault(v, []).append(k)

    clusters_dim = [
        len(list(group))
        for _, group in groupby(sorted(clusters_tags))
    ]

    ordered_variables = [
                            x for _, x in
                            sorted(zip(clusters_tags, clustering_variables))
                        ] + list(target)

    return clusters, clusters_dim, ordered_variables


def __plot_results(sorted_cov_matrix, sorted_clustering_matrix_full,
                   clusters_dim,
                   target, **kwargs):
    height = max(10, len(sorted_cov_matrix.columns) // 5)
    plt.rcParams['figure.figsize'] = (18, height)

    titles = ['sorted_cov_matrix', 'sorted_clustering_matrix']
    matrices = [sorted_cov_matrix, sorted_clustering_matrix_full]

    for title, matrix in zip(titles, matrices):
        g = seaborn.heatmap(
            data=matrix,
            cmap='viridis',
            linecolor='black',
            linewidths=0.1,
            **kwargs)

        g.axes.hlines(numpy.cumsum(clusters_dim)[:-1], *g.axes.get_xlim(),
                      colors='white', )
        g.axes.vlines(numpy.cumsum(clusters_dim)[:-1], *g.axes.get_xlim(),
                      colors='white')

        if len(target) > 0:
            g.axes.hlines(numpy.cumsum(clusters_dim)[-1],
                          *g.axes.get_xlim(),
                          colors='red', )
            g.axes.vlines(numpy.cumsum(clusters_dim)[-1],
                          *g.axes.get_xlim(),
                          colors='red')

        g.set_title(title)
        plt.show()
