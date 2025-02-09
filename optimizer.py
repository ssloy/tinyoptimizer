from ir import *

def dominance_frontiers(cfg):
    def dfs(block, visited, postorder):
        visited.add(block)
        for b in block.successors:
            if b not in visited: dfs(b, visited, postorder)
        postorder.append(block)
    postorder = []                                              # for efficiency reasons, we visit blocks in a way that ensures
    dfs(cfg.blocks['entry'], set(), postorder)                  # processing of each block after its predecessors have been processed

    dom = { b : set(cfg.blocks.values()) for b in cfg.blocks.values() }
    dom[ cfg.blocks['entry'] ] = { cfg.blocks['entry'] }        # dom[b] contains every block that dominates b
    changed = True
    while changed:                                              # the iterative dominator algorithm [Cooper, Harvey and Kennedy, 2006]
        changed = False
        for b in postorder[-2::-1]:                             # for all blocks (except the source) in reverse postorder
            new_dom = set.intersection(*[ dom[p] for p in b.predecessors ]) | { b }
            if dom[b] != new_dom:
                dom[b] = new_dom
                changed = True

    idom = { cfg.blocks['entry'] : None }                       # idom[b] contains exactly one block, the immediate dominator of b
    for b in postorder[-2::-1]:                                 # reverse or not we do not care here, but do not visit the source block
        idom[b] = max(dom[b] - {b}, key=lambda x: len(dom[x]))  # immediate dominator is the one with the maximum number of dominators (except the block itself)

    df = { b : set() for b in cfg.blocks.values() }             # the dominance-frontier algorithm
    for b in filter(lambda x: x in postorder and len(x.predecessors) > 1,
                    cfg.blocks.values()):                       # iterate through reachable blocks with multiple predecessors
        for p in b.predecessors:
            runner = p
            while runner != idom[b]:
                df[runner].add(b)
                runner = idom[runner]
    return df

def mem2reg(cfg):
    df = dominance_frontiers(cfg)
    variables = { i.op[0] : i.string.split()[-1] for i in cfg.blocks['entry'].instructions if 'alloca' in i.string } # name -> type
    for v in variables.copy().keys(): # TODO really ugly check, rewrite it. By the way, instead of removing these variables from store-load, optimization, we can insert a correct store prior to a func call
        for b in cfg.blocks.values():
            for i in b.instructions:
                if f'* %{v}' in i.string and v in variables:
                    del variables[v]

    phi = { v:set() for v in variables.keys() }                        # map (variable -> set of basic blocks)
    for v in variables.keys():                                         # Fig 9.9b in [Cooper and Torczon, Engineering a Compiler Broché]
        blocks_with_store = { b for b in cfg.blocks.values() for i in b.instructions if 'store' in i.string and i.op[1]==v }
        blocks_to_consider = blocks_with_store.copy()
        while blocks_to_consider:
            block = blocks_to_consider.pop()
            for frontier in df[block]:
                if frontier in phi[v]: continue
                phi[v].add(frontier)
                blocks_to_consider.add(frontier)

    for v, bb in phi.items():                                   # insert phi nodes (for the moment without choices)
        for b in bb:
            b.phi_functions.append(Phi(v + '_' + b.label, variables[v]))

    def store_load(block, prev, visited, stack):
#        print(stack)
        def find_variable(v, stack):                            # walk the stack back until
            for frame in reversed(stack):                       # the current variable instance is found
                if v in frame:
#                    print(frame[v])
                    return frame[v]

        for phi in block.phi_functions:                         # place phi node choice for the current path
            v = phi.reg[:-len(block.label)-1]                   # phi saves the choice into a register named foo_bar, where foo is the name of the variable, and bar is the name of the basic block
#            print(v, stack)
            b, val = find_variable(v, stack)
#            phi.choice[b] = val
            phi.choice[prev.label] = val
#            print('choice', b,val)
            stack[-1][v] = [block.label, phi.reg]
        if block in visited: return                             # we need to revisit blocks with phi functions as many times as we have incoming edges,
        visited.add(block)                                      # therefore the visited check is made after the choice placement

        for i in block.instructions[:]:                         # iterate through a copy since we modify the list
            if 'load' in i.string and i.op[1] in variables.keys():
                _, val = find_variable(i.op[1], stack)
                block.instructions.remove(i)
                block.find_and_replace(i.op[0], val)
            elif 'store' in i.string and i.op[1] in variables.keys():
                stack[-1][i.op[1]] = [block.label, i.op[0]]
                block.instructions.remove(i)
            elif 'br i1' in i.string:
                stack.append({})
                store_load(cfg.blocks[i.op[1]], block, visited, stack)
                stack.pop()
                stack.append({})
                store_load(cfg.blocks[i.op[2]], block, visited, stack)
                stack.pop()
            elif 'br label' in i.string:
#                print(block.label, 'br', i.op[0])
#                for v in stack[-1].keys():
#                    stack[-1][v][0] = i.op[0]
                store_load(cfg.blocks[i.op[0]],  block, visited, stack)
    stack = [{}] # stack of maps (variable -> (block, value)); necessary for storing context while branching
    store_load(cfg.blocks['entry'], None, set(), stack)
#   print(cfg.header)
#   print()
#   print()
#   print()
