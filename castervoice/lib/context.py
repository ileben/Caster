import time

from dragonfly import AppContext, Pause, ActionBase, ActionError

from castervoice.lib.dfplus.state.async import AsyncState, AsyncItem
from castervoice.lib import utilities, settings
from castervoice.lib.actions import Key
from castervoice.lib.clipboard import Clipboard
import natlink

class BracketCompare(object):
    EQUAL = 0
    GREATEREQUAL = 1
    LESSEREQUAL = 2
    
class BracketClamp(object):
    NONE = 0
    POSITIVE = 1
    NEGATIVE = 2

    
_context = ""
_index = -1
_brackets = 0
_selection_size = 0
_target_index = -1
_target_token = ""

bracket_count = 0
target_bracket_count = 0
target_bracket_compare = BracketCompare.EQUAL
target_bracket_clamp = BracketClamp.POSITIVE
arg_count = 0


# Override dragonfly.AppContext with aenea.ProxyAppContext if the 'use_aenea'
# setting is set to true.
if settings.SETTINGS["miscellaneous"]["use_aenea"]:
    try:
        from aenea import ProxyAppContext as AppContext
    except ImportError:
        print("Unable to import aenea.ProxyAppContext. dragonfly.AppContext "
              "will be used instead.")


def _target_is_character(target):
    '''determines if the target is a single character'''
    if len(target) == 1:
        return True
    '''if the character is in the character group:'''
    for s in target.split("~"):
        if s in ".,()[]{}<>":
            return True
    return False


def _find_index_in_context(target, context, look_left, start_index = None):
    '''attempts to find index of target in clipboard content'''
    if (start_index is None) or start_index == -1:
        start_index = len(context)-1 if look_left else 0
        
    tlist = target.split("~")
    index = -1
    token = ""
    if look_left:
        index = -99999
        for t in tlist:
            tmpindex = context.lower().rfind(t.lower(), 0, start_index + 1)  #
            if tmpindex != -1 and tmpindex > index:  # when looking left, we want the largest index
                index = tmpindex
                token = t
    else:
        index = 99999  # arbitrarily large number
        for t in tlist:
            tmpindex = context.lower().find(t.lower(), start_index)
            if tmpindex != -1 and tmpindex < index:  # conversely, when looking right, we want the smallest index
                index = tmpindex
                token = t
    if index == 99999 or index == -99999:
        return -1, ""
    return index, token

def _count_find_list(context, target):
    tlist = target.split("~")
    total_count = 0
    for t in tlist:
        total_count += _count_find(context, t)
    return total_count
       
def _count_find(context, target):
    count = 0
    length = len(context)
    index = 0
    while index < length:
        i = context.find(target, index)
        if i == -1:
            return count
        count += 1
        index = i + 1
    return count
  
def _count_brackets(context, look_left, starting_brackets, clamp):
    brackets = starting_brackets
    for c in (reversed(context) if look_left else context):
        
        if c=="(" or c=="[" or c=="{":
            brackets += (-1 if look_left else +1)
        if c==")" or c=="]" or c=="}":
            brackets += (+1 if look_left else -1)
        
        if clamp == BracketClamp.NEGATIVE:
            brackets = min(0, brackets)
        elif clamp == BracketClamp.POSITIVE:
            brackets = max(0, brackets)
    
    return brackets
    
def _compare_bracket_state(state, target, compare):
    if compare==BracketCompare.EQUAL:
        return state == target
    if compare==BracketCompare.GREATEREQUAL:
        return state >= target
    if compare==BracketCompare.LESSEREQUAL:
        return state <= target

def reset_bracket_count(count=0, factor=1, offset=0, compare = BracketCompare.EQUAL, clamp = BracketClamp.POSITIVE):
    #print("arg: {} factor: {} offset: {}".format(count, factor, offset))
    global bracket_count
    global target_bracket_count
    global target_bracket_compare
    global target_bracket_clamp
    bracket_count = 0
    target_bracket_count = count * factor + offset
    target_bracket_compare = compare
    target_bracket_clamp = clamp
    print("setting bracket_count target:{} compare:{} clamp:{}".format(target_bracket_count, compare, clamp))
          
