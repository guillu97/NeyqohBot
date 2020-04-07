import constant


class Role:
    emoji = None
    nb = 0
    nb_max = 1

    def __str__(self):
        return self.roleName

    def display_role(self):
        return self.roleName + "\n" + self.description

# /!\ this class is only to have the emoji /!\


class Mayor(Role):
    def __init__(self):
        self.image_filename = "maire.png"


class LoupGarou(Role):
    nb = constant.DEFAULT_NB_LOUP
    nb_max = 100000

    def __init__(self):
        self.roleName = "**Loup-Garou**"
        self.description = "Son objectif est d'éliminer tous les innocents (ceux qui ne sont pas Loups-Garous). Chaque nuit, il se réunit avec ses compères Loups pour décider d'une victime à éliminer...\n "
        self.image_filename = "loup_garou.png"


class LoupBlanc(LoupGarou):
    nb = constant.DEFAULT_NB_LOUP_BLANC
    nb_max = 1

    def __init__(self):
        self.roleName = "**Loup-Garou Blanc**"
        self.description = "Son objectif est de terminer SEUL la partie. Les autres Loups-Garous croient qu'il est un loup normal, mais une nuit sur deux il peut assassiner un loup de son choix...\n "
        self.image_filename = "loup_garou_blanc.png"

# class to know who is Villageois


class Villageois(Role):
    pass


class SimpleVillageois(Villageois):
    nb = 0
    nb_max = 100000

    def __init__(self):
        self.roleName = "**Simple Villageois**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il ne dispose d'aucun pouvoir particulier : uniquement sa perspicacité et sa force de persuasion.\n "
        self.image_filename = "villageois.png"


class Voyante(Villageois):
    nb = constant.DEFAULT_NB_VOYANTE
    nb_max = 1

    def __init__(self):
        self.roleName = "**Voyante**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Chaque nuit, elle peut espionner un joueur et découvrir sa véritable identité...\n "
        self.image_filename = "voyante.png"


class Sorcière(Villageois):
    nb = constant.DEFAULT_NB_SORCIERE
    nb_max = 1

    def __init__(self):
        self.roleName = "**Sorcière**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Elle dispose de deux potions : une potion de vie pour sauver la victime des Loups, et une potion de mort pour assassiner quelqu'un.\n "
        self.image_filename = "sorciere.png"
        self.lifePotion = True
        self.deathPotion = True


class Chasseur(Villageois):
    nb = constant.DEFAULT_NB_CHASSEUR
    nb_max = 1

    def __init__(self):
        self.roleName = "**Chasseur**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. A sa mort, il doit éliminer un joueur en utilisant sa dernière balle...\n "
        self.image_filename = "chasseur.png"
        self.target_choice = None


class Ange(Villageois):
    nb = constant.DEFAULT_NB_ANGE
    nb_max = 1

    def __init__(self):
        self.roleName = "**Ange**"
        self.description = "Son objectif est d'être éliminé par le village lors du premier vote de jour. S'il réussit, il gagne la partie. Sinon, il devient un Simple Villageois.\n "
        self.image_filename = "ange.png"


class Cupidon(Villageois):
    nb = 0
    nb_max = 1

    def __init__(self):
        self.roleName = "**Cupidon**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Dès le début de la partie, il doit former un couple de deux joueurs. Leur objectif sera de survivre ensemble, car si l'un d'eux meurt, l'autre se suicidera.\n "
        self.image_filename = "cupidon.png"


class Salvateur(Villageois):
    nb = 0
    nb_max = 1

    def __init__(self):
        self.roleName = "**Salvateur**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Chaque nuit, il peut protéger quelqu'un de l'attaque des Loups-Garous...\n "
        self.image_filename = "salvateur.png"
        self.target_choice = None


class Ancien(Villageois):
    nb = 0
    nb_max = 1

    def __init__(self):
        self.roleName = "**Ancien**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il peut résister à la première attaque des loups. Mais s'il est tué par un ou des innocent(s), tous les innocents perdront leurs pouvoirs !\n "
        self.image_filename = "ancien.png"
        self.powerUsed = False
        self.innocentKilledHim = False


class EnfantSauvage(Villageois):
    nb = 0
    nb_max = 1

    def __init__(self):
        self.roleName = "**Enfant Sauvage**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il choisit un modèle au début du jeu, si ce dernier meurt, il devient Loup-Garou et joue dans leur camp.\n "
        self.image_filename = "enfant_sauvage.png"
        self.target_choice = None


class EnfantSauvageTransforme(LoupGarou):
    nb = 0
    nb_max = 1
    emoji = EnfantSauvage.emoji

    def __init__(self):
        self.roleName = "**Enfant Sauvage**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il choisit un modèle au début du jeu, si ce dernier meurt, il devient Loup-Garou et joue dans leur camp.\n "
        self.image_filename = "enfant_sauvage.png"
        self.target_choice = None


class EnfantSauvageTransforme(LoupGarou):
    nb = 0
    nb_max = 1
    emoji = EnfantSauvage.emoji

    def __init__(self):
        self.roleName = "**Enfant Sauvage**"
        self.description = "Son objectif est d'éliminer tous les Loups-Garous. Il choisit un modèle au début du jeu, si ce dernier meurt, il devient Loup-Garou et joue dans leur camp.\n "
        self.image_filename = "enfant_sauvage.png"
        self.target_choice = None


# TODO: add implemented roles when their turn is coded
IMPLEMENTED_ROLES = [SimpleVillageois(), Voyante(), Salvateur(), Sorcière(), Cupidon(),
                     Chasseur(), Ancien(), Ange(), EnfantSauvage(), LoupGarou(), LoupBlanc()]
