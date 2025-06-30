import subprocess

APPLY_CONFIGS_FILE = "/host/apply_all_configs.sh"

def apply_config():
    # Lancio lo script e aspetto che finisca
    result = subprocess.run(
        ['bash', APPLY_CONFIGS_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True        # decodifica in str invece che bytes
    )

    return result