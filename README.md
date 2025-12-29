# Sphere-CAN

Sphere-CAN is a remote-controllable CAN experimentation framework designed for
vehicular cybersecurity research, testing, and demonstrations. It provides
`candump`- and `cangen`-like functionality over a network via an API, making
it suitable for remote testbeds.

The system consists of:
- a **FastAPI server** that interfaces with Linux SocketCAN
- a **pip-installable CLI** that offers standard CAN tooling
- a **teensy 4.0 relay controller** for controlling hardware

---

## Architecture

CLI → HTTP / WebSocket → FastAPI Server → python-can → SocketCAN → Kernel


- CAN TX uses background generator threads
- CAN RX is streamed via WebSockets
- CLI generators run in the foreground (Ctrl+C semantics)
- Server is client-IP agnostic

---

## Repository Layout

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
│   └── config.py
│
└── README.md


---

## Requirements

### System
- Linux
- SocketCAN enabled (`can0`, `vcan0`, etc.)
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
uvicorn sphere_can.main:app
```
or
```bash
uvicorn sphere_can.main:app --host <TAILSCALE_IP> --port 8000
```

Default address:

http://127.0.0.1:8000

The server must run on a machine with access to SocketCAN interfaces.

## Client Usage

```bash
cd sphere-can/cli
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Environment Variables (Client)

The CLI locates the server using the SPHERE_CAN_API environment variable.

Set this inside the client venv:

```bash
export SPHERE_CAN_API=http://<TAILSCALE_IP>:8000
``` 

## REST API
### POST /can/send/{can_interface}

Start a CAN traffic generator.

Example request body:

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

    Spawns a background generator thread

    Runs until stopped or count is reached

### POST /can/stop/{name}

Stop a running generator.

POST /can/stop/example-gen

    Signals the generator thread to stop

    Cleans up server state

### GET /status

Returns server state:

{
  "can_interfaces": ["can0"],
  "generators": [],
  "ecus": {
    "cummins": false,
    "ddec": false,
    "bendix": false
  }
}

### WebSocket API
/ws/readcan/{can_interface}

Streams received CAN frames as JSON arrays.

Example payload:

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

    Push-only

    Client-side filtering

    Candump-compatible formatting in CLI

## CLI Usage
### Install the CLI

cd cli
pip install -e .

### Verify:

sphere-can --help

### readcan

Read CAN traffic (candump-style).

sphere-can readcan <can_interface> [OPTIONS]

Examples:

sphere-can readcan can0
sphere-can readcan can0 --filter-id 0x123
sphere-can readcan can0 --log can0.log
sphere-can readcan can0 --filter-id 0x18FEF100 --log j1939.log

Options:
Option	Description
can_interface	CAN interface (e.g., can0)
--filter-id	Hex arbitration ID to match
--log	Append output to a log file

Output format:

(1712859342.123456) can0 0x123#deadbeef01020304

### sendcan

Generate CAN traffic (cangen-style). Runs in the foreground.

sphere-can sendcan <can_interface> [OPTIONS]

Examples:

sphere-can sendcan can0 \
  --id 123 \
  --data DEADBEEF01020304 \
  --len 8 \
  --gap-ms 10

Extended ID:

sphere-can sendcan can0 \
  --extended \
  --id 18FEF100 \
  --data AAAAAAAAAAAAAAAA \
  --len 8

DoS / flood:

sphere-can sendcan can0 --extended --id 00000000 --data 0000000000000000 --len 8 --gap-ms 0

Options:
Option	Description
can_interface	CAN interface
--id	Arbitration ID (hex)
--extended	Use 29-bit ID
--data	Hex payload
--len	DLC (default 8)
--gap-ms	Inter-frame gap (float, ms)
--count	Number of frames
--random-id	Random IDs
--random-data	Random payloads

## Notes:

    Ctrl+C stops transmission cleanly

    --gap-ms 0 performs best-effort flooding

    Kernel TX backpressure is handled safely

## Design Notes

    Generator lifecycle uses threading.Event

    HTTP requests are one-shot; generators outlive requests

    WebSocket RX is push-only

    Client-side filtering avoids server-side state explosion

    Intended for operation behind VPN/WireGuard

## Known Limitations

    Sub-millisecond gaps are best-effort (Linux scheduling)

    High-rate logging can bottleneck disk I/O

    No built-in authentication (handled by network layer)

## Intended Use

    CAN DoS and spoofing demonstrations

    Remote vehicular testbeds

    Data collection for forensics and provenance research

    Reproducible security experiments

## License

Research and internal use. Licensing to be defined by the project owner.

## Status

Functional, stable, and demo-ready.

