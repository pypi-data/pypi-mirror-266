import json


class Parser:
    display_name = None
    _id = None

    def parse_input(self, form):
        data = json.loads(form['jsonData'])
        selected_indexes = json.loads(form['selectedIndexes'])
        return [res for index, res in enumerate(data['data']) if index in selected_indexes]
