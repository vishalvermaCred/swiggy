class Rating:
    def __init__(self, rating) -> None:
        self.rating = int(rating)

    def filter(self, item):
        return item["rating"] and item["rating"] >= self.rating
