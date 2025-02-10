from ir import *
cfg = ControlFlowGraph('define i32 @fib(i32 %n) {', '}')
cfg.add_block('entry')
cfg.last.instructions = [
    Instruction('%{op[0]} = alloca i32', 'retval'),
    Instruction('%{op[0]} = alloca i32', 'n.addr'),
    Instruction('%{op[0]} = alloca i32', 'a'),
    Instruction('%{op[0]} = alloca i32', 'b'),
    Instruction('%{op[0]} = alloca i32', 'i'),
    Instruction('%{op[0]} = alloca i32', 'c'),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', 'n', 'n.addr'),
    Instruction('store i32 {op[0]}, ptr %{op[1]}', 0, 'a'),
    Instruction('store i32 {op[0]}, ptr %{op[1]}', 1, 'b'),
    Instruction('store i32 {op[0]}, ptr %{op[1]}', 1, 'i'),
    Instruction('store i32 {op[0]}, ptr %{op[1]}', 0, 'c'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '0', 'n.addr'),
    Instruction('%{op[0]} = icmp eq i32 %{op[1]}, {op[2]}', 'cmp', '0', 0),
    Instruction('br i1 %{op[0]}, label %{op[1]}, label %{op[2]}', 'cmp', 'if.then', 'if.end')
]

cfg.add_block('if.then')
cfg.last.instructions = [
    Instruction('store i32 {op[0]}, ptr %{op[1]}', 0, 'retval'),
    Instruction('br label %{op[0]}', 'return')
]

cfg.add_block('if.end')
cfg.last.instructions = [
    Instruction('br label %{op[0]}', 'while.cond')
]

cfg.add_block('while.cond')
cfg.last.instructions = [
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '1', 'i'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '2', 'n.addr'),
    Instruction('%{op[0]} = icmp slt i32 %{op[1]}, %{op[2]}', 'cmp1', '1', '2'),
    Instruction('br i1 %{op[0]}, label %{op[1]}, label %{op[2]}', 'cmp1', 'while.body', 'while.end')
]

cfg.add_block('while.body')
cfg.last.instructions = [
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '3', 'b'),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', '3', 'c'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '4', 'a'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '5', 'b'),
    Instruction('%{op[0]} = add i32 %{op[1]}, %{op[2]}', 'add', '4', '5'),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', 'add', 'b'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '6', 'c'),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', '6', 'a'),
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '7', 'i'),
    Instruction('%{op[0]} = add i32 %{op[1]}, {op[2]}', 'add2', '7', 1),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', 'add2', 'i'),

    Instruction('br label %{op[0]}', 'while.cond')
]

cfg.add_block('while.end')
cfg.last.instructions = [
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '8', 'b'),
    Instruction('store i32 %{op[0]}, ptr %{op[1]}', '8', 'retval'),
    Instruction('br label %{op[0]}', 'return')
]

cfg.add_block('return')
cfg.last.instructions = [
    Instruction('%{op[0]} = load i32, ptr %{op[1]}', '9', 'retval'),
    Instruction('ret i32 %{op[0]}', '9')
]
cfg.compute_adjacency()


from optimizer import *
mem2reg(cfg)
print(cfg)
