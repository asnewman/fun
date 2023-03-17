import curses
 
# get the curses screen window
screen = curses.initscr()
 
# turn off input echoing
curses.noecho()
 
# respond to keys immediately (don't wait for enter)
curses.cbreak()
 
# map arrow keys to special values
screen.keypad(True)
 
try:
    while True:
        char = screen.getch()
        c = chr(char)
        if char == ord('q'):
            break
        elif char == curses.KEY_RIGHT:
            # print doesn't work with curses, use addstr instead
            screen.addstr(0, 0, 'right')
        elif char == curses.KEY_LEFT:
            screen.addstr(0, 0, 'left ')       
        elif char == curses.KEY_UP:
            screen.addstr(0, 0, 'up   ')       
        elif char == curses.KEY_DOWN:
            screen.addstr(0, 0, 'down ')
        elif char == 544:
            screen.addstr(0, 0, 'option left ')
        else:
          break
finally:
    # shut down cleanly
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
    print(curses.KEY_LEFT)
    print(char)
    print(c)
