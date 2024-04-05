# -*- coding: utf-8 -*-
"""Module for postprocessing steps like adding singletons and hrl reads.
"""
import random
import string
import numpy as np

from .rad_reads import ProtoReadp7, ProtoReadp5, RADRead
from .generation import random_seq, get_p_from_gc_content
from .initialization import create_perfect_hrl_locus
from . import read_mutation_handling


class SingletonGenerator:
    """Generator to create sinleton reads."""

    def __init__(self, individuals, args):
        """Create a new generator from a set of individuals and other arguments.

        Arguments:
            individuals (iterable): A list containing the barcoding information
                for all individuals in the sample.
            args (argparse.Namespace): From argparser.
        """
        # estimate the total dataset size, i.e. the expected number of reads
        # that will be created, in order to calculate the number of singletons
        # created as a fraction of the total read number
        self.estimated_size = args.nr_loci * len(individuals) * args.cov
        # choose number of singleton reads to create
        if args.no_singletons:
            self.nr_singletons = 0
        else:
            self.nr_singletons = np.random.binomial(self.estimated_size, 0.15)
        self.individuals = individuals
        # extract parameters from arguments object
        # sequence parameters
        self.dbr_seq = args.dbr
        self.p7_overhang = args.p7_overhang
        self.p5_overhang = args.p5_overhang
        self.p7_overhang = args.p7_overhang
        self.p5_rec_site = args.p5_rec_site
        self.p7_rec_site = args.p7_rec_site
        self.read_length = args.read_length
        self.single_end = args.single_end
        self.nr_pcr_copies = 0
        # probabilities and other parameters
        self.prob_seq_error = args.prob_seq_error
        self.max_pcr_copy_nr = args.max_pcr_copy_nr
        self.gc_content = args.gc_content
        # singletons do not get pcr duplicates that often.
        # most of them are noise.
        self.prob_pcr_copy = (args.prob_pcr_copy * args.singleton_pcr_copies)

    def reads(self):
        """Create and yield a set of Singleton reads.

        Create a dummy locus for each singleton.

        Yields:
            RADRead: RADRead objects that do not have any connection to any
            locus.
        """
        seqprobs = get_p_from_gc_content(self.gc_content)

        for i in range(self.nr_singletons):
            # uniformly randomly choose an individual as origin
            (barcode_p5, p7_bc), (spacer_p5, p7_spacer, individual_name, *_) = random.choice(self.individuals)

            # create a new p7 and p5 sequences for each singleton
            protoread_p7 = ProtoReadp7(p7_bc, p7_spacer, self.dbr_seq,
                                       self.p7_overhang, self.p7_rec_site,
                                       self.gc_content, self.read_length)
            sequence_p5 = random_seq(self.read_length, p=seqprobs,
                                     excluded_motif=self.p5_rec_site)

            meta_info = [
                "read_from:'{}'".format(individual_name),
                "at_locus:'{}_{}'".format("singleton", i),
                "p5_bc:'{}'".format(barcode_p5.decode()),
                "p7_bc:'{}'".format(protoread_p7.barcode.decode()),
                "rID:'{}'".format("".join([random.choice(string.ascii_lowercase) for _ in range(5)]))
            ]
            # calculate the prefix length and truncate the raw read sequence
            # to match total read length
            prefix_length_p5 = ProtoReadp5.p5_prefix_length(barcode_p5,
                                                            spacer_p5,
                                                            self.p5_overhang)
            sequence_p5_truncated = sequence_p5[:self.read_length - prefix_length_p5]
            # create a read object and finalize it
            rad_read = RADRead.from_p7_protoread(
                barcode_p5,
                spacer_p5,
                individual_name,
                self.p5_overhang,
                self.p5_rec_site,
                sequence_p5_truncated,
                protoread_p7,
                self.gc_content,
                self.read_length,
                self.single_end,
                meta_info,
                )
            rad_read.finalize_dbr()
            rad_read.add_seq_errors(self.prob_seq_error)
            # Add PCR copies, if needed, otherwise jump to the next read
            if random.random() < self.prob_pcr_copy:
                yield rad_read
                # create and add PCR copies
                _, copies = read_mutation_handling.shallow_pcr_copies(rad_read, self.max_pcr_copy_nr)
                for read in copies:
                    self.nr_pcr_copies += 1
                    yield read
            else:
                yield rad_read

    def read_blocks(self, blocksize):
        """Iterate over Singleton reads block-wise.

        Arguments:
            blocksize (int): Number of reads per block.

        Yields:
            list: Each list contains blocksize RADRead objects.
        """
        reads = self.reads()
        try:
            while True:  # until reads iterator is depleted
                # aggregate read object into blocks and return them
                block = []
                for _ in range(blocksize):
                    block.append(next(reads))
                yield block
        except StopIteration:
            # flush out the last partial block
            yield block


