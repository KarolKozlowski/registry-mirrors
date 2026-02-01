YQ ?= yq

.DELETE_ON_ERROR:

SRC_DIR := src
COMMON := $(SRC_DIR)/common.yml
CUSTOM_DIR := $(SRC_DIR)/custom
CONFIG_DIR := config
TARGETS := $(addprefix $(CONFIG_DIR)/,dockerio.yml ghcr.yml lscr.yml quay.yml)
REGISTRIES_DIR := web-public/registries
DOMAIN_PARTS ?= 2

all: $(TARGETS) registries

$(CONFIG_DIR)/%.yml: $(COMMON) $(CUSTOM_DIR)/%.yml
	@mkdir -p $(CONFIG_DIR)
	$(YQ) -y -s '.[0] * .[1]' $^ > $@

clean:
	rm -f $(TARGETS)

registries:
	@mkdir -p $(REGISTRIES_DIR)
	@for f in $(CUSTOM_DIR)/*.yml; do \
		url=$$($(YQ) -r '.proxy.remoteurl' "$$f"); \
		host=$${url#*://}; host=$${host%%/*}; host=$${host%%:*}; \
		name=$$(echo "$$host" | awk -F. -v n=$(DOMAIN_PARTS) '{ if (NF<=n) {print $$0; next} for (i=NF-n+1; i<=NF; i++) { printf "%s%s", (i==NF-n+1 ? "" : "."), $$i } print "" }'); \
		mkdir -p "$(REGISTRIES_DIR)/$$name"; \
	done

.PHONY: all clean registries
