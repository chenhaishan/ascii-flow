# python standard libs
import sys

# ascii-flow libs
import ui

filename = None
if len(sys.argv) > 1:
    filename = sys.argv[1]
ui = ui.UI(filename)
ui.main()


