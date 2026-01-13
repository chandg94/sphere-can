# sphere-can

**sphere-can** is a remote-controllable CAN experimentation framework designed for
vehicular cybersecurity research, testing, data collection and demonstrations. It provides
`can-utils`-like functionality over a network via an API to a reconfigurable hardware testbed, making
it suitable for hardware in the loop remote testing.

The system consists of:
- a **FastAPI server** that interfaces with a SAE J1939 network via Linux SocketCAN
- a **pip-installable CLI** that offers standard tooling to interact with the testbed via the API
- a **teensy 4.0 relay controller** for controlling hardware setup over the network

---

## Architecture

CLI → HTTP / WebSocket → FastAPI Server → python-can → SocketCAN → Kernel → CAN Bus 

---

## Repository Layout

```bash
sphere-can/
├── server/
│ ├── pyproject.toml
│ └── sphere_can/
│   ├── main.py # FastAPI entrypoint
│   ├── can.py # CAN TX generator logic
│   ├── ws.py # WebSocket RX streaming
│   ├── state.py # Global server state
│   ├── status.py # Status endpoint
│   └── relay.py # ECU relay control
│
├── firmware/
│    ├── main.ino # Relay control logic
│
├── cli/
│ ├── pyproject.toml
│ └── sphere_can/
│   ├── main.py # CLI entrypoint
│   ├── readcan.py # candump-style RX
│   ├── sendcan.py # cangen-style TX
│   ├── status.py
│   ├── config.py
│   └── stop.py
│
└── README.md
```
---

## Requirements

### System
- Linux
- SocketCAN enabled (`can0`, `vcan0`, etc.)
- ```bash
  sudo ip link set <can_interface> up type can bitrate <bitrate>
  ```
- Python ≥ 3.9

### Python dependencies
- fastapi
- uvicorn
- python-can
- websocket-client
- requests
- typer

### Installing Tailscale

On **both server and client machines**:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```
Example output:
```bash
100.94.12.37
```
---

## Server Usage

### Start the server

```bash
cd sphere-can/server
python3 -m venv venv
source venv/bin/activate
python3 -m uvicorn sphere_can.main:app --host <SERVER_IP> --port 8000
```

### Client Usage

```bash
pip install --upgrade pip
pip install sphere-can
```

### Environment Variables (Client)

The CLI locates the server using the SPHERE_API environment variable. Its by default set to point to the server.

To change, set this inside the client venv:

```bash
export SPHERE_API=http://<SERVER_IP>:8000
``` 
---
## REST API
### POST /can/send/{can_interface}

Start a CAN traffic generator.

Example request body:
```bash
{
  "name": "example-gen",
  "arbitration_id": 291,
  "extended": false,
  "data": [222, 173, 190, 239, 1, 2, 3, 4],
  "random_id": false,
  "random_data": false,
  "dlc": 8,
  "interval_us": 10000,
  "count": null
}
```
Spawns a background generator thread. Runs until stopped or count is reached.

### POST /can/stop/{name}

Stop a running generator.
```bash
POST /can/stop/example-gen
```
Signals the generator thread to stop. Cleans up server state.

### GET /status

Returns server state:
```bash
{
  "can_interfaces": ["can0"],
  "generators": [],
  "ecus": {
    "cummins": false,
    "ddec": false,
    "bendix": false
  }
}
```
### WebSocket API
/ws/readcan/{can_interface}

Streams received CAN frames as JSON arrays. Example payload:
```bash
[
  {
    "ts": 1712859342.123456,
    "bus": "can0",
    "id": "0x123",
    "dlc": 8,
    "data": "deadbeef01020304",
    "ext": false
  }
]
```
Push-only. Client-side filtering.

## CLI Usage

### Verify:
```bash
sphere-can --help
```
### readcan

Read CAN traffic (candump-style).
```bash
sphere-can readcan <can_interface> [OPTIONS]
```
Examples:
```bash
sphere-can readcan can0
sphere-can readcan can0 --filter-id 0x123
sphere-can readcan can0 --log can0.log
sphere-can readcan can0 --filter-id 0x18FEF100 --log j1939.log
```
Options:
Option	Description
can_interface	CAN interface (e.g., can0)
--filter-id	Hex arbitration ID to match
--log	Append output to a log file

Output format:
```bash
(1712859342.123456) can0 0x123#deadbeef01020304
```
### sendcan

Generate CAN traffic (cangen-style). Runs in the foreground.
```bash
sphere-can sendcan <can_interface> [OPTIONS]
```
Examples:
```bash
sphere-can sendcan can0 \
  --id 123 \
  --data DEADBEEF01020304 \
  --len 8 \
  --gap-ms 10
```
Extended ID:
```bash
sphere-can sendcan can0 \
  --extended \
  --id 18FEF100 \
  --data AAAAAAAAAAAAAAAA \
  --len 8
```
DoS / flood:
```bash
sphere-can sendcan can0 --extended --id 00000000 --data 0000000000000000 --len 8 --gap-ms 0
```
Options:
  Option	Description
-  can_interface	CAN interface
-  --id	Arbitration ID (hex)
-  --extended	Use 29-bit ID
-  --data	Hex payload
-  --len	DLC (default 8)
-  --gap-ms	Inter-frame gap (float, ms)
-  --count	Number of frames
-  --random-id	Random IDs
-  --random-data	Random payloads
---
## Notes:
- --gap-ms 0 performs best-effort flooding
- Kernel TX backpressure is handled safely
---
## License
- Research and internal use. Licensing to be defined by the project owner.
---
## Status
- Functional, stable, and demo-ready.
---
