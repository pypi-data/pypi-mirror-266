#
# Trims FASTQ files and runs FASTQC on them.
#

# SRR numbers may also be used as input.
SRR ?= SRR1553425

# The input read pairs.
R1 ?= reads/${SRR}_1.fastq
R2 ?=

# Set MODE to SE if R2 is empty otherwise PE
ifeq ($(R2),)
	MODE ?= SE
	Q1 ?= trim/$(notdir ${R1})
	Q2 ?=
else
	MODE ?= PE
	Q1 ?= trim/$(notdir ${R1})
	Q2 ?= trim/$(notdir ${R2})
endif


# Number of CPUS to use.
NCPU ?= 2

# The adapter sequence for trimming.
ADAPTER ?= AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC

# The statistics on the reads files.
READ_STATS ?= $(basename ${Q1}).stats

# FASTP html report.
FASTP_HTML = $(basename ${Q1}).html

# Makefile customizations.
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# Print usage
usage:
	@echo "#"
	@echo "# fastp.mk: FASTQ quality control"
	@echo "#"
	@echo "# SRR=${SRR} MODE=${MODE} NCPU=${NCPU}"
	@echo "#"
	@echo "# Input:"
	@echo "#"
	@echo "#   R1=${R1}"
	@echo "#   R2=${R2}"
	@echo "#"
	@echo "# Output:"
	@echo "#"
	@echo "#   Q1=${Q1}"
	@echo "#   Q2=${Q2}"
	@echo "#"
	@echo "#  make run "
	@echo "#"

# List the FLAGS used as trimming options
FASTP_FLAGS ?= --adapter_sequence ${ADAPTER} --cut_right --cut_right_window_size 4 --cut_right_mean_quality 30 --length_required 50 -j /dev/null -h ${FASTP_HTML}

ifeq ($(MODE), PE)
CMD = fastp -i ${R1} -I ${R2} -o ${Q1} -O ${Q2}  -w ${NCPU} ${FASTP_FLAGS}
else
CMD = fastp -i ${R1} -o ${Q1} -w ${NCPU}  ${FASTP_FLAGS}
endif

# Perform the trimming
${Q1} ${Q2}: ${R1} ${R2}
	 mkdir -p $(dir ${Q1})
	 ${CMD}

run: ${Q1} ${Q2}
	 @ls -lh ${Q1} ${Q2}

# Removes the trimmed files.
run!:
	 rm -f ${Q1} ${Q2}

# Test the module
test:
	make -f src/run/sra.mk run SRR=${SRR} N=1000  MODE=PE
	make -f src/run/fastp.mk run! run R1=reads/${SRR}_1.fastq Q1=trim/${SRR}_1.SE.fastq
	make -f src/run/fastp.mk run! run R1=reads/${SRR}_1.fastq R2=reads/${SRR}_2.fastq  Q1=trim/${SRR}_1.PE.fastq Q2=trim/${SRR}_2.PE.fastq

# Installation instuctions
install:
	@echo mamba install fastp

# Targets that are not valid files.
.PHONY: run install usage