def _find_index_in_context_with_brackets_old(target, context, look_left, start_index = None):
    global bracket_count
    global target_bracket_count
    global target_bracket_clamp
    global target_bracket_clamp
    
    index, token = _find_index_in_context(target, context, look_left, start_index)
    length = len(token)
    while index != -1: # target found
               
        # If bracket state before token doesn't match desired, ignore this token and try again
        context_before = (context[index+length:] if look_left else context[:index])
        brackets_before = _count_brackets(context_before, look_left, bracket_count, target_bracket_clamp)
        
        #print("token:'{}'".format(token))
        #print("context_before: {}".format(context_before))
        #print("brackets_before: {}".format(brackets_before))
        
        if  not _compare_bracket_state(brackets_before, target_bracket_count, target_bracket_compare):
            index += (-1 if look_left else length)
            index, token = _find_index_in_context(target, context, look_left, index)
            length = len(token)
            continue
                
        bracket_count = brackets_before
        return index, token
    
    brackets_in_context = _count_brackets(context, look_left, bracket_count, target_bracket_clamp)
    bracket_count = brackets_in_context
    return index, token
    
def select_argument():
    
    Key("s-home").execute()
    
    context = read_nmax_tries(5, .01, same_is_okay=True)
    if context is None:
        Key("right").execute()
    
    reset_bracket_count()
    
    index, token = _find_index_in_context_with_brackets_old("(~,", context, look_left=True)
    arg_left = (context if index==-1 else context[index + len(token):])
    arg_left = arg_left.lstrip()
    
    Key("right, left:" + str(len(arg_left))).execute()
    select_right_bounded(",~)")
    
def select_right_bounded(terminator):
    Key("s-end").execute();
    
    context = read_nmax_tries(5, .01, same_is_okay=True)
    if context is None:
        Key("left").execute()
       
    # find where the selection ends
    reset_bracket_count()
    index, token = _find_index_in_context_with_brackets_old(terminator, context, look_left=False)
    context_terminated = (context if index==-1 else context[:index])
    
    # jump over initial white space
    context_lstrip = context_terminated.lstrip()
    Key("left, right:" + str(len(context_terminated) - len(context_lstrip))).execute()
    
    # select everything except ending white space
    context_terminated = context_terminated.strip()
    Key("s-right:" + str(len(context_terminated))).execute()
    
    print("context_terminated:'{}'".format(context_terminated))

def select_left_bounded(terminator):    
    Key("s-home").execute();
    
    context = read_nmax_tries(5, .01, same_is_okay=True)
    if context is None:
        Key("right").execute()
       
    # find where the selection ends
    reset_bracket_count()
    index, token = _find_index_in_context_with_brackets_old(terminator, context, look_left=True)
    context_terminated = (context if index==-1 else context[index + len(token):])
    
    # jump over initial white space
    context_rstrip = context_terminated.rstrip()
    Key("right, left:" + str(len(context_terminated) - len(context_rstrip))).execute()
    
    # select everything except ending white space
    context_terminated = context_terminated.strip()
    Key("s-left:" + str(len(context_terminated))).execute()
    
    print("context_terminated:'{}'".format(context_terminated))
    
    
def select_more(nav_state, look_left, keep_selection=False):
    
    # make sure nothing is highlighted to boot
    if not keep_selection:
        if len(nav_state.context) > 0:
            Key("left" if look_left else "right").execute()
        else:
            Key("left, right" if look_left else "right, left").execute()
        nav_state.reset_context()
          
    # select progressively more lines to amortize cost
    nav_state.selection_size = (1 if nav_state.selection_size == 0 else min(nav_state.selection_size * 2, 8))
    #nav_state.selection_size = 1    
    for i in range(0, nav_state.selection_size):
        if look_left:
            Key("s-home, cs-left, s-left").execute()
        else:
            Key("s-end, s-right").execute()
    
    new_context = read_nmax_tries(5, .01, same_is_okay=True)
    if new_context is None:
        raise ActionError("select_more")
        
    # initialize index on fresh selection
    if nav_state.index == -1:
        nav_state.index = len(new_context)-1 if look_left else 0
    
    # offset indices to new context on expanded selection
    elif keep_selection and look_left:
        extra_length = len(new_context) - len(nav_state.context)
        nav_state.index += extra_length
        if nav_state.target_index != -1:
            nav_state.target_index += extra_length
        
    nav_state.context = new_context
    
    
    print("select _index: {} _context: {}".format(nav_state.index, nav_state.context))
    return True
    
