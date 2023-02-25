import curses
from curses import wrapper
import logging
import sys

# Capture ctrl + c and gracefully shutdown
import signal
def signal_handler(sig, frame):
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
##########################################

EDITOR_HEIGHT = 1
EDITOR_WIDTH = 1

logger = logging.getLogger(__file__)
hdlr = logging.FileHandler(__file__ + ".log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

logger.info("begin")

def move_left(cursor_y, cursor_x, editor_y, state):
  is_cursor_at_line_beginning = cursor_x == 0
  is_cursor_at_editor_top = cursor_y == 0

  # 4 scenerios
  # Go left
  # Go to previous line - beginning of line
  # Scroll up - top of life with content above
  # Do nothing - top of file

  if is_cursor_at_line_beginning and is_cursor_at_editor_top and editor_y == 0:
    return (cursor_y, cursor_x, editor_y)

  previous_line = state[editor_y + cursor_y - 1]
  previous_line_end = len(previous_line)

  if is_cursor_at_line_beginning and is_cursor_at_editor_top:
    return (cursor_y, previous_line_end, editor_y - 1)

  if is_cursor_at_line_beginning:
    return (cursor_y - 1, previous_line_end, editor_y)

  return (cursor_y, cursor_x - 1, editor_y)

def move_right(cursor_y, cursor_x, editor_y, state):
  curr_line_text = state[cursor_y + editor_y]
  logger.debug(f"curr_line_text {curr_line_text}")


  is_cursor_at_line_end = cursor_x == len(curr_line_text) or cursor_x == EDITOR_WIDTH - 1
  is_cursor_at_editor_bottom = cursor_y == EDITOR_HEIGHT

  # If content is shorter than the editor, bottom is earlier
  if len(state) < EDITOR_HEIGHT:
    is_cursor_at_editor_bottom = cursor_y + 1 == len(state)

  is_cursor_at_file_end = \
    is_cursor_at_line_end and \
    is_cursor_at_editor_bottom and \
    cursor_y + editor_y == len(state) - 1

  # 4 scenerios
  # Go right
  # Go to next line - end of line
  # Go to next line and scroll - end of line and bottom of editor
  # Do nothing - end of file

  if is_cursor_at_file_end:
    return (cursor_y, cursor_x, editor_y)

  if is_cursor_at_line_end and is_cursor_at_editor_bottom:
    return (cursor_y, 0, editor_y + 1)

  if is_cursor_at_line_end:
    return (cursor_y + 1, 0, editor_y)

  return (cursor_y, cursor_x + 1, editor_y)

def move_up(cursor_y, cursor_x, editor_y, state):
  # Top of the file, don't do anything
  if cursor_y == 0 and editor_y == 0:
    return (cursor_y, cursor_x, editor_y)

  previous_line = state[cursor_y + editor_y - 1]

  # if the previous line is shorter than the current one
  # set x to the last character position
  previous_line_x = cursor_x
  if cursor_x > len(previous_line) - 1:
    previous_line_x = len(previous_line)

  # Need to scroll up
  if cursor_y == 0:
    return (cursor_y, previous_line_x, editor_y - 1)

  return (cursor_y - 1, previous_line_x, editor_y)

def move_down(cursor_y, cursor_x, editor_y, state):
  # Cursor is at the end of the file
  if cursor_y + editor_y == len(state) - 1:
    return (cursor_y, cursor_x, editor_y)

  next_line = state[cursor_y + editor_y + 1]

  # if the next line is shorter than the current one
  # set x to the last character position
  next_line_x = cursor_x
  if cursor_x > len(next_line) - 1:
    next_line_x = len(next_line)

  # Cursor is at the end of the screen, scroll down
  if cursor_y == EDITOR_HEIGHT:
    return (cursor_y, next_line_x, editor_y + 1)

  # Cursor can just move down
  return (cursor_y + 1, next_line_x, editor_y)

def render(editor, state, editor_y):
  editor.clear()
  for i in range(len(state)):
    tabcnt = state[i].count("  ")
    editor.attron(curses.color_pair(tabcnt % 3 + 1))
    editor.addstr(state[i][0 : EDITOR_WIDTH])
    editor.attroff(curses.color_pair(tabcnt % 3 + 1))

    # Add new lines on all lines except for the last one
    if (i != len(state) - 1):
      editor.addstr("\n")
  editor.refresh(editor_y, 0, 0, 0, EDITOR_HEIGHT, EDITOR_WIDTH)

def main(scr):
  curses.noecho()
  curses.start_color()
  curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
  curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

  logger.debug(scr.getmaxyx())
  screen_height, screen_width = scr.getmaxyx()
  global EDITOR_HEIGHT
  global EDITOR_WIDTH
  EDITOR_HEIGHT = screen_height - 1
  EDITOR_WIDTH = screen_width - 1

  logger.debug(f"EDITOR_HEIGHT: {EDITOR_HEIGHT} EDITOR_WIDTH: {EDITOR_WIDTH}")

  if len(sys.argv) < 2:
    exit()
  file_name = sys.argv[1]

  text_file = open(file_name, "r")
  raw_state = text_file.read()
  state = raw_state.split("\n")
  logger.debug(state)
  text_file.close()

  editor = curses.newpad(10000, EDITOR_WIDTH)
  scr.refresh()

  start_y = 0
  try:
    start_y = int(sys.argv[2]) - 1
  except ValueError as e:
    # find line of code that matches
    i = 0
    for i in range(len(state)):
      if "def " + sys.argv[2] in state[i]:
        break
    start_y = i + 1
  except:
    pass

  editor_y = 0

  if start_y > 0 and start_y - EDITOR_HEIGHT > 0:
    editor_y = start_y - EDITOR_HEIGHT
    start_y = start_y - editor_y - 1
  
  render(editor, state, editor_y)

  if start_y:
    scr.move(start_y, 0)
  else:
    scr.move(0, 0)

  while True:
    key = scr.getch()
    y, x = scr.getyx()

    new_y = y
    new_x = x
    new_editor_y = editor_y

    logger.debug(f"current cursor position - y: {y} x: {x}")
    logger.debug(key)

    if key == curses.KEY_LEFT:
      new_y, new_x, new_editor_y = move_left(y, x, editor_y, state)
    elif key == curses.KEY_RIGHT:
      new_y, new_x, new_editor_y = move_right(y, x, editor_y, state)
    elif key == curses.KEY_UP:
      new_y, new_x, new_editor_y = move_up(y, x, editor_y, state)
    elif key == curses.KEY_DOWN:
      new_y, new_x, new_editor_y = move_down(y, x, editor_y, state)
    # Delete line with CTRL + d
    elif key == 4:
      state = []
    # CTRL + F
    elif key == 6:
      key = scr.getch()
      # c
      if key == 99:
        exit()
      # d
      if key == 100:
        new_x = 0
        if y != 0:
          new_y = y - 1
        del state[y + editor_y]
        render(editor, state, new_editor_y)
      # s
      elif key == 115:
        text_file = open(file_name, "w")
        text_file.write("\n".join(state))
        text_file.close()
      scr.move(new_y, new_x)
      continue
    else:
      char = chr(key)
      logger.debug(char)
      if char == "\n":
        logger.debug("new line detected")
        new_y = y
        if y != EDITOR_HEIGHT:
          new_y = y + 1
        new_x = 0
        state.insert(new_y + editor_y, "" + state[y + editor_y][x:])
        state[y + editor_y] = state[y + editor_y][:x]
      elif key == curses.KEY_BACKSPACE or key == 127:
        cursor_at_file_beginning = y == 0 and editor_y == 0
        if x != 0:
          state[y + editor_y] = state[y + editor_y][:x - 1] + state[y + editor_y][x:]
          new_x = x - 1
        else:
          if len(state[y + editor_y]) == 0 and not cursor_at_file_beginning:
            del state[y + editor_y]
            new_y = y - 1
            new_x = len(state[y + editor_y - 1])
          elif not cursor_at_file_beginning:
            # Delete line, push left over to previous line
            state[y + editor_y - 1] = state[y + editor_y - 1] + state[y + editor_y]
            del state[y + editor_y]
            new_x = len(state[y + editor_y - 1])
            new_y = y - 1
      else:
        new_x = x + 1
        curr_line_num = y + editor_y
        curr_line_text = state[curr_line_num]

        # all tabs are two spaces in fun because I want it that way
        if char == "\t":
          char = "  "
          new_x += 1

        state[y + editor_y] = state[y + editor_y][:x] + char + state[y + editor_y][x:]

      render(editor, state, new_editor_y)

    if editor_y != new_editor_y:
      editor.refresh(new_editor_y, 0, 0, 0, EDITOR_HEIGHT, EDITOR_WIDTH)
      editor_y = new_editor_y
    logger.debug(f"new locations - y: {new_y} x: {new_x}")
    scr.move(new_y, new_x)

wrapper(main)
