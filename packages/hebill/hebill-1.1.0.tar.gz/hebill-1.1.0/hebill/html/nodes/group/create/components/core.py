class Components:
    def __init__(self, sir):
        self.senior = sir

    def table(self):
        from .....components import Table
        return Table(self.senior)
