class Player:
    def __init__(self, discordMember):
        self.discordMember = discordMember
        self.private_channel = None
        self.role = None

    def __str__(self):
        return self.discordMember.display_name
