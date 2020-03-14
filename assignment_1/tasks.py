from functools import reduce
from collections import namedtuple
from operator import mul
from typing import Tuple


def find_fold_number(n: int) -> int:
    s = str(n)
    ans = 0
    while len(s) > 1:
        s = str(reduce(lambda a, b: int(a) * int(b), s, 1))
        ans += 1
    return ans


def rle(string: str) -> str:
    def append(acc: Tuple[str, str, int], sym: str) -> Tuple[str, str, int]:
        if sym == acc[1]:
            return acc[0], sym, acc[2] + 1
        else:
            return acc[0] + acc[1] + (str(acc[2]) if acc[2] != 1 else ''), sym, 1
    return (reduce(append, string + '|', ('', '', 0))[0])[1:]


test_rle_str = 'ffffbbbbbbbbbbbbbsssssssssssssgggggggggggggggeeeeeeeeeeeellllllllllllllllllooooooooooooffffiiiiiirrrrrrrrrrrrrruuuuuuuummmmmiiiiiiiiiiiiiiiqqqxxxxxxxxxxxxxxxxxzzzzzzwwwwzzzzzzzzzzzzzzzzzzzoooooookkkkkkkkkkiiiiiiiiiiiiiiiizzzzzzzzzzzzzzzzhhhhhhhooooooooooccccccccccccccrrrrrrrkkkxxxxxxxxxxxxxxxxxkkssssssssmcccdddddddddddppppppppppppppnnnnnnnnnnnnnnssssssssssssbbbbbraaaaaasjjjjjjjjjjkkkkkkkkkrrrrrrrrryyyyyyyyyyyyaaaaaaaaaaauuuuuuuuuuuuwwwwwwwwwwgggggggglllllllllvvvvvvvvvvvbbgggggggggggggggqqqqqqlllllllllllllllxxxxxxxxxxaaaaaeeeeeeeeeeeeevvvvvvvvvvvvvdddddddddddpccccddddddddddddddddpppppppppppppppssssssssssssddddddddddddddddddzzzzzzzzzzzzzzzzzzzaaaaaaaaaaaaaaaaaaabfffffffffkkkkkxxxxxwwwwwhhhhhhhhhhhhtttttttttrrrrrrrrrrrrrrrrrroooooooooooooooooooccccccccccccccccppphhhhhhhhhhhhuuuuuurrrrrrrrrrrrrrrrrrryyyyyyyyyyyyyyyyyjjjjjjjjjjjjjjjjjjjjjjjjgggaaaxxxxxxxxxxxlllllllluuuuuuuuuummmmmmmmmmffffffmmmmmmmmmmmmmmmmmmggggggggggggggtttjjjjjjjjjjjjjjjjjjj'
