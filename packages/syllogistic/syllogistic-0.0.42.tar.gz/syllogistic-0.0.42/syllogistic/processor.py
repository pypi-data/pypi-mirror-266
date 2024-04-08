import os
import re

from enum import StrEnum
from pathlib import Path


# https://is.gd/4s1GdR
# tl;dr: I chose it, I published it, it's baked in, it's too late to change it! Thank you for understanding.
PACKAGES_DIR = '.tic_pkgs'

class MagicComment(StrEnum):
  """
    Supported 'magic' comment types used by this build system
  """
  GROUP_START='#group:start'
  GROUP_END='#group:end'
  IMPORT='#import'
  INCLUDE='#include'
  EXPORTS='#exports'

class ProcessorGroup:
  def __init__(self, name, disabled):
    self.name = name
    self.disabled = disabled

class ProcessorContext:
  exports = set()
  groups = []
  disabled = False
  line = None
  number = -1

  def __init__(self, path, lines, strict=False, files=None, aka=None, included=None, excluded=None, watched=False, root=None):
    self.path = path
    self.lines = lines
    self.strict = strict
    self.files = set() if files is None else files
    self.aka = aka
    self.included = set() if included is None else included
    self.excluded = set() if excluded is None else excluded
    self.watched = watched
    self.root = os.path.dirname(os.path.abspath(path)) if root is None else root;

  def current_group(self):
    return self.groups[len(self.groups) - 1]

  def _update_status(self):
    # We might be checking his often so it makes sense to do it on group
    # add/remove rather than on every access to the enabled prop
    disabled = False

    for group in self.groups:
      if group.disabled:
        disabled = True
        break

    self.disabled = disabled

  def _is_disabled(self, name, default):
    if name in self.included:
      return False
    elif name in self.excluded:
      return True

    return default

  def push_group(self, name):
    if name.startswith('-'):
      name = name[1:]
      self.groups.append(ProcessorGroup(name, self._is_disabled(name, True)))
    elif name.startswith('+'):
      name = name[1:]
      self.groups.append(ProcessorGroup(name, self._is_disabled(name, False)))

    self._update_status()

  def pop_group(self, name):
    if name != self.current_group().name:
      raise ProcessorException(f"Invalid group '{name}' nesting", self)

    self.groups.pop()
    self._update_status()

class ProcessorException(Exception):

  def __init__(self, message, context):
    super().__init__(message)

    self.file = context.path
    self.line = context.number


def raise_concern(message, context):
  if context.strict:
    raise ProcessorException(message, context)

  prefix = '\n' if context.watched else ''
  print(prefix + 'Warning: ' + message)

# Important stuff
def resolve_package(context, path, mangled):
  name = path.split('/')[0]
  current = Path(context.root)

  # Check for reserved names
  if re.match(r'^\W', path):
    raise ProcessorException(f"Invalid package name '{name}'", context)

  # There's probably some better way of walking up and doing this?
  while not current.joinpath(PACKAGES_DIR, path).exists() and current.name:
    current = current.parent

  # Fall back to the user's home directory
  if not current.joinpath(PACKAGES_DIR, path).exists():
    current = Path.home()

  if not current.joinpath(PACKAGES_DIR, path).exists():
    # Unmangle our sugar
    if mangled:
      name = re.sub(r'[/\\]index.lua', '', name)
    raise ProcessorException(f"Unable to resolve package '{name}'", context)

  # os.path.abspath is to match our usages of that elsewhere so things are consistent
  return os.path.abspath(str(current.joinpath(PACKAGES_DIR, path).absolute()))

