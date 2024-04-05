"""Take a file simulated with ddrage --multiple-p7-barcodes and split it up by the p7 barcode.

Writes two files named 'reads_<BARCODE_1.fq(.gz)>' and 'reads_<BARCODE_2.fq(.gz)>' for each barcode found.
These files are stored in the current directory.
"""
import os
import sys

import argparse
import dinopy as dp


def split_files(args):
    fqr_fw = dp.FastqReader(args.p5_file)
    fqr_rev = dp.FastqReader(args.p7_file)
    prefix, suffix = os.path.splitext(args.p5_file)
    if suffix == ".gz":
        suffix = os.path.splitext(prefix)[1] + suffix

    output_files = {}
    for (fw, rev) in zip(fqr_fw.reads(), fqr_rev.reads()):
        # get the nameline of the read (forward or reverse doesn't matter)
        nl = rev.name
        # keep only the entry that defines the p7 barcode
        items = [entry for entry in nl.split() if entry.startswith(b"p7_bc")]

        # This uses the perfect p7 barcode from the annotation
        # To use the simulated barcode, which can contain sequencing errors,
        # use items[1].split[b":"][-1]
        if len(items) == 1:
            # extract the barcode sequence
            p7_bc = items[0].split(b":")[1].strip(b"'")
        else:
            print("Failed to parse name line {}".format(nl))
            print("No entry starts with 'p7_bc'")
            sys.exit(1)

        # check if a file writer for the barcode is already available
        if p7_bc not in output_files:
            filename_fw = "reads_{}_1{}".format(p7_bc.decode(), suffix)
            filename_rev = "reads_{}_2{}".format(p7_bc.decode(), suffix)
            fqw_fw = dp.FastqWriter(filename_fw, force_overwrite=args.force)
            fqw_rev = dp.FastqWriter(filename_rev, force_overwrite=args.force)
            fqw_fw.open()
            fqw_rev.open()
            print("\nFound new barcode: {}".format(p7_bc.decode()))
            print("Writing to:")
            print("  -> {}".format(filename_fw))
            print("  -> {}".format(filename_rev))
            output_files[p7_bc] = (fqw_fw, fqw_rev)
        else:
            fqw_fw, fqw_rev = output_files[p7_bc]

        # write reads back to the writer with the chosen barcode
        fqw_fw.write(*fw)
        fqw_rev.write(*rev)


def get_argument_parser():
    description_text = ("Split a multi-barcode file created by ddRAGE p7 barcode.\n"
                        "Output files are written into the current folder."
    )
    parser = argparse.ArgumentParser(
        description=description_text)

    parser.add_argument(
        help="Path to forward read file.",
        action="store",
        dest="p5_file",
        type=str,
    )

    parser.add_argument(
        help="Path to reverse read file.",
        action="store",
        dest="p7_file",
        type=str,
    )

    parser.add_argument(
        "-f", "--force",
        help="Overwrite existing files when creating the output.",
        action="store_true",
        dest="force",
        default=False,
    )

    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    split_files(args)


if __name__ == "__main__":
    main()
