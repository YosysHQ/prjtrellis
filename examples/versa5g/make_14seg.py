import sys
# From http://www.plusea.at/downloads/print/AllMySegment-handout.pdf
# NB odd numbering
font = {
 "A": ['e', 'f', 'a', 'b', 'c', 'p', 'k'],
 "B": ['e', 'f', 'a', 'j', 'p', 'l', 'd'],
 "C": ['d', 'e', 'f', 'a'],
 "D": ['e', 'f', 'g', 'n'],
 "E": ['d', 'e', 'f', 'a', 'p'],
 "F": ['e', 'f', 'a', 'p'],
 "G": ['d', 'e', 'f', 'a', 'k', 'c'],
 "H": ['e', 'f', 'p', 'k', 'b', 'c'],
 "I": ['a', 'h', 'm', 'd'],
 "J": ['b', 'c', 'd'],
 "K": ['e', 'f', 'p', 'j', 'l'],
 "L": ['d', 'e', 'f'],
 "M": ['e', 'f', 'g', 'j', 'b', 'c'],
 "N": ['e', 'f', 'g', 'l', 'c', 'b'],
 "O": ['e', 'f', 'a', 'b', 'c', 'd'],
 "P": ['e', 'f', 'a', 'b', 'k', 'p'],
 "Q": ['e', 'f', 'a', 'b', 'c', 'd', 'l'],
 "R": ['e', 'f', 'a', 'j', 'p', 'l'],
 "S": ['a', 'f', 'p', 'k', 'c', 'd'],
 "T": ['a', 'h', 'm'],
 "U": ['f', 'e', 'd', 'c', 'b'],
 "V": ['f', 'e', 'n', 'j'],
 "W": ['f', 'e', 'n', 'l', 'c', 'b'],
 "X": ['g', 'l', 'n', 'j'],
 "Y": ['g', 'j', 'm'],
 "Z": ['a', 'j', 'n', 'd'],
 " ": [],
 "\n": []
}
seg_names = "abcdefghjklmnp"
text = sys.stdin.read()
print ("    localparam pat_len = {};".format(len(text)))
print ("    wire [13:0] display_pat[0:pat_len-1];")
for i in range(len(text)):
    segs = font[text[i]]
    bits = [(seg_names[k] in segs) for k in range(14)]
    bit_lit = "14'b{}".format("".join(reversed(["1" if b else "0" for b in bits])))
    print ("    assign display_pat[{}] = {};".format(i, bit_lit))