def process_include(context, args):
  if not context.disabled:
    path = ''
    terminated = 1
    included = context.included
    excluded = context.excluded
    aka = None
    mangled = False

    if args[0].startswith("'") and not args[0].endswith('"'):
      terminated = -1

      for i in range(len(args)):
        path = path + args[i]

        if args[i].endswith("'"):
          terminated = i + 1
          break

      if terminated == -1:
        raise ProcessorException("Unterminated ' in include", context)

      # remove quotes
      path = path[1:len(path)-1]

      # Probably a better way to do that...
      if not os.path.splitext(path)[1]:
        mangled = True
        path = os.path.join(path, 'index.lua')

    if len(args) > terminated and args[terminated] == 'as':
      terminated = terminated + 1

      if len(args) > terminated:
        aka = args[terminated]
        terminated = terminated + 1
      else:
        raise ProcessorException('Invalid import, missing name after \'as\'', context)

    # process remainder
    for i in range(terminated, len(args)):
      items = args[i].split(',')

      if items[0].startswith('+'):
        items[0] = items[0][1:]
        included = included.union(set(items))
      elif items[0].startswith('-'):
        items[0] = items[0][1:]
        excluded = excluded.union(set(items))
      else:
        raise_concern(f"Unrecognized group modifier prefix '{items[0][0]}', ignoring", context)

    if len(included.intersection(excluded)):
      raise_concern('Group names duplicated between include and exclude in include', context)

    # Handle relative paths
    if path.startswith('.'):
      # dirname is safe to do here since we added index.lua above for folders
      parent = os.path.dirname(context.path)
      path = os.path.join(parent, path)

    elif not path.startswith('/'):
      path = resolve_package(context, path, mangled)

    if not path:
      raise ProcessorException('Invalid include path; Did you forget quotes?', context)

    fullpath = os.path.abspath(path)

    if not fullpath in context.files:
      try:
        with open(path, 'r') as file:
          # Succeed in opening, *then* add to the list of files
          context.files.add(fullpath)

          return process_lines(ProcessorContext(
            path,
            file.read().split('\n'),
            strict=context.strict,
            files=context.files,
            aka=aka,
            included=included,
            excluded=excluded,
            watched=context.watched,
            root=context.root
          ))
      except FileNotFoundError:
        raise ProcessorException(f"Unable to locate included file '{path}'", context)
    else:
      # Future improvements could maybe seek to like remove other copies and replace them with this one if it would be a superset
      # of the original include
      raise_concern(f"File '{path}' included more than once; Did you include a file also included by your dependencies?", context)

  return ''

def process_group_start(context, args):
  context.push_group(args[0])
  return ''

def process_group_end(context, args):
  context.pop_group(args[0])
  return ''

def process_exports(context, args):
  context.exports = set(args[0].split(','))
  return ''

def process_import(context, args):
  if context.enabled:
    raise_concern('Import not supported. Use include.', context)
  return ''

def process_unknown(context, args):
  if len(args) and args[0].startswith('#'):
    raise_concern(f"Unrecognized magic comment '{command}', skipping", context)
    return ''
  return context.line

def process_lines(context):
  output = []

  for i in range(len(context.lines)):
    context.line = context.lines[i]
    context.number = i
    processed = context.line

    if context.line.strip().startswith('--'):
      parts = context.line.strip().split()
      directive = parts[1] if len(parts) > 1 else ''
      args = parts[2:] if len(parts) > 2 else []

      # This could be refactored into a map -> processor since they currently
      # take all the same arguments and with the context, there's no real reason
      # for any to take different arguemnts except for convenience
      match directive:
        case MagicComment.GROUP_START:
          processed = process_group_start(context, args)

        case MagicComment.GROUP_END:
          processed = process_group_end(context, args)

        case MagicComment.IMPORT:
          processed = process_import(context, args)

        case MagicComment.INCLUDE:
          processed = process_include(context, args)

        case MagicComment.EXPORTS:
          processed = process_exports(context, args)

        case _:
          processed = process_unknown(context, args)

    # We want to preserve line breaks from the input, but not ones that would be
    # caused by our preprocessing.
    if not context.disabled and (len(processed) or not len(context.line)):
      output.append(processed)

  output = '\n'.join(output)

  if len(context.exports) and context.aka:
    output = context.aka + '={__autogen=true}\n' + output

    # FIXME This really needs a proper parser to get context and determine if we should be replacing something...
    for export in context.exports:
      output = re.sub(
        r'(?:(?<=\n)' + export + r'(?=\W))|(?:(?<![\w.])' + export + r'(\.))|(?:(?<=function )' + export + r'(?=\W))',
        f'{context.aka}.{export}\\1', output
      )

  return output

