#########
Changelog
#########

*************
Version 1.8.0
*************

- Added support up to Python 3.12. Please note that the bioconda installation
  is currently only supported for Python versions up to 3.10. For newer Python
  versions, ddrage can be installed from PyPI via pip.
- Removed support for Python <=3.7
- Updated project structure to use pyproject.toml
- Added compatibility for bokeh >=2.5.0.
- Minor documentation updates.


*************
Version 1.7.1
*************

Bugs fixed
==========

Fixed newer version of scipy to prevent errors with the import of `comb`.


*************
Version 1.7.0
*************

Bugs fixed
==========

In low coverage scenarios, it is possible for incomplete digestion (ID) to
affect all reads of an individual at a locus. This update fixes a possible crash
due to an empty list when this conincides with a homozygous mutation event.

Documentation
=============

- Fixed some typos.

Other changes
=============

Added support for Python 3.8.


*************
Version 1.6.3
*************

Other changes
=============

Refactored the content of the annotation output file to be more informative.
Added a visualization for the distribution of simulated read types (valid, PCR
duplicate, HRL, singleton, etc.) and clarified the names of the read types.

*************
Version 1.6.2
*************

Bugs fixed
==========

Singletons from individuals not in the data set
-----------------------------------------------

Singletons with p5-p7 barcode combinations that were not in the barcode file
could be created. More precisely, additional barcode combinations of specified
p5 and p7 barcodes were created.

This is no longer possible.


*************
Version 1.6.0
*************

New features
============

Added the ``--no-singletons`` parameter to disable singleton generation.

Documentation
=============

- Fixed description of ``-o`` parameter to reflect actual behaviour.

- Fixed some typos.


*************
Version 1.5.2
*************

Other changes
=============

- Control bits in the CASAVA header are now set to 0.

- Added the ``--version`` flag to show the installed version of ddRAGE.

- Fixed broken link in file format documentation.


*************
Version 1.5.1
*************

Added compatibility with Python 3.7, restored compatibility with Python 3.5.

*************
Version 1.5.0
*************


New features
============

Splitting files by p7 barcode
-----------------------------

After creating a multi-p7 barcode set using the ``--multiple-p7-barcodes``
parameter, the ``split_by_p7_barcode`` tool can be used to splits the
generated FASTQ files up by their p7 barcode.

Example:


.. code::

   $ rage --multiple p7 barcodes
   Simulating reads from 3 individuals at 3 loci with a coverage of 30.

   Created output files:
       p5 reads                  data_folder/ddRAGEdataset_2_p7_barcodes_1.fastq
       p7 reads                  data_folder/ddRAGEdataset_2_p7_barcodes_2.fastq
       ground truth              data_folder/ddRAGEdataset_2_p7_barcodes_gt.yaml
       barcode file              data_folder/ddRAGEdataset_2_p7_barcodes_barcodes.txt
       annotation file           data_folder/logs/ddRAGEdataset_2_p7_barcodes_annotation.txt
       statistics file           data_folder/logs/ddRAGEdataset_2_p7_barcodes_statstics.pdf

   $ cat data_folder/logs/ddRAGEdataset_2_p7_barcodes_annotation.txt
   #  Ind.	p5 bc	p7 bc	p5 spc	p7 spc	Annotation
   Individual 05	ACAGTG	ATCACG	AC		Annotation 1
   Individual 12	CTTGTA	ATCACG	GAC		Annotation 1
   Individual 54	GCCAAT	TAGCTT		AT	Annotation 3

The files contain reads with two different p7 barcodes (ATCACG and TAGCTT).
To split them up, call ``split_by_p7_barcode file_1.fq file_2.fq`` and pass the two FASTQ
files as parameters:

.. code::

   $ split_by_p7_barcode data_folder/ddRAGEdataset_2_p7_barcodes_1.fastq data_folder/ddRAGEdataset_2_p7_barcodes_2.fastq

   Found new barcode: TAGCTT
   Writing to:
     -> reads_TAGCTT_1.fastq
     -> reads_TAGCTT_2.fastq

   Found new barcode: GGCTAC
   Writing to:
     -> reads_GGCTAC_1.fastq
     -> reads_GGCTAC_2.fastq

