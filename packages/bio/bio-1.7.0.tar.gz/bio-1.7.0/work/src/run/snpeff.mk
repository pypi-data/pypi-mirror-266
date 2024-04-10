#
# Annotating SNP effects with SNPeff.
#

# Where it stores the database.
DIR = idx

# Genbank accession number.
ACC = AF086833

# Existing Variant calls.
VCF ?= vcf/SRR1553425.bcftools.vcf.gz

# The prefix for the annotated files
ANN = vcf/results

# Annotated variants.
ANN_VCF ?= ${ANN}.snpeff.vcf.gz

# The SNPeff html report.
ANN_HTML ?= ${ANN}.snpeff.html

# The SNPeff CXV report.
ANN_CSV ?= ${ANN}.snpeff.csv

# Genome accession label
LABEL ?= ${ACC}

# The GenBank annotation file.
GBK ?= refs/${ACC}.gb

# The SNPeff database.
SNPEFF_DB ?= ${DIR}/${LABEL}/snpEffectPredictor.bin

# Makefile customizations.
SHELL := bash
.RECIPEPREFIX = >
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# General usage information.
usage::
> @echo "#"
> @echo "# snpeff.mk: annotate variants calls with SNPeff."
> @echo "#"
> @echo "# ACC=${ACC}"
> @echo "# VCF=${VCF}"
> @echo "#"
> @echo "# make run"
> @echo "#"

# Fetch GenBank file.
${GBK}:
> bio fetch ${ACC} > $@

# Building a custom snpEff database snpeff needs the files in specific folders.
# 1. copy the genbank to its location.
# 2. append entry to current genome to the config.
# 3. Build the snpEff database.

${SNPEFF_DB}: ${GBK}
> mkdir -p ${DIR}/${LABEL}
> cp -f ${GBK} ${DIR}/${LABEL}/genes.gbk
> echo "${LABEL}.genome : ${LABEL}" >> snpeff.config
> snpEff build -dataDir ${DIR} -v ${LABEL}

# Create the annotated VCF file.
${ANN_VCF} ${ANN_HTML} ${ANN_CSV}: ${SNPEFF_DB}
> snpEff ann -csvStats ${ANN_CSV} -s ${ANN_HTML} -dataDir ${DIR} -v ${LABEL} ${VCF} | bcftools view -O z > ${ANN_VCF}
> bcftools index ${ANN_VCF}

# Creates the SNPeff database
index: ${SNPEFF_DB}
> @ls -lh ${SNPEFF_DB}

# Removes the SNPeff database
index!:
> rm -f ${SNPEFF_DB}

# Runs the SNPeff tool.
run: ${ANN_VCF} ${ANN_HTML} ${ANN_CSV}
> @ls -lh ${ANN_VCF}
> @ls -lh ${ANN_HTML}
> @ls -lh ${ANN_CSV}

# Removes the SNPeff output
run!:
> rm -f ${ANN_VCF} ${ANN_HTML}

# Shows the usage information.
install::
>@echo mamba install snpeff

.PHONY: run
