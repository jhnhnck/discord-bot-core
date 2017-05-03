class Perms:

  def __init__(self, id):
    # is server owner?
    # perms = full access
    # rank = 0
    # is member of group Admin
    # perms = full access
    # rank = 1
    # is member of group Moderators
    # perms = allowed commands ['help']
    #         escalated commands ['reload', ...]
    #
    self.id = id

    # Is user a member of server?
    self.rank = -1
    # elif is user server owner?
    self.rank = 0
    # else
    self.rank, self.rank_name = self._find_group()
    # find group should return rank and rank_name
    self.rank_name = 0

    self.full_access = False
    self.cmd_whitelist = []
    self.cmd_blacklist = []
    self.cmd_escalated = []