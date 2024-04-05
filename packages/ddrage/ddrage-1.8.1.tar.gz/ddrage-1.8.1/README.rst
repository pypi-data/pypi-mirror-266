.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4390216.svg 
   :target: https://doi.org/10.5281/zenodo.4390216

#############################
ddRAGE - ddRAD Data Generator
#############################


ddRAGE (ddRAD Data Generator) is a software to simulate double digest restriction site associated DNA sequencing reads.
The generated data sets can be used to test ddRAD analysis tools and validate their results.

The documentation, including a tutorial, can be found `here <https://ddrage.readthedocs.io/>`_.
The code is hosted on `bitbucket`_, `PyPI`_, and `bioconda`_.

.. _bitbucket: https://bitbucket.org/genomeinformatics/rage
.. _PyPI: https://pypi.python.org/pypi/ddrage/
.. _bioconda: https://bioconda.github.io/recipes/ddrage/README.html


*******************
System Requirements
*******************

- python >= 3.8
- numba
- numpy
- matplotlib
- pyyaml
- scipy
- seaborn


For the docs:

- sphinx

For parameter visualization:

- bokeh >= 3.1.1


************
Installation
************

We recommend the installation using conda:

.. code-block:: shell

   $ conda create -n ddrage -c bioconda ddrage
   $ source activate ddrage

Alternatively, you can download the source code from `bitbucket`_ and install it using pip:

.. code-block:: shell

   $ git clone https://bitbucket.org/genomeinformatics/rage.git ddrage
   $ cd ddrage
   /ddrage$ pip install .  # basic version
   # OR
   # to install with support to build the documentation and visualize bbd parameters
   /ddrage$ pip install .[documentation,BBD-visualization]


*****
Usage
*****

To simulate a ddRAD data set, call ddrage from the command line:

.. code-block:: shell

   $ ddrage

you can specify parameters to change data set parameters such as number of individuals (``-n``), nr of loci (``-l``), and coverage (``--coverage``):

.. code-block:: shell

   $ ddrage -n 6 -l 10000 --coverage 30

This creates a data set with reads from 6 individuals at 10000 loci with an expected coverage of 30.

A more detailed tutorial can be found `on readthedocs <https://ddrage.readthedocs.io/en/latest/getting-started/>`_.


*************
Citing ddRAGE
*************

Our paper describing ddRAGE has been published in `Molecular Ecology Resources <http://onlinelibrary.wiley.com/doi/10.1111/1755-0998.12743/full>`_.
You can cite it as follows:

.. code-block::

    Timm H, Weigand H, Weiss M, Leese F, Rahmann S. ddRAGE: A data set generator to evaluate ddRADseq analysis software. Mol Ecol Resour. 2018;18:681–690. https://doi.org/10.1111/1755-0998.12743

BibTeX version:

.. code-block:: latex

    @article{timm2018ddrage,
      title={ddrage: A data set generator to evaluate ddRADseq analysis software},
      author={Timm, Henning and Weigand, Hannah and Weiss, Martina and Leese, Florian and Rahmann, Sven},
      journal={Molecular Ecology Resources},
      volume={18},
      number={3},
      pages={681--690},
      year={2018},
      url = {http://dx.doi.org/10.1111/1755-0998.12743},
      doi = {10.1111/1755-0998.12743},
    }

The source code itself is also published on `Zenodo <https://zenodo.org>`_ under the DOI `10.5281/zenodo.4390216 <https://doi.org/10.5281/zenodo.4390216>`_.
