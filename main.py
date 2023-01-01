import curses
from curses import wrapper
import logging

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
	logger = setupLogger()

	curses.noecho()
	state = ""

	stdscr.clear()

	while True:
		key = stdscr.get_wch()
		y, x = stdscr.getyx()
		new_y_position = y
		new_x_position = x
		logger.debug(f"current cursor position - y: {y} x: {x}")

		logger.debug(key)

		if key == curses.KEY_BACKSPACE:
			state = state[:x - 1] + state[x:]
			new_x_position = x - 1
		elif key == curses.KEY_LEFT:
			new_x_position = x - 1
		elif key == curses.KEY_RIGHT:
			new_x_position = x + 1
		elif key == curses.KEY_UP:
			new_y_position = y - 1
		elif key == curses.KEY_DOWN:
			new_y_position = y + 1
			continue
		# Delete line with CTRL + d
		elif key == 4:
			state = ""
		else:
			insert_x = x

			if key == "\n":
				logger.debug("new line detected")
				new_y_position = y + 1
				new_x_position = 0
			else:
				new_x_position = x + 1

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

			state = state[:insert_x] + key + state[insert_x:]

		stdscr.clear()
		stdscr.addstr(state)
		logger.debug(f"new locations - y: {new_y_position} x: {new_x_position}")
		stdscr.move(new_y_position, new_x_position)
		stdscr.refresh()

wrapper(main)
