class mealType:
    def __init__(self, meal_type) -> None:
        self.meal_type = meal_type.value

    def filter(self, item):
        return self.meal_type == item["meal_type"]
