============
Input Format
============

.. _barcode_filespec:

Barcode File
------------
A barcode file describes the individuals that can be contained in a data set,
as well as their barcodes and spacer sequences.
The file contains three blocks of information as tab separated values:

 1. A mapping of p5 barcode index to p5 barcode sequence.

 2. A mapping of p7 barcode index to p7 barcode sequence.

 3. A mapping of p5 index and p7 index to p5 spacer, p7 spacer, individual name and further information.


Example::

    # p5 barcodes
    1	ATCACG
    2	CGATGT
    3	TTAGGC
    4	TGACCA
    
    # p7 barcodes
    1	ATCACG
    8	ACTTGA
    
    # specimen
    1	1			Individual 1	Annotation 1
    3	1	AC		Individual 2	Annotation 1
    2	8	GAC	AT	Individual 3	Annotation 2
    4	8	C	AT	Individual 4	Annotation 1

This file shows four individuals.
The individual ``Individual 2`` is encoded using the the p5 barcode ``TTAGGC`` (index 3) and the p7 barcode ``ATCACG`` (index 1).
The p5 reads if this indiviual have a spacer of ``AC``, while the p7 reads have an empty spacer sequence.
Any additional information, here only the generic ``Annotation 1``, can be added separated by additional tabs.

It is possible to simulate different barcode lengths in the same dataset:

Example::

    # p5 barcodes
    1	ATCA
    2	CGATGTAC
    3	TTAGGCG
    4	TGACCATGTACCG
    
    # p7 barcodes
    1	ATCACG
    8	ACTTGATG
    
    # specimen
    1	1			Individual 1	Annotation 1
    3	1	AC		Individual 2	Annotation 1
    2	8	GAC	AT	Individual 3	Annotation 2
    4	8	C	AT	Individual 4	Annotation 1

The combination of barcode length and spacer length determines, how much of the simulated
genomic sequence is discoverable in a read. Given the fixed read length, individuals with
short barcodes have more free space for genomic sequence in the read setup than individuals
with long barcodes. A set of example barcode files can be found in the `bitbucket repository <https://bitbucket.org/genomeinformatics/rage/src/master/ddrage/barcode_handler/barcodes/>`_.

Note, that only individuals who share a p7 barcode can occur in one data set.

.. _qmodel_filespec:

Quality Model
-------------

The quality model used by ddRAGE to sample quality values is saved as a probability vector for each read position.
Consider a small example with three positions::

           P(q=0)    P(q=1)    P(q=2)
    pos 0  [0.0,      0.2,      0.8]
    pos 1  [0.1,      0.3,      0.6]
    pos 2  [0.5,      0.3,      0.2]
    pos 3  [0.6,      0.3,      0.1]

The probabilities are saved as a 2d numpy array of doubles and read by ddRAGE using the function `numpy.loadtxt <https://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html>`_.

You can specify your own quality model by creating a qmodel file.
One way to achieve this using python is to create a numpy array and write it to a qmodel file using `numpy.savetxt <https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html>`_.


.. code-block:: python

    import numpy as np

    nr_positions = 100
    nr_quality_values = 104-33 # only consider valid PHRED scores in Illumina 1.8 format
    values = np.zeros(shape=(nr_quality_values, nr_positions), dtype=np.double)

    # fill in all probability values
    for pos in range(nr_positions):
        for phred_value in range(nr_quality_values): 
            # compute probability for the phred_value occuring at read position pos
            values[phred_value][pos] = prob(phred_value, pos)

    # save the file
    np.savetxt("mymodel.qmodel", values)


If the desired read length (defined by ``-r`` parameter) surpasses the number of positions defined in the qmodel 
the last value will be used to pad the probability matrix.
In this example with ::

             P(q=0)    P(q=1)    P(q=2)

    pos 0     0.0,      0.2,      0.8    
    pos 1     0.1,      0.3,      0.6    
    pos 2     0.5,      0.3,      0.2    
    pos 3     0.6,      0.3,      0.1 

    pos 4     0.6,      0.3,      0.1      padded from pos 3
    ...                 ...
    pos n     0.6,      0.3,      0.1      padded from pos 3


All vectors after an empty or non-1 probability vector will be ignored and overwritten using the last valid entry::


             P(q=0)    P(q=1)    P(q=2)

    pos 0     0.0,      0.2,      0.8    
    pos 1     0.1,      0.3,      0.6    
    pos 2     0.0,      0.0,      0.0      this line does not sum up to 1
    pos 3     0.6,      0.3,      0.1      this line will be ignored

    
    pos 2     0.1,      0.3,      0.6      padded from pos 1
    pos 3     0.1,      0.3,      0.6      padded from pos 1
    pos 4     0.1,      0.3,      0.6      padded from pos 1
    ...                 ...
    pos n     0.1,      0.3,      0.6      padded from pos 1



.. _numpy: https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html
