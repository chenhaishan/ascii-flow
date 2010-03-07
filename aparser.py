import simplehsm
import figure

#
# State machine signals
#

## process an ascii character
SIG_CHAR = simplehsm.SIG_USER
## we have reached the end of the ascii file
SIG_EOF = simplehsm.SIG_USER + 1

#
# Parser State Machine event
#

## Parser state machine events
class ParseEvent(simplehsm.StateEvent):

    ## The position of the character 
    pos = None

    ## The ascii character to process
    char = None

    ## Parser state machine event constructor
    # @param sig The signal associated with this event
    # @param pos The position of the ascii character
    # @param char The ascii character to process
    def __init__(self, sig, pos, char):
        simplehsm.StateEvent.__init__(self, sig)
        self.pos = pos
        self.char = char

#
# Search direction constants
#

SEARCH_EAST = 1
SEARCH_SOUTH = 2
SEARCH_WEST = 3
SEARCH_NORTH = 4

#
# Char constants
#

BOX_CORNER = '+'
BOX_VIRT = '|'
BOX_HORT = '-'

#
# Helper functions
#

def increment_position(pos, dir):
    global SEARCH_EAST, SEARCH_SOUTH, SEARCH_WEST, SEARCH_NORTH
    x, y = pos
    if dir == SEARCH_EAST:
        x += 1
    elif dir == SEARCH_SOUTH:
        y += 1
    elif dir == SEARCH_WEST:
        x -= 1
    elif dir == SEARCH_NORTH:
        y -= 1
    return (x, y)

def check_position_valid(ascii, pos):
    x, y = pos
    if x < 0 or y < 0:
        return False
    if y >= len(ascii):
        return False
    if x >= len(ascii[y]):
        return False
    return True

