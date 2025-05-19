#!/usr/bin/env just

set dotenv-load := true

fmt :
  uvx black main.py

lint :
  uvx ruff check main.py
