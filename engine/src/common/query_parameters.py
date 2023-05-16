class SkipLimitOrderByAndOrder:
    def __init__(self, skip: int = 0, limit: int = 100, order_by: str = None, order: str = None):
        self.skip = skip
        self.limit = limit
        self.order_by = order_by
        self.order = order
