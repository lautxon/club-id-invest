# Club ID Invest - Development Container
# Python 3.11 + Node.js 20 + Development Tools

FROM mcr.microsoft.com/devcontainers/python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NODE_ENV=development

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Install additional development tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    libpq-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install WeasyPrint dependencies (for PDF generation)
RUN apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspaces

# Expose ports
EXPOSE 3000 8000

# Default command
CMD ["tail", "-f", "/dev/null"]
