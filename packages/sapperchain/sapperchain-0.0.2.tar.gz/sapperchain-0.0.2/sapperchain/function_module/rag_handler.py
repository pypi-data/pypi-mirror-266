class DataViewDefiner:
    def __init__(self, storage_loc, data_loader):
        self.storage_loc = storage_loc
        self.data_loader = data_loader

    def define_data(self, file_path, data_source, relation_db, vector_db, valid_field, search_expression, view_name,
                    storage_form, output_form):
        if storage_form == "Link":
            pass

        else:
            self.storage_loc[view_name] = {
                "FilePath": file_path,
                "RelationDB": relation_db,
                "VectorDB": vector_db,
                "Valid_Field": valid_field,
                "DataSource": data_source,
                "SearchExpression_Elements": search_expression,
                "StorageForm": storage_form,
                "OutputForm": output_form
            }


class DBGetter:
    def __init__(self):
        self.database = {}

    def get_db(self, file_path):
        db = self.database[file_path]
        return db


class DataRetriever:
    def __init__(self, valid_fields, search_expression_elements, output_format):
        self.valid_fields = valid_fields
        self.search_expression_elements = search_expression_elements
        self.output_format = output_format
        self.db_server = None

    def execute(self, view):
        pass



