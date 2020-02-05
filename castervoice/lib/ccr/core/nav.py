'''
Created on Sep 1, 2015

@author: synkarius
'''
from castervoice.lib.imports import *
from dragonfly.actions.action_mimic import Mimic
from castervoice.lib.ccr.standard import SymbolSpecs
from castervoice.lib.ccr.core.punctuation import text_punc_dict, double_text_punc_dict
from castervoice.lib.alphanumeric import caster_alphabet
from castervoice.lib.context import BracketClamp
from castervoice.lib.context import NavigationAction
from castervoice.lib import lex

_NEXUS = control.nexus()

for key, value in double_text_punc_dict.items():
    if len(value) == 2:
        double_text_punc_dict[key] = value[0] + "~" + value[1]
    elif len(value) == 4:
        double_text_punc_dict[key] = value[0:1] + "~" + value[2:3]
    else:
        raise Exception(
            "Need to deal with nonstandard pair length in double_text_punc_dict.")

capitalization_dict = {
    "yell": 1,
    "title": 2,
    "camel": 3,
    "sing": 4,
    "laws": 5
}

spacing_dict = {
    "gum": 1,
    "gun": 1,
    "spine": 2,
    "snake": 3,
    "pebble": 4,
    "incline": 5,
    "dissent": 6,
    "descent": 6
}
        
