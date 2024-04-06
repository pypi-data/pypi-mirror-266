from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


__all__ = ('PetrichorScriptLexer')


class PetrichorScriptLexer(RegexLexer):
    name = 'PetrichorScript'
    aliases = ['petrichor','ptcr']
    filenames = ['*.petrichor','*.ptcr']

    tokens = {
        'root': [
            (r'\s+', Text), # whitespace
            (r'\\.', String.Escape), # escaped character
            (r'//.*\n', Comment.Single),
            (r',', Punctuation),
            (r'[\{\}]', Operator),
            (r'>>', Operator),
            (r'([a-z][a-z0-9\-]*)(\s*)(:)', bygroups(Keyword.Reserved, Text, Operator)),
            (r'\[[a-z\-]+\]', Name.Variable),
            (r'"', String, 'string'),
            (r'[0-9]+', Number),
            (r'.', Text),
        ],
        'string': [
            (r'\\.', String.Escape),
            (r'"', String, '#pop'),
            (r'[^\\"]+', String),
        ]
    }
