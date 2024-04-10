#
# Generates alignments with minimap2
#

# First in pair.
R1 ?= reads/read1.fq

# Second in pair.
R2 ?=

# Set MODE to SE if R2 is empty otherwise PE
ifeq ($(R2),)
	MODE ?= SE
else
	MODE ?= PE
endif

# Number of CPUS
NCPU ?= 2

# Additional minimap2 options. Also common: --secondary=no --sam-hit-only
MINI2_FLAGS = -x sr

# Sam flags to filter the BAM file before sorting.
SAM_FLAGS ?=

# Test the entire pipeline.
ACC ?= AF086833
REF ?= refs/${ACC}.fa

# The alignment file.
BAM ?= bam/minimap2.bam

# The unsorted BAM file.
BAM_TMP ?= $(basename ${BAM}).unsorted.bam

# The directory that holds the index.
IDX_DIR = $(dir ${REF})/idx

# The indexed reference genome.
IDX ?=  ${IDX_DIR}/$(notdir ${REF}).mmi

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
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# The first target is always the help.
usage::
	@echo "#"
	@echo "# minimap2.mk: align read using minimap2 "
	@echo "#"
	@echo "# R1=${R1}"
	@echo "# R2=${R2}"
	@echo "# REF=${REF}"
	@echo "# IDX=${IDX}"
	@echo "# BAM=${BAM}"
	@echo "#"
	@echo "# make index run"
	@echo "#"

# Index the reference genome.
${IDX}:
	@if [ ! -f ${REF} ]; then
		echo "# file not found: REF=${REF}";
		exit -1
	fi
	mkdir -p $(dir ${IDX})
	minimap2 -t ${NCPU} -x sr -d ${IDX} ${REF}

# Generate the index.
index: ${IDX}
	@echo "# minimap2 index:" $(basename ${IDX})

# Remove the index.
index!:
	rm -f ${IDX}

# Paired end alignment.
${BAM_TMP}: ${R1} ${R2}
	@if [ ! -f ${IDX} ]; then
		echo "# minimap2 genome index not found: IDX=${IDX}";
		exit -1
	fi
	mkdir -p $(dir $@)
	minimap2 -a --MD -t ${NCPU} ${MINI2_FLAGS} -R ${RG} ${IDX} ${R1} ${R2} | \
			 samtools view -b ${SAM_FLAGS} > ${BAM_TMP}

# Sort the BAM file.
${BAM}: ${BAM_TMP}
	samtools sort -@ ${NCPU} ${BAM_TMP} > ${BAM}

# Create the BAM index file.
${BAM}.bai: ${BAM}
	samtools index ${BAM}

# Generate the alignment.
align: ${BAM}.bai
	@ls -lh ${BAM}

# Create a wiggle coverage file.
wiggle: align
	make -f src/run/wiggle.mk BAM=${BAM} REF=${REF} run

# Running creates the wiggle file as well.
run: wiggle

# Remove the BAM file.
run!:
	rm -rf ${BAM} ${BAM}.bai ${BAM_TMP}

# Test the entire pipeline.
test:
	make -f src/run/tester.mk test_aligner MOD=src/run/minimap2.mk

# Install required software.
install::
	@echo mamba install minimap2 samtools

# Reads must exist.
${R1}:
	@echo "# file not found: R1=${R1}"
	@exit -1

# Targets that are not files.
.PHONY: align align! install usage index test
