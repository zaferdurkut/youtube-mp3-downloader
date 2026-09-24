VENV ?= venv
PYTHON ?= python3
PY := $(VENV)/bin/python
PORT ?= 8000

# make download URL=... [FORMAT=mp3|m4a|mp4] [LIMIT=10] [SINGLE=1] [OUT=~/Music]
FORMAT ?= mp3
DOWNLOAD_ARGS := --url "$(URL)" --format $(FORMAT) \
	$(if $(LIMIT),--limit $(LIMIT)) $(if $(SINGLE),--single) $(if $(OUT),--output_folder "$(OUT)")

.DEFAULT_GOAL := help
.PHONY: help install ui download test update clean

help:
	@echo "make install                 Create the virtualenv and install dependencies"
	@echo "make ui                      Start the web UI at http://127.0.0.1:$(PORT)"
	@echo "make download URL=...        Download from the command line"
	@echo "     [FORMAT=mp3|m4a|mp4] [LIMIT=10] [SINGLE=1] [OUT=folder]"
	@echo "make test                    Run the tests"
	@echo "make update                  Update yt-dlp (try this first when downloads break)"
	@echo "make clean                   Remove the virtualenv"

# Reinstall only when the requirements change
$(VENV)/.installed: requirements.txt requirements-dev.txt
	@command -v ffmpeg >/dev/null || { echo "ffmpeg is missing: brew install ffmpeg"; exit 1; }
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt -r requirements-dev.txt
	touch $@

install: $(VENV)/.installed

ui: install
	@(sleep 1.5 && $(PY) -m webbrowser http://127.0.0.1:$(PORT) >/dev/null) &
	PORT=$(PORT) $(PY) app.py

download: install
	@test -n "$(URL)" || { echo 'Usage: make download URL="https://..."'; exit 1; }
	$(PY) downloader.py $(DOWNLOAD_ARGS)

test: install
	$(PY) -m pytest -q tests

update: install
	$(PY) -m pip install -q -U "yt-dlp[default]"

clean:
	rm -rf $(VENV)
