# Genbank accession number.
ACC ?= AF086833

# A root to derive output default names from.
SRR ?= SRR1553425

# Number of CPUS
NCPU ?= 2

# The reference genome.
REF ?= refs/${ACC}.fa

# The alignment file.
BAM ?= bam/${SRR}.bam

# The variant file.
VCF ?= vcf/$(notdir $(basename ${BAM})).deepvariant.vcf.gz

# The temporary intermediate results.
TMP ?= tmp/$(notdir ${VCF})

# The model type in deep variant.
MODEL ?= WGS

# Directory to mount in the singularity container.
MNT ?= $(shell pwd):$(shell pwd)

# Deepvariant singularity image
SIF ?= deepvariant_1.5.0.sif

# The deepvariant command line run
CMD ?= singularity run -B ${MNT} ${SIF}

# Additional bcf flags for calling process.
CALL_FLAGS ?=

# Example:
# CALL_FLAGS = --regions chr1:1-1000000

# Makefile customizations.
SHELL := bash
.RECIPEPREFIX = >
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# The first target is always the help.
usage::
> @echo "#"
> @echo "# deepvariant.mk: call variants using Google Deepvariant"
> @echo "#"
> @echo "# REF=${REF}"
> @echo "# BAM=${BAM}"
> @echo "# VCF=${VCF}"
> @echo "#"
> @echo "# make vcf"
> @echo "#"

${REF}.fai: ${REF}
> samtools faidx ${REF}

# Generate the variant calls.
${VCF}: ${BAM} ${REF} ${REF}.fai
> mkdir -p $(dir $@)
> ${CMD} \
  /opt/deepvariant/bin/run_deepvariant \
  --model_type=${MODEL} \
  --ref ${REF} \
  --reads ${BAM} \
  --output_vcf ${VCF}  \
  --num_shards ${NCPU} \
  --intermediate_results_dir ${TMP} \
  ${CALL_FLAGS}

# Create the VCF index
${VCF}.tbi: ${VCF}
> bcftools index -t -f $<

# Generating a VCF file.
vcf: ${VCF}.tbi
> @ls -lh ${VCF}

vcf!:
> rm -rf ${VCF} ${VCF}.tbi

# Test the entire pipeline.
test:
# Get the reference genome.
> make -f src/run/genbank.mk ACC=${ACC} fasta
# Get the FASTQ reads.
> make -f src/run/sra.mk SRR=${SRR} get
# Align the FASTQ reads.
> make -f src/run/bwa.mk BAM=${BAM} REF=${REF} index align
# Call the variants.
> make -f src/run/deepvariant.mk VCF=${VCF} BAM=${BAM} REF=${REF} vcf! vcf

# Installation instructions.
install:
>@echo singularity pull docker://google/deepvariant:1.5.0"

.PHONY: usage vcf test install