This leaves you with two FASTQ files for each barcode,
that are placed in the current working folder.
The tool preserves the file ending, hence if you pass two ``.fq.gz`` files,
the output will also be in gzipped FASTQ format.

If these target files are already present, you need to pass the
``--force`` parameter to overwrite them.


Bugs fixed
==========

Index error when placing SNPs in the multiple p7 barcodes case
--------------------------------------------------------------

When simulating reads with multiple p7 barcodes, the length variability
of the p7 reads was not taken into account. This resulted in SNPs being
placed in a region that was not present in some reads, causing ddRAGE
to crash with:

.. code::

   IndexError: bytearray index out of range

This does no longer occur.


Documentation
=============

Fixed example barcodes files, which contained an invalid combination of indexes.


Other changes
=============

Pseudounique CASAVA headers
---------------------------

Some analysis tools have problems with reads with duplicate names.
Until now this was quite likely to happen, since only two entries of
the (simulated) CASAVA header were random. Now, the run, flowcell_id, and
lane fields are filled with a random integer between 0 and 10000.
The lane, tile, xpos, and ypos fields contain a random integer between 0
and 1000000000. This should avoid collisions for most data sets.



*************
Version 1.4.0
*************

New features
============

p5 ID reads
-----------

ID reads are now simulated for both the p5 and the p7 side of the read.
Before only p7 ID reads were simulated. To account for the lower
probability of p5 ID reads (the p5 cutter is a rare cutter so
incompletely digested fragments are unlikely to pass size selection in
the ddRAD pipeline) 1% of the ID events are on the p5 side of the read.


PCR rates for HRLs and singletons
---------------------------------

The PCR copy rate relative to valid reads can now be changed using the
``--hrl-pcr-copies`` and ``--singleton-pcr-copies`` parameters
respectively. Both take a fraction and are used to modify the basic
``--prob-pcr-copy`` parameter. For example, with ``--prob-pcr-copy 0.1``
and ``--hrl-pcr-copies 1 --singleton-pcr-copies 0.2``, PCR duplicates
for HRL reads are as likely as for valid reads, while PCR duplicates
for singletons only occur with a chance of ``0.1 * 0.2 = 0.02`` per read.


*************
Version 1.3.1
*************

Bugfixes
========

Fixed bug in ``remove_annotation`` script that caused it to crash.


*************
Version 1.3.0
*************

New features
============

Barcode files
-------------

A barcodes file, containing a list of individuals in the sample and
their associated barcodes, is automatically written as output.

Two larger standard barcode files have been added as default barcode
sets. The ``big`` barcode file contains 91 p5 barcodes of length 6 and
one p7 barcode of the same length. The ``huge`` barcode file contains
1461 p5 barcodes of length 10 and one p7 barcode of the same length.
These two barcode sets can be accessed with the ``-b`` parameter,
like: ``-b huge``.

Added the ``--get-barcodes`` parameter, which copies the default
barcode files to a local folder named ``barcode_files``. No existing
files are overwritten by this. This can be used to extract the barcode
files if ddRAGE has been installed via conda or pip.


Zipped output
-------------

FASTQ files can be written as gzipped files, by passing the ``-z``
parameter to ddRAGE. Note that the ``randomize_fastq`` script is unable
to read gzipped files. However, it can write gzipped files, by passing
a file name ending with ``".gz"`` as output file.

.. code::
   
      me@machine:~/$ randomize_fastq ddRAGEds_ATCACG_1.fastq ddRAGEds_ATCACG_2.fastq ddRAGEds_ATCACG_randomized_1.fastq.gz ddRAGEds_ATCACG_randomized_2.fastq.gz

The ability to read zipped input has been added to the ``remove_annotation`` script.

Paired-end quality models
-------------------------

