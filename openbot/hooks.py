import openbot.logger

__events__ = []
_store = {}
_important = []


def dbc_hook(event: str):
  def _hook_wrapper(ftn):
    _register_hook(ftn, event)
  return _hook_wrapper


def important(ftn):
  _important.append(ftn)


def _register_hook(ftn, event: str):
  if event not in __events__:
    openbot.logger.log(ftn.__name__,
                       event=event,
                       parent='core.debug.register_hook_bad_event',
                       send_to_chat=False)

  if event in _store:
    if ftn in _important:
      openbot.logger.log(ftn.__name__,
                         event=event,
                         parent='core.debug.register_hook_important',
                         send_to_chat=False)
      _store.get(event).insert(0, ftn)
    else:
      openbot.logger.log(ftn.__name__,
                         event=event,
                         parent='core.debug.register_hook',
                         send_to_chat=False)
      _store.get(event).append(ftn)
  else:
    _store[event] = [ftn]


def execute_hook(event: str, *args, **kwargs):
  if event not in _store:
    openbot.logger.log(event,
                       parent='core.debug.run_hook_no_events',
                       send_to_chat=False)
    return

  for ftn in _store.get(event):
    try:
      openbot.logger.log(ftn.__name__,
                         event=event,
                         parent='core.debug.run_hook',
                         send_to_chat=False)
      ftn(*args, **kwargs)
    except Exception as e:
      openbot.logger.log(ftn.__name__,
                         hook=event,
                         error_point=e,
                         parent='core.error.run_hook_failed',
                         send_to_chat=False)