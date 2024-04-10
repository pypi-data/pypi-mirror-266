#
# Generates SNP calls with freebaye
#

# A root to derive output default names from.
SRR=SRR1553425

# Number of CPUS
NCPU ?= 2

# The alignment file.
BAM ?= bam/${SRR}.bam

# Genbank accession number.
ACC = AF086833

# The reference genome.
REF ?= refs/${ACC}.fa

# Name of the VCF with all variants.
VCF ?= vcf/$(notdir $(basename ${BAM})).fb.vcf.gz

# Additional flags passed to freebayes
BAYES_FLAGS = --pvar 0.5

# Makefile customizations.
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# The first target is always the help.
usage::
	@echo "#"
	@echo "# freebayes.mk: calls variants using freebayes"
	@echo "#"
	@echo "# REF=${REF}"
	@echo "# BAM=${BAM}"
	@echo "# VCF=${VCF}"
	@echo "#"
	@echo "# make run"
	@echo "#"

# Call SNPs with freebayes.
${VCF}: ${BAM} ${REF}
	mkdir -p $(dir $@)
	freebayes ${BAYES_FLAGS} -f ${REF} ${BAM} | bcftools norm -f ${REF} -d all -O z  > ${VCF}

# The VCF index file.
${VCF}.tbi: ${VCF}
	bcftools index -t -f $<

# The main action.
run:: ${VCF}.tbi
	@ls -lh ${VCF}

# Undo the main action.
run!::
	rm -rf ${VCF}

# Test the entire pipeline.
test:
# Get the reference genome.
	make -f src/run/genbank.mk ACC=${ACC} fasta
# Get the FASTQ reads.
	make -f src/run/sra.mk SRR=${SRR} get
# Align the FASTQ reads.
	make -f src/run/bwa.mk BAM=${BAM} REF=${REF} index align
# Call the variants.
	make -f src/run/freebayes.mk VCF=${VCF} BAM=${BAM} REF=${REF} run! run


# Print installation instructions.
install::
	@echo mamba install bcftools freebayes

# Targets that are not files.
.PHONY: run run! install usage index test

