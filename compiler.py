import io, sys
from lexer import WendLexer
from parser import WendParser
from analyzer import decorate
from ir_builder import build_ir
from optimizer import *

if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
if True:
#try:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
    decorate(ast)
    ir = build_ir(ast)

    for cfg in ir.fun:
        mem2reg(cfg)

    print(ir)
#except Exception as e:
#    print(e)
