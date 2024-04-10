#
# Download data via the curl downloader.
#

# The URL to be downloaded
URL ?= https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/bigZips/wuhCor1.fa.gz

# Destination file.
FILE ?= refs/$(notdir ${URL})

# Aria2c flags.
FLAGS = -L

#
# Cute trick. The module also allows to fetch a limited number of lines
# from a remote gzipped url.
#

# How many lines to get
N =

# Apply the header
ifeq ($(strip $(N)),)
    HEAD =
else
    HEAD = | head -n ${N}
endif

# Should it unzip
GUNZIP  =

ifeq ($(strip $(GUNZIP)),)
    GUNZIP_CMD =
else
    GUNZIP_CMD  = | gunzip -c
endif

# Should it rezip
BGZIP =

ifeq ($(strip $(BGZIP)),)
    BGZIP_CMD =
else
    BGZIP_CMD  = | bgzip -@ 4 -c
endif

FILTER = ${GUNZIP_CMD} ${HEAD} ${BGZIP_CMD}

# Makefile customizations.
.DELETE_ON_ERROR:
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables --no-print-directory

# General usage information.
usage:
	@echo "#"
	@echo "# curl.mk: downloads data"
	@echo "#"
	@echo "#  make run URL=? FILE=?"
	@echo "#"

# Download the file with aria2c.
${FILE}:
	mkdir -p $(dir $@)
	curl ${FLAGS} ${URL} ${FILTER} > $@

run: ${FILE}
	@ls -lh $<

# For all cases remove the file and temporary file.
run!:
	rm -f ${FILE}

# Installation instructions
install:
	@echo "# no installation required"

.PHONY:: usage run run! install
