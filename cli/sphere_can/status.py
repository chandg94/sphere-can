# import requests
# from sphere_can.config import api_base

# def status():
#     """
#     Show server status
#     """
#     url = f"{api_base()}/status"
#     r = requests.get(url)
#     r.raise_for_status()

#     data = r.json()

#     print("ECUs:")
#     for ecu, state in data["ecus"].items():
#         print(f"  {ecu}: {'ON' if state else 'OFF'}")

#     print("\nCAN interfaces:")
#     for c in data["can_interfaces"]:
#         print(f"  {c}")
import requests
from sphere_can.config import api_base


def status():
    """
    Show SPHERE-CAN network status.
    """
    url = f"{api_base()}/status"
    r = requests.get(url)
    r.raise_for_status()

    data = r.json()
    ecus = data["ecus"]

    # Fixed physical topology
    ecu_names = ["cummins", "ddec", "bendix"]

    column_width = 20
    total_width = column_width * len(ecu_names)

    print("\nSPHERE-CAN Network\n")

    # ECU names
    print("".join(
        f"{ecu.upper():^{column_width}}"
        for ecu in ecu_names
    ))

    # ECU state
    print("".join(
        f"{'[ON]' if ecus.get(ecu, False) else '[OFF]':^{column_width}}"
        for ecu in ecu_names
    ))

    # Connection lines only for powered-on ECUs
    print("".join(
        f"{'│' if ecus.get(ecu, False) else '':^{column_width}}"
        for ecu in ecu_names
    ))

    print("".join(
        f"{'│' if ecus.get(ecu, False) else '':^{column_width}}"
        for ecu in ecu_names
    ))

    # Build CAN bus
    bus = ["═"] * total_width

    for i, ecu in enumerate(ecu_names):
        if ecus.get(ecu, False):
            pos = i * column_width + column_width // 2
            bus[pos] = "╧"

    print("".join(bus))
    print(f"{'can0':^{total_width}}\n")
