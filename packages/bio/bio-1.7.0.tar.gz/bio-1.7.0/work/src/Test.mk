#
# Main testing makefile
#


# The follow
N = 10000

SRR = SRR1553425

ACC = AF086833
REF = refs/${ACC}.fa
R1 = reads/${SRR}_1.fastq
R2 = reads/${SRR}_2.fastq
BAM = bam/${SRR}
VCF = vcf/${SRR}

# Makefile customizations.
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

usage:
	@echo "#"
	@echo "# Usage: make test test_all test_salmon rwar"
	@echo "#"

# Shortcut for running the tests.
test: test_modules

# Read names.
R1 = reads/${SRR}_1.fastq
R2 = reads/${SRR}_2.fastq

# BAM file name
BAM = bam/${SRR}.bam

# Module tests.
test_modules:
	@mkdir -p test && cd test && ln -sf ../src .
	make -f src/run/sra.mk run SRR=${SRR} N=${N}
	make -f src/run/fastp.mk run! run SRR=${SRR}
	make -f src/run/genbank.mk fasta ACC=${ACC}

	# Test paired end run.
	make -f src/run/bwa.mk test
	make -f src/run/bowtie2.mk test
	make -f src/run/minimap2.mk test
	make -f src/run/hisat2.mk test
	make -f src/run/wiggle.mk run
	make -f src/run/bcftools.mk run
	make -f src/run/freebayes.mk run
	make -f src/run/aria.mk run

# Salmon is not installed by default.
test_salmon:
	@mkdir -p test && cd test && ln -sf ../src .
	make -f src/run/salmon.mk index run

# Test the workflows.
test_recipes:
	@mkdir -p test && cd test && ln -sf ../src .
	make -f src/recipes/short-read-alignments.mk run
	make -f src/recipes/variant-calling.mk run
	make -f src/recipes/rnaseq-with-hisat.mk run
	make -f src/recipes/rnaseq-with-salmon.mk run

# Test the workflows.
test_workflows:
	@mkdir -p test && cd test && ln -sf ../src .
	make -f src/workflows/airway.mk design run
	make -f src/workflows/presenilin.mk design run
	make -f src/workflows/snpcall.mk run

# Test all functionality.
test_all: test_modules test_salmon test_recipes test_workflows

# Undo the test folder.
test!:
	rm -rf test/*

.PHONY: usage test test_modules test_salmon test_workflows test_all test!
