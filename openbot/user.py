# noinspection PyTypeChecker
class User:

  def __init__(self, username=None, id=None, discriminator=None, avatar=None, bot=False, **kwargs):
    self.name = username
    self.id = id
    self.discriminator = discriminator
    self.avatar = avatar
    self.bot = bot

    # Try to future proof but also not break things
    known_values = ['name', 'id', 'discriminator', 'avatar', 'bot', '__dict__']
    for key in self.__slots__:
      if key not in known_values:
        setattr(self, key, kwargs.get(key, None))

    if type(self).dbc_patched is False:
      import openbot.logger
      import openbot.user

      type(self)._enum_perms = openbot.user.User._enum_perms
      type(self).has_perm = openbot.user.User.has_perm
      type(self).grant_perm = openbot.user.User.grant_perm
      type(self).revoke_perm = openbot.user.User.revoke_perm

      openbot.logger.log('discord.user.User', parent='core.debug.bootstrapped_success', send_to_chat=False)
      type(self).dbc_patched = True

    self.dbc_perms = self._enum_perms()


  def _enum_perms(self):
    # for each user on server
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
    return []


  def has_perm(self, key):
    # TODO: Stub function > Tests if user has listed permission
    return True


  def grant_perm(self, key, value):
    # TODO: Stub function > Gives from user the permission if they do not already have it
    pass


  def revoke_perm(self, key, value):
    # TODO: Stub function > Removes from user the permission if they already have it
    pass