FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY . .
RUN uv sync

CMD ["uv", "run", "sub_to_handle.py", \
    "--handle", "bsky.social", \
    "--handle", "segyges.bsky.social", \
    "--handle", "jay.bsky.team", \
    "--handle", "pfrazee.com"] 