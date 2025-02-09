from ir import *

class Optimizer:
    def __init__(self, cfg):
        self.cfg, self.entry = cfg, cfg.blocks['entry']
        self.reachable, self.postorder = set(), []  # for efficiency reasons, we visit blocks in a way that ensures
        self.dfs(self.entry)                        # processing of each block after its predecessors have been processed

    def dfs(self, block):
        self.reachable.add(block)
        for b in block.successors:
            if b not in self.reachable: self.dfs(b)
        self.postorder.append(block)

    def dominators(self):                       # the iterative dominator algorithm [Cooper, Harvey and Kennedy, 2006]
        dom = { b : set(self.cfg.blocks.values()) for b in self.cfg.blocks.values() }
        dom[ self.entry ] = { self.entry }
        changed = True
        while changed:
            changed = False
            for b in self.postorder[-2::-1]:    # for all blocks (except the source) in reverse postorder
                new_dom = set.intersection(*[ dom[p] for p in b.predecessors ]) | { b }
                changed = dom[b] != new_dom
                dom[b]  = new_dom
        return dom                              # dom[b] contains every block that dominates b

    def immediate_dominators(self):
        dom = self.dominators()
        idom = { self.entry : None }                                # idom[b] contains exactly one block, the immediate dominator of b
        for b in self.postorder[-2::-1]:                            # reverse or not we do not care here, but do not visit the source block
            idom[b] = max(dom[b] - {b}, key=lambda x: len(dom[x]))  # immediate dominator is the one with the maximum number of dominators (except the block itself)
        return idom

    def dominance_frontiers(self):
        idom = self.immediate_dominators()
        df = { b : set() for b in self.reachable }
        for b in filter(lambda x: len(x.predecessors)>1, self.reachable): # iterate through junction points among reachable blocks
            for p in b.predecessors:
                runner = p
                while runner != idom[b]:
                    df[runner].add(b)
                    runner = idom[runner]
        return df

class mem2reg(Optimizer):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.allocas = self.remove_promotable_allocas()
        self.place_phi()
        stack = [{}] # stack of maps (variable -> value); necessary for storing context while branching
        self.remove_store_load(self.entry, None, set(), stack)

    def remove_promotable_allocas(self):
        allocas = { i.op[0] : i.string.split()[-1] for i in self.entry.instructions if 'alloca' in i.string } # find all allocas in the entry block
        for v in allocas.copy().keys():             # for every variable
            for b in self.reachable:
                for i in b.instructions:            # for every instruction in the CFG
                    if f'* %{v}' in i.string:       # if we find a funcall with a reference to the variable
                        allocas.pop(v, None)        # then the variable is not promotable
        for i in self.entry.instructions[:]:
            if 'alloca' in i.string and i.op[0] in allocas:
                self.entry.instructions.remove(i)   # remove promotable allocas
        return allocas # variable name -> type dictionary

    def place_phi(self):                                        # Fig 9.9b in [Cooper and Torczon, Engineering a Compiler Broché]
        df = self.dominance_frontiers()
        phi_places = { v:set() for v in self.allocas.keys() }   # map (variable -> set of basic blocks)
        for v in self.allocas.keys():
            blocks_with_store = { b for b in self.reachable for i in b.instructions if 'store' in i.string and i.op[1]==v }
            blocks_to_consider = blocks_with_store.copy()
            while blocks_to_consider:
                block = blocks_to_consider.pop()
                for frontier in df[block]:
                    if frontier in phi_places[v]: continue
                    phi_places[v].add(frontier)
                    blocks_to_consider.add(frontier)
        for v, bb in phi_places.items():                        # insert phi nodes (for the moment without choices)
            for b in bb:
                b.phi_functions.append(Phi(v + '_' + b.label, self.allocas[v]))

    def remove_store_load(self, block, prev, visited, stack):
        def find_variable(v, stack):                # walk the stack back until
            for frame in reversed(stack):           # the current variable instance is found
                if v in frame: return frame[v]      # N.B. we suppose that the variables were initialized explicitly

        for phi in block.phi_functions:             # place phi node choice for the current path
            v = phi.reg[:-len(block.label)-1]       # phi saves the choice into a register named foo_bar, where foo is the name of the variable, and bar is the name of the basic block
            val = find_variable(v, stack)
            phi.choice[prev.label] = val
            stack[-1][v] = phi.reg

        if block in visited: return                 # we need to revisit blocks with phi functions as many times as we have incoming edges,
        visited.add(block)                          # therefore the visited check is made after the choice placement

        for i in block.instructions[:]:             # iterate through a copy since we modify the list
            if 'load' in i.string and i.op[1] in self.allocas:
                val = find_variable(i.op[1], stack)
                block.instructions.remove(i)
                block.find_and_replace(i.op[0], val)
            elif 'store' in i.string and i.op[1] in self.allocas:
                stack[-1][i.op[1]] = i.op[0]
                block.instructions.remove(i)
            elif 'br i1' in i.string:
                stack.append({})
                self.remove_store_load(self.cfg.blocks[i.op[1]], block, visited, stack)
                stack.pop()
                stack.append({})
                self.remove_store_load(self.cfg.blocks[i.op[2]], block, visited, stack)
                stack.pop()
            elif 'br label' in i.string:
                self.remove_store_load(self.cfg.blocks[i.op[0]],  block, visited, stack)
