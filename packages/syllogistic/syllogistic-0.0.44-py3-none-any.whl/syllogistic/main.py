import argparse
import os
import sys

from importlib import metadata
from syllogistic.watcher import BuildWatcher


# test.lua.tic -> test, .lua.tic
def splitext2(path):
  filename, ext = os.path.splitext(path)

  if len(filename) > 1:
    filename2 = os.path.splitext(filename)

    if len(filename2) > 1:
      ext = filename2[1] + ext
      filename = filename2[0]

  return (filename, ext)

def main():
  version = metadata.version('syllogistic')

  argparser = argparse.ArgumentParser(
    prog='syllogistic',
    description=f'Build system for TIC-80 fantasy computer carts. v{version}'
  )
  argparser.add_argument('input', nargs='+', help='input file')
  argparser.add_argument('-o', '--out', default=os.getcwd(), metavar='str', help='output file or directory')
  argparser.add_argument('-s', '--strict', action='store_const', const=True, help='enable strict checking')
  argparser.add_argument('-w', '--watch', action='store_const', const=True, help='watch for file changes')

  args = argparser.parse_args()
  file = args.input[0]
  filename = splitext2(args.input[0])
  outfile = os.path.join(args.out, filename[0] + '.build' + filename[1]) if os.path.isdir(args.out) else args.out

  watcher = BuildWatcher(version, file, outfile, args.strict)
 
  if args.watch:
    watcher.start()
  else:
    watcher.build()
    print('')

if __name__ == '__main__':
  main()
