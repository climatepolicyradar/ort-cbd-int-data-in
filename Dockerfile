FROM prefecthq/prefect:3.4-python3.13

RUN useradd -m -u 1000 prefect_user

# This ensures that the dependencies are installed at system python level
# without having to activate a venv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

# Copy your source code
COPY ./app /app/app
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv (fast Python dependency manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies using the lockfile
RUN uv sync

WORKDIR /app/

# Set up permissions for prefect_user
RUN mkdir -p /opt/prefect && \
    chown -R prefect_user:prefect_user /opt/prefect && \
    chmod -R 755 /opt/prefect && \
    chown -R prefect_user:prefect_user /home/prefect_user && \
    chown -R prefect_user:prefect_user /usr/local/lib/python3.13/site-packages && \
    chown -R prefect_user:prefect_user /app

# Switch to non-root user
USER prefect_user
