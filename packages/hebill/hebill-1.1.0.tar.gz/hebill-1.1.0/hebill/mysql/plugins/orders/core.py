class Orders(dict):
    def __init__(self):
        super().__init__()

    def set_order(self, column, order_by="ASC"):
        if not column:
            return False
        self[column] = "ASC" if order_by == "ASC" else "DESC"
        return True

    def set_orders(self, data: dict = None):
        if not data:
            return False
        for k, v in data.items():
            self.set_order(k, v)
        return True

    def output(self):
        if len(self) < 1:
            return ""
        order_string = ", ".join(f'`{k}` {v}' for k, v in self.items())
        return f" ORDER BY {order_string}"
