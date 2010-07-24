#
# Char constants
#

CORNER = '+'
VERT = '|'
VERT_DASH = ':'
HORT = '-'
HORT_DASH = '='
CORNER_CURVE_NW_SE = '/'
CORNER_CURVE_NE_SW = '\\'
LINE_EAST = '>'
LINE_WEST = '<'
LINE_SOUTH = 'V'
LINE_SOUTH2 = 'v'
LINE_NORTH = '^'

CHAR_X = 12
CHAR_Y = 16

#
# direction constants
#

DIR_EAST = 1
DIR_SOUTH = 2
DIR_WEST = 3
DIR_NORTH = 4

#
# Helper functions
#

def is_corner(char):
    return char == CORNER or char == CORNER_CURVE_NW_SE or char == CORNER_CURVE_NE_SW

def is_curved_corner(char):
    return char == CORNER_CURVE_NE_SW or char == CORNER_CURVE_NW_SE

def is_hort(char):
    return char == HORT or char == HORT_DASH

def is_vert(char):
    return char == VERT or char == VERT_DASH

def is_dashed(char):
    return char == HORT_DASH or char == VERT_DASH

def is_line_end(char):
    return char == LINE_EAST or char == LINE_WEST or char == LINE_SOUTH or char == LINE_SOUTH2 or char == LINE_NORTH

