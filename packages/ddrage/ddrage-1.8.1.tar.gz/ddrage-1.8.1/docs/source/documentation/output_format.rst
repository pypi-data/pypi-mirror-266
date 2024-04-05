*************
Output Format
*************

Rage writes three types of output files:
Simulated reads that can be analyzed,
supplementary files that contain additional information about the reads as well as statistics
and ground truth files, that contain expected results of an analysis.


Reads
=====

The reads are written to disk as FASTQ files.
Because paired-end reads are simulated two files are created.
The first file with the suffix ``_1.fastq`` contains the p5 (or forward) reads
while the file with the suffix ``_2.fastq`` contains the p7 (reverse) reads respectively.

The reads are sorted by locus ID and individual.
While this makes it easy to validate results manually,
it might create unreasonably easy problem instances for analysis tools.
In order to assure a realistic instance of the problem
please consider shuffling the FASTQ files, as described :ref:`here <randomize_read_order>`.

Annotation
----------

Each effect simulated for a specific read is annotated in the name line of that read in the FASTQ file.
As usual for current Illumina sequencers, the name line starts with a CASAVA style name line like

.. code-block:: bash

    @instrument:29:42:72:23:0:0 1:N:0:ACTTGA 

which contains information provided by the sequencer.
The instrument name always is ``instrument``, and the following six entries (run id, flowcell id,
lane, tile, x-coordinate, y-coordinate) are populated with random integer values.
Run, flowcell id and lane are uniformly chosen from [0, 10000) and tile, x-coordinate and y-coordinate
from [0, 1000000). These entries result in a high probability of accidental collisions.

In the second group, the pair entry is set to 1 for p5 reads and to 2 for
p7 reads. The filtered entry is N (no) for all reads and none of the control bits is set.
The most interesting part here is the p7 index barcode.

After the CASAVA line, separated by a space, follows a space separated list of key-value-pairs.
Each of these pairs is formatted as `key:'value'`.
The key is guaranteed to contain no spaces, the value can contains spaces.
The following keys can occur:

+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| Key                   | Value                                                                         | Format/ Type                     | Example                       |
+=======================+===============================================================================+==================================+===============================+
| read_from             | | Name of the individual from which this read originates.                     | | Individual name as string      | | read_from:'Individual 20'   |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| at_locus              | | For valid reads: Name/ Number of the locus from which this read originates. | | Integer                        | | at_locus:'42'               |
|                       | | For singletons/ HRL reads: Locus type and Name/ Number of origin locus.     | | String                         | | at_locus:'singleton_35'     |
|                       |                                                                               | | String                         | | at_locus:'hrl_23'           |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| p5_bc                 | | Sequence of the p5 barcode.                                                 | | String                         | | p5_bc:'ACTTGA'              |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| p7_bc                 | | Sequence of the p7 barcode.                                                 | | String                         | | p7_bc:'GGCTAC'              |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| rID                   | | Pseudounique read ID.                                                       | | String                         | | rID:'fjibo'                 |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| type                  | | Individual event type that created this read.                               | | String                         | | type:'common'               |
|                       |                                                                               |                                  | | type:'PCR copy'             |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| p5_seq_errors         | | Sequencing errors in the p5 read.                                           | | Semicolon separated positions  | | p5_seq_errors:'17;23'       |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| p7_seq_errors         | | Sequencing errors in the p7 read.                                           | | Semicolon separated positions  | | p7_seq_errors:'17;23'       |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| p7_barcode_seq_errors | | Sequencing errors in the p7 index barcode.                                  | | Semicolon separated positions  | | p7_barcode_seq_errors:'5'   |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| mutations             | | Types of mutations in this read. Can be empty for het. mutations            | | String                         | | mutations:'p7@36(20):A>T'   |
|                       | | including the common allele (Allele 0)                                      |                                  |                               |
|                       | | For a full list see :ref:`notation of mutations <mutations>`.               |                                  |                               |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+
| genotype              | | Which allele has been applied to this read along the zygosity.              | | String                         | | genotype:'het. Allele 1'    |
|                       |                                                                               |                                  | | genotype:'hom. Allele 42'   |
+-----------------------+-------------------------------------------------------------------------------+----------------------------------+-------------------------------+

Note that some ddRAd analysis tools can not handle this addition to the FASTQ name line.
For these, the annotation has to be removed using the ``remove_annotation`` script, as described in the :doc:`the tools chapter <tools>`.

Supplementary Files
===================

The supplementary files contain additional information about the data set and the simulated events.
They consist of:

    - An **annotation file** containing a list of the used parameters, sequences etc.

    - A **statistics file** in pdf format. This is a graphical aggregation of important parameters
      of the simulation. It includes plots for the distribution of locus types, number of SNPs
      etc.

    - A barcode file containing barcodes and spacers used for individuals in the data set.


Ground Truth
============

