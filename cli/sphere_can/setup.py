import typer
import requests
from sphere_can.config import api_base

setup = typer.Typer(help="ECU relay control")

@setup.command("on")
def ecu_on(ecu: str):
    """
    Turn ECU relay ON
    """
    url = f"{api_base()}/relay"
    r = requests.post(url, params={"ecu": ecu, "on": True})
    r.raise_for_status()
    print(f"{ecu}: ON")

@setup.command("off")
def ecu_off(ecu: str):
    """
    Turn ECU relay OFF
    """
    url = f"{api_base()}/relay"
    r = requests.post(url, params={"ecu": ecu, "on": False})
    r.raise_for_status()
    print(f"{ecu}: OFF")

@setup.command("status")
def ecu_status():
    """
    Show ECU relay status
    """
    url = f"{api_base()}/status"
    r = requests.get(url)
    r.raise_for_status()

    ecus = r.json()["ecus"]
    for ecu, state in ecus.items():
        print(f"{ecu}: {'ON' if state else 'OFF'}")

@setup.command("list")
def ecu_list():
    """
    List known ECUs
    """
    for ecu in ["cummins", "ddec", "bendix"]:
        print(ecu)
