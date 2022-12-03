import argparse
from python_graphs import program_graph, program_graph_graphviz
from simplified_ast import get_simplified_ast
from utils import (
    remove_comments_and_docstrings, collapse_nodes, 
    label_nodes, sast_to_prog)
from visualizers import render_sast


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True)
    parser.add_argument('--dfg', action='store_true')
    parser.add_argument('--cfg', action='store_true') 
    args = parser.parse_args()

    file = f"./examples/{args.file}.py"
    with open(file, 'r') as fp:
        source = fp.read()
    
    # remove comments and docstrings
    source = remove_comments_and_docstrings(source)

    ##### PGRAPHS #####
    pgraph = program_graph.get_program_graph(source)
    program_graph_graphviz.render(pgraph, path="tmp/pgraph.png")

    # ##### SAST #####
    sast = get_simplified_ast(source, dfg=args.dfg, cfg=args.cfg)
    sast = collapse_nodes(sast)
    if sast is not None:
        sast = label_nodes(sast, source)
        render_sast(sast, path="tmp/sast.png", spans=True)
        # print(sast_to_prog(sast))
    else:
        print("SAST is an empty graph :(")
