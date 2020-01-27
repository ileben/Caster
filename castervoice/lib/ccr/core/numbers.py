from castervoice.lib.imports import *

class Numbers(MergeRule):
    pronunciation = CCRMerger.CORE[2]
    mapping = {
        "word number <wn>":
            R(Function(alphanumeric.word_number, extra="wn")),
        "numb [<multiplier>] <wnKK>":
            R(Function(alphanumeric.numbers2, extra="wnKK"),
              rspec="Number")*Repeat(extra="multiplier"),
        "hexa":
            R(Text("0x"))
    }
    
    extras = [
        IntegerRefST("wn", 0, 10),
        IntegerRefST("wnKK", 0, 1000000),
        Choice("multiplier", {
            "single": 1,
            "double": 2,
            "triple": 3,
            "Quadra": 4
        }),
    ]
    defaults = {
        "multiplier": 1,
    }

control.global_rule(Numbers())
