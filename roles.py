class Role:
    def __str__(self):
        return self.roleName

    def display_role(self):
        return self.roleName + "\n" + self.description


class LoupGarou(Role):
    def __init__(self):
        self.roleName = "Loup Garou"
        self.description = "Un loup normal"


class Villageois(Role):
    def __init__(self):
        self.roleName = "Villageois"
        self.description = "Un villageaois normal"
