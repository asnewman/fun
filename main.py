import curses
from curses import wrapper
import logging
import sys

EDITOR_HEIGHT = 10
EDITOR_WIDTH = 100

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
	previous_line_end = len(previous_line) - 1

	if is_cursor_at_line_beginning and is_cursor_at_editor_top:
		return (cursor_y, previous_line_end, editor_y - 1)

	if is_cursor_at_line_beginning:
		return (cursor_y - 1, previous_line_end, editor_y)

	return (cursor_y, cursor_x - 1, editor_y)

def move_right(cursor_y, cursor_x, editor_y, state):
	curr_line_text = state[cursor_y + editor_y]

	is_cursor_at_line_end = cursor_x == len(curr_line_text)
	is_cursor_at_editor_bottom = cursor_y == EDITOR_HEIGHT
	is_cursor_at_file_end = \
		is_cursor_at_line_end and \
		is_cursor_at_editor_bottom and \
		cursor_y + editor_y == len(state) - 2

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
	# -2 because cursor_y and editor_y both index at 0
	if cursor_y + editor_y == len(state) - 2:
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

	editor = curses.newpad(200, 10000)
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


		if key == curses.KEY_LEFT:
			new_y, new_x, editor_y = move_left(y, x, editor_y, state)
		elif key == curses.KEY_RIGHT:
			new_y, new_x, editor_y = move_right(y, x, editor_y, state)
		elif key == curses.KEY_UP:
			new_y, new_x, editor_y = move_up(y, x, editor_y, state)
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
				text_file.write("\n".join(state))
				text_file.close()
				exit()
			scr.move(new_y_position, new_x_position)
			continue
		else:
			char = chr(key)
			logger.debug(char)
			if char == "\n":
				logger.debug("new line detected")
				new_y = y + editor_y + 1
				new_x = 0
				state.append("" + state[y + editor_y][x:])
				state[y + editor_y] = state[y + editor_y][:x]
			elif key == curses.KEY_BACKSPACE:
				state[y + editor_y] = state[y + editor_y][:x - 1] + state[y + editor_y][x:]
				new_x = x - 1
			else:
				new_x = x + 1
				state[y + editor_y] = state[y + editor_y][:x] + char + state[y + editor_y][x:]

			editor.clear()
			editor.addstr("\n".join(state))

		editor.refresh(editor_y, 0, 0, 0, EDITOR_HEIGHT, EDITOR_WIDTH)
		logger.debug(f"new locations - y: {new_y} x: {new_x}")
		scr.move(new_y, new_x)

wrapper(main)
