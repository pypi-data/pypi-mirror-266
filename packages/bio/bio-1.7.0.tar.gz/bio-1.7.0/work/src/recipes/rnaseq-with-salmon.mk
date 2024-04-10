#
# Biostar Workflows: https://www.biostarhandbook.com/
#


# The URL for the data.
DATA_URL = http://data.biostarhandbook.com/data/uhr-hbr.tar.gz

# The downloaded data file.
DATA_FILE = $(notdir ${DATA_URL})

# Chromosome 22 at UCSC
GENOME_URL = http://hgdownload.cse.ucsc.edu/goldenpath/hg38/chromosomes/chr22.fa.gz

# Genome reference.
REF = refs/chr22.transcripts.fa

# Genome annotation file.
GTF = refs/chr22.gtf

# The design file
DESIGN = design.csv

# Final combined counts in CSV format.
COUNTS_CSV = res/counts-salmon.csv

# Makefile settings
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# Flags passed to parallel.
PFLAGS = --eta --lb --header : --colsep ,

# Number of CPUS to use
NCPU = 4

# Print usage
usage:
	@echo "#"
	@echo "# make data align count"
	@echo "#"

# Generate the design file.
${DESIGN}:
	@cat << EOF > ${DESIGN}
	sample,group
	HBR_1,HBR
	HBR_2,HBR
	HBR_3,HBR
	UHR_1,UHR
	UHR_2,UHR
	UHR_3,UHR
	EOF

# Show the design file.
design: ${DESIGN}
	@ls -lh ${DESIGN}

# Download the sequencing data and references.
${DATA_FILE}:
	# Download the sequencing data
	wget -nc  ${DATA_URL}
	tar xzvf uhr-hbr.tar.gz

# Trigger the data download
data: ${DATA_FILE}
	@ls -lh ${DATA_FILE}

# Generate the HISAT2 index
index: ${DESIGN}
	make -f src/run/salmon.mk index  REF=${REF} NCPU=${NCPU}

# Run salmon on the data
align: index
	cat ${DESIGN} | parallel ${PFLAGS} make -f src/run/salmon.mk run \
					MODE=SE REF=${REF} BAM=bam/{sample}.bam  \
					R1=reads/{sample}_R1.fq NCPU=${NCPU} SAMPLE={sample}

# Combine the counts into a single file
${COUNTS_CSV}:
	# Make the directory name for the counts.
	mkdir -p $(dir $@)

	# Combine the outputs into a single file.
	micromamba run -n stats Rscript src/r/combine_salmon.r -d ${DESIGN} -o ${COUNTS_CSV}

# Print the counts
counts: ${COUNTS_CSV}
	@ls -lh ${COUNTS_CSV}

run: data align counts

.PHONY: usage data align counts run
