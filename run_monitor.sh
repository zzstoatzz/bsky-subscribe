#!/bin/bash
nohup uv run sub_to_did.py --did did:plc:z72i7hdynmk6r22z27h6tvur > monitor.log 2>&1 &
echo $! > monitor.pid 