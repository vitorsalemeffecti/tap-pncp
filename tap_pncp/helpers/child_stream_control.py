
class ChildStreamControl():
    """ Avoid duplication of children streams by ids"""

    def __init__(self) -> None:
        self.created_stream_ids = []

    def should_not_create(self, id:str):
        if id in self.created_stream_ids:
            return True
        else:
            return False

    def add_to_control(self, id:str):
        self.created_stream_ids.append(id)