YQ ?= yq

.DELETE_ON_ERROR:

SRC_DIR := src
COMMON := $(SRC_DIR)/common.yml
CUSTOM_DIR := $(SRC_DIR)/custom
TARGETS := dockerio.yml ghcr.yml lscr.yml quay.yml

all: $(TARGETS)

%.yml: $(COMMON) $(CUSTOM_DIR)/%.yml
	$(YQ) -y -s '.[0] * .[1]' $^ > $@

clean:
	rm -f $(TARGETS)

.PHONY: all clean
