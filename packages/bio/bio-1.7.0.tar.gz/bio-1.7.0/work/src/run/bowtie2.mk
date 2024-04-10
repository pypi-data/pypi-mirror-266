#
# Generates alignments with bowtie2
#

# A root to derive default file names from.
SRR=SRR1553425

# Number of CPUS
NCPU ?= 2

# Additional bowtie2 options.
BOWTIE2_FLAGS = --sensitive-local

# Sam flags to filter the BAM file before sorting.
SAM_FLAGS ?=

# First in pair.
R1 ?= reads/reads1.fq

# Second in pair.
R2 ?=

# Set MODE to SE if R2 is empty otherwise PE
ifeq ($(R2),)
	MODE ?= SE
else
	MODE ?= PE
endif

# The reference genome.
REF ?= refs/genome.fa

# The alignment file.
BAM ?= bam/bowtie2.bam

# Unsorted BAM file.
BAM_TMP ?= $(basename ${BAM}).unsorted.bam

# The directory that holds the index.
IDX_DIR = $(dir ${REF})/idx

# The name of the index
IDX ?= ${IDX_DIR}/$(notdir ${REF})

# File in the index directory.
IDX_FILE = ${IDX}.1.bt2

# Set the values for the read groups.
ID ?= run1
SM ?= sample1
LB ?= library1
PL ?= ILLUMINA
RG ?= "@RG\tID:${ID}\tSM:${SM}\tLB:${LB}\tPL:${PL}"

# Makefile customizations.
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# The first target is always the help.
usage::
	@echo "#"
	@echo "# bowtie2.mk: aligns read using bowtie2 "
	@echo "#"
	@echo "# R1=${R1}"
ifneq (${R2},)
	@echo "# R2=${R2}"
endif
	@echo "# REF=${REF}"
	@echo "# BAM=${BAM}"
	@echo "#"
	@echo "# make index run"
	@echo "#"

# Read 1 must exist.
${R1}:
	@echo "# Read 1 file not found: R1=${R1}"
	@exit -1

# If R2 is set, it must exist.
ifneq (${R2},)
${R2}:
	@echo "# Read 2 file not found: R2=${R2}"
	@exit -1
endif


# Index the reference genome.
${IDX_FILE}:
	@if [ ! -f ${REF} ]; then
		echo "# file not found: REF=${REF}";
		exit -1
	fi
	mkdir -p $(dir ${IDX_FILE})
	bowtie2-build ${REF} ${IDX}

# Generate the index.
index: ${IDX_FILE}
	@echo "# bowtie2 index: ${IDX}"

# Remove the index.
index!:
	rm -f ${IDX_FILE}

# If R2 is null, it is single end.
ifeq ($(R2),)
CMD ?= bowtie2 ${BOWTIE2_FLAGS} -p ${NCPU} -x ${IDX} -U ${R1}
else
CMD ?= bowtie2 ${BOWTIE2_FLAGS} -p ${NCPU} -x ${IDX} -1 ${R1} -2 ${R2}
endif

# Generate the unsorted BAM file.
${BAM_TMP}: ${R1} ${R2}
	@if [ ! -f ${IDX_FILE} ]; then
		echo "# bowtie2 index not found: IDX=${IDX}";
		exit -1
	fi
	@mkdir -p $(dir $@)
	${CMD} | samtools view -b ${SAM_FLAGS} > ${BAM_TMP}

# Sorted BAM file.
${BAM}: ${BAM_TMP}
	mkdir -p $(dir $@)
	samtools sort -@ ${NCPU} ${BAM_TMP} -o ${BAM}

# Create the BAM index file.
${BAM}.bai: ${BAM}
	samtools index ${BAM}
# Generate the alignment.
align: ${BAM}.bai
	@ls -lh ${BAM}

# Create a wiggle coverage file.
wiggle: align
	@make -f src/run/wiggle.mk BAM=${BAM} REF=${REF} run

# Running creates the wiggle file as well.
run: wiggle

# Remove the BAM file.
run!:
	rm -rf ${BAM} ${BAM}.bai ${BAM_TMP}

# Test the entire pipeline.
test:
	make -f src/run/tester.mk test_aligner MOD=src/run/bowtie2.mk

# Install required software.
install::
	@echo mamba install bowtie2 samtools

# Targets that are not files.
.PHONY: run run! install usage index test
