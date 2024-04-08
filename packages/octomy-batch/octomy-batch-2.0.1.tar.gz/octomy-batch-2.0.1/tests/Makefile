ROOT_DIR:=$(shell dirname "$(realpath $(lastword $(MAKEFILE_LIST)))")
APP_DIR:=${ROOT_DIR}/..
TESTS_DIR:=${APP_DIR}/tests
TEST_CMD:=python -m pytest

.PHONY: h all devops unit integration load regressions help

h: help

all: unit regressions

devops: unit

unit:
	$(TEST_CMD) -vv unit

integration:
	$(TEST_CMD) -vv integration

load:
	$(TEST_CMD) -vv load

regressions:
	$(TEST_CMD) -vv regressions


############### Help ####################

help:
	@echo ""
	@echo " General targets:"
	@echo ""
	@echo " + make help            Show this help"
	@echo " + make all             Run all tests"
	@echo " + make devops          Run devops tests"
	@echo " + make load            Run load tests (WIP)"
	@echo ""
	@echo "Unit targets:"
	@echo ""
	@echo " + make unit            Run unit tests"
	@echo ""
	@echo "Integration targets:"
	@echo ""
	@echo " + make integration     Run integration tests"
	@echo ""
	@echo "Load targets:"
	@echo ""
	@echo " + make load            Run load tests"
	@echo ""
	@echo "Regression targets:"
	@echo ""
	@echo " + make regressions     Run regression tests"
	@echo ""
