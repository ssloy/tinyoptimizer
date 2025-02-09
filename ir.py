class Instruction:
    def __init__(self, string, *args):
        self.string, self.op = string, args # string and parameters (typically three)

    def __repr__(self):
        return self.string.format(op = self.op)

class Phi:
    def __init__(self, reg, t, choice=None):
        self.reg, self.t, self.choice = reg, t, choice or {}

    def __repr__(self):
        choice = ', '.join([ '[{percent}{value}, %{block}]'.format(percent = '%' if type(value) is str else '', value=value, block=block) for block, value in self.choice.items() ])
        return f'%{self.reg} = phi {self.t} {choice}'

class BasicBlock:
    def __init__(self, label):
        self.label = label
        self.phi_functions, self.instructions  = [], []
        self.successors, self.predecessors = set(), set()

    def find_and_replace(self, find, replace):
        for i in self.instructions:
            i.op = list( replace if s==find else s for s in i.op )

    def __repr__(self):
        return f'{self.label}:\n' + \
                ''.join( [ f'\t{phi}\n' for phi in self.phi_functions ] ) + \
                ''.join( [ f'\t{i}\n'   for i   in self.instructions  ] )

class ControlFlowGraph:                  # a control flow graph is made of basic blocks and
    def __init__(self, header, footer):  # header + footer strings to form a valid LLVM IR program
        self.header, self.footer, self.blocks, self.last = header, footer, {}, None

    def add_block(self, label):
        self.blocks[label] = BasicBlock(label)
        self.last = self.blocks[label]   # the last block added to the CFG, heavily used by the IR builder

    def __repr__(self):
        return f'{self.header}\n' + \
               ''.join( [ f'{block}' for block in self.blocks.values() ] ) + \
               f'{self.footer}\n'

    def compute_adjacency(self):
        for b1 in self.blocks.values():
            if any('unreachable' in i.string or 'ret ' in i.string for i in b1.instructions):
                continue # even if there is a br instruction later on in the block, there are no outgoing edges
            for succ in b1.instructions[-1].op[int('br i1' in b1.instructions[-1].string):]:
                b2 = self.blocks[succ]
                b1.successors.add(b2)
                b2.predecessors.add(b1)

class IR:
    def __init__(self, prog):           # self.prog is an entry point string + data section
        self.prog, self.fun = prog, []  # self.fun is a list of control flow graphs (one per function)

    def __repr__(self):
        return self.prog + ''.join([str(f) for f in self.fun])
