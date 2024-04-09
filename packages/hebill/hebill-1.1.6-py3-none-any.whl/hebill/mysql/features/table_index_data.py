class TableIndexData(dict):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def Table(self): return self.get('Table')

    @property
    def Non_unique(self): return self.get('Non_unique')

    @property
    def Key_name(self): return self.get('Key_name')

    @property
    def Seq_in_index(self): return self.get('Seq_in_index')

    @property
    def Column_name(self): return self.get('Column_name')

    @property
    def Collation(self): return self.get('Collation')

    @property
    def Cardinality(self): return self.get('Cardinality')

    @property
    def Sub_part(self): return self.get('Sub_part')

    @property
    def Packed(self): return self.get('Packed')

    @property
    def Null(self): return self.get('Null')

    @property
    def Index_type(self): return self.get('Index_type')

    @property
    def Comment(self): return self.get('Comment')

    @property
    def Index_comment(self): return self.get('Index_comment')