The ``learn_qmodel`` script now supports different models for p5 and
p7 reads. This change replaces the old plain-text ``.qmodel`` files
with binary ``.qmodel.npz`` files.
Additionally the script can now show the progress of the analysis
(``-v``, opens a constantly updating plot), can write a plot of the
learned distribution (``-p`` a pdf file with the same name prefix as
the output file), and plot the distribution for a given quality model
file (``-s custom.qmodel.npz``).
New quality models have also been added.


Single-end mode
---------------
Single-end datasets can now be simulated using the ``--single-end``
parameter. Only a p5 read file will be written and no mutations or
sequencing errors are written for the p7 read.


Fragment mode
-------------
A FASTA file can now be passed to the ``-l, --loci`` (former
``--nr-loci``) parameter to create reads from the contained sequences.
This allows to simulate reads from a reference genome.
The number of simulated loci is the number of sequences in the file.


Overlap
-------
The overlap of simulate reads can now be influenced with the
``--overlap`` parameter. The default value (0.0) means that reads do
not overlap, and the maximum value (1.0) makes reads overlap
significantly (the exact value depends on the adaptor setup of the
reads).
In fragment mode, the overlap is determined from the length of the
sequences in the FASTA file and this parameter has no effect.


New Mutation Types
------------------
In addition to p7 null allele mutation that alter the p7 sequence,
three additional mutation types have been added:

  - p5 na mutations that alter the p5 seqeunce
  - p5 dropout mutations that make one allele drop out
  - p7 dropout mutations that make one allele drop out 

The ``--mutation-type-probability`` parameter has been apadted to now
use 7 probabilities: 

.. code::
   
   PROB_SNP PROB_INSERTION PROB_DELETION PROB_P5_NA_MUTATION PROB_P7_NA_MUTATION PROB_P5_NA_DROPOUT PROB_P7_NA_DROPOUT

In Order to make entering small probabilities easier, each of these
values can now be written as a small equation in python syntax. To do
this put the equation in single or double quotes:

.. code::

   python ddrage.py --mutation-type-probabilities 0.8999 0.05 0.05 '0.0001*(1/24)' '0.0001*(7/24)' '0.0001/3' '0.0001/3'
   

Other changes
=============

Name change
-----------
We fully renamed the program to ddRAGE including all file paths, file names, etc.

File names
----------

Removed colons from the default ISO timestamp folder names.
These caused escaping issues and have been replaced with dots.

.. code::

   old: 2017-09-18T11:14:09_ddRAGEdataset
   new: 2017-09-18T11.14.09_ddRAGEdataset

Consensus sequences in YAML file
--------------------------------

The consensus sequence reported in the YAML file are now the longest
read sequence found in the dataset. Individuals with long barcodes
will have less of this sequence present in the generated reads, since
read lengths are truncated to a fixed length determined by the ``-r``
parameter.


Performance Improvements
------------------------
Several improvements, drastically reducing the memory footprint while
also reducing runtime.


Other
-----

Fixed several typos in documentation, plots, and source code.

Bugfixes
========

Fixed ``randomize_fastq`` not working when writing to stdout when using only one input file.


*************
Version 1.2.0
*************

New features
============

Visualization of BBD parameters
-------------------------------

Added bokeh visualization of BBD parameter choice which is available using the ``visualize_bbd`` script:

.. code:: 

    $ visualize_bbd

This opens a browser window displaying an interactive plot of the BBD that can be used to select
alpha- and beta-parameters.


Removal of FASTQ annotations
----------------------------

Added ``remove_annotation`` script to remove annotations written in the FASTQ name lines of RAGE files,
since some analysis tools can not handle the extended name lines:

.. code::

    $ remove_annotation RAGEdataset_ATCACG_1.fastq RAGEdataset_ATCACG_2.fastq

The simulated files will remain unchanged and two new files without annotation are written.
The extracted annotations are written to a new file with the ``_annotation.txt`` suffix.
This file contains one line per read in the FASTQ file.


Other changes
=============

Also mad some minor fixes in the documentation and added a list of restriction enzymes to the docs.

*************
Version 1.1.0
*************

Added ``learn_qmodel`` script, which allows generating a .qmodel file from a set of FASTQ files.


*************
Version 1.0.0
*************

Initial release.
