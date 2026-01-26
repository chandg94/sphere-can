# SPHERE-CAN CLI Tutorial (Client Usage)

This tutorial walks you through using the SPHERE-CAN command-line interface to interact with a CAN testbed at Colorado State University via SPHERE.
It is intended for first-time users and focuses entirely on client-side usage.

## Prerequisites

- A SPHERE account
- Access to the csuautomotive project
- A web browser
- Basic familiarity with terminal commands

## Step 1: Log in to SPHERE

Open a browser and go to:
```bash
https://launch.sphere-testbed.net
```
Log in using your SPHERE credentials.

## Step 2: Navigate to the Correct Project

From the SPHERE dashboard, select the project:
```bash
csuautomotive
```
Inside the project, navigate to:
```bash
xdc
```

## Step 3: Start a Locally Hosted Jupyter Server

In the xdc environment, start a locally hosted Jupyter server.

Once the Jupyter interface is running, open a Terminal from within Jupyter.

All remaining steps are performed inside the terminal environment.

## Step 4: Install the SPHERE-CAN CLI

First, ensure pip is up to date:
```bash
pip install --upgrade pip
```
Then install the SPHERE-CAN CLI (if not already installed):
```bash
pip install sphere-can
```
Verify installation:
```bash
sphere-can --help
```
You should see a list of available commands.

## Step 5: Configure Environment Variables (Client)

The CLI locates the SPHERE server using the SPHERE_API environment variable.

**By default, this is already configured to point to the correct server.**
If you need to change it, inside the terminal, run:
```bash
export SPHERE_API=http://<SERVER_IP>:8000
```
Replace <SERVER_IP> with the server address provided for your setup.

## Step 6: Check System Status

Before enabling anything, check the current system status:
```bash
sphere-can status
```
This shows which controllers and interfaces are currently active.

## Step 7: Turn On a Controller

Enable the DDEC controller:
```bash
sphere-can setup on ddec
```
You can do the same for other controllers using the same command. Use the following instead of **<ddec>**. Available controllers:
- cummins
- bendix

Wait a moment, then verify again:
```bash
sphere-can status
```
You should now see the controller enabled.

## Step 8: Read CAN Traffic (Listener)

Start reading CAN data from interface can0.

**The --timeout option is mandatory.**
This ensures the command exits cleanly without relying on SIGINT, which is not available in this environment.
```bash
sphere-can readcan can0 --timeout <TIME_IN_SECONDS>
```

## Step 9: Open a Second Terminal

In Jupyter:

Open another Terminal tab

Leave the first terminal running readcan

## Step 10: Launch a Network Flood / Denial-of-Service Test

Set the TIME_IN_SECONDS in the previous step to more than 60 (1min), otherwise, you can't observe the effect.

From the second terminal, send a high-rate CAN message flood:
```bash
sphere-can sendcan can0 \
  --extended \
  --id 00000000 \
  --data 0000000000000000 \
  --len 8 \
  --gap-ms 0
```

This command:

- Sends extended-ID CAN frames

- Uses a fixed arbitration ID and payload

- Sends messages as fast as possible (gap-ms 0)

## Step 11: Observe Traffic

Switch back to the readcan terminal.

You should see messages with:
```bash
00000000#0000000000000000
```
appearing in the output.

## Step 12: Stop the Traffic Generator

Follow the instructions printed by sendcan when it started.
Typically, this will look like:
```bash
sphere-can stop <name>
```

Once stopped, the traffic should cease.

### Step 13: Shut Down the Controller

Turn off the DDEC controller:
```bash
sphere-can setup off ddec
```

If you have turned any other controllers ON, turn them off as well with the same command. Use the name of the controller instead of **<ddec>** (example **<cummins>** and **<bendix>**).

**NOTE: You must turn off all controllers before logging off.**

Verify:
```bash
sphere-can status
```

Everything should now be inactive.
