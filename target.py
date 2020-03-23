from player import Player


class Target:
    def __init__(self, actual_num, player, accusator):
        self.actual_num = actual_num
        self.player = player
        self.accusator = [accusator]

    def add_accusator(self, accusator):
        self.accusator.append(accusator)

    def __str__(self):
        message = f"{len(self.accusator)} votes:\n"
        for accusator in self.accusator:
            message += f"{accusator.display_name} "
        return message
