class QueryParameters:
    def __init__(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order: str = None,
            status: str = None,
            tags: str = None,
            ai: bool = None
    ):
        self.search = search
        self.skip = skip
        self.limit = limit
        self.order_by = order_by
        self.order = order
        self.status = status
        self.tags = tags
        self.ai = ai
