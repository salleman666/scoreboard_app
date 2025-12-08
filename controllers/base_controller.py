class BaseController:
    """
    Minimal shared controller API.
    Will be expanded as logic grows.
    """

    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg

    def log(self, msg):
        # Optional helper if needed later
        print(f"[CONTROLLER] {msg}")
