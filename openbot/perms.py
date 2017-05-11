from discord.user import User
import openbot.config

perm_groups = {}            # Permission Groups as defined in config
user_perms = {}             # Permissions unpacked to each user


class PermGroup:
  def __init__(self,
               name,
               owner=False,
               auto_summon=False,
               full_access=False,
               grant_to=None,
               whitelist=None,
               blacklist=None):
    self.rank_name = name

    self.full_access = full_access
    self.auto_summon = auto_summon
    self.owner = owner

    self.whitelist = [] if whitelist is None else whitelist
    self.blacklist = [] if blacklist is None else blacklist
    self.grant_to = [] if grant_to is None else grant_to
    self.granted = []


  def __contains__(self, item):
    if isinstance(item, User):
      return item.id in self.grant_to or item.id in self.granted
    return False


  def granted_explict(self, perm):
    return self.owner or perm in self.whitelist and perm not in self.blacklist


  def granted_implict(self, perm):
    return not self.granted_explict(perm) and self.full_access


  def granted(self, perm):
    return self.granted_explict(perm) or self.granted_implict(perm)


  def update(self):
    pass


  @property
  def store(self):
    return {
      'full_access': self.full_access,
      'whitelist': self.whitelist,
      'blacklist': self.blacklist,
      'auto_summon': self.auto_summon,
      'grant_to': self.grant_to,
      'owner': self.owner
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


def get_perm(user):
  return get_perms_by_id(user.id)


def set_perm(user, perm, state=True):
  # TODO: Stub function > Gives from user the permission if they do not already have it by creating a "user group"
  pass


def has_perm(user, perm, explict=False):
  # TODO: Stub Function > Returns if the permission is granted
  pass