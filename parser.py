# *****************************************************************************
# Python AST parser for the ADL project
# Version 0.1.0, Teemu Sirkia

# Reads a given Python program and creates a JSON object
# describing line-by-line which language elements exist
# in the code.
#
# For the list of the available nodes, see:
# https://docs.python.org/3/library/ast.html#abstract-grammar
# *****************************************************************************

import ast, json, sys

# These nodes will be ignored and are not added to the node list.
#
# For example, the operators are skipped because the actual operator
# will be added to the list instead of the operator family.
nodesToSkip = {'Store', 'Load', 'Name', 'Expr', 'arguments', 'Subscript', 'BoolOp', 'BinOp', 'Compare', 'UnaryOp'}

# *****************************************************************************
# Special handlers for some nodes

def handleNameConstant(node, line):
    """ Converts the NameConstant node to represent the type of the value (True, False, None). """
    return str(node.value)

def handleNum(node, line):
    """ Converts the Num node to represent the type of the value (Int, Float). """
    return node.n.__class__.__name__.capitalize()

handlers = {'Num' : handleNum, 'NameConstant' : handleNameConstant}
# *****************************************************************************

def simpleTraverse(node, line, nodes):

    name = node.__class__.__name__

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    if name not in nodesToSkip:
        if line not in nodes['lines']:
            nodes['lines'][line] = set()
        if name not in handlers:
            nodes['lines'][line].add(name)
        else:
            nodes['lines'][line].add(handlers[name](node, line))

    for child in ast.iter_child_nodes(node):
        simpleTraverse(child, line, nodes)

def complexTraverse(node, line, nodes):

    name = node.__class__.__name__

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    endLine = line

    current = {'name': name, 'startLine': line}

    if name not in nodesToSkip:
        if line not in nodes['lines']:
            nodes['lines'][line] = []
        if name not in handlers:
            nodes['lines'][line].append(current)
        else:
            current['name'] = handlers[name](node, line)
            nodes['lines'][line].append(current)

    maxLine = endLine
    for child in ast.iter_child_nodes(node):
        maxLine = max(maxLine, complexTraverse(child, line, nodes))

    if maxLine != line:
        current['endLine'] = maxLine

    return maxLine

def hierarchicalTraverse(node, line, currentNode):

    name = node.__class__.__name__

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    endLine = line

    current = {'name': name, 'startLine': line, 'children': []}

    if name not in nodesToSkip:
        if name not in handlers:
            currentNode['children'].append(current)
        else:
            current['name'] = handlers[name](node, line)
            currentNode['children'].append(current)
    else:
        current = currentNode

    maxLine = endLine
    for child in ast.iter_child_nodes(node):
        maxLine = max(maxLine, hierarchicalTraverse(child, line, current))

    if maxLine != line:
        current['endLine'] = maxLine

    return maxLine

def main():

    data = input()
    parsed = json.loads(data)
    code = parsed['code']
    mode = parsed.get('mode', 'simple')
    nodes = {'lines' : {}}

    try:

        tree = ast.parse(code)
        startNode = {'name': 'root', 'children': []}

        # Traverse all the nodes in the AST

        if mode == 'complex':
            for node in ast.iter_child_nodes(tree):
                complexTraverse(node, 0, nodes)
        elif mode == 'hierarchical':
            for node in ast.iter_child_nodes(tree):
                hierarchicalTraverse(node, 0, startNode)
        elif mode in ('simple', 'concepts'):
            for node in ast.iter_child_nodes(tree):
                simpleTraverse(node, 0, nodes)
        else:
            print('Parsing failed!\n\nError occurred: Unknown parsing mode', file=sys.stderr)
            sys.exit(1)

        # Convert sets to lists before JSON transformation
        if mode == 'simple' or mode == 'complex':
            for line in nodes['lines']:
                nodes['lines'][line] = list(nodes['lines'][line])
        elif mode == 'hierarchical':
                nodes = startNode
        elif mode == 'concepts':
            concepts = set()
            for line in nodes['lines']:
                for concept in list(nodes['lines'][line]):
                    concepts.add(concept)
            nodes = list(concepts)

        print(json.dumps(nodes))

    except Exception as e:
        print('Parsing failed!\n\nError occurred: ' + str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
