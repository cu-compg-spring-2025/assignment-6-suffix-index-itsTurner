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

class SuffixTrie():
    __algorithm_name__ = 'Suffix trie'
    SUB = 0
    CHILDREN = 1

    def __init__(self, s: str = None):
        self.s, self.trie = None, None
        if s is not None:
            self.setup(s)

    def setup(self, s):
        self.s = s
        self.trie = self.build_suffix_trie(self.s)
    
    def align(self, query):
        return self.search_trie(self.trie, query)

    def build_suffix_trie(self, s):
        s += "$"

        nodes = [ ['', {}] ]

        for suf_offset in reversed(range(len(s))):
            # suf = s[i:]
            node_index, char_index = 0, 0
            while char_index < len(s)-suf_offset:
                curr_char = s[char_index+suf_offset]
                if curr_char not in nodes[node_index][self.CHILDREN]:
                    new_node_index = len(nodes)
                    nodes.append([curr_char, {}])
                    nodes[node_index][self.CHILDREN][curr_char] = new_node_index
                    node_index = new_node_index
                else:
                    node_index = nodes[node_index][self.CHILDREN][curr_char]
                char_index += 1
        
        return nodes

    def search_trie(self, trie, pattern):
        P = pattern
        P += "$"
        
        node_index, pattern_index = 0, 0
        while pattern_index < len(P):
            substring_index = 0

            node_substring = trie[node_index][self.SUB]

            if (pattern_index + substring_index) < len(P) and substring_index < len(node_substring) and P[pattern_index + substring_index] == node_substring[substring_index]:
                substring_index += 1
            
            pattern_index += substring_index
            if substring_index == len(node_substring):
                if pattern_index == len(P): # Complete match
                    return pattern_index - 1
                else: # Pattern isn't fully matched yet
                    if P[pattern_index] in trie[node_index][self.CHILDREN]:
                        node_index = trie[node_index][self.CHILDREN][P[pattern_index]]
                    else:
                        return pattern_index
            else:
                return pattern_index

def main():
    args = get_args()

    T = None

    if args.string:
        T = args.string
    elif args.reference:
        reference = utils.read_fasta(args.reference)
        T = reference[0][1]

    print('Extracted file')

    T = T[:5000]

    trie = SuffixTrie(T)

    print('Trie built')

    if args.query:
        for query in args.query:
            match_len = trie.align(query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