class NavigationNon(MergeRule):
    mapping = {
        "new word <text>":
            R(Function(context.newWord)),
        "<direction> <time_in_seconds>":
            AsynchronousAction([L(S(["cancel"], Key("%(direction)s"), consume=False))],
                               repetitions=1000,
                               blocking=False),
        "erase multi clipboard":
            R(Function(navigation.erase_multi_clipboard, nexus=_NEXUS)),
        'save':
            R(Key("c-s"), rspec="save"),
        "find":
            R(Key("c-f")),
        "find next [<n>]":
            R(Key("f3"))*Repeat(extra="n"),
        "find prior [<n>]":
            R(Key("s-f3"))*Repeat(extra="n"),
        "find everywhere":
            R(Key("cs-f")),
        "replace":
            R(Key("c-h")),
        "(F to | F2)":
            R(Key("f2")),
        "(F six | F6)":
            R(Key("f6")),
        "(F nine | F9)":
            R(Key("f9")),
        "[show] context menu":
            R(Key("s-f10")),
        "lean":
            R(Function(navigation.right_down, nexus=_NEXUS)),
        "hoist":
            R(Function(navigation.right_up, nexus=_NEXUS)),
        "kick mid":
            R(Function(navigation.middle_click, nexus=_NEXUS)),
        "shift right click":
            R(Key("shift:down") + Mouse("right") + Key("shift:up")),
        #"curse <direction> [<direction2>] [<nnavi500>] [<dokick>]":
            #R(Function(navigation.curse)),
        "curse":
            R(Function(lex.follow_gaze, enable=True)),
        "uncurse":
            R(Function(lex.follow_gaze, enable=False)),
        "scree <direction> [<nnavi500>]":
            R(Function(navigation.wheel_scroll)),
        "fly [<nnavi500>]":
            R(Function(lex.follow_gaze, enable=False)) + 
            R(Function(navigation.wheel_scroll, direction="up")),
        "dive [<nnavi500>]":
            R(Function(lex.follow_gaze, enable=False)) + 
            R(Function(navigation.wheel_scroll, direction="down")),
        "colic":
            R(Key("control:down") + Mouse("left") + Key("control:up")),
        #"garb [<nnavi500>]":
            #R(
                #Mouse("left") + Mouse("left") +
                #Function(navigation.stoosh_keep_clipboard, nexus=_NEXUS)),
        #"drop [<nnavi500>]":
            #R(
                #Mouse("left") + Mouse("left") + Function(navigation.drop_keep_clipboard,
                                                         #nexus=_NEXUS,
                                                         #capitalization=0,
                                                         #spacing=0)),
        "sure stoosh":
            R(Key("c-c")),
        "sure cut":
            R(Key("c-x")),
        "sure spark":
            R(Key("c-v")),
        "refresh":
            R(Key("c-r")),
        # window management
        "minimize":
            R(Function(lambda: Window.get_foreground().minimize())),
        "maximize":
            R(Function(lambda: Window.get_foreground().maximize())),
        "remax":
            R(Key("a-space/10,r/10,a-space/10,x")),
        "maxiwin":
            R(Key("w-up")),
        "close window":
            R(Key("a-f4")),
        "move window":
            R(Key("a-space, r, a-space, m")),
        "window (left | lease) [<n>]":
            R(Key("w-left"))*Repeat(extra="n"),
        "window (right | ross) [<n>]":
            R(Key("w-right"))*Repeat(extra="n"),
        "monitor (left | lease) [<n>]":
            R(Key("sw-left"))*Repeat(extra="n"),
        "monitor (right | ross) [<n>]":
            R(Key("sw-right"))*Repeat(extra="n"),
        "(next | prior) window":
            R(Key("ca-tab, enter")),
        #"switch [window | windows]":
        "altar|alter [<nnavi10>]":
            R(Key("alt:down, tab/20:%(nnavi10)d, alt:up"), rdescript="Core: switch to most recent Windows"),
        "Wendy|windy":
            R(Key("ca-tab"))*Repeat(extra="n"),
        #"next tab [<n>]":
        "nexxy [<n>]":
            R(Key("c-pgdown"))*Repeat(extra="n"),
        #"prior tab [<n>]":
        "proxy [<n>]":
            R(Key("c-pgup"))*Repeat(extra="n"),
        "close tab [<n>]":
            R(Key("c-w/20"))*Repeat(extra="n"),
        "elite translation <text>":
            R(Function(alphanumeric.elite_text)),

        # Workspace management
        "show work [spaces]":
            R(Key("w-tab")),
        "(create | new) work [space]":
            R(Key("wc-d")),
        "close work [space]":
            R(Key("wc-f4")),
        "close all work [spaces]":
            R(Function(utilities.close_all_workspaces)),
        "next work [space] [<n>]":
            R(Key("wc-right"))*Repeat(extra="n"),
        "(previous | prior) work [space] [<n>]":
            R(Key("wc-left"))*Repeat(extra="n"),
        "go work [space] <n>":
            R(Function(lambda n: utilities.go_to_desktop_number(n))),
        "send work [space] <n>":
            R(Function(lambda n: utilities.move_current_window_to_desktop(n))),
        "move work [space] <n>":
            R(Function(lambda n: utilities.move_current_window_to_desktop(n, True))),
    }

    extras = [
        Dictation("text"),
        Dictation("mim"),
        IntegerRefST("n", 1, 50),
        IntegerRefST("nnavi10", 1, 11),
        IntegerRefST("nnavi500", 1, 500),
        Choice("time_in_seconds", {
            "super slow": 5,
            "slow": 2,
            "normal": 0.6,
            "fast": 0.1,
            "superfast": 0.05
        }),
        navigation.get_direction_choice("direction"),
        navigation.get_direction_choice("direction2"),
        navigation.TARGET_CHOICE,
        Choice("dokick", {
            "kick": 1,
            "psychic": 2
        }),
        Choice("wm", {
            "ex": 1,
            "tie": 2
        }),
    ]
    defaults = {
        "n": 1,
        "mim": "",
        "nnavi10": 1,
        "nnavi500": 1,
        "direction2": "",
        "dokick": 0,
        "text": "",
        "wm": 2
    }


