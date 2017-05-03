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

    import openbot.logger
    import openbot.config
    try:
      self.dbc_perms = openbot.config.get_perms_by_id(self.id)

      type(self).has_perm = self.dbc_perms.has_perm
      type(self).grant_perm = self.dbc_perms.User.grant_perm
      type(self).revoke_perm = self.dbc_perms.User.revoke_perm

      openbot.logger.log('discord.user.User', parent='core.debug.bootstrapped_success', send_to_chat=False)
      self.dbc_patched = True
    except Exception as e:
      openbot.logger.log(self, error_point=e, parent='core.error.bootstrapped_fail', send_to_chat=False)