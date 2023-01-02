import curses
from curses import wrapper
import logging
import sys

def setupLogger():
	logger = logging.getLogger(__file__)
	hdlr = logging.FileHandler(__file__ + ".log")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)

	logger.info("begin")
	return logger

def main(stdscr):
	if len(sys.argv) != 2:
		exit()
	file_name = sys.argv[1]

	text_file = open(file_name, "r")
	state = text_file.read()
	text_file.close()

	stdscr.addstr(state)
	stdscr.refresh()

	logger = setupLogger()

	curses.noecho()

	while True:
		key = stdscr.getch()
		y, x = stdscr.getyx()

		insert_x = x
		if y > 0:
			logger.debug("multiple lines detected")
			# Go to respective y
			newlines = []
			for i in range(len(state)):
				if state[i] == "\n":
					newlines.append(i)
			logger.debug(f"len line length: {len(newlines)} y: {y}")
			if len(newlines) >= y:
				insert_x = x + newlines[y - 1] + 1
			else:
				insert_x = x


		new_y_position = y
		new_x_position = x
		logger.debug(f"current cursor position - y: {y} x: {x}")

		logger.debug(key)

		if key == curses.KEY_BACKSPACE:
			state = state[:insert_x - 1] + state[insert_x:]
			new_x_position = x - 1
		elif key == curses.KEY_LEFT:
			new_x_position = x - 1
		elif key == curses.KEY_RIGHT:
			new_x_position = x + 1
		elif key == curses.KEY_UP:
			new_y_position = y - 1
		elif key == curses.KEY_DOWN:
			new_y_position = y + 1
		# Delete line with CTRL + d
		elif key == 4:
			state = ""
		# CTRL + F
		elif key == 6:
			key = stdscr.getch()
			# d
			if key == 100:
				new_x_position = 0
				new_y_position = 0
				state = ""
				stdscr.clear()
			# s
			elif key == 115:
				text_file = open(file_name, "w")
				text_file.write(state)
				text_file.close()
				exit()
			stdscr.move(new_y_position, new_x_position)
			continue
		else:
			char = chr(key)
			if char == "\n":
				logger.debug("new line detected")
				new_y_position = y + 1
				new_x_position = 0
			else:
				new_x_position = x + 1

			state = state[:insert_x] + char + state[insert_x:]

		stdscr.clear()
		stdscr.addstr(state)
		logger.debug(f"new locations - y: {new_y_position} x: {new_x_position}")
		stdscr.move(new_y_position, new_x_position)
		stdscr.refresh()

wrapper(main)
