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
import typer
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

    # Odd width ensures the ECU connection lines align
    # exactly with the CAN bus junctions.
    column_width = 21
    total_width = column_width * len(ecu_names)

    print("\nSPHERE-CAN Network\n")

    # ECU names
    print("".join(
        f"{ecu.upper():^{column_width}}"
        for ecu in ecu_names
    ))

    # ECU states with color
    state_line = ""

    for ecu in ecu_names:
        is_on = ecus.get(ecu, False)

        state = "[ON]" if is_on else "[OFF]"
        color = typer.colors.GREEN if is_on else typer.colors.RED

        # Center manually before applying ANSI color.
        # This prevents color escape sequences from affecting alignment.
        padding = column_width - len(state)
        left = padding // 2
        right = padding - left

        state_line += (
            " " * left
            + typer.style(state, fg=color, bold=True)
            + " " * right
        )

    print(state_line)

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

    # CAN interface label
    print(f"{'can0':^{total_width}}\n")
