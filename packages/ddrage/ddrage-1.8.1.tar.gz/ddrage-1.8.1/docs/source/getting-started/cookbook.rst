.. _cookbook:

***************
ddRAGE Cookbook
***************

This page lists some parameter combinations for ddRAGE to generate
some common patterns of ddRAD datasets.
For this tutorial, we assume that you have installed ddRAGE as
described :doc:`here <tutorial>`.



Deep sequencing of a diverse population
=======================================

This parameter set emulates a deep sequencing run of 12 individuals
with a number of different alleles per locus and an increased chance
for mutation events.

.. code-block:: Bash

   (ddrage) me@machine:~$ ddrage -l 10000 -n 12 --coverage 100 --diversity 5.0 --event-probabilities 0.8 0.05 0.15


'Budget' sequencing run
=======================

These parameters emulate a cheap sequencing run with low coverage,
a single end library, and 96 individuals in one file.

.. code-block:: Bash

   (ddrage) me@machine:~$ ddrage -l 10000 -n 96 --coverage 10 --combine-p7-bcs --single-end


Sequencing of a large genome with short fragments
=================================================

This parameters create a dataset with many loci and long reads, but the ends of the reads overlap.

.. code-block:: Bash

   (ddrage) me@machine:~$ ddrage -l 300000 -n 24 -r 250 --overlap 0.3



Simulate reads from a reference genome
======================================

This tutorial assumes that you already have a FASTA file (here: `fragments.fa`) that contains generated fragments.
The restriction enzymes used to create the fragments (for example by in-silico digestion) are also specified.
In this case, the p5 restriction enzyme has the recognition site `AATT` and does not leave an overhang,
and the p7 enzymes has the recognition site `CCGG` and leaves the overhang `CGG` in the reads.

Overlap is controlled by the size of the fragments in relation to the read length.

.. code-block:: Bash

   (ddrage) me@machine:~$ ddrage -l fragments.fa --p5-rec-site AATT --p5-overhang "" --p7-rec-site CCGG --p7-overhang CGG



Low quality sequencing
======================
These parameters alter the coverage model to only yield values below 30
and a per base error probability of 5%, simulating a low quality dataset.

The precise shape of the expected quality distribution can be seen by
entering the `--BBD-alpha 8.1 --BBD-beta 1.6` parameters in the
:doc:`visualize_bbd <../documentation/tools>` script.

.. code-block:: Bash

   (ddrage) me@machine:~$ ddrage -l 10000 -n 24 --coverage 25 --BBD-alpha 8.1 --BBD-beta 1.6 --prob-seq-error 0.05
