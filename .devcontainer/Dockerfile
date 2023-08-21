FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

###############
# OS packages #
###############

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # resolve libg1.so.1
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install nvm
# see https://github.com/nvm-sh/nvm#installing-and-updating
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash
