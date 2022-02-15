from UTILS import *
from CUBE import *

def pattern_count(infile, outfile, min_matches, min_face_entropy, buffer_size, cull_size, pattern):
    '''
        NOT A REGEX!! REGEX WAS WAAAAAYYYY TOO SLOW!
        This function searches ALL data in a flat file, or any text file byte by byte.

        It is used to find cubes that have the same face sequence/slice stuff spread out over the genome.
        I suggest running --show_pattern <slice format> <slice order> <slice rotations> 
         For example:
                   abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!
            0 MAP: abcd....ijkl....qrst....yzAB....................................
          0 INDEX: [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27]
             0->5: ....................................BAzy....tsrq....lkji....dcb

         If looking for cubes that may be along the H axis in a '8x8'/0,1,2,3/0,0,0,0 LWH cube, check the 0/5 faces for repeats:
             pattern = [0,1,2,3, 8,9,10,11, 16,17,18,19, 24,25,26,27, 36,37,38,39, 44,45,46,47, 52,53,53,55, 60,61,62,63] 

        This will find (If there are a lot of them, and if they do exist) all of the possible, and different, vertical 
          columns in a cube of cubes.

        There is a huge tradeoff between sequence length and the amount of memory to be used.
            If you use a long sequence, I hope you have Terabytes of memory.
            If you don't then once memory starts to get full, if a large number of the sequences haven't been found
             in close reltation to one another in the genome, then it will be culled.
        If you use a short sequence, then you will have a high count, but useless information.

        It may be worthwhile to explore looking at a subset of the, for example, 0 face and 5 face instead of
         and entire match for both of them.

        IT takes in an ordered list of integers 
            where the integers represent the the new pattern to generate from the data in the file
        For example [1,3,5,7,9] applied to 'ABCDEFGHIJ-----AxCxExGxHxIxJ' will generate a pattern Of.
        B.D.F.H.J -> where a '.' can be anything
        The string BDFHJ is then added to a dictionary and a count of 1 is set.
        If a byte/base sequence is ever ecountered again (6 iterations,steps,counts later in the example above), the pattern:
         BDFHJ will be generated again and the counter will be incremented.

         This is inherently a single process type of operation unless a HADOOP map-reduce type of operation can be done on it.

         The hash that contains the counts quickly becomes too large for memory.  After the hash is filled up to a 
         user-specified amount, --buffer_size <Default 10M>, 
             it iterates through the hash and removes keys that have a count less than that of --cull_size
         It is only looking for results that have a count of min_matches <which is default to 500> so it should catch
          the vast majority of results (As long as at least 5 are within one cull check).

         If the search is run on a computer with a large amount of memory, a --buffer_size of 8300000000 could be used and not
          fire off a culling. As the buffer fills up the time between cullings is reduced, and if not careful, it could become
          deadlocked.

         If cull_size is small and buffer_size is large the computer will run out of memory and the HDD will thrash with swapping
         It may take several runs to get a good mix.. or get a computer with 64+GB of memory.
         The output is a .json object with keys of the total count of a match and its opposite/inverse/compliment
         The value matching that key is an object with both the key, its reverse, their counts, and the entropy of the key
         Using min_face_entropy because generally will be searching on face-sizes.
         out = { "2222":{"AACCGGTTAACCGGTT":1111, "TTGGCCAATTGGCCAA":1111, "entropy":1.1234123123 }, "123":{....

         I suppose we could save off anything that is culled to disk and then loop through that looking for more matches.
           That would be like a poor man's map-reduce more so than this already is.
    '''


    data = read_file(infile, 0, -1)
    datalen = len(data)

    #Get how many bytes forward we need to read at most to match the pattern.
    # For example if looking at an 8x8 face 5 with 0,1,2,3 slice orderings the bases 63,62,61,60 will be read.
    #  with 63 being the largest.
    pattern_largest = 0 
    for l in pattern:
        if l > pattern_largest:
            pattern_largest = l

    p = -1
    counts = {}
    while p < datalen - pattern_largest - 1:
        p = p+1
        if p%250000 == 0:
            print("At byte " + str(p) + " of  " + str(datalen) + " Fraction done: " + str(float(p)/float(datalen)) + " Len Counts: " + str(len(counts)))
            c = len(counts)
            k = 0
            if c > buffer_size:
                r_len = cull_size
                keep = {}
                for x in counts:
                    if counts[x] >= r_len:
                        keep[x] = counts[x]
                del(counts)
                counts = keep
                k = len(keep)

                print("Culled: " + str(c - k) + " from counts because threashold not met.")

        t = data[p:p+pattern_largest+1] #temporary small buffer so big data isn't touched again this p
        f = ''
        for x in pattern:
            f += t[x]
        if f not in counts:
            counts[f] = 1
        else:
            counts[f] += 1

    print("FINISHED LOOPING - Trimming low counts")
    keep = {}
    for x in counts:
        if counts[x] >= min_matches and entropy(x) >= min_face_entropy:
            keep[x] = counts[x]
    del(counts)
    print("Count meeting minimum threashold: " + str(len(keep)))

    #print("Sorting by highest counts")
    #pattern_string = ''
    #for x in pattern:
    #    pattern_string += str(x) + ','
    #pattern_string = pattern_string[:-1]

    #p = {}
    #for key1 in keep:
    #    key1_total = keep[key1]
    #    key2_total = 0
    #    key2 = reverse_seq(compliment_seq(key1))
    #    if key2 in keep:
    #        key2_total = keep[key2]
     #   total = key1_total + key2_total
    #    key_entropy = entropy(key1)
    #    if key_entropy < min_face_entropy:
    #        continue
    #    while total in p:
    #        total += 1
    #    p[total] = {'match':key1, 
    #                'match_total':key1_total, 
    #                'compliment':key2, 
    #                'compliment_total':key2_total, 
    #                'entropy':key_entropy, 
    #                'pattern':pattern_string}

    #del(keep)
    #o = []
    #for total in p:
    #    o.append(total)
    #o.sort()
    #o.reverse()
    #out = {}
    #for num in o:
    #    out[p[num]['match']] = p[num]
    #del(o)
    #del(p)

    dump_json(keep, outfile)
    print("Wrote: " + outfile)
    print("Found " + str(len(keep)) + " unique sequences")

