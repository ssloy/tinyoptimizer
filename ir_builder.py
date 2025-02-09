from syntree import *
from ir import *

def build_ir(n):
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
    cfg = ControlFlowGraph(f'define {rettype} @{label}({args}) {{', '}')
    cfg.add_block('entry')
    for v in n.args:
        cfg.last.instructions += [ Instruction('%{{op[0]}} = alloca {t}'.format(t=lltype(v.deco['type'])), v.deco['fullname']) ]
        cfg.last.instructions += [ Instruction('store {t} %{{op[0]}}, {t}* %{{op[1]}}'.format(t=lltype(v.deco['type'])), f'{v.deco["fullname"]}.arg', v.deco['fullname']) ]
    for v in n.var:
        cfg.last.instructions += [ Instruction('%{{op[0]}} = alloca {t}'.format(t=lltype(v.deco['type'])), v.deco['fullname']) ]
        cfg.last.instructions += [ Instruction('store {t} {{op[0]}}, {t}* %{{op[1]}}'.format(t=lltype(v.deco['type'])), 0, v.deco['fullname']) ] # zero initialized variables
    for f in n.fun: fun(f, ir)
    for s in n.body: stat(s, cfg)
    cfg.last.instructions += [ Instruction('ret void' if n.deco['type']==Type.VOID else 'unreachable') ]
    cfg.compute_adjacency()
    ir.fun.append(cfg)

def stat(n, cfg):
    match n:
        case Print():
            match n.expr.deco['type']:
                case Type.INT:
                    stat(n.expr, cfg)
                    cfg.last.instructions += [ Instruction('call i32 (i8*, ...)* @printf(ptr @integer, i32 %{op[0]})', LabelFactory.cur_label()) ]
                case Type.BOOL:
                    stat(n.expr, cfg)
                    label1 = LabelFactory.cur_label()
                    label2 = LabelFactory.new_label()
                    cfg.last.instructions += [ Instruction(f'%{label2}.offset = select i1 %{{op[0]}}, i32 6, i32 0', label1),
                                               Instruction(f'%{label2}.ptr = getelementptr [11 x i8], ptr @bool, i32 0, i32 %{label2}.offset'),
                                               Instruction(f'call i32 (i8*, ...) @printf(ptr %{label2}.ptr)') ]
                case Type.STRING:
                    label = n.expr.deco['label']
                    cfg.last.instructions += [ Instruction(f'call i32 (i8*, ...) @printf(ptr @string, ptr @{label})') ]
                case other: raise Exception('Unknown expression type', n.expr)
            if n.newline:
                cfg.last.instructions += [ Instruction('call i32 (i8*, ...) @printf(ptr @newline)') ]
        case Return():
            if n.expr:
                stat(n.expr, cfg)
                t = lltype(n.expr.deco['type'])
                cfg.last.instructions += [ Instruction(f'ret {t} %{{op[0]}}', LabelFactory.cur_label()) ]
            else:
                pass
                cfg.last.instructions += [ Instruction('ret void') ]
        case Assign():
            stat(n.expr, cfg)
            t = lltype(n.deco['type'])
            cfg.last.instructions += [ Instruction(f'store {t} %{{op[0]}}, {t}* %{{op[1]}}', LabelFactory.cur_label(), n.deco['fullname']) ]
        case Integer():
            cfg.last.instructions += [ Instruction('%{op[0]} = add i32 {op[1]}, {op[2]}', LabelFactory.new_label(), 0, n.value) ]
        case Boolean():
            cfg.last.instructions += [ Instruction('%{op[0]} = or i1 {op[1]}, {op[2]}', LabelFactory.new_label(), 0, int(n.value)) ]
        case Var():
            t = lltype(n.deco['type'])
            cfg.last.instructions += [ Instruction(f'%{{op[0]}} = load {t}, {t}* %{{op[1]}}', LabelFactory.new_label(), n.deco['fullname']) ]
        case ArithOp() | LogicOp():
            stat(n.left, cfg)
            left = LabelFactory.cur_label()
            stat(n.right, cfg)
            right = LabelFactory.cur_label()
            t = lltype(n.left.deco['type'])
            op = {'+':'add', '-':'sub', '*':'mul', '/':'sdiv', '%':'srem','||':'or', '&&':'and','<=':'icmp sle', '<':'icmp slt', '>=':'icmp sge', '>':'icmp sgt', '==':'icmp eq', '!=':'icmp ne'}[n.op]
            cfg.last.instructions += [ Instruction(f'%{{op[0]}} = {op} {t} %{{op[1]}}, %{{op[2]}}', LabelFactory.new_label(), left, right) ]
        case FunCall():
            pointers = ', '.join([ '{ptype}* %{pname}'.format(ptype=lltype(ptype), pname=pname) for pname, ptype in n.deco['nonlocal'] ]) # external variable pointers
            argline = ', '.join(['{t} %{{op[{cnt}]}}'.format(t=lltype(e.deco['type']), cnt=str(cnt)) for cnt,e in enumerate(n.args) ])    # actual function arguments
            if pointers and argline: pointers += ', '
            argnames = []
            for e in n.args:
                stat(e, cfg)
                argnames.append(LabelFactory.cur_label())
            offset = len(argnames)
            if n.deco['type']==Type.VOID:
                cfg.last.instructions += [ Instruction(f'call void @{{op[{offset}]}}({pointers}{argline})', *argnames, n.deco['label']) ]
            else:
                t = lltype(n.deco['type'])
                cfg.last.instructions += [ Instruction(f'%{{op[{offset}]}} = call {t} @{{op[{offset+1}]}}({pointers}{argline})', *argnames, LabelFactory.new_label(), n.deco['label']) ]
        case IfThenElse():
            stat(n.expr, cfg)
            label1 = LabelFactory.cur_label()
            label2 = LabelFactory.new_label()
            cfg.last.instructions += [ Instruction('br i1 %{op[0]}, label %{op[1]}, label %{op[2]}', label1, label2 + '.then', label2 + '.else') ]
            cfg.add_block(label2 + '.then')
            for s in n.ibody:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %{op[0]}', label2 + '.end') ]
            cfg.add_block(label2 + '.else')
            for s in n.ebody:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %{op[0]}', label2 + '.end') ]
            cfg.add_block(label2 + '.end')
        case While():
            label = LabelFactory.new_label()
            cfg.last.instructions += [ Instruction('br label %{op[0]}', label + '.cond') ]
            cfg.add_block(label + '.cond')
            stat(n.expr, cfg)
            cfg.last.instructions += [ Instruction('br i1 %{op[0]}, label %{op[1]}, label %{op[2]}', LabelFactory.cur_label(), label + '.body', label + '.end') ]
            cfg.add_block(label + '.body')
            for s in n.body:
                stat(s, cfg)
            cfg.last.instructions += [ Instruction('br label %{op[0]}', label + '.cond') ]
            cfg.add_block(label + '.end')
        case other: raise Exception('Unknown instruction', n)
