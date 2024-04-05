Barcode File Handler
=====================

Module to process and handle barcode files.
A DeBarcoder object will be created that contains a bunch of
dictionaries for all needed applications:

  * Get all possible p7 barcodes for a given p5 barcode
  * Get all possible p5 barcodes for a given p7 barcode
  * Get the p5 spacer sequence for a p5 barcode
  * Get the p7 spacer sequence for a p7 barcode
  * Get the spacer pair (p5, p7) for a barcode pair (p5, p7)
  * Get the individual name for for a barcode pair (p5, p7)
  * Get the population name for for a barcode pair (p5, p7)
  * Get the additional information for for a barcode pair (p5, p7)
  * Check if a barcode pair (p5, p7) is valid
  * Get all information for a barcode pair (p5, p7)
  * Create an individual matrix, showing p5 barcodes x p7 barcodes
    where each entry is an individuals name.
