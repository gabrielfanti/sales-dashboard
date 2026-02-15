PYTHON := ./venv/bin/python
PIP := ./venv/bin/pip

.PHONY: install run quality ci

install:
	$(PIP) install -r requirements.txt

run:
	./venv/bin/streamlit run dashboards.py

quality:
	PYTHONPATH=src $(PYTHON) scripts/run_quality_checks.py
	PYTHONPATH=src $(PYTHON) scripts/generate_business_snapshot.py

ci: quality
