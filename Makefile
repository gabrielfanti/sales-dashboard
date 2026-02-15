PYTHON ?= python3
PIP ?= pip3
VENV_PYTHON := ./venv/bin/python
VENV_PIP := ./venv/bin/pip

ifeq ("$(wildcard $(VENV_PYTHON))","")
PYTHON_CMD := $(PYTHON)
PIP_CMD := $(PIP)
else
PYTHON_CMD := $(VENV_PYTHON)
PIP_CMD := $(VENV_PIP)
endif

.PHONY: install run quality ci

install:
	$(PIP_CMD) install -r requirements.txt

run:
	PYTHONPATH=src $(PYTHON_CMD) -m streamlit run dashboards.py

quality:
	PYTHONPATH=src $(PYTHON_CMD) scripts/run_quality_checks.py
	PYTHONPATH=src $(PYTHON_CMD) scripts/generate_business_snapshot.py

ci: quality
