#
# Downloads NCBI run information based on a bioproject number
#

# Project number
ID ?= PRJNA257197

# Project runinfo file.
OUT ?= ${ID}.csv

# Makefile customizations.
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# General usage information.
usage::
	@echo "#"
	@echo "# bioproject.mk: downloads runinfo for an SRA bioproject"
	@echo "#"
	@echo "# make get ID=${ID}"
	@echo "#"
	@echo "# creates: ${OUT}"
	@echo "#"

# Project run information.
${OUT}:
	mkdir -p $(dir $@)
	bio search ${ID} --header --csv > $@

# Target to download all the data.
get::  ${OUT}
	@ls -lh ${OUT}

# Remove bioprject
get!::
	rm -rf ${OUT}

# Installation instructions
install::
	@echo "pip install bio --upgrade"
