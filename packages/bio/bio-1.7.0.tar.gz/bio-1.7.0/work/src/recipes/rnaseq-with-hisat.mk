#
# Biostar Workflows: https://www.biostarhandbook.com/
#
# The URL for the data.
DATA_URL = http://data.biostarhandbook.com/data/uhr-hbr.tar.gz

# The downloaded data file.
DATA_FILE = $(notdir ${DATA_URL})

# Genome reference.
REF=refs/chr22.genome.fa

# Genome annotation file.
GTF=refs/chr22.gtf

# The counts in tab delimited format.
COUNTS_TXT = res/counts-hisat.txt

# Final combinted counts in CSV format.
COUNTS_CSV = res/counts-hisat.csv

# The design file
DESIGN = design.csv

# Makefile settings
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# Flags passed to parallel.
FLAGS = --eta --lb --header : --colsep ,

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
index:
	make -f src/run/hisat2.mk index REF=${REF}

# Run the alignment
align: ${DESIGN}

	cat ${DESIGN} | parallel ${FLAGS} \
		make -f src/run/hisat2.mk \
		NCPU=${NCPU} \
	  	REF=${REF} \
		R1=reads/{sample}_R1.fq \
	  	BAM=bam/{sample}.bam \
		run

# The counts file.
${COUNTS_TXT}:
	# Make the directory name for the counts
	mkdir -p $(dir $@)

	# Count the features
	cat ${DESIGN} | \
		parallel --header : --colsep , -k echo bam/{sample}.bam | \
		parallel -u --xargs featureCounts -a ${GTF} -o ${COUNTS_TXT} {}

# The final counts in CSV format.
${COUNTS_CSV}: ${COUNTS_TXT}
	micromamba run -n stats Rscript src/r/format_featurecounts.r -c ${COUNTS_TXT} -o ${COUNTS_CSV}

# Trigger the counting explicitly
count: ${COUNTS_CSV}
	@ls -lh ${COUNTS_TXT}
	@ls -lh ${COUNTS_CSV}

run: data index align count

.PHONY: usage design data index align count all
