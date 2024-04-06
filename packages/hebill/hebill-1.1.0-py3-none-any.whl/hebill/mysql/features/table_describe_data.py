import re


class TableDescribeData(dict):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def Field(self): return self.get('Field')

    @property
    def Type(self): return self.get('Type')

    @property
    def Null(self): return self.get('Null')

    @property
    def Key(self): return self.get('Key')

    @property
    def Default(self): return self.get('Default')

    @property
    def Extra(self): return self.get('Extra')

    @property
    def tyre_name(self): return re.sub(r'\([^()]*\)', '', self.Type).upper()

    @property
    def is_type_int(self): return self.tyre_name == 'INT'

    @property
    def is_type_big_int(self): return self.tyre_name == 'BIGINT'

    @property
    def is_auto_increment(self): return self.Extra.lower() == 'auto_increment'
