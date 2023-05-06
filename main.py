import argparse
from simplified_ast import get_simplified_ast
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

    sast = get_simplified_ast(source, dfg=args.dfg, cfg=args.cfg)
    
    if sast is not None:
        render_sast(sast, path="tmp/sast.png", spans=True, relpos=True)
    else:
        print("SAST is an empty graph :(")
