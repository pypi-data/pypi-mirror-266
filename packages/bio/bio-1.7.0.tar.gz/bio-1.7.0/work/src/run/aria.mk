#
# Download data via the aria2c downloader.
#

# The URL to be downloaded
URL ?= https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/bigZips/wuhCor1.fa.gz

# The directory to put the data into
DIR=.

# Destination file.
FILE ?= ${DATA}/$(notdir ${URL})

# Aria2c flags.
FLAGS = -x 5 -c --summary-interval=10

# Makefile customizations.
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# General usage information.
usage:
	@echo "#"
	@echo "# aria.mk: downloads data"
	@echo "#"
	@echo "#  make run URL=?"
	@echo "#"

# Download the file with aria2c.
${FILE}:
	mkdir -p $(dir $@)
	aria2c ${FLAGS} -o $@ ${URL}

run: ${FILE}
	@ls -lh $<

# Remove the file.
run!:
	rm -f ${FILE}

# Installation instructions
install:
	@echo "mamba install aria2"

.PHONY:: usage run run! install