def find_target_in_context(nav_state, target, look_left, match_brackets = True):
    print("find target: '{}' _index: {} _context: {} ".format(target, nav_state.index, nav_state.context))
    
    # start search where we left off last time
    start_index = nav_state.index
    index, token = _find_index_in_context(target, nav_state.context, look_left, start_index)
    length = len(token)
    while index != -1:
               
        # update bracket state up to the token
        context_before = (nav_state.context[index+length:start_index] if look_left else nav_state.context[start_index:index])
        brackets_before = _count_brackets(context_before, look_left, nav_state.bracket_count, nav_state.target_bracket_clamp)
        
        print("token:'{}'".format(token))
        print("context_before: {}".format(context_before))
        print("brackets_before: {}".format(brackets_before))
        
        # if bracket state before token doesn't match desired, ignore this token and try again
        if match_brackets and (not nav_state.brackets_match_target(brackets_before)):
            index += (-1 if look_left else length)
            index, token = _find_index_in_context(target, nav_state.context, look_left, index)
            length = len(token)
            continue
        
        # next search will begin after the token
        nav_state.bracket_count = brackets_before
        nav_state.index = (index - 1 if look_left else index + length)
        nav_state.target_index = index
        nav_state.target_token = token
        print("found _index: {} index: '{}' token: '{}' bracket_count:{}".format(_index, index, token, nav_state.bracket_count))
        return True
    
    context_before = (nav_state.context[:start_index] if look_left else nav_state.context[start_index:])
    brackets_before = _count_brackets(context_before, look_left, nav_state.bracket_count, nav_state.target_bracket_clamp)
    #brackets_in_context = _count_brackets(nav_state.context, look_left, nav_state.bracket_count, nav_state.target_bracket_clamp)
    #nav_state.bracket_count = brackets_in_context
    nav_state.bracket_count = brackets_before
    nav_state.index = -1 if look_left else len(nav_state.context)
    nav_state.target_index = -1
    nav_state.target_token = ""
    print("NOT found bracket_count:{}".format(nav_state.bracket_count))
    return False
        
def find_target(async_state, nav_state, direction, target, keep_selection=False, match_brackets=True):
    
    look_left = str(direction) == "left"
    did_select = False
    
    # select new context if empty
    if len(nav_state.context) == 0:
        select_more(nav_state, look_left, keep_selection)
        did_select = True
            
    # search existing context
    if ((not find_target_in_context(nav_state, target, look_left, match_brackets)) and
        (not did_select)):
    
        # if that fails expand selection and try again
        select_more(nav_state, look_left, keep_selection)
        find_target_in_context(nav_state, target, look_left, match_brackets)
        
    async_state.complete = (nav_state.target_index != -1)
        
def reach_target(async_state, nav_state, direction, move_over=False, select=False):
    
    # cache these before we reset context
    look_left = str(direction) == "left"
    index = nav_state.target_index
    length = len(nav_state.target_token)
    context_before = (nav_state.context[index+length:] if look_left else nav_state.context[:index])
    print("reaching index:{} length:{}".format(index, length))
    print("context_before:'{}'".format(context_before))
    
    # deselect context
    Key("right" if look_left else "left").execute()
    nav_state.reset_context()
    
    # move up to the target
    context_before = context_before.replace("\r\n", "\n")
    Key(("left:" if look_left else "right:") + str(len(context_before))).execute()
    
    if move_over:
        Key(("left:" if look_left else "right:") + str(length)).execute()
    elif select:
        Key(("s-left:" if look_left else "s-right:") + str(length)).execute()
           
    async_state.complete = True
    
def select_to_target(async_state, nav_state, direction):
    
    # cache these before we reset context
    look_left = str(direction) == "left"
    index = nav_state.target_index
    length = len(nav_state.target_token)
    context_before = (nav_state.context[index+length:] if look_left else nav_state.context[:index])
    print("selecting up to index:{} length:{}".format(index, length))
    print("context_before:'{}'".format(context_before))
        
    # deselect context
    Key("right" if look_left else "left").execute()
    nav_state.reset_context()
    
    # jump over initial white space
    context_before = context_before.replace("\r\n", "\n")
    context_strip = (context_before.rstrip() if look_left else context_before.lstrip())
    Key(("left:" if look_left else "right:") + str(len(context_before) - len(context_strip))).execute()
    
    # select everything except ending white space
    context_strip = context_strip.strip()
    Key(("s-left:" if look_left else "s-right:") + str(len(context_strip))).execute()
   
    async_state.complete = True
    
