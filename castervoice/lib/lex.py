from castervoice.lib import context
from castervoice.lib.imports import *

import ctypes
import traceback
import os
import subprocess

keyword = {
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'elif' : 'ELIF',
    'def' : 'DEF',
    'return' : "RETURN",
    'try' : 'TRY',
    'except' : 'EXCEPT',
    'raise' : 'RAISE',
    'from' : 'FROM',
    'import' : 'IMPORT',
    'as' : 'AS',
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',
    'pass' : 'PASS'
    
}

tokens = [
    'NAME','STRING','THIN_STRING','NUMBER',
] + list(keyword.values())
 
t_STRING  = r'".*?"'
t_THIN_STRING  = r"'.*?'"

def t_NAME(t):
     r'[a-zA-Z_][a-zA-Z_0-9]*'
     t.type = keyword.get(t.value,'NAME')    # Check for reserved words
     return t
     
def t_NUMBER(t):
    r'\d+'
    try:
        #t.value = int(t.value)
        pass
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

def next_expression(async_state, nav_state, direction, count):     
    global lexer
    
    look_left = str(direction) == "left"
    context.select_more(nav_state, look_left, keep_selection=True)
    lexer.input(nav_state.context)
    context_length = len(nav_state.context)
    
    tokens = []
    for t in lexer:
        if (t.type == "NAME" or
            t.type == "NUMBER" or 
            t.type == "STRING" or 
            t.type == "THIN_STRING"):
            if ((not look_left and t.lexpos > 0) or 
                (look_left and t.lexpos + len(t.value) < context_length)):
                tokens.append(t)
        
    if len(tokens) >= count:
        t = tokens[-count if look_left else count-1]
        nav_state.target_index = t.lexpos
        nav_state.target_token = t.value
        async_state.complete = True
        
    #print tokens
    
    r""
    
try:
    #d = ctypes.CDLL(r"I:\Projects\Code\Source\EyeTrackingHooks\Release\EyeTrackingCLR.dll")
    d = ctypes.CDLL(r"D:\MobileDevelopment\third_party\EyeTrackingHooks\Release\EyeTrackingCLR.dll")
    d.Test2.restype = ctypes.c_char_p
    d.GetCurrentFile.restype = ctypes.c_char_p
    d.GetCurrentFolder.restype = ctypes.c_char_p
    
    d.Initialize()
    i = d.Test()
    d.Connect()
    x = d.GetX()
    y = d.GetY()
    print("x:{} y:{}".format(x, y))
    
    print("Initializing character recognition...")
    d.InitCharacterRecognition()
    print("Done.")
    
except Exception as e:
    print("Exception: {}".format(e))
    track = traceback.format_exc()
    print(track)
    
def get_gaze_position():
    global d
    x = d.GetX()
    y = d.GetY()
    print("x:{} y:{}".format(x, y))
    
def follow_gaze(enable):
    global d
    if enable:
        d.EnableFollowGaze()
    else:
        d.DisableFollowGaze()
    
def teleport_cursor():
    global d
    text = d.TeleportCursor()
    
def strafe():
    global d
    d.Strafe()
    
def orbit():
    global d
    d.Orbit()
    
def stop_moving():
    global d
    d.StopMoving()
    
def click_text(textnv):
    global d
    d.ClickText(ctypes.c_char_p(str(textnv)))
    
def touch_text(textnv):
    global d
    d.TouchText(ctypes.c_char_p(str(textnv)))
    
def test_text():
    global d
    d.TestText()
    
def test2():
    global d
    text = d.Test2()
    print("{}".format(text))
    
def get_current_file():
    global d
    text = d.GetCurrentFile()
    print("Current file: {}".format(text))
    return text
    
def get_current_folder():
    global d
    text = d.GetCurrentFolder()
    print("Current folder: {}".format(text))
    return text
    
def current_file_command(command, folder=False):
    file = get_current_folder() if folder else get_current_file()
    if len(file) > 0:
        run_detached_process(command.format(file))
        
def current_folder_command(command):
    file = get_current_folder()
    if len(file) > 0:
        run_detached_process(command.format(file))
        
def run_detached_process(command):
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS = 0x00000008
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS)
        
def zoom():
    global d
    d.Zoom()
    
def unzoom():
    global d
    d.Unzoom()
    
def zoom_push():
    global d
    d.ZoomPush()
    
