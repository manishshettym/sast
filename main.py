import gast as ast
import argparse
import re

from python_graphs.program_graph import ProgramGraph
from python_graphs import program_graph, program_graph_graphviz
from python_graphs import program_graph_dataclasses as pb
from simple_ast import get_simplified_ast
from visualizers import render_sast


def remove_node(sast: ProgramGraph, id):
    '''remove a node from the program graph'''
    edges_to_pop = []
    for edge in sast.edges:
        if edge.id1 == id or edge.id2 == id:
            edges_to_pop.append(edge)
    
    # remove the edges
    for edge in edges_to_pop:
        sast.edges.remove(edge)
        n1, n2 = edge.id1, edge.id2

        if n1 in sast.child_map:
            try:
                sast.child_map[n1].remove(n2)
            except:
                pass

        if n2 in sast.parent_map:
            del sast.parent_map[n2]

        if n1 in sast.neighbors_map:
            try:
                sast.neighbors_map[n1].remove((edge, n2))
            except:
                pass
        if n2 in sast.neighbors_map:
            try:
                sast.neighbors_map[n2].remove((edge, edge.id1))
            except:
                pass

    # pop the node
    sast.nodes.pop(id)


def filter_non_ast(sast: ProgramGraph):
    nodes_to_pop = []
    for node in sast.all_nodes():
        if node.ast_node is None:
            nodes_to_pop.append(node.id)
    
    for i in nodes_to_pop:
        remove_node(sast, i)
    
    return sast


def collapse_nodes(sast: ProgramGraph):
    '''collapse noisy nodes from the program graph to create
    a simplified AST'''

    sast = filter_non_ast(sast)

    nodes_to_pop = []
    for node in sast.all_nodes():
        parent = sast.parent(node)
        children = [c for c in sast.children(node)]

        # if range of the node is 0:0
        if (not isinstance(node.ast_node, ast.Module)
                and node.ast_node.range == (0, 0)):
            for child in children:
                sast.add_new_edge(parent, child, pb.EdgeType.FIELD)
            
            nodes_to_pop.append(node.id)
        
        # if empty function
        elif isinstance(node.ast_node, ast.Module):
            child = children[0]
            if child.ast_node.range == (0, 0):
                return None
        
        # if only 1 child w/ same range; e.g. Expr-->Call
        elif len(children) == 1:
            child = children[0]

            if node.ast_node.range == child.ast_node.range:
                sast.add_new_edge(parent, child, pb.EdgeType.FIELD)
                nodes_to_pop.append(node.id)
            
    for i in nodes_to_pop:
        remove_node(sast, i)

    return sast


def label_nodes(sast: ProgramGraph, source: str):
    '''label nodes for the simplified AST'''
    for node in sast.all_nodes():
        if isinstance(node.ast_node, ast.Module):
            setattr(node, 'span', '#')
            continue
            
        children = [c for c in sast.children(node)]
        children = sorted(children, key=lambda node: node.ast_node.range[0])

        l, r = node.ast_node.range
        span = source[l: r]
        offset = l
        
        for c in children:
            c_l, c_r = c.ast_node.range
            c_len = c_r - c_l
            c_l -= offset
            c_r = c_l + c_len

            span = span[:c_l] + '#' + span[c_r:]
            offset += (c_r - c_l) - 1
        
        span = re.sub('\s+', ' ', span)
        setattr(node, 'span', span)

    return sast

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True)
    parser.add_argument('--dfg', action='store_true')
    parser.add_argument('--cfg', action='store_true') 
    args = parser.parse_args()

    file = f"./examples/{args.file}.py"
    with open(file, 'r') as fp:
        source = fp.read()

    ##### PGRAPHS #####
    pgraph = program_graph.get_program_graph(source)
    program_graph_graphviz.render(pgraph, path="tmp/pgraph.png")

    # ##### SAST #####
    sast = get_simplified_ast(source, dfg=args.dfg, cfg=args.cfg)
    sast = collapse_nodes(sast)
    if sast is not None:
        sast = label_nodes(sast, source)
        render_sast(sast, path="tmp/sast.png", spans=True)
    else:
        print("SAST is an empty graph :(")
