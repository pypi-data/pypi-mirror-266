class Columns(list):
    def __init__(self):
        super(Columns, self).__init__()

    def set_column(self, column=None):
        if not column:
            return False
        column = column.lower()
        if column not in self:
            self.append(column)
        return True

    def set_columns(self, data=None):
        if not data:
            return False
        for column in data:
            self.set_column(column)
        return True

    def output(self):
        if len(self) < 1:
            return "*"
        return ", ".join(self)
