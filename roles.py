class Role:
    def __str__(self):
        return self.roleName

    def display_role(self):
        return self.roleName + "\n" + self.description


class LoupGarou(Role):
    def __init__(self):
        self.roleName = "Loup-Garou"
        self.description = "Son objectif est d'éliminer tous les innocents (ceux qui ne sont pas Loups-Garous). Chaque nuit, il se réunit avec ses compères Loups pour décider d'une victime à éliminer..."
        self.image_filename = "loup-garou.png"


class LoupBlanc(LoupGarou):
    def __init__(self):
        self.roleName = "Loup-Garou Blanc"
        self.description = "Son objectif est de terminer SEUL la partie. Les autres Loups-Garous croient qu'il est un loup normal, mais une nuit sur deux il peut assassiner un loup de son choix..."
        self.image_filename = "loupBlanc.png"
        self.target_choice = None


class Villageois(Role):
    def __init__(self):
        self.roleName = "Simple Villageois"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il ne dispose d'aucun pouvoir particulier : uniquement sa perspicacité et sa force de persuasion."
        self.image_filename = "villageois.png"


class Voyante(Villageois):
    def __init__(self):
        self.roleName = "Voyante"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Chaque nuit, elle peut espionner un joueur et découvrir sa véritable identité..."
        self.image_filename = "voyante.png"
        self.targets = []


class Sorcière(Villageois):
    def __init__(self):
        self.roleName = "Sorcière"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Elle dispose de deux potions : une potion de vie pour sauver la victime des Loups, et une potion de mort pour assassiner quelqu'un."
        self.image_filename = "sorcière.png"
        self.lifePotion = True
        self.deathPotion = True
        self.target_choice = None


class Chasseur(Villageois):
    def __init__(self):
        self.roleName = "Chasseur"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. A sa mort, il doit éliminer un joueur en utilisant sa dernière balle..."
        self.image_filename = "chasseur.png"
        self.target_choice = None


class Ange(Villageois):
    def __init__(self):
        self.roleName = "Ange"
        self.description = "Son objectif est d'être éliminé par le village lors du premier vote de jour. S'il réussit, il gagne la partie. Sinon, il devient un Simple Villageois."
        self.image_filename = "ange.png"


class Cupidon(Villageois):
    def __init__(self):
        self.roleName = "Cupidon"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Dès le début de la partie, il doit former un couple de deux joueurs. Leur objectif sera de survivre ensemble, car si l'un d'eux meurt, l'autre se suicidera."
        self.image_filename = "cupidon.png"
        self.targets_choice = []

# TODO:


class Salvateur(Villageois):
    self.roleName = "Salvateur"
    self.description = "Son objectif est d'éliminer tous les Loups-Garous. Chaque nuit, il peut protéger quelqu'un de l'attaque des Loups-Garous..."
    self.image_filename = "salvateur.png"
    self.target_choice = None
