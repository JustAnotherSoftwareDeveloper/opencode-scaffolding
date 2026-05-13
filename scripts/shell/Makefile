.PHONY: help run example

SCRIPT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

help:
	@printf '%s\n' 'Available targets:'
	@printf '%s\n' '  help     Show this help message'
	@printf '%s\n' '  run      Run the placeholder shell entry point from src/'
	@printf '%s\n' '  example  Run the example shell script from src/'

run:
	@bash "$(SCRIPT_DIR)src/main.sh"

example:
	@bash "$(SCRIPT_DIR)src/example.sh"
