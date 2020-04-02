from data_struct.player import Player


class Target:
    def __init__(self, actual_num, player, accusator=None):
        self.actual_num = actual_num
        self.player = player
        self.accusators = [accusator]

    def add_accusator(self, accusator):
        self.accusators.append(accusator)

    def __str__(self):
        message = f"{len(self.accusators)} votes pour **{self.player}** :\t| "
        for accusator in self.accusators:
            message += f"*{accusator}* |\t"
        return message


class TargetEmoji:
    def __init__(self, player, accusators):
        self.player = player
        self.accusators = accusators

    def __str__(self):
        message = f"{len(self.accusators)} votes pour **{self.player}** :\t| "
        for accusator in self.accusators:
            message += f"*{accusator}* |\t"
        return message

    def nb_accusators(self):
        return len(self.accusators)
