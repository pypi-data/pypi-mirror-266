.. _enzymes:

Enzymes
-------

List of commonly used restriction enzymes and the required parameters to use them with ddRAGE:


+-----------+----------+-----------------------+----------------------+
| Name      | Type     | Recognition Sequence  | Residue              |
+===========+==========+=======================+======================+
| Csp6I     | Frequent | GTAC                  | TAC                  |
+-----------+----------+-----------------------+----------------------+
| PstI      | Frequent | CTGCAG                | G                    |
+-----------+----------+-----------------------+----------------------+
|           |          |                       |                      |
+-----------+----------+-----------------------+----------------------+
| NsiI      | Rare     | ATGCAT                | TGCAT                |
+-----------+----------+-----------------------+----------------------+
| BamHI     | Rare     | GGATCC                | GATCC                |
+-----------+----------+-----------------------+----------------------+
|           |          |                       |                      |
+-----------+----------+-----------------------+----------------------+
| FatI      |          | CATG                  |                      |
+-----------+----------+-----------------------+----------------------+
| NlaIII    |          | GATG                  |                      |
+-----------+----------+-----------------------+----------------------+
| MluCI     |          | AATT                  |                      |
+-----------+----------+-----------------------+----------------------+
| EcoRI     |          | GAATTC                | ATTC                 |
+-----------+----------+-----------------------+----------------------+
| MspI      |          | CCGG                  | CGG                  |
+-----------+----------+-----------------------+----------------------+
| SbfI      |          | CCTGCAGG              | GG                   |
+-----------+----------+-----------------------+----------------------+


The recognition sequence needs to be passed to the ``--p5/p7-rec-site`` parameter and the residue to the ``--p5/p7-overhang`` parameter.
Example:

.. code-block:: bash

    me@machine:~$ ddrage --p5-rec-site GGATCC --p5-overhang GATCC --p7-rec-site GTAC --p7-overhang TAC

Use *BamHI* as rare cutter and *Csp6I* as frequent cutter.