##
# Box parser state machine
#
# state hierachy
#
# main
#  searching
#  top_left
#  top_right
#  bottom_right
#  finished
#  error
class BoxParser(simplehsm.SimpleHsm):

    search_dir = None
    top_left_pos = None
    top_right_pos = None
    bottom_right_pos = None
    bottom_left_pos = None

    ## Box parser state machine constructor
    #
    # Sets the initial state
    def __init__(self):
        self.Initialize(self.main);

    def reset(self):
        self.Initialize(self.main)

    def find_box(self, ascii, pos):
        result = None
        x, y = pos
        # check if current position is the start of a box
        line = ascii[y]
        char = line[x]
        self.SignalCurrentState(ParseEvent(SIG_CHAR, pos, char))
        if not self.IsInState(self.searching):
            # complete box search
            while True:
                # increment position
                pos = x, y = increment_position(pos, self.search_dir)
                if not check_position_valid(ascii, pos):
                    return result
                char = ascii[y][x]
                self.SignalCurrentState(ParseEvent(SIG_CHAR, pos, char))
                if self.IsInState(self.finished):
                    # create box figure
                    x, y = self.top_left_pos
                    x2, y2 = self.bottom_right_pos
                    result = figure.Box(x, y, x2 - x, y2 - y)
                    self.reset()
                    break
                elif self.IsInState(self.error):
                    self.reset()
                    break
                else:
                    # continue
                    pass
        return result                

    ##
    # The top level main state
    # 
    # @param state_event The signal to send to this state
    # @return Aways returns None indicating that this is the top level state
    #
    def main(self, state_event):
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "main: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_INIT):
            self.InitTransitionState(self.searching)
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "main: exiting state"
            return None
        return None

    ##
    # The searching state
    #
    # At this stage we are looking for the top left character of a box figure
    # 
    # @param state_event The signal to send to this state
    # @return None if the signal is handled, otherwise the parent state (main())
    #
    def searching(self, state_event):
        global SIG_CHAR, BOX_CORNER
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  searching: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "  searching: exiting state"
            return None
        elif (state_event.sig == SIG_CHAR):
            #print "  searching: CHAR signal!"
            if state_event.char == BOX_CORNER:
                self.top_left_pos = state_event.pos
                self.search_dir = SEARCH_EAST
                self.TransitionState(self.top_left)
            return None;
        return self.main;

    ##
    # The top_left state
    #
    # Now we are looking for the top right corner of the box
    # 
    # @param state_event The signal to send to this state
    # @return None if the signal is handled, otherwise the parent state (main())
    #
    def top_left(self, state_event):
        global SIG_CHAR, BOX_CORNER, BOX_HORT
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  top_left: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "  top_left: exiting state"
            return None
        elif (state_event.sig == SIG_CHAR):
            #print "  top_left: CHAR signal!"
            if state_event.char == BOX_CORNER:
                self.top_right_pos = state_event.pos
                self.search_dir = SEARCH_SOUTH
                self.TransitionState(self.top_right)
            elif state_event.char == BOX_HORT:
                # keep going
                pass
            else:
                self.TransitionState(self.error)
            return None;
        return self.main;

    ##
    # The top_right state
    #
    # Now we are looking for the bottom right corner of the box
    # 
    # @param state_event The signal to send to this state
    # @return None if the signal is handled, otherwise the parent state (main())
    #
    def top_right(self, state_event):
        global SIG_CHAR, BOX_CORNER, BOX_VIRT
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  top_right: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "  top_right: exiting state"
            return None
        elif (state_event.sig == SIG_CHAR):
            #print "  top_right: CHAR signal!"
            if state_event.char == BOX_CORNER:
                self.bottom_right_pos = state_event.pos
                self.search_dir = SEARCH_WEST
                self.TransitionState(self.bottom_right)
            elif state_event.char == BOX_VIRT:
                # keep going
                pass
            else:
                self.TransitionState(self.error)            
            return None;
        return self.main;    

    ##
    # The bottom_right state
    #
    # Now we are looking for the bottom left corner of the box
    # 
    # @param state_event The signal to send to this state
    # @return None if the signal is handled, otherwise the parent state (main())
    #
    def bottom_right(self, state_event):
        global SIG_CHAR, BOX_CORNER, BOX_HORT
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  bottom_right: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "  bottom_right: exiting state"
            return None
        elif (state_event.sig == SIG_CHAR):
            #print "  bottom_right: CHAR signal!"
            if state_event.char == BOX_CORNER:
                self.bottom_left_pos = state_event.pos
                self.search_dir = SEARCH_NORTH
                self.TransitionState(self.bottom_left)
            elif state_event.char == BOX_HORT:
                # keep going
                pass
            else:
                self.TransitionState(self.error)    
            return None;
        return self.main;        

    ##
    # The bottom_left state
    #
    # Now we are want to hook up to the box origin
    # 
    # @param state_event The signal to send to this state
    # @return None if the signal is handled, otherwise the parent state (main())
    #
    def bottom_left(self, state_event):
        global SIG_CHAR, BOX_CORNER, BOX_VIRT
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  bottom_left: entering state"
            return None
        elif (state_event.sig == simplehsm.SIG_EXIT):
            #print "  bottom_left: exiting state"
            return None
        elif (state_event.sig == SIG_CHAR):
            #print "  bottom_left: CHAR signal!"
            if state_event.char == BOX_CORNER:
                self.TransitionState(self.finished)
            elif state_event.char == BOX_VIRT:
                # keep going
                pass
            else:
                self.TransitionState(self.error)                
            return None;
        return self.main;            

    ##
    # The finshed state
    #
    # @param state_event The signal to send to this state
    # @return The parent state (main())
    #
    def finished(self, state_event):
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  finished: entering state"
            return None
        return self.main

    ##
    # The error state
    #
    # @param state_event The signal to send to this state
    # @return The parent state (main())
    #
    def error(self, state_event):
        if (state_event.sig == simplehsm.SIG_ENTRY):
            #print "  error: entering state"
            return None
        return self.main
    
## Search for figures using a left to right, top to bottom method
#  @param ascii A list of text lines 
#  @return A list of figures
def parse(ascii):
    result = []
    bparse = BoxParser()
    for i in range(len(ascii)):
        line = ascii[i]
        for j in range(len(line)):
            box = bparse.find_box(ascii, (j, i))
            if box:
                result.append(box)
    return result
