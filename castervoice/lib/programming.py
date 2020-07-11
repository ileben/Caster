from castervoice.lib.imports import *
from castervoice.lib.ccr.core.alphabet import Alphabet
from castervoice.lib.ccr.core.punctuation import RecursivePunctuation

format_dict = {
    "yell":  (1, 3),
    "title": (2, 1),
    "camel": (3, 1),
    "snake": (5, 3),
    "sing":  (4, 0),
    "say":   (5, 0)
}

def format_text(format, text):
    textformat.master_format_text(capitalization=format[0], spacing=format[1], textnv=text)

# By default process_recognition Is only called on the top level rule in the recognition.
# This rule recursively calls process_recognition on all of the nested rules
class RecursiveRule(CompoundRule):
        
    def process_recognition(self, node):
        self.process_node(node)
        
    def process_node(self, node):
        if isinstance(node.actor, RuleRef):
            rule = node.children[0].actor
            rule.process_recognition(node.children[0])
        else:
            for child in node.children:
                self.process_node(child)
        
    
class TextFormatting(MappingRule):
    mapping = {
        "<format> <text>":
            R(Function(format_text)),
        #"<format>":
            #R(Text("Formatting")),
    }
    extras = [
        Dictation("text", format=False),
        Choice("format", format_dict),
    ]
    
class Spelling(RecursiveRule):
    spec = "spell <letters>"
    extras = [
        Repetition(RuleRef(Alphabet()), max=20, name="letters"),
    ]
    
class ProgrammingOptions(RecursiveRule):
    spec = "<TextFormatting> | <Spelling> | <Punctuation>"
    extras = [
        RuleRef(TextFormatting(), name="TextFormatting"),
        RuleRef(Spelling(), name="Spelling"), 
        RuleRef(RecursivePunctuation(), name="Punctuation")
    ]
    
class Programming(RecursiveRule):
    spec = "<ProgrammingOptions>"
    extras = [
        Repetition(RuleRef(ProgrammingOptions()), name="ProgrammingOptions", max=20),
    ]
    
# Including dictation in a grammar weakens the recognition of everything else, such as spelling.
# This can be avoided by moving the speed/accuracy slider in Dragon further up towards accuracy
# but that makes everything much slower. This rule here is a workaround to improve accuracy
# when you're only using spelling and punctuation. For this to work it has to be in a separate grammar.
class NoDictProgrammingOptions(RecursiveRule):
    spec = "<Spelling> | <Punctuation>"
    extras = [
        RuleRef(TextFormatting(), name="TextFormatting"),
        RuleRef(Spelling(), name="Spelling"), 
        RuleRef(RecursivePunctuation(), name="Punctuation")
    ]
    
class NoDictProgramming(RecursiveRule):
    spec = "<ProgrammingOptions>"
    extras = [
        Repetition(RuleRef(NoDictProgrammingOptions()), name="ProgrammingOptions", max=20),
    ]
    
# This is for when you really want to make sure that everything is recognized as a literal word
class JustDictation(MappingRule):
    mapping = {
        "dictate <text>":
            R(Text("%(text)s")),
    }
    extras = [
        Dictation("text"),
    ]

grammar = Grammar("ProgrammingWithoutDictation")
grammar.add_rule(NoDictProgramming())
grammar.load()

grammar = Grammar("Programming")
grammar.add_rule(Programming())
grammar.load()

grammar = Grammar("JustDictation")
grammar.add_rule(JustDictation())
grammar.load()

