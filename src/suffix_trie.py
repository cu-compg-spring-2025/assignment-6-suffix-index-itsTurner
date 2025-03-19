import argparse
import utils

def get_args():
    parser = argparse.ArgumentParser(description='Suffix Trie')

    parser.add_argument('--reference',
                        help='Reference sequence file',
                        type=str)

    parser.add_argument('--string',
                        help='Reference sequence',
                        type=str)

    parser.add_argument('--query',
                        help='Query sequences',
                        nargs='+',
                        type=str)

    return parser.parse_args()

SUB = 0
CHILDREN = 1

def add_suffix(nodes, suf):
    n = 0
    i = 0
    while i < len(suf):
        b = suf[i] 
        children = nodes[n][CHILDREN]
        if b not in children:
            n2 = len(nodes)
            nodes.append([suf[i], {}])
            nodes[n][CHILDREN][b] = n2
            i += 1
        else:
            n2 = children[b]

        n = n2

def build_suffix_trie(s):
    s += "$"

    nodes = [ ['', {}] ]

    for i in reversed(range(len(s))):
        add_suffix(nodes, s[i:])
    
    return nodes

def search_trie(trie, pattern):
    P = pattern
    P += "$"
    
    n = 0
    i = 0

    while i < len(P):
        j = 0

        sub = trie[n][SUB]

        if (i + j) < len(P) and j < len(sub) and P[i + j] == sub[j]:
            j += 1
        
        i += j
        if j == len(sub):
            if i == len(P):
                # print(f'Complete match on {P}')
                return i - 1
            else:
                # print(f'Match {P[:i]} with {sub}')
                if P[i] in trie[n][CHILDREN]:
                    n = trie[n][CHILDREN][P[i]]
                else:
                    return i
        else:
            return i

def main():
    args = get_args()

    T = None

    if args.string:
        T = args.string
    elif args.reference:
        reference = utils.read_fasta(args.reference)
        T = reference[0][1]

    print('Extracted file')

    trie = build_suffix_trie(T)
    # print(trie)

    print('Tree built')

    if args.query:
        for query in args.query:
            match_len = search_trie(trie, query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
