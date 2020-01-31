from castervoice.lib.imports import *

class Alphabet(MergeRule):
    pronunciation = CCRMerger.CORE[0]
    
    mapping = {
        "[<big>] <letter>":
            R(Function(alphanumeric.letters2, extra={"big", "letter"})),
        "caps":
            R(Function(alphanumeric.set_lock_caps)), 
        "uncaps":
            R(Function(alphanumeric.set_unlock_caps)),
    }
    extras = [
        alphanumeric.get_alphabet_choice("letter"),
        Choice("big", {
            "big": True,
        }),
    ]
    defaults = {
        "big": False,
    }

#control.global_rule(Alphabet())
