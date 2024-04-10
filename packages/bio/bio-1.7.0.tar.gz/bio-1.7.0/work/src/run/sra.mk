#
# Downloads sequencing reads from SRA.
#

# The directory that stores FASTQ reads that we operate on.
DIR ?= reads

# SRR number (sequencing run from the Ebola outbreak data of 2014)
SRR ?= SRR1553425

# The name of the unpacked reads
P1 ?= ${DIR}/${SRR}_1.fastq
P2 ?= ${DIR}/${SRR}_2.fastq

# The name of the final reads (may be the same)
R1 ?= ${P1}
R2 ?= ${P2}

# How many reads to download (N=ALL downloads everything).
N ?= 10000

# Makefile customizations.
.DELETE_ON_ERROR:
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# Print usage information.
usage::
	@echo "#"
	@echo "# sra.mk: downloads FASTQ reads from SRA"
	@echo "#"
	@echo "# make run SRR=${SRR} N=${N}"
	@echo "#"

# Set the flags for the download
ifeq ($(N), ALL)
FLAGS ?= -F --split-files
else
FLAGS ?= -F --split-files -X ${N}
endif

# Obtain the reads from SRA.
${R1}:
	mkdir -p ${DIR}
	fastq-dump ${FLAGS} -O ${DIR} ${SRR}

	mv -f ${P1} ${R1}
	@if [ -f ${P2} ]; then
		mv -f ${P2} ${R2}
	fi

# List the data. We don't know if the reads are paired or not.
run: ${R1}
	@if [ -f ${R2} ]; then
		@ls -lh ${R1} ${R2}
	else
		@ls -lh ${R1}
	fi

# Removes the SRA files.
run!:
	rm -f ${P1} ${P2} ${R1} ${R2}

test:
	# Get the FASTQ reads.
	make -f src/run/sra.mk SRR=${SRR} run! run

install::
	@echo mamba install sra-tools

# Targets that are not files.
.PHONY: usage run run! test install
