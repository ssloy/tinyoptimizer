from syntree import *
from cfg import *

class IR:
    def __init__(self, prog):
        self.prog, self.fun = prog, []

    def __repr__(self):
        return self.prog + ''.join([str(f) for f in self.fun])

def ir(n):
    data  = ''.join(['@{label} = constant [{size} x i8] c"{string}\\00"\n'.format(
                    label  = label,
                    size   = len(string)+1,                               # +1 for null termination
                    string = ''.join(['\\%02x' % ord(x) for x in string]) # hex escape the string
                ) for label,string in n.deco['strings']])
    entry = n.deco['label']
    prog  = f'''declare i32 @printf(i8*, ...)
@newline = constant [ 2 x i8] c"\\0a\\00"
@integer = constant [ 3 x i8] c"%d\\00"
@string  = constant [ 3 x i8] c"%s\\00"
@bool    = constant [11 x i8] c"false\\00true\\00"
{data}
define i32 @main() {{
	call void @{entry}()
	ret i32 0
}}
'''
    ir = IR(prog)
    fun(n, ir)
    return ir

def lltype(t):
    return ['void', 'i32', 'i1'][t]

def fun(n, ir):
    label   = n.deco['label']
    args    = ', '.join([ '{t}* %{n}'   .format(n = a[0], t = lltype(a[1])) for a in n.deco['nonlocal'] ] +
                        [ '{t} %{n}.arg'.format(n = a.deco['fullname'], t = lltype(a.deco['type'])) for a in n.args ])
    rettype = lltype(n.deco['type'])
    retval  = 'ret void' if n.deco['type']==Type.VOID else 'unreachable'
    cfg = ControlFlowGraph(f'define {rettype} @{label}({args}) {{', f'\t{retval}\n}}')
    cfg.add_block('0')
    for v in n.args + n.var:
        cfg.last.instructions += [ Instruction('%{a} = alloca {t}', lltype(v.deco['type']), v.deco['fullname']) ]
    for v in n.args:
        cfg.last.instructions += [ Instruction('store {t} %{a}.arg, {t}* %{a}', lltype(v.deco['type']), v.deco['fullname']) ]
    for f in n.fun: fun(f, ir)
    for s in n.body: stat(s, cfg)
    ir.fun.append(cfg)

def stat(n, cfg):
    match n:
        case Print():
            match n.expr.deco['type']:
                case Type.INT:
                    stat(n.expr, cfg)
                    cfg.last.instructions += [ Instruction('call i32 (i8*, ...)* @printf(ptr @integer, i32 %{a})', 'i32', LabelFactory.cur_label()) ]
                case Type.BOOL:
                    stat(n.expr, cfg)
                    cfg.last.instructions += [ Instruction('%{a}.offset = select i1 %{a}, i32 6, i32 0', None, LabelFactory.cur_label()),
                                               Instruction('%{a}.ptr = getelementptr [11 x i8], ptr @bool, i32 0, i32 %{a}.offset', None, LabelFactory.cur_label()),
                                               Instruction('call i32 (i8*, ...) @printf(ptr %{a}.ptr)', None, LabelFactory.cur_label()) ]
                case Type.STRING:
                    cfg.last.instructions += [ Instruction('call i32 (i8*, ...) @printf(ptr @string, ptr @{a})', None, n.expr.deco['label']) ]
                case other: raise Exception('Unknown expression type', n.expr)
            if n.newline:
                cfg.last.instructions += [ Instruction('call i32 (i8*, ...) @printf(ptr @newline)') ]
        case Return():
            if n.expr:
                stat(n.expr, cfg)
                cfg.last.instructions += [ Instruction('ret {t} %{a}', lltype(n.expr.deco['type']), LabelFactory.cur_label()) ]
            else:
                pass
                cfg.last.instructions += [ Instruction('ret void') ]
        case Assign():
            stat(n.expr, cfg)
            cfg.last.instructions += [ Instruction('store {t} %{a}, {t}* %{b}', lltype(n.deco['type']), LabelFactory.cur_label(), n.deco['fullname']) ]
        case Integer():
            cfg.last.instructions += [ Instruction('%{a} = add i32 0, {b}', None, LabelFactory.new_label(), n.value) ] # TODO need to decide whether n.value is int or string
        case Boolean():
            cfg.last.instructions += [ Instruction('%{a} = or i1 0, {b}', None, LabelFactory.new_label(), int(n.value)) ]
        case Var():
            cfg.last.instructions += [ Instruction('%{a} = load {t}, {t}* %{b}', 'i1' if n.deco['type']==Type.BOOL else 'i32', LabelFactory.new_label(), n.deco["fullname"]) ]
        case ArithOp() | LogicOp():
            stat(n.left, cfg)
            left = LabelFactory.cur_label()
            stat(n.right, cfg)
            right = LabelFactory.cur_label()
            op = {'+':'add', '-':'sub', '*':'mul', '/':'sdiv', '%':'srem','||':'or', '&&':'and','<=':'icmp sle', '<':'icmp slt', '>=':'icmp sge', '>':'icmp sgt', '==':'icmp eq', '!=':'icmp ne'}[n.op]
            cfg.last.instructions += [ Instruction('%{a} = ' + op + ' {t} %{b}, %{c}', lltype(n.left.deco['type']), LabelFactory.new_label(), left, right) ]
        case FunCall():
            args = []
            for e in n.args:
                stat(e, cfg)
                args.append(lltype(e.deco['type']) + ' %' + LabelFactory.cur_label())
            args = ', '.join([ '{t}* %{n}'.format(n = a[0], t = lltype(a[1])) for a in n.deco['nonlocal'] ] + args) # external variable pointers + actual function parameters
            if n.deco['type']==Type.VOID:
                cfg.last.instructions += [ Instruction('call void @{a}(' + args + ')', None, n.deco['label']) ] # TODO mem2reg won't work if args are baked into the instruction
            else:
                cfg.last.instructions += [ Instruction('%{a} = call {t} @{b}(' + args + ')', lltype(n.deco['type']), LabelFactory.new_label(), n.deco['label']) ]
        case IfThenElse():
            stat(n.expr, cfg)
            label1 = LabelFactory.cur_label()
            label2 = LabelFactory.new_label()
            cfg.last.instructions += [ Instruction('br i1 %{a}, label %' + label2 + '.then, label %' + label2 + '.else', None, label1) ]
            cfg.add_block(label2 + '.then')
            for s in n.ibody:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %' + label2 + '.end') ] # TODO unbake labels
            cfg.add_block(label2 + '.else')
            for s in n.ebody:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %' + label2 + '.end') ]
            cfg.add_block(label2 + '.end')
        case While():
            label = LabelFactory.new_label()
            cfg.last.instructions += [ Instruction('br label %' + label + '.cond') ]
            cfg.add_block(label + '.cond')
            stat(n.expr, cfg)
            cfg.last.instructions += [ Instruction('br i1 %{a}, label %' + label + '.body, label %' + label + '.end', None, LabelFactory.cur_label()) ]
            cfg.add_block(label + '.body')
            for s in n.body:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %' + label + '.cond') ]
            cfg.add_block(label + '.end')
        case other: raise Exception('Unknown instruction', n)
