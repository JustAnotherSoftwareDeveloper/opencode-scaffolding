.PHONY: help run-main run-example run example lint format format-check test coverage check clean deps-check run-tool-versions validate-skill-meta

SCRIPT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SCRIPTS_PYTHON_DIR := $(abspath $(SCRIPT_DIR)../python)
SKILLS_DIR := $(abspath $(SCRIPT_DIR)../../skills)

# Tool detection
SHELLCHECK := $(shell command -v shellcheck 2>/dev/null)
SHFMT     := $(shell command -v shfmt 2>/dev/null)
BATS      := $(shell command -v bats 2>/dev/null)
BASHCOV   := $(shell command -v bashcov 2>/dev/null)

# Bats helper library system-installed paths (installed by apt)
BATS_ASSERT_SYS   := /usr/lib/bats/bats-assert
BATS_SUPPORT_SYS  := /usr/lib/bats/bats-support
BATS_FILE_SYS     := /usr/lib/bats/bats-file

help:
	@printf '%s\n' 'Available targets:'
	@printf '%s\n' '  help          Show this help message'
	@printf '%s\n' '  run-main      Run the placeholder shell entry point from src/'
	@printf '%s\n' '  run-example   Run the example shell script from src/'
	@printf '%s\n' '  lint          Run shellcheck on all shell scripts in src/ and test/'
	@printf '%s\n' '  format        Run shfmt -w to format all shell scripts in place'
	@printf '%s\n' '  format-check  Run shfmt -d to check formatting without modifying'
	@printf '%s\n' '  test          Run bats test suite (requires bats and test helpers)'
	@printf '%s\n' '  coverage      Run bats tests under bashcov with 100% coverage threshold'
	@printf '%s\n' '  check         Run lint + format-check + test + coverage (default gate)'
	@printf '%s\n' '  clean         Remove tmp/ directory'
	@printf '%s\n' '  deps-check    Verify shellcheck, shfmt, bats, bashcov, and system-installed bats helpers (apt)'
	@printf '%s\n' '  run-tool-versions  Detect CLI tool versions and report as JSON'
	@printf '%s\n' '  validate-skill-meta  Validate all skill SKILL.md frontmatter (tags, quality, structure)'

run-main:
	@bash "$(SCRIPT_DIR)src/main.sh"

run-example:
	@bash "$(SCRIPT_DIR)src/example.sh"

run:
	@bash "$(SCRIPT_DIR)src/main.sh"

example:
	@bash "$(SCRIPT_DIR)src/example.sh"

lint:
ifndef SHELLCHECK
	$(error shellcheck is not installed; install it via your package manager (apt install shellcheck, brew install shellcheck, etc.))
endif
		"$(SHELLCHECK)" -x -S warning "$(SCRIPT_DIR)src/"*.sh "$(SCRIPT_DIR)lib/"*.sh "$(SCRIPT_DIR)lib/"*/*.sh
	@$(MAKE) validate-skill-meta

format:
ifndef SHFMT
	$(error shfmt is not installed; install it via your package manager (apt install shfmt, brew install shfmt, etc.))
endif
	"$(SHFMT)" -w "$(SCRIPT_DIR)src/"*.sh "$(SCRIPT_DIR)lib/"*.sh "$(SCRIPT_DIR)lib/"*/*.sh

format-check:
ifndef SHFMT
	$(error shfmt is not installed; install it via your package manager (apt install shfmt, brew install shfmt, etc.))
endif
	"$(SHFMT)" -d "$(SCRIPT_DIR)src/"*.sh "$(SCRIPT_DIR)lib/"*.sh "$(SCRIPT_DIR)lib/"*/*.sh

test:
ifndef BATS
	$(error bats is not installed; install it via your package manager (npm install -g bats, apt install bats, brew install bats, etc.))
endif
	"$(BATS)" "$(SCRIPT_DIR)test/"*.bats "$(SCRIPT_DIR)tests/"*.bats

coverage:
ifndef BASHCOV
	$(error bashcov is not installed; install it via 'gem install bashcov' (approved fallback — no apt package))
endif
	@cd "$(SCRIPT_DIR)" && cov_output=$$("$(BASHCOV)" -- bats test/*.bats tests/*.bats 2>&1); \
	 echo "$$cov_output"; \
	 cov_pct=$$(echo "$$cov_output" | sed -n 's/.*Line Coverage: \([0-9.]*\)%.*/\1/p'); \
	 if [ -z "$$cov_pct" ]; then \
	   echo "ERROR: Could not parse coverage from bashcov output"; \
	   exit 1; \
	 fi; \
	 cov_int=$$(echo "$$cov_pct" | cut -d. -f1); \
	 if [ "$$cov_int" -lt 100 ] 2>/dev/null; then \
	   echo "FAIL: Line coverage $$cov_pct% is below minimum 100%"; \
	   exit 1; \
	 else \
	   echo "PASS: Line coverage $$cov_pct% meets minimum 100%"; \
	 fi

check: lint format-check test coverage

clean:
	rm -rf "$(SCRIPT_DIR)tmp/"
	rm -f "$(SCRIPT_DIR)coverage/"*.gcda "$(SCRIPT_DIR)coverage/"*.gcno "$(SCRIPT_DIR)coverage/"*.gcov

deps-check:
	@echo "=== Dependency Check ==="
	@echo -n "shellcheck .......... "; \
	if command -v shellcheck >/dev/null 2>&1; then echo "found ($$(shellcheck --version 2>&1 | head -1))"; else echo "MISSING — install via: apt install shellcheck"; fi
	@echo -n "shfmt ............... "; \
	if command -v shfmt >/dev/null 2>&1; then echo "found ($$(shfmt --version 2>&1))"; else echo "MISSING — install via: apt install shfmt"; fi
	@echo -n "bats ................ "; \
	if command -v bats >/dev/null 2>&1; then echo "found ($$(bats --version 2>&1))"; else echo "MISSING — install via: apt install bats, fallback: npm install -g @bats-core/bats"; fi
	@echo -n "bashcov ............. "; \
	if command -v bashcov >/dev/null 2>&1; then echo "found ($$(bashcov --version 2>&1))"; else echo "MISSING — install via: gem install bashcov (approved fallback — no apt package)"; fi
	@echo -n "bats-assert ........ "; \
	if [ -d "$(BATS_ASSERT_SYS)" ]; then echo "found (system: $(BATS_ASSERT_SYS))"; else echo "MISSING — install via: apt install bats-assert, fallback: npm install -g @bats-core/assert"; fi
	@echo -n "bats-support ....... "; \
	if [ -d "$(BATS_SUPPORT_SYS)" ]; then echo "found (system: $(BATS_SUPPORT_SYS))"; else echo "MISSING — install via: apt install bats-support, fallback: npm install -g @bats-core/support"; fi
	@echo -n "bats-file .......... "; \
	if [ -d "$(BATS_FILE_SYS)" ]; then echo "found (system: $(BATS_FILE_SYS))"; else echo "MISSING — install via: apt install bats-file, fallback: npm install -g @bats-core/file"; fi
	@echo "========================"

run-tool-versions:
	@bash "$(SCRIPT_DIR)src/tool-versions.sh"

validate-skill-meta:
	@uv run --directory "$(SCRIPTS_PYTHON_DIR)" validate-skill-meta "$(SKILLS_DIR)"/*/SKILL.md --format text