class Navigation(MergeRule):
    non = NavigationNon
    pronunciation = CCRMerger.CORE[1]

    mapping = {
        "test":
            #R(Function(context.test)),
            R(Function(lex.get_gaze_position)),
        "testy testy":
            R(Function(lex.test2)),
        "zoom in|zooming|enhance":
            R(Function(lex.zoom)),
        "follow gaze":
            R(Function(lex.follow_gaze, enable=True)),
        "unfollow gaze":
            R(Function(lex.follow_gaze, enable=False)),
        # "periodic" repeats whatever comes next at 1-second intervals until "terminate"
        # or "escape" (or your SymbolSpecs.CANCEL) is spoken or 100 tries occur
        "periodic":
            ContextSeeker(forward=[
                L(
                    S(["cancel"], lambda: None),
                    S(["*"],
                      lambda fnparams: UntilCancelled(
                          Mimic(*filter(lambda s: s != "periodic", fnparams)), 1).execute(
                          ),
                      use_spoken=True))
            ]),
        # VoiceCoder-inspired -- these should be done at the IDE level
        "backfill <textnv>":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, {"textnv":"target"}, direction="left", match_brackets=False) +
                               AsyncFunction(context.reach_target, direction="left", select=True)
                               )))], time_in_seconds=0, repetitions=10),
        "(fill|feel) <textnv>":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, {"textnv":"target"}, direction="right", match_brackets=False) +
                               AsyncFunction(context.reach_target, direction="right", select=True)
                               )))], time_in_seconds=0, repetitions=10),
        "leaf [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(lex.next_expression, {"nnavi10":"count"}, direction="left") +
                               AsyncFunction(context.reach_target, direction="left", select=True)
                               )))], time_in_seconds=0, repetitions=10),
        "reef [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(lex.next_expression, {"nnavi10":"count"}, direction="right") +
                               AsyncFunction(context.reach_target, direction="right", select=True)
                               )))], time_in_seconds=0, repetitions=10),
        "narg [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="right", target=",")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="right", move_over=True) +
                               AsyncFunction(context.find_target, direction="right", target=",~)", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="right")
                               )))], time_in_seconds=0, repetitions=10),
        "bark [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target=",")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="left", move_over=True) +
                               AsyncFunction(context.find_target, direction="left", target="(~,", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="left")
                               )))], time_in_seconds=0, repetitions=10),
        "shackle bracket [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target="(~[~{") +
                               AsyncFunction(context.reach_target, direction="left") +
                               AsyncFunction(context.find_target, direction="right", target=")~]~}", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="right")
                               )))], time_in_seconds=0, repetitions=10),
        "shackle argument":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target="(~,") +
                               AsyncFunction(context.reach_target, direction="left") +
                               AsyncFunction(context.find_target, direction="right", target=",~)", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="right")
                               )))], time_in_seconds=0, repetitions=10),
        "(jump in|jumping) [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="right", target="(~[~{")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="right", move_over=True) +
                               AsyncFunction(context.find_target, direction="right", target=",~;~]~)~}", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="right")
                               )))], time_in_seconds=0, repetitions=10),
        "jump out [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="right", target=")~]~}")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="right", move_over=True)
                               )))], time_in_seconds=0, repetitions=10),
        "bounce out [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target="(~[~{")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="left", move_over=True)
                               )))], time_in_seconds=0, repetitions=10),
        "(bounce in|bouncing) [<nnavi10>]":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target=")~]~}")*AsyncRepeat(extra="nnavi10") +
                               AsyncFunction(context.reach_target, direction="left", move_over=True) +
                               AsyncFunction(context.find_target, direction="left", target=",~;~[~(~{", keep_selection=True) +
                               AsyncFunction(context.select_to_target, direction="left")
                               )))], time_in_seconds=0, repetitions=10),
        "jump over":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="right", target="(~[~{") +
                               AsyncFunction(context.find_target, direction="right", target=")~]~}") +
                               AsyncFunction(context.reach_target, direction="right", move_over=True)
                               )))], time_in_seconds=0, repetitions=50),
        "bounce over":
            AsynchronousAction([L(S(["cancel"], NavigationAction(
                               AsyncFunction(context.find_target, direction="left", target=")~]~}") +
                               AsyncFunction(context.find_target, direction="left", target="(~[~{") +
                               AsyncFunction(context.reach_target, direction="left", move_over=True)
                               )))], time_in_seconds=0, repetitions=50),
        # keyboard shortcuts
        '(shock|Shaw|show) [<nnavi50>]':
            R(Key("enter"), rspec="shock")*Repeat(extra="nnavi50"),
        # "(<mtn_dir> | <mtn_mode> [<mtn_dir>]) [(<nnavi500> | <extreme>)]":
        #     R(Function(text_utils.master_text_nav)), # this is now implemented below
        "shift click":
            R(Key("shift:down") + Mouse("left") + Key("shift:up")),
        "copy [<nnavi500>]":
            R(Function(navigation.stoosh_keep_clipboard, nexus=_NEXUS), rspec="copy"),
        "cut [<nnavi500>]":
            R(Function(navigation.cut_keep_clipboard, nexus=_NEXUS), rspec="cut"),
        "cut line":
            R(Key("end, s-home/5, c-x/5, s-home/5, backspace, backspace")),
        "blank above [<nnavi50>]":
            R(Key("left, right, end, home") + Key("enter, up")*Repeat(extra="nnavi50"), rspec="blank above"),
        "blank below [<nnavi50>]":
            R(Key("right, left, end, enter:%(nnavi50)d"), rspec="blank above"),
        "paste above":
            R(Key("left, right, end, home, enter, up, end") +
              Function(navigation.drop_keep_clipboard, nexus=_NEXUS), rspec="paste above"),
        "paste below [<below_left>]":
            R(Key("right, left, end, enter, s-tab:%(below_left)d") +
              Function(navigation.drop_keep_clipboard, nexus=_NEXUS), rspec="paste below"),
        "paste [<nnavi500>] [(<capitalization> <spacing> | <capitalization> | <spacing>) [(bow|bowel)]]":
            R(Function(navigation.drop_keep_clipboard, nexus=_NEXUS), rspec="paste"),
        #"splat [<splatdir>] [<nnavi10>]":
        "slap [<splatdir>] [<nnavi10>]":
            R(Key("c-%(splatdir)s"), rspec="splat")*Repeat(extra="nnavi10"),
        "nuke line [<nnavi10>]":
            R(Key("end, s-home/5, s-home/5, del, del"))*Repeat(extra="nnavi10"),
        "nuke above [<nnavi10>]":
            R(Key("up, end, s-home/5, s-home/5, del, del, home"))*Repeat(extra="nnavi10"),
        "nuke below [<nnavi10>]":
            R(Key("down, end, s-home/5, s-home/5, backspace, backspace, home"))*Repeat(extra="nnavi10"),
        "nuke empty [<nnavi10>]":
            R(Key("s-home/5, del, del, end"))*Repeat(extra="nnavi10"),
        "nuke empty above [<nnavi10>]":
            R(Key("end, up, s-home/5, del, del, home"))*Repeat(extra="nnavi10"),
        "nuke empty below [<nnavi10>]":
            R(Key("end, down, s-home/5, backspace, backspace, home"))*Repeat(extra="nnavi10"),
        "deli [<nnavi50>]":
            R(Key("del/5"), rspec="deli")*Repeat(extra="nnavi50"),
        #"clear [<nnavi50>]":
		"becky [<nnavi50>]":
            R(Key("backspace/5:%(nnavi50)d"), rspec="back"),
        SymbolSpecs.CANCEL:
            R(Key("escape"), rspec="cancel"),
        "chain":
            R(Key("c-left, cs-right"), rspec="chain"),
        "shackle":
            R(Key("end, s-home"), rspec="shackle"),
        #"(tell | tau) <semi>":
        #    R(Function(navigation.next_line), rspec="tell dock"),
        "duple [<nnavi50>]":
            R(Function(navigation.duple_keep_clipboard), rspec="duple"),
        "Kraken":
            R(Key("c-space"), rspec="Kraken"),
        "(undo|negate) [<nnavi10>]":
            R(Key("c-z"))*Repeat(extra="nnavi10"),
        "redo [<nnavi10>]":
            R(
                ContextAction(default=Key("c-y")*Repeat(extra="nnavi10"),
                              actions=[
                                  (AppContext(executable=["rstudio", "foxitreader"]),
                                   Key("cs-z")*Repeat(extra="nnavi10")),
                              ])),

        # text formatting
        #"set [<big>] format (<capitalization> <spacing> | <capitalization> | <spacing>) [(bow|bowel)]":
            #R(Function(textformat.set_text_format)),
        #"clear castervoice [<big>] formatting":
            #R(Function(textformat.clear_text_format)),
        #"peek [<big>] format":
            #R(Function(textformat.peek_text_format)),
        # moved to a separate rule below
        #"(<capitalization> <spacing> | <capitalization> | <spacing>) [(bow|bowel)] <textnv> [brunt]":
        #    R(Function(textformat.master_format_text)),
        "convert format (<capitalization> <spacing> | <capitalization> | <spacing>)":
            R(Function(textformat.convert_format)),
        #"[<big>] format <textnv>":
            #R(Function(textformat.prior_text_format)),
        #"<word_limit> [<big>] format <textnv>":
            #R(Function(textformat.partial_format_text)),
        "hug <enclosure>":
            R(Function(text_utils.enclose_selected)),

        # Ccr Mouse Commands
        "(kick|push) [<nnavi3>]":
            R(Function(lex.follow_gaze, enable=False))+
            R(Function(navigation.left_click, nexus=_NEXUS))*Repeat(extra="nnavi3"),
        "(fly kick) [<nnavi3>]":
            R(Function(lex.teleport_cursor))+
            R(Function(navigation.left_click, nexus=_NEXUS))*Repeat(extra="nnavi3"),
        "psychic":
            R(Function(lex.follow_gaze, enable=False))+
            R(Function(navigation.right_click, nexus=_NEXUS)),
        "(kick double|double kick|double push)":
            R(Function(lex.follow_gaze, enable=False))+
            R(Function(navigation.left_click, nexus=_NEXUS)*Repeat(2)),
        "squat":
            R(Function(navigation.left_down, nexus=_NEXUS))+
            R(Function(lex.unzoom)),
        "bench":
            R(Function(lex.follow_gaze, enable=False))+
            R(Function(navigation.left_up, nexus=_NEXUS)),

        # keystroke commands
        "<direction> [<nnavi500>]":
            R(Key("%(direction)s")*Repeat(extra='nnavi500'), rdescript="arrow keys"),
		"home [<nnavi10>]":
            R(Key("home:%(nnavi10)s")),
		"(end | and) [<nnavi10>]":
            R(Key("end:%(nnavi10)s")),
		"whoops [<nnavi10>]":
			R(Key("s-home, s-home, s-up:%(nnavi10)s")),
		"dupes [<nnavi10>]":
			R(Key("s-end, s-down:%(nnavi10)s, s-end")),
        #"sauce wally [<nnavi10>]":
            #R(Key("c-home:%(nnavi10)s")),
        #"dunce wally [<nnavi10>]":
            #R(Key("c-end:%(nnavi10)s")),
        "loom [<nnavi500>]":
            R(Key("c-left:%(nnavi500)s")),
        "rush [<nnavi500>]":
            R(Key("c-right:%(nnavi500)s")),
        #"lease [<nnavi500>]":
            #R(Key("s-left:%(nnavi500)s")),
        #"ross [<nnavi500>]":
            #R(Key("s-right:%(nnavi500)s")),
        "(lick | leak) [<nnavi500>]":
            R(Key("cs-left:%(nnavi500)s")),
        "rock [<nnavi500>]":
            R(Key("cs-right:%(nnavi500)s")),
        "<modifier> <button_dictionary_500> [<nnavi500>]":
            R(Key("%(modifier)s%(button_dictionary_500)s")*Repeat(extra='nnavi500'),
              rdescript="press modifier keys plus buttons from button_dictionary_500"),
        "<modifier> <button_dictionary_10> [<nnavi10>]":
            R(Key("%(modifier)s%(button_dictionary_10)s")*Repeat(extra='nnavi10'),
              rdescript="press modifier keys plus buttons from button_dictionary_10"),
        "<modifier> <button_dictionary_1>":
              R(Key("%(modifier)s%(button_dictionary_1)s"),
              rdescript="press modifiers plus buttons from button_dictionary_1, non-repeatable"),

        # "key stroke [<modifier>] <combined_button_dictionary>":
        #     R(Text('Key("%(modifier)s%(combined_button_dictionary)s")')),

        # "key stroke [<modifier>] <combined_button_dictionary>":
        #     R(Text('Key("%(modifier)s%(combined_button_dictionary)s")')),
    }
    tell_commands_dict = {"dock": ";", "doc": ";", "sink": "", "com": ",", "deck": ":"}
    tell_commands_dict.update(text_punc_dict)

    # I tried to limit which things get repeated how many times in hopes that it will help prevent the bad grammar error
    # this could definitely be changed. perhaps some of these should be made non-CCR
    button_dictionary_500 = {
        "(tab | tabby)": "tab",
        "(backspace | clear)": "backspace",
        "(delete|deli)": "del",
        "(escape | cancel)": "escape",
        "(enter | shock)": "enter",
        "(left | lease)": "left",
        "(right | ross)": "right",
        "(up | sauce)": "up",
        "(down | dunce)": "down",
        "page (down | dunce)": "pgdown",
        "page (up | sauce)": "pgup",
        "space": "space"
    }
    button_dictionary_10 = {
        "function {}".format(i): "f{}".format(i)
        for i in range(1, 10)
    }
    button_dictionary_10.update(caster_alphabet)
    button_dictionary_10.update(text_punc_dict)
    longhand_punctuation_names = {
        "minus": "hyphen",
        "hyphen": "hyphen",
        "comma": "comma",
        "deckle": "colon",
        "colon": "colon",
        "slash": "slash",
        "backslash": "backslash"
    }
    button_dictionary_10.update(longhand_punctuation_names)
    button_dictionary_1 = {
        "(home | lease wally | latch)": "home",
        "(end | ross wally | ratch)": "end",
        "insert": "insert",
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9"
    }
    combined_button_dictionary = {}
    for dictionary in [button_dictionary_1, button_dictionary_10, button_dictionary_500]:
        combined_button_dictionary.update(dictionary)

    modifier_choice_object = Choice("modifier", {
            #"(control | fly)": "c-", #TODO: make DRY
            "control": "c-",
            "(shift | shin)": "s-",
            "alt": "a-",
            "(control shift | que)": "cs-",
            "control alt": "ca-",
            "(shift alt | alt shift)": "sa-",
            "(control alt shift | control shift alt)": "csa-",  # control must go first
            "windows": "w-",  # windows should go before alt/shift
            "control windows": "cw-",
            "control windows alt": "cwa-",
            "control windows shift": "cws-",
            "windows shift alt": "wsa-",
            "windows alt shift": "was-",
            "windows shift": "ws-",
            "windows alt": "wa-",
            "control windows alt shift": "cwas-",
            "hit": "",
        })
    extras = [
        IntegerRefST("nnavi10", 1, 11),
        IntegerRefST("nnavi3", 1, 4),
        IntegerRefST("nnavi50", 1, 50),
        IntegerRefST("nnavi500", 1, 500),
        Dictation("textnv"),
        Choice("enclosure", double_text_punc_dict),
        Choice("direction", {
            #"dunce": "down",
            #"sauce": "up",
            "duck|doc|dog": "down",
            "neck|Nick": "up",
            "lease": "left",
            "ross": "right",
            #"down": "down",
            #"up": "up",
            #"left": "left",
            #"right": "right",
        }),
        modifier_choice_object,
        Choice("button_dictionary_1", button_dictionary_1),
        Choice("button_dictionary_10", button_dictionary_10),
        Choice("button_dictionary_500", button_dictionary_500),
        Choice("combined_button_dictionary", combined_button_dictionary),

        Choice("capitalization", capitalization_dict),
        Choice("spacing", spacing_dict),
        Choice("semi", tell_commands_dict),
        Choice("word_limit", {
            "single": 1,
            "double": 2,
            "triple": 3,
            "Quadra": 4
        }),
        navigation.TARGET_CHOICE,
        navigation.get_direction_choice("mtn_dir"),
        Choice("mtn_mode", {
            "shin": "s",
            "queue": "cs",
            "fly": "c",
        }),
        Choice("extreme", {
            "Wally": "way",
        }),
        Choice("big", {
            "big": True,
        }),
        Choice("splatdir", {
            "lease": "backspace",
            "ross": "delete",
        }),
        Choice("below_left", {
            "left": 1,
        })
    ]

    defaults = {
        "nnavi500": 1,
        "nnavi50": 1,
        "nnavi10": 1,
        "nnavi3": 1,
        "textnv": "",
        "capitalization": 0,
        "spacing": 0,
        "mtn_mode": None,
        "mtn_dir": "right",
        "extreme": None,
        "big": False,
        "splatdir": "backspace",
        "modifier": "",
        "below_left": 0,
    }

	
control.global_rule(Navigation())

class Reuse(MappingRule):
    mapping = {
        "(<capitalization> <spacing> | <capitalization> | <spacing>) [(bow|bowel)] <textnv>":
            R(Function(textformat.master_format_text)),
        #"reuse <textnv>":
        #    R(Function(textformat.master_format_text, spacing="snake", capitalization="laws")),
    }
    
    extras = [
        Dictation("textnv"),
        Choice("capitalization", capitalization_dict),
        Choice("spacing", spacing_dict),
    ]
    defaults = {
        "capitalization": 0,
        "spacing": 0,
    }
    
class JustDictation(MappingRule):
    mapping = {
        "say <text>":
            R(Text("%(text)s")),
    }
    
    extras = [
        Dictation("text"),
    ]
    
grammar = Grammar("EveryUseGrammar")
grammar.add_rule(Reuse())
grammar.add_rule(JustDictation())
grammar.load()