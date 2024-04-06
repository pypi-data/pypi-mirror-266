class Limits(dict):
    def __init__(self):
        super().__init__({
            'start': 0,
            'quantity': 0
        })

    @property
    def start(self): return self["start"]

    @start.setter
    def start(self, number: int): self["start"] = number if number > 0 else 0

    @property
    def quantity(self): return self["quantity"]

    @quantity.setter
    def quantity(self, quantity: int): self["quantity"] = quantity if quantity > 0 else 0

    def output(self):
        if self.quantity <= 0:
            return ""
        return f' LIMIT {self.start}, {self.quantity}'
