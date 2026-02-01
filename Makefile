PYTHON ?= python3
TOOLS := scripts/config_tools.py

.DELETE_ON_ERROR:

SRC_DIR := src
COMMON := $(SRC_DIR)/common.yml
CUSTOM_DIR := $(SRC_DIR)/custom
CONFIG_FILE := config.yml
CONFIG_DIR := config
TARGETS := $(addprefix $(CONFIG_DIR)/,dockerio.yml ghcr.yml lscr.yml quay.yml)
REGISTRIES_DIR := web-public/registries
DOMAIN_PARTS ?= 2

all: $(TARGETS) registries

$(CONFIG_DIR)/%.yml: $(CONFIG_FILE) $(TOOLS)
	@mkdir -p $(CONFIG_DIR)
	$(PYTHON) $(TOOLS) merge $(CONFIG_FILE) $* -o $@

clean:
	rm -f $(TARGETS)

registries:
	@mkdir -p $(REGISTRIES_DIR)
	@for registry in $$($(PYTHON) $(TOOLS) list-registries $(CONFIG_FILE)); do \
		name=$$($(PYTHON) $(TOOLS) registry-name $(CONFIG_FILE) "$$registry" --parts $(DOMAIN_PARTS)); \
		mkdir -p "$(REGISTRIES_DIR)/$$name"; \
	done

.PHONY: all clean registries
