# File: Makefile
.PHONY: install lint test run docker-build docker-run clean

install:
	@python -m venv .venv
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -r requirements.txt

lint:
	@.venv/bin/flake8 app tests

test:
	@.venv/bin/pytest -v

run:
	@.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-build:
	@docker build -t gush-release-manager .

docker-run:
	@docker run -d -p 8000:8000 --env-file .env --name gush_release_manager gush-release-manager

clean:
	@rm -rf .venv __pycache__ .pytest_cache htmlcov
MIT License

Copyright (c) 2026 Gush Systems

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT text – see the repository LICENSE file]
# 1️⃣ Clone & cd
git clone https://github.com/gush-ai/github-release-manager.git
cd github-release-manager

# 2️⃣ Create .env from the example
cp .env.example .env
# → edit .env with your token & org

# 3️⃣ Run locally
make install
make run      # or: uvicorn app.main:app --reload

# 4️⃣ Or run via Docker
make docker-build
make docker-run