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

class SuffixArray():
    __algorithm_name__ = 'Suffix array'

    def __init__(self, T: str = None):
        self.T, self.array = None, None
        if T is not None:
            self.setup(T)
    
    def setup(self, T):
        self.T = T
        self.array = self.build_suffix_array()

    def align(self, query):
        return len(self.search_array(query))

    def build_suffix_array(self):
        self.T += '$'
        return sorted((rot for rot in range(len(self.T))), key=lambda rot: self.T[rot:])

    def sa_index_matches_query(self, q, i):
            offset = self.array[i]
            if len(self.T) - offset < len(q):
                return False
            return self.T[offset:offset+len(q)] == q

    def search_array(self, q):
        def boundary_binary_search(border_match_condition, boundary_min = 0, decreasing_mode=True):
            boundary_max = len(self.array)
            boundary_mid = int((boundary_max + boundary_min) / 2)
            while (boundary_max - boundary_min > 1):
                if self.sa_index_matches_query(q, boundary_mid):
                    if border_match_condition(boundary_mid):
                        break # boundary found
                    else:
                        if decreasing_mode:
                            boundary_max = boundary_mid
                        else:
                            boundary_min = boundary_mid
                else:
                    if self.T[self.array[boundary_mid]:] < q:
                        boundary_min = boundary_mid
                    else:
                        boundary_max = boundary_mid
                boundary_mid = int((boundary_max + boundary_min) / 2)
            
            if self.sa_index_matches_query(q, boundary_mid) and border_match_condition(boundary_mid):
                return boundary_mid
            else:
                return None # No match
        
        # lo boundary search
        lo_border_match_condition = lambda mid: mid - 1 < 0 or not self.sa_index_matches_query(q, mid - 1)
        lo = boundary_binary_search(lo_border_match_condition, boundary_min=0, decreasing_mode=True)
        
        if lo is None:
            return None # No match

        # hi binary search
        hi_border_match_condition = lambda mid: mid + 1 >= len(self.T) or not self.sa_index_matches_query(q, mid + 1)
        hi = boundary_binary_search(hi_border_match_condition, boundary_min=lo, decreasing_mode=False)

        if hi is None:
            return None # No match, but this should never happen since lo should catch first
        
        return range(lo, hi + 1)

def main():
    args = get_args()

    T = None

    if args.string:
        T = args.string
    elif args.reference:
        reference = utils.read_fasta(args.reference)
        T = reference[0][1]

    array = SuffixArray(T)

    if args.query:
        for query in args.query:
            match_len = array.align(query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
