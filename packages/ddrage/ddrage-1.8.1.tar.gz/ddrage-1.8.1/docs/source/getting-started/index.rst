###########################
Getting Started with ddRAGE
###########################

***************
What is ddRAGE?
***************
ddRAGE is a simulation tool for double digest restriction site associated DNA sequencing data.
With one run of ddRAGE you can create a set of FASTQ files with ddRAD reads and the results expected from an analysis of these reads.

*********************
How does ddRAGE work?
*********************
ddRAGE simulates a set of independent loci without using a reference genome.
Each individual can show one of three different types at each locus: common, dropout, and mutation.
The simulated effect is annotated in the name line of the generated FASTQ files and written to a ground truth file (in YAML format).

For a detailed explanation of the simulation, please take a look at `the paper`_ and `its supplement`_.

****************
What to do next?
****************

- Follow the tutorial: :doc:`tutorial`.
- Read more about :doc:`input formats <../documentation/input_format>`.
- Read more about :doc:`output formats <../documentation/output_format>`.
- Browse a list of :doc:`command line parameters <../documentation/parameters>`.
- Take a look at the :doc:`ddRAGE cookbook <../getting-started/cookbook>`.


.. toctree::
   :maxdepth: 1

   tutorial
            
.. _the paper: https://doi.org/10.1111/1755-0998.12743
.. _its supplement: https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2F1755-0998.12743&file=men12743-sup-0001-AppendixS1.pdf