class HighlyRepetitiveLocusGenerator:
    """Generator to create reads from highly repetitive loci."""

    def __init__(self, individuals, fragment_generator, args):
        """Create a new generator.

        Arguments:
            individuals (iterable): A list containing the barcoding information
                for all individuals in the sample.
            args (argparse.Namespace): From argparser.
        """
        # compute number of HRL loci to be added to the dataset
        self.nr_hrl_loci = int(args.nr_loci * args.hrl_number)
        self.individuals = individuals
        self.args = args
        self.nr_pcr_copies = 0
        self.nr_hrl_reads = 0
        self.hrl_coverages = dict()
        self.verbosity = args.verbosity
        self.single_end = args.single_end
        self.fragment_generator = fragment_generator

    def reads(self):
        """Create and yield reads from HRL loci.

        Note:
            In order to read several reads at once use the ``read_blocks``
            method.

        Yields:
            RADRead: objects that do not have any connection to any locus.
        """
        prob_seq_error = self.args.prob_seq_error
        # specify pcr copy rate for hrls
        prob_pcr_copy = self.args.prob_pcr_copy * self.args.hrl_pcr_copies
        max_pcr_copy_nr = self.args.max_pcr_copy_nr
        resolution = 20 if self.nr_hrl_loci >= 20 else 1

        # create the HRL reads
        # create pseudo loci in a fashion similar to the initialization step
        # to make sure all individuals are affected by the HRL
        for hrl_locus_name in range(1, self.nr_hrl_loci+1):
            if self.verbosity >= 1 \
               and hrl_locus_name % (self.nr_hrl_loci // resolution) == 0:
                print(" {:>7}/{:>7}".format(hrl_locus_name, self.nr_hrl_loci))
            hrl_locus = create_perfect_hrl_locus(hrl_locus_name, self.args,
                                                 self.individuals,
                                                 self.fragment_generator)
            # Add the actual HRL reads. This is a method similar to the
            # pick_event_type method in rad read
            hrl_locus.add_highly_repetitive_reads(self.args)
            hrl_coverages = hrl_locus.get_hrl_coverage()
            self.nr_hrl_reads += sum([cov for name, cov in hrl_coverages])
            loc_name = "HRL Locus {}".format(hrl_locus_name)
            self.hrl_coverages[loc_name] = {name: cov for name, cov in hrl_coverages}

            # finalize all reads
            for rad_read in hrl_locus.modified_reads_at_locus:
                rad_read.finalize_dbr()

                # add PCR copies, if needed, otherwise jump to the next read
                if random.random() < prob_pcr_copy:
                    # create, count and add PCR copies
                    pcr_copy_nr, copies = read_mutation_handling.shallow_pcr_copies(rad_read, max_pcr_copy_nr)

                    rad_read.add_seq_errors(prob_seq_error)
                    yield rad_read
                    for read in copies:
                        read.add_seq_errors(prob_seq_error)
                        self.nr_pcr_copies += 1
                        yield read
                else:
                    rad_read.add_seq_errors(prob_seq_error)
                    yield rad_read
            del hrl_locus.modified_reads_at_locus
            del hrl_locus

    def read_blocks(self, blocksize):
        """Iterate over HRL reads block-wise.

        Arguments:
            blocksize (int): Number of reads per block.

        Yields:
            list: Each list contains blocksize RADRead objects.
        """
        reads = self.reads()
        try:
            while True:  # until reads iterator is depleted
                # aggregate read object into blocks and return them
                block = []
                for _ in range(blocksize):
                    block.append(next(reads))
                yield block
        except StopIteration:
            # flush out the last partial block
            yield block
