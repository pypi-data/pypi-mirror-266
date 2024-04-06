class TableStatusData(dict):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def Name(self): return self.get('Name')

    @property
    def Engine(self): return self.get('Engine')

    @property
    def Version(self): return self.get('Version')

    @property
    def Row_format(self): return self.get('Row_format')

    @property
    def Rows(self): return self.get('Rows')

    @property
    def Avg_row_length(self): return self.get('Avg_row_length')

    @property
    def Data_length(self): return self.get('Data_length')

    @property
    def Max_data_length(self): return self.get('Max_data_length')

    @property
    def Index_length(self): return self.get('Index_length')

    @property
    def Data_free(self): return self.get('Data_free')

    @property
    def Auto_increment(self): return self.get('Auto_increment')

    @property
    def Create_time(self): return self.get('Create_time')

    @property
    def Update_time(self): return self.get('Update_time')

    @property
    def Check_time(self): return self.get('Check_time')

    @property
    def Collation(self): return self.get('Collation')

    @property
    def Checksum(self): return self.get('Checksum')

    @property
    def Create_options(self): return self.get('Create_options')

    @property
    def Comment(self): return self.get('Comment')
