PYTHON ?= python3
TOOLS := scripts/config_tools.py

.DELETE_ON_ERROR:

CONFIG_FILE := config.yml
CONFIG_DIR := config
TARGETS := $(addprefix $(CONFIG_DIR)/,$(addsuffix .yml,$(shell $(PYTHON) $(TOOLS) list-registries $(CONFIG_FILE))))
REGISTRIES_DIR := web-public/registries
DOMAIN_PARTS ?= 2
COMPOSE_TEMPLATE := docker-compose.yml.j2
COMPOSE_OUTPUT := docker-compose.yml

all: $(TARGETS) registries

compose: $(COMPOSE_TEMPLATE) $(CONFIG_FILE) $(TOOLS)
	$(PYTHON) $(TOOLS) render-compose $(COMPOSE_TEMPLATE) $(CONFIG_FILE) -o $(COMPOSE_OUTPUT)

$(CONFIG_DIR)/%.yml: $(CONFIG_FILE) $(TOOLS)
	@mkdir -p $(CONFIG_DIR)
	$(PYTHON) $(TOOLS) merge $(CONFIG_FILE) $* -o $@

clean:
	rm -f $(TARGETS) $(COMPOSE_OUTPUT)

registries:
	@mkdir -p $(REGISTRIES_DIR)
	@for registry in $$($(PYTHON) $(TOOLS) list-registries $(CONFIG_FILE)); do \
		name=$$($(PYTHON) $(TOOLS) registry-name $(CONFIG_FILE) "$$registry" --parts $(DOMAIN_PARTS)); \
		mkdir -p "$(REGISTRIES_DIR)/$$name"; \
	done

.PHONY: all clean registries compose