def action_series1(count, async_state):
    print str(count)
    print("111 iteration: {}".format(async_state.iteration))
    async_state.complete = (async_state.iteration == 2)
    
def action_series2(count, async_state):
    print str(count)
    print("222 iteration: {}".format(async_state.iteration))
    async_state.complete = (async_state.iteration == 3)
    
def test():
    try : 
        reset_context()
        reset_bracket_count()
        if find_target("right", ",~)", keep_selection=False):
            if find_target("right", ",~)", keep_selection=False):
                reach_target("right", move_over=True)
                print"A"
                if find_target("right", ",~)", keep_selection=True):
                    print"B"
                    select_to_target("right")
                    
    except Exception as e:
        print e
        pass

 
def navigate_to_character(direction3, target, fill=False, match_brackets=False):
    try:
        global bracket_count
        global target_bracket_count
        
        look_left = str(direction3) == "left"

        # make sure nothing is highlighted to boot
        if not fill:  # (except when doing "fill" -- if at end of line, there is no space for this )
            Key("right, left" if look_left else "left, right").execute()
            
        # select one line at a time
        if look_left:
            Key("s-home, s-left").execute()
        else:
            Key("s-end, s-right").execute()
        #time.sleep(1)
        
        # copy and read clipboard
        context = read_nmax_tries(5, .01, same_is_okay=True)
        if context is None:
            if look_left:
                Key("right").execute()
            else:
                Key("left").execute()
            return True
        
        # if nothing selected, must be at the start or end of line
        if len(context) == 0:
            #Key("left" if look_left else "right").execute()
            #Key("up, end" if look_left else "down, home").execute()
            Key("right, up, end" if look_left else "left, down, home").execute()
            return False
        
        # if we got to this point, we have a copy result
        print("bracket_count: {} target: {}".format(bracket_count, target_bracket_count))
        print("context: {}".format(context))
        
        index = -1
        token = ""
        length = 0
        
        if match_brackets:
            index, token = _find_index_in_context_with_brackets_old(target, context, look_left)
            length = len(token)
        else:
            index, token = _find_index_in_context(target, context, look_left)
            length = len(token)
        
        if index != -1: # target found
            '''move the cursor to the right of the context if looking left,
            to the left of the context if looking right:'''
            Key("right" if look_left else "left").execute()
            '''number of times to press left or right to reach the target
            (the target may be a part of a larger context): '''
            nt = len(context) - index - length if look_left else index
            if nt > 0:
                Key("left:" + str(nt) if look_left else "right:" + str(nt)).execute()
            '''highlight only the target'''
            if fill:
                Key("s-left:" + str(length) if look_left else "s-right:" + str(length)).execute()
            else:
                Key("left:" + str(length) if look_left else "right:" + str(length)).execute()
            return True
        else:
            Key("right, up, end" if look_left else "left, down, home").execute()
            return False
        
    except Exception:
        utilities.simple_log()


def read_nmax_tries(n, slp=0.1, same_is_okay=False):
    tries = 0
    while True:
        tries += 1
        results = read_selected_without_altering_clipboard(same_is_okay)
        error_code = results[0]
        if error_code == 0:
            return results[1]
        if tries > n:
            return None
        time.sleep(slp)


def read_selected_without_altering_clipboard(same_is_okay=False, pause_time="0"):
    '''Returns a tuple:
    (0, "text from system") - indicates success
    (1, None) - indicates no change
    (2, None) - indicates clipboard error
    '''

    time.sleep(settings.SETTINGS["miscellaneous"]["keypress_wait"]/
               1000.)  # time for previous keypress to execute
    cb = Clipboard(from_system=True)
    temporary = None
    prior_content = None
    max_tries = 20

    prior_content = Clipboard.get_system_text()
    Clipboard.set_system_text("<_error_>")
    Key("c-c").execute()
    
    for i in range(0, max_tries):
        failure = False
        try:
            Pause(pause_time).execute()
            time.sleep(settings.SETTINGS["miscellaneous"]["keypress_wait"]/
                       1000.)  # time for keypress to execute
            temporary = Clipboard.get_system_text()
            if temporary == "<_error_>":
                failure = True
                temporary = None
            
        except Exception:
            print("clipboard exception")
            failure = True
            utilities.simple_log(False)
        if not failure:
            break
        print("Clipboard Read Attempts " + str(i))  # Debugging
        if i is max_tries:
            return 2, None
    
    cb.copy_to_system()
    
    if prior_content == temporary and not same_is_okay:
        return 1, None
    return 0, temporary


