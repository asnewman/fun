import curses
from curses import wrapper
import logging
import sys

EDITOR_HEIGHT = 10
EDITOR_WIDTH = 30

logger = logging.getLogger(__file__)
hdlr = logging.FileHandler(__file__ + ".log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

logger.info("begin")

def move_down(cursor_y, cursor_x, editor_y, state):
	logger.debug(f"{cursor_y} {editor_y} {len(state)}")

	# Cursor is at the end of the file
	# -2 because cursor_y and editor_y both index at 0
	if cursor_y + editor_y == len(state) - 2:
		return (cursor_y, cursor_x, editor_y)

	# Cursor is at the end of the screen, scroll down
	if cursor_y == EDITOR_HEIGHT:
		return (cursor_y, cursor_x, editor_y + 1)

	# Cursor can just move down
	return (cursor_y + 1, cursor_x, editor_y)

def main(scr):
	curses.noecho()

	if len(sys.argv) != 2:
		exit()
	file_name = sys.argv[1]

	text_file = open(file_name, "r")
	raw_state = text_file.read()
	state = raw_state.split("\n")
	logger.debug(state)
	text_file.close()

	editor = curses.newpad(100, 100)
	scr.refresh()

	editor_y = 0
	editor.addstr(raw_state)
	editor.refresh(editor_y, 0, 0, 0, EDITOR_HEIGHT, EDITOR_WIDTH)

	while True:
		key = scr.getch()
		y, x = scr.getyx()

		new_y = y
		new_x = x

		logger.debug(f"current cursor position - y: {y} x: {x}")
		logger.debug(key)

		if key == curses.KEY_BACKSPACE:
			state[y] = state[y][:x - 1] + state[y][x:]
			new_x = x - 1
		elif key == curses.KEY_LEFT:
			new_x = x - 1
		elif key == curses.KEY_RIGHT:
			new_x = x + 1
		elif key == curses.KEY_UP:
			pass
		elif key == curses.KEY_DOWN:
			new_y, new_x, editor_y = move_down(y, x, editor_y, state)
			logger.debug(f"new_y: {new_y} new_x: {new_x} editor_y: {editor_y}")
		# Delete line with CTRL + d
		elif key == 4:
			state = []
		# CTRL + F
		elif key == 6:
			key = scr.getch()
			# d
			if key == 100:
				new_x_position = 0
				new_y_position = 0
				state = ""
				scr.clear()
			# s
			elif key == 115:
				text_file = open(file_name, "w")
				text_file.write(state)
				text_file.close()
				exit()
			scr.move(new_y_position, new_x_position)
			continue
		else:
			char = chr(key)
			if char == "\n":
				logger.debug("new line detected")
				new_y = y + 1
				new_x = 0
			else:
				new_x = x + 1

			state[y] = state[y][:x] + char + state[x:]

		editor.clear()
		editor.addstr("\n".join(state))
		editor.refresh(editor_y, 0, 0, 0, EDITOR_HEIGHT, EDITOR_WIDTH)
		logger.debug(f"new locations - y: {new_y} x: {new_x}")
		scr.move(new_y, new_x)
		scr.refresh()

wrapper(main)
