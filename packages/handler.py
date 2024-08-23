class DataHandler:
    def check_type(self, check_class, data):
        data = check_class(**data)
        return data
