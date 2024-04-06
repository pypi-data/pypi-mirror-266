from fire import Fire

def scan(filename: str):
    """Scan markdown todo history, highlight days and priority"""
    with open(filename, "r") as f:
        history_md = f.read()
        history_md = history_md.replace("###", "--> ")
        print(history_md)

Fire(scan)
