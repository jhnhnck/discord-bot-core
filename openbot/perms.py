from discord.user import User
import openbot.config

perm_groups = {}            # Permission Groups as defined in config
user_perms = {}             # Permissions unpacked to each user


class PermGroup:
  def __init__(self, name, auto_summon=False, full_access=False, grant_to=None, whitelist=None, blacklist=None):
    self.rank_name = name

    self.full_access = full_access
    self.auto_summon = auto_summon

    self.whitelist = [] if whitelist is None else whitelist
    self.blacklist = [] if blacklist is None else blacklist
    self.grant_to = [] if grant_to is None else grant_to
    self.granted = []


  def __contains__(self, item):
    if isinstance(item, User):
      return item.id in self.grant_to or item.id in self.granted
    return False


  def update(self):
    pass


  @property
  def store(self):
    return {
      'full_access': self.full_access,
      'whitelist': self.whitelist,
      'blacklist': self.blacklist,
      'auto_summon': self.auto_summon,
      'grant_to': self.grant_to
    }


def init_perms():
  global perm_groups
  perm_groups = {}

  for name, group in openbot.config.get_config('user_perms', safe_mode=False).items():
    try:
      perm_groups[name] = PermGroup(name, **perm_groups)
    except Exception as e:
      # log perm group invalid syntax e
      continue


@property
def default_perms():
  """
  Get Default Permissions.
  Generate a new permissions dictionary from the default values and permissions found in discord

  Returns:
    Default permissions values
  """
  return {
    'Owner': {},
    'Admin': {},
    'User': {},
    'Restricted': {}
  }


def get_perms_by_id(id):
  global user_perms

  if id in user_perms:
    return user_perms.get(id)
  else:
    user_perms = {}
    for name, group in perm_groups.items():
      group.update()
      return user_perms.get(id)


def get_perm(user, perm):
  # TODO: Stub function > Tests if user has listed permission
  return True


def set_perm(user, perm, state=True):
  # TODO: Stub function > Gives from user the permission if they do not already have it
  pass