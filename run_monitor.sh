#!/bin/bash
nohup uv run sub_to_handle.py --handle bsky.social > monitor.log 2>&1 &
echo $! > monitor.pid 