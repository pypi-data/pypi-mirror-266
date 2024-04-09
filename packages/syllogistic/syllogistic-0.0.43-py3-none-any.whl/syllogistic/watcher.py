import math
import os
import time

from time import time, strftime
from datetime import datetime
from pakettic import ticfile
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from syllogistic.processor import ProcessorContext, ProcessorException, process_lines

class BuildWatcher(FileSystemEventHandler):
  files = set()
  dirs = set()
  watches = dict()

  def __init__(self, version, file, outfile, strict):
    self.version = version
    self.file = os.path.abspath(file)
    self.outfile = outfile
    self.strict = strict
    self.observer = Observer()
    self.last_src = None
    self.last_time = time()

  def _build(self):
    dirs = set()
    context = self.build(True)

    if context:
      self.files = context.files
      self.files.add(self.file)

      for file in self.files:
        # Assumed to already be absolute paths
        dirs.add(os.path.dirname(file))

      for dir in self.dirs.difference(dirs):
        if dir in self.watches:
          self.observer.unschedule(self.watches[dir])
          del self.watches[dir]

      for dir in dirs.difference(self.dirs):
        self.watches[dir] = self.observer.schedule(self, dir)

      self.dirs = dirs

  def build(self, watched=False):
    context = None

    try:
      start = time()
      beginmsg = f'\r[{strftime("%H:%M")}] File updated, building...'
      print(beginmsg, end='')

      cart = ticfile.join_code(ticfile.read(self.file))

      for chunk in [chunk for chunk in cart if chunk[1] == ticfile.ChunkID.CODE]:
        code = cart[chunk].decode('ascii')
        context = ProcessorContext(self.file, code.split('\n'), strict=self.strict, watched=True);
        result = process_lines(context)
        result = f'-- builder: SyllogisTIC v{self.version}\n-- built: {datetime.now()}Z\n' + result
        cart[chunk] = result.encode('ascii')
        ticfile.write(cart, self.outfile)

      end = (time() - start) * 1000
      end = math.floor(end) / 1000 if end > 1000 else str(math.floor(end)) + 'm'
      print(f'\r[{strftime("%H:%M")}] Built in {end}s'.ljust(len(beginmsg), ' '), end='')

    except ProcessorException as pe:
      print(f'\nError: {pe.args[0]}; in {pe.file} on line {pe.line}')
      print(f'[{strftime("%H:%M")}] Build failed with errors')

    return context

  def start(self):
    print('')
    self._build()
    self.observer.start()

    try:
      while self.observer.is_alive():
        self.observer.join(1)
    except KeyboardInterrupt:
      print('\nAsked to quit. Goodbye...')
    finally:
      self.stop()

  def stop(self):
    self.observer.stop()
    try:
      self.observer.join()
    except:
      pass

  def on_deleted(self, event):
    if event.src_path == self.file:
      print('\nInput file deleted. Ending watch.')
      self.stop()

  def on_modified(self, event):
    now = time()

    # 10ms is probably adequate for debouncing if we get called more than once for the same modification
    # The author's Windows 10 Pro is seeing ~5-6ms between the first and second of the doubled event
    if event.src_path in self.files and (event.src_path != self.last_src or (now - self.last_time) * 1000 > 10):
      self.last_src = event.src_path
      self.last_time = now
      self.build()

  def on_moved(self, event):
    if event.src_path == self.file:
      # Technically we could update self.file and keep on going,
      # but things could get weird depending on where it's moved to
      print('\nInput file moved. Ending watch.')
      self.stop()
