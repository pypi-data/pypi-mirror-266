


class KomodoDataSource:
    def __init__(self, name, type="filesystem", id=None):
        self.name = name
        self.type = type
        self.id = id or name.lower().replace(' ', '_')

    def __str__(self):
        return f"{self.id}: {self.name} ({self.type})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }

    def list_items(self):
        raise NotImplementedError("list_items method not implemented")

    def list_items_with_details(self):
        raise NotImplementedError("list_items method not implemented")

    def get_item(self, key):
        raise NotImplementedError("get_item method not implemented")
