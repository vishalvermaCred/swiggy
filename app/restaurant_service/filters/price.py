class Price:
    def __init__(self, price_range) -> None:
        self.price_range = price_range.split("-")
        self.lower_price = int(self.price_range[0])
        self.upper_price = int(self.price_range[1])

    def filter(self, item):
        return self.lower_price <= item.get("price") <= self.upper_price