def paste_string_without_altering_clipboard(content, pause_time="1"):
    '''
    True - indicates success
    False - indicates clipboard error
    '''
    time.sleep(settings.SETTINGS["miscellaneous"]["keypress_wait"]/
               1000.)  # time for previous keypress to execute
    cb = Clipboard(from_system=True)
    max_tries = 20

    for i in range(0, max_tries):
        failure = False
        try:
            Clipboard.set_system_text(unicode(content))
            Pause(pause_time).execute()
            Key("c-v").execute()
            time.sleep(settings.SETTINGS["miscellaneous"]["keypress_wait"]/
                       1000.)  # time for keypress to execute
            cb.copy_to_system()
        except Exception:
            print("Clipboard Write Attempts " + str(i))  # Debugging
            failure = True
            utilities.simple_log(False)
            if i is max_tries:
                return False
        if not failure:
            break
    return True


def fill_within_line(target, nexus):
    print("searching for: '{}'".format(target))
    result = navigate_to_character("left", str(target), True)
    if result:
        nexus.state.terminate_asynchronous(True)
    return result
	
def fill_forward(target, nexus):
    print("searching for: '{}'".format(target))
    result = navigate_to_character("right", str(target), True)
    if result:
        nexus.state.terminate_asynchronous(True)
    return result

def nav(parameters):
    result = navigate_to_character(str(parameters[0]), str(parameters[1]), fill=False, match_brackets=True)
    return result
    
def set_arg_count(count=1, factor=1):
    global arg_count
    print("setting argument count:{}".format(count))
    arg_count = count
    
def narg():
    global arg_count
    if navigate_to_character("right", ",~;", match_brackets=True) == True:
        arg_count -= 1
        if arg_count == 0:
            select_right_bounded(",~;~)")
            return True
            
    return False
    
def bark():
    global arg_count
    if navigate_to_character("left", ",~;", match_brackets=True) == True:
        arg_count -= 1
        if arg_count == 0:
            select_left_bounded("(~;~,")
            return True
    
    return False
 
def newWord(text):
    try:
        wordToAdd = read_nmax_tries(5, .01)
        print("wordToAdd:{} text: {}".format(wordToAdd, text))
        
        results = natlink.addWord("RIDEV_INPUTSINK", 0x00000001, "on")
        print("add_result:{}".format(results))
        
        info = natlink.getWordInfo("RIDEV_INPUTSINK")
        print("info:{}".format(info))
        
        pronunciations = natlink.getWordProns("RIDEV_INPUTSINK")
        print(" pronunciations:{}".format(pronunciations))
    except Exception:
        print("some exception")
        
class NavigationState:
    def __init__(self):
        self.selection_size = 0
    
        self.context = ""
        self.index = -1
        self.target_index = -1
        self.target_token = ""
        
        self.bracket_count = 0
        self.target_bracket_count = 0
        self.target_bracket_compare = BracketCompare.EQUAL
        self.target_bracket_clamp = BracketClamp.POSITIVE
        self.arg_count = 0
     
    def reset_context(self):
        self.context = ""
        self.index = -1
        self.target_index = -1
        self.target_token = ""
    
    def reset_bracket_count(self, count=0, factor=1, offset=0, compare = BracketCompare.EQUAL, clamp = BracketClamp.POSITIVE):
        #print("arg: {} factor: {} offset: {}".format(count, factor, offset))
        self.bracket_count = 0
        self.target_bracket_count = count * factor + offset
        self.target_bracket_compare = compare
        self.target_bracket_clamp = clamp
        print("setting bracket_count target:{} compare:{} clamp:{}".format(self.target_bracket_count, compare, clamp))
        
    def brackets_match_target(self, bracket_count):
        return _compare_bracket_state(bracket_count, self.target_bracket_count, self.target_bracket_compare)
     
class NavigationAction(AsyncItem):
    def __init__(self, action):
        AsyncItem.__init__(self)
        self._action = action
        self._nav_state = NavigationState()
        
    def execute(self, data=None):
        async_state = data["async_state"]
        if async_state.iteration == 0:
            self._nav_state = NavigationState()
            
        data["nav_state"] = self._nav_state
        return self._action.execute(data)
            
