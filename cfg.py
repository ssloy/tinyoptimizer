class Instruction:
    def __init__(self, string, *args):
        self.string, self.op = string, args # string and (typically three) parameters

    def __repr__(self):
        return self.string.format(op = self.op)

class Phi:
    def __init__(self, reg, choice=None):
        self.reg, self.choice = reg, choice or {}

    def __repr__(self):
        choice = ', '.join([ f'[{value}, {block}]' for block, value in self.choice.items() ])
        return f'{self.reg} = phi {choice}'

class BasicBlock:
    def __init__(self, label):
        self.label = label
        self.phi_functions, self.instructions  = [], []
        self.successors, self.predecessors = set(), set()

    def find_and_replace(self, find, replace):
        for i in self.instructions:
            i.a, i.b, i.c = ( replace if s==find else s for s in (i.a, i.b, i.c) )

    def __repr__(self):
        return f'{self.label}:\n' + \
                ''.join( [ f'\t{phi}\n' for phi in self.phi_functions ] ) + \
                ''.join( [ f'\t{i}\n'   for i   in self.instructions  ] )

class ControlFlowGraph:
    def __init__(self, header, footer):
        self.header, self.footer, self.blocks, self.last = header, footer, {}, None

    def add_block(self, label):
        self.blocks[label] = BasicBlock(label)
        self.last = self.blocks[label]

    def __repr__(self):
        return f'{self.header}\n' + \
               ''.join( [ f'{block}' for block in self.blocks.values() ] ) + \
               f'{self.footer}\n'
