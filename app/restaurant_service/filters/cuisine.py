class Cuisine:
    def __init__(self, cuisine_type) -> None:
        self.cuisine_type = cuisine_type if isinstance(cuisine_type, list) else [cuisine_type]

    def filter(self, item):
        """
        Cuisine type filter
        """
        item_cuisine_type = item.get("cuisine_type")
        item_cuisine_type = item_cuisine_type if isinstance(item_cuisine_type, list) else [item_cuisine_type]
        return bool(set(self.cuisine_type) & set(item_cuisine_type))
