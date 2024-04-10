#
# Generate alignments with bwa
#

# The reference genome.
REF ?= refs/genome.fa

# The directory that holds the index.
IDX_DIR = $(dir ${REF})/idx

# The name of the index
IDX ?= ${IDX_DIR}/$(notdir ${REF})

# A file in the index directory.
IDX_FILE ?= ${IDX}.ann

# Number of CPUS
NCPU ?= 2

# Additional flags to pass to BWA.
BWA_FLAGS ?= -t ${NCPU}

# Sam filter flags to filter the BAM file before sorting.
SAM_FLAGS ?=

# First in pair.
R1 ?= reads/reads1.fq

# Second in pair. Runs in single end mode if not defined.
R2 ?=

# The alignment file.
BAM ?= bam/bwa.bam

# Unsorted BAM file.
BAM_TMP ?= $(basename ${BAM}).unsorted.bam

# Set the values for the read groups.
ID ?= run1
SM ?= sample1
LB ?= library1
PL ?= ILLUMINA

# Build the read groups tag.
RG ?= '@RG\tID:${ID}\tSM:${SM}\tLB:${LB}\tPL:${PL}'

# Makefile customizations.
.DELETE_ON_ERROR:
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# Print usage information.
usage:
	@echo "#"
	@echo "# bwa.mk: align reads using BWA"
	@echo "#"
	@echo "# R1=${R1}"
ifneq (${R2},)
	@echo "# R2=${R2}"
endif
	@echo "# REF=${REF}"
	@echo "# IDX=${IDX}"
	@echo "# BAM=${BAM}"
	@echo "#"
	@echo "# make index align"
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

# Bail out if reference is not found
${REF}:
	echo "# Reference not found: ${REF}";
	exit -1

# Index the reference genome.
${IDX_FILE}: ${REF}
	@mkdir -p $(dir $@)
	bwa index -p ${IDX} ${REF}

# Create the index.
index: ${IDX_FILE}
	@echo "# bwa index: ${IDX}"

# Remove the index.
index!:
	rm -rf ${IDX_FILE}

# Paired end alignment.
${BAM_TMP}: ${R1} ${R2}
	@if [ ! -f ${IDX_FILE} ]; then
		echo "# bwa index not found: IDX=${IDX}";
		exit -1
	fi
	mkdir -p $(dir $@)
	bwa mem ${BWA_FLAGS} -R ${RG} ${IDX} ${R1} ${R2} | samtools view -b ${SAM_FLAGS} -o ${BAM_TMP}

# Sort the BAM file.
${BAM}: ${BAM_TMP}
	mkdir -p $(dir $@)
	samtools sort -@ ${NCPU} ${BAM_TMP} -o ${BAM}

# Create the BAM index file.
${BAM}.bai: ${BAM}
	samtools index ${BAM}

# Generate the alignment.
align: ${BAM}.bai
	@ls -lh ${BAM}

# Generate the alignment.
align!:
	rm -f ${BAM_TMP} ${BAM} ${BAM}.bai

# Create a wiggle coverage file.
wiggle: ${BAM}.bai ${REF}
	@make -f src/run/wiggle.mk BAM=${BAM} REF=${REF} run

# Running creates the wiggle file as well.
run: align wiggle

# Remove the BAM file.
run!:
	rm -rf ${BAM} ${BAM_TMP} ${BAM}.bai

# Run the test.
test:
	make -f src/run/tester.mk test_aligner MOD=src/run/bwa.mk

# The name of the stats file.
STATS = $(basename ${BAM}).stats

# Generate stats on the alignme
${STATS}: ${BAM}.bai
	samtools flagstat ${BAM} > ${STATS}

# Trigger the statistics generation.
stats: ${STATS}
	@echo "# ${STATS}"
	@cat ${STATS}

# Install required software.
install::
	@echo mamba install bwa samtools



# Targets that are not files.
.PHONY: usage index align run run! test wiggle install
