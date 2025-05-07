import argparse
import utils

def get_args():
    parser = argparse.ArgumentParser(description='Suffix Tree')

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


class SuffixTree():
    __algorithm_name__ = 'Suffix tree'
    SUB = 0
    CHILDREN = 1

    def __init__(self, s: str = None):
        self.s, self.tree = None, None
        if s is not None:
            self.setup(s)

    def setup(self, s):
        self.s = s
        self.tree = self.build_suffix_tree(self.s)
    
    def align(self, query):
        return self.search_tree(query)

    def add_suffix(self, nodes, suf):
        n = 0
        i = 0
        while i < len(suf):
            b = suf[i] 
            children = nodes[n][self.CHILDREN]
            if b not in children:
                n2 = len(nodes)
                nodes.append([suf[i:], {}])
                nodes[n][self.CHILDREN][b] = n2
                return
            else:
                n2 = children[b]

            sub2 = nodes[n2][self.SUB]
            j = 0
            while j < len(sub2) and i + j < len(suf) and suf[i + j] == sub2[j]:
                j += 1

            if j < len(sub2):
                n3 = n2 
                n2 = len(nodes)
                nodes.append([sub2[:j], {sub2[j]: n3}])
                nodes[n3][self.SUB] = sub2[j:]
                nodes[n][self.CHILDREN][b] = n2

            i += j
            n = n2

    def build_suffix_tree(self, text):
        text += "$"

        nodes = [ ['', {}] ]

        for i in range(len(text)):
            self.add_suffix(nodes, text[i:])
        
        return nodes

    def search_tree(self, P):
        P += "$"
        
        n = 0
        i = 0

        while i < len(P):
            j = 0

            sub = self.tree[n][self.SUB]

            while (i + j) < len(P) and j < len(sub) and P[i + j] == sub[j]:
                j += 1
            
            i += j
            if j == len(sub):
                if i == len(P):
                    # print(f'Complete match on {P}')
                    return i - 1
                else:
                    # print(f'Match {P[:i]} with {sub}')
                    if P[i] in self.tree[n][self.CHILDREN]:
                        n = self.tree[n][self.CHILDREN][P[i]]
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

    tree = SuffixTree(T)

    print('Tree built')
    
    if args.query:
        for query in args.query:
            match_len = tree.align(query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
