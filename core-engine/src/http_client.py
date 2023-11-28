import httpx


class HttpClient(httpx.AsyncClient):
    def __init__(self):
        super().__init__()
