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


class Voyante(Villageois):
    def __init__(self):
        self.roleName = "Voyante"
        self.description = "Une voyante qui peut voir"
        self.targets = []


# TODO :


class Sorcière(Villageois):
    def __init__(self):
        self.roleName = "Sorcière"
        self.description = "Une sorcière avec 2 potions"

# TODO:


class Chasseur(Villageois):
    def __init__(self):
        self.roleName = "Chasseur"
        self.description = "Un chasseur avec un fusil"

# TODO:


class Ange(Villageois):
    def __init__(self):
        self.roleName = "Ange"
        self.description = "Un ange malicieux"