The ground truth generated by ddRAGE is saved in YAML format.
It contains three separated documents:

1. **Individual information**: Containing the auxiliary sequences associated with the individuals in the sample.
2. **Locus entries**: One entry, named ``Locus i`` where ``i`` is the locus number, starting with 0 for each valid locus.
   Each locus entry contains the locus sequence, coverage and genotype information for the individuals.
3. **HRL entries**: One entry per HRL locus, named ``HRL Locus i``. Contains the coverage for each individual at the HRL locus.

These three segments are saved as disjoint YAML documents in the same file (separated by lines containing only ``--``).
The can be unpacked using the ``load_all`` function supplied by most YAML readers.


Specification
-------------

+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+
| Key                        | Content                                 | Content Format                                                            |
+============================+=========================================+===========================================================================+
| Individual Information     | Auxiliary sequences for all             | One dictionary per individual containing: 'dbr', 'p5 bc', 'p5 spacer',    |
|                            | individuals in the sample.              | 'p5 overhang', 'p7 bc', 'p7 spacer', 'p7 overhang'.                       |
+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+
|                                                                                                                                                  |
+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+
| | Locus ``i``              | Simulated events for the locus.         | | allele coverages (dict: allele name -> int),                            |
| | (one entry per locus)    |                                         | | allele frequency (dict: allele name -> float),                          |
|                            |                                         | | total locus coverage (int),                                             |
|                            |                                         | | nr of id reads (int),                                                   |
|                            |                                         | | individual genotypes (dict: individual name -> allele; allele is a      |
|                            |                                         |   dict: allele name -> (cov (int), mutations (list of string              |
|                            |                                         |   representation of all mutations of the allele))                         |
|                            |                                         |                                                                           |
+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+
|                                                                                                                                                  |
+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+
| | HRL locus ``j``          | Coverages for the individuals at the    | Dictionary mapping individual names (str) to coverage values (int).       |
| | (one entry per HRL)      | HRL locus.                              |                                                                           |
+----------------------------+-----------------------------------------+---------------------------------------------------------------------------+

.. _mutations:

Notation of Mutations
---------------------

The four kinds of mutations simulated by ddRAGE, namely: SNPs, insertions, deletions, and null alleles, are notated as follows:

+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+
| Mutation Type                              | Representation                                       | Example           | Translation                                                                       |
+============================================+======================================================+===================+===================================================================================+
| SNP                                        | [p5,p7]@[seq. pos]([read pos)]:[base from]>[base to] | p5@33(54):A>T     | An A>T polymorphism in the p5 read. At genomic position 33 (without               |
|                                            |                                                      |                   | auxiliary sequences) and read position 54 (including auxiliary sequences).        |
+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+
| Insertion                                  | [p5,p7]@[seq. pos]([read pos)]:+[insert bases]       | p5@33(54):+ACG    | An insertion of the sequence ACG in the p5 read after genomic position 33         |
|                                            |                                                      |                   | (read position 54).                                                               |
+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+
| Deletion                                   | [p5,p7]@[seq. pos]([read pos)]:-[deleted bases]      | p5@33(54):-T      | A deletion of the sequence T in the p5 read after genomic position 33             |
|                                            |                                                      |                   | (read position 54).                                                               |
+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+
| Null Alleles with alternative sequences    | p7:NA_alternative, p5:NA_alternative                 | p7:NA_alternative | Null alleles changing the whole p5 or p7 seqeunce of a read.                      |
+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+
| Null Alleles with dropout                  | p7:NA_dropout, p5:NA_dropout                         | p4:NA_dropout     | Null alleles preventing reads from being generated (can only be seen in _gt file) |
+--------------------------------------------+------------------------------------------------------+-------------------+-----------------------------------------------------------------------------------+

Regular expression for SNPs, Insertions, and Deletions:

.. code-block:: python

   import re
   
   mutation_string = "p5@33(54):+ACG"
   reg_exp = re.compile("(p\d)@(\d+)\((\d+)\):(.*)")
   read_direction, read_position, genomic_position, diff = reg_exp.search(mutation_string).groups()



Genomic Position vs. Read Position
----------------------------------

If two positions for a mutation are listed, the position in braces is a :ref:`read position <pos_notation>`, while the other is the sequence position.

The read position describes the position measured from the beginning of the read, including all auxiliary sequences.
This is equivalent to the position of the mutation in the reads in the FASTQ files.

The sequence position, on the other hand, denotes the position in the genomic sequence of the reads.
This is helpful when only the genomic sequence is present and all auxiliary sequences have been removed during analysis.


Barcode file
------------

The barcode file contains a header and one line for each individual in
the dataset. Each line contains, in this order and separated by tabs,
the following information:

- individual name
- p5 barcode
- p7 barcode
- p5 spacer seqeunce
- p7 spacer seqeunce
- individual annotation
