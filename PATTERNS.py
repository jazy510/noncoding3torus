from UTILS import *
from CUBE import *
from CUBEOPS import *
from TORUSCREATOR import *
from multiprocessing import shared_memory


def show_patterns(slice_format, slice_order, slice_rotations):
    '''
        INPUT: slice format 4x4x4 etc, order of slices as a list eg: [0,2,1,3], slice rotations as a list eg: [0,2,3,0]
        ACTION: Compute the patterns from a reference cube that can be used to compute matching face
        OUTPUT: Prints patterns that can be used for matching face
    '''
    print("Slice format:    " + str(slice_format))
    print("Slice order:     " + str(slice_order))
    print("Slice rotations: " + str(slice_rotations))

    seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    c = cube(seq, 0, slice_format, slice_order, slice_rotations)

    print("ALL OF THE x->(5-x) lines are the compliment, BUT CAN'T THINK OF A GOOD WAY TO SHOW THAT")
    print("INITIAL Face -> Mapped to Rotated Twice Face = Should be the match")
    print("         " + seq)
    for this_face in range(0,6):
        p = list('.'*64)
        o = list('.'*64) #Original Face
        o_index = []
        face_seq = c.face_to_seq(c.faces[0][this_face])
        mirror_sequence = mirror_seq(face_seq)
        fake_face_seq = c.face_to_seq(c.faces[2][5-this_face])
        for index in range(0,16):
            plocation = seq.find(fake_face_seq[index])
            p[plocation] = mirror_sequence[index] # Just have to know it is mirror

            olocation = seq.find(face_seq[index])
            o_index.append(olocation)
            o[olocation] = face_seq[index]
        pattern = ''
        for x in p:
            pattern += x
        original = ''

        for x in o:
            original += x

        print("  " + str(this_face) + " MAP: " + original)
        print(str(this_face) + " INDEX: " + str(o_index).replace(' ', ''))
        print("   " + str(this_face) + "->" + str(5 - this_face) + ": " + pattern)
        print("")

def get_face_byte_pattern(slice_format, slice_order, slice_rotations, face):
    '''
        INPUT: slice format 4x4x4 etc, 
               order of slices as a list eg: [0,2,1,3], 
               slice rotations as a list eg: [0,2,3,0],
               face to get pattern of
        OUTPUT: returns list of bytes that correspond to the given face
    '''
    seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    c = cube(seq, 0, slice_format, slice_order, slice_rotations)

    byte_patterns= []
    for this_face in range(0,6):
        p = list('.'*64)
        o = list('.'*64) #Original Face
        o_index = []
        face_seq = c.face_to_seq(c.faces[0][this_face])
        mirror_sequence = mirror_seq(face_seq)
        fake_face_seq = c.face_to_seq(c.faces[2][5-this_face])
        for index in range(0,16):
            plocation = seq.find(fake_face_seq[index])
            p[plocation] = mirror_sequence[index] # Just have to know it is mirror

            olocation = seq.find(face_seq[index])
            o_index.append(olocation)
            o[olocation] = face_seq[index]
        pattern = ''
        for x in p:
            pattern += x
        original = ''

        for x in o:
            original += x
        byte_patterns.append(o_index)

    return byte_patterns[face]

def get_patterns(s_slice_format, s_slice_order, s_slice_rotations, input_seq, t_slice_format, t_slice_order, t_slice_rotations):
    '''
        PURPOSE: Generate a dict of byte locations and a sub-sequences for each face of a cube that can be used
                   to test if a given test-sequence of 64 bases might be a match for the input_sequence/cube.
                TLDR; Get a Dict with keys that are the faces.  The values are the bytes to test to see if it is match.
                      This is a "MATCH_FACES" thing without generating a cube in real time.  MUCH FASTER.
        INPUT: slice format, slice order, slice rotations, input sequence
        ACTION: Generate a fake cube with a unique sequnce with the given slice parameters.
         Loop over the faces of the cube.  
         Generate what a matching opposite face map would be. 
         THen take that map and apply it to the input cube's original face rotated complimented and mirrored
          This is what the opposite face sequence should be and where it would be.

        OUTPUT: {0:([48,49,50,..],'GTCCAGAGCTACCGT'), 1:....}
            The list is the 0 indexed location in the 64 base test string that should be extracted (in what order), to
             generate the 16-base sequence string that is the second-half of the tuple.

        ---- ASSUMPTION -> The opposing face will be numbered opposite of source cube.  
                            EG: If looking for match to face 2 of source cube, will be trying to match face 3 of opposite cube
                            IF this weren't the case, There would be a WHOLE LOT OF MATCHES TO TRY.
                             And there would be a LOT of false positives.  But that may in fact be the case.
                            This assumes that all cubes in a cube of cubes are oriented the same.
                            I DO NOT LIKE THIS ASSUMPTION.  WILL HAVE TO REVISIT.
                              WOULD BE 36 elements in return object instead of 6.

        ---- ASSUMPTION -> Opposite/Matching face will be source face sequence mirrored, rotated twice, and complimented

        ---- ASSUMPTION -> The input_sequecne Slice Parameters are the same as the sequence being testing
                            This could be a VERY bad assumption. What if:
                            Input Slice format = '8x8' and Target Slice = '16x4'?
                            Input Slice Order = 0,1,2,3 and target Slice order = 0,2,1,3?
                            Input Slice Rotations = 0,0,0,0 and target slice rotations = 0,1,3,0?
                 This assumption bothered me too much.  
                 Including parameters for target cube format.

        Note that a rotation of 0,1,1,0/0,2,2,0/0,3,3,0/1,0,0,1/2,0,0,2/3,0,0,3 of a onesself cube i
         will still be a onesself cube.
        Shall we should try all of these combinations when searching for neighbors?
            
    '''
    seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    c = cube(input_seq, 0, s_slice_format, s_slice_order, s_slice_rotations) #REAL/INPUT CUBE
    fc = cube(seq, 0, t_slice_format, t_slice_order, t_slice_rotations) #TARGET FAKE CUBE
    r = {}
    for this_face in range(0,6):
        mapp = []
        matching_seq = c.face_to_seq(c.rmc_face(c.faces[0][this_face], 2)) # ASSUMPTIONS -> Face2 RMC'ed = Face 3
        fcs = fc.face_to_seq(fc.faces[0][5-this_face]) #ASSUMPTIONS -> Face 2 Matches Face 3 -> Same orientation.
        for index in range(0,16):
            mapp.append(seq.find(fcs[index]))
        r[this_face] = (mapp, matching_seq)
    return r

def pattern_extract(outfile, scratchfile, proc, shm_name, server_num, min_cube_entropy, search):
    '''
        ----- WARNING -----
         THIS IS CALLED USING mp_execute!
         THAT MEANS THAT THE CONTENTS OF outfile MUST be an object with key/value pairs, and the value must be a list
         ----- WARNING -------


        This is basically a grep, but can do multiple patterns at once and is distributed.

         search though the shared_memory byte-by-byte looking for seqeucnes that would match any of the patterns.

        The idea is that we have a cube, such as a onesself cube, and want to match any other cube in the
         gnome :) that may be adjacent.

         Multiple possible cubes could be found, and they should all be returned.

         The patterns to search against should be gotten from get_patterns.
             Multiple different patterns for different slice information can be tested against.
               For example: maybe we have an input cube of '8x8' [0,1,2,3] [0,0,0,0],
                 but want to find a cube that is 16x4 [3,0,2,1] [1,2,3,3]

         This does assume that the cubes are oriented in teh same direction because it relies on get_patterns,
            and all of its assumptions.
         -------ASSUMPTION -> All assumptions inhereted from get_patterns if used.
         ------ ASSUMPTION -> ALL MIRRORING AND WHAT NOT HAS BEEN DONE BEFORE PASSING THE PATTERN HERE.
                              THIS ONLY DOES THE PATTERN SEARCHING AND SEQUENCE EXTRACTION
         Once a pattern is matched, since we are expecting certain values at a known byte location,
          we can extract the whole cube sequence.

        search object format:
            {'AAAGTACATCAGTACCCA..':[ {slice_format:<x>,
                                       slice_order:<y>,
                                       slice_rotations:<z>,
                                       face:<w>,  #WIll be the face of the Target Sequence.
                                       byte_array:[ordered,int,byte,locations],
                                       sequence:<BASES TO MATCH>
                                       matches:[(offset, <CUBE SEQUENCE>)] #Cube sequence will be assumed to start at 0.
                                      },
                                    ]
            }

        The search object will have to be constructed from calls to get_patterns.
        get_patterns returns objects of format:
        { <face#>:([ordered list of bytes], <BASE Sequence To Match> }

        Once a pattern has been found, the offset the match was found at and the extracted cube sequence will
           be appended to the matches list in tuple format.

        There will be MULTIPLE keys that will be searched on for every byte sequence in the list.
        Advance a byte in the gnome :), and loop over all of the cube sequences, and all of the searches for each sequence.

        The output could get very large very fast.

        After a sequence has been found, the min_cube_entropy is applied.

        If the Cube Sequence is equal to the key of the search, it is ignored.  We are not looking for its own onesself.

    '''
    proc_num, start_offset, datalen = proc
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf

    p = start_offset -1
    end = start_offset + datalen - 64
    match_count = 0
    steps = 0
    while p < end:
        p = p+1
        steps += 1
        if steps%250000 == 0:
            print("Proc: " + str(proc_num) +
                  " At step " + str(steps) + " of  " + str(datalen) +
                  " Fraction done: " + str(float(steps)/float(datalen)) +
                 " Full Matches: " + str(match_count))

        t = bytes(buf[p:p+64]).decode()

        #Loop over each of the match tests
        #    {'AAAGTACATCAGTACCCA..':[ {slice_format:<x>,
        #                               slice_order:<y>,
        #                               slice_rotations:<z>,
        #                               t_slice_format:<x>,
        #                               t_slice_order:<y>,
        #                               t_slice_rotations:<z>,
        #                               face:<w>,  #WIll be the face of the Target Sequence.
        #                               byte_array:[ordered,int,byte,locations],
        #                               sequence:<BASES TO MATCH>
        #                               matches:[(offset, <CUBE SEQUENCE>)] #Cube sequence will be assumed to start at 0.
        #                              },
        #                            ]
        #    }

        ## MINIMUM IS {'<SEQ>':[ { byte_array:[], sequence:<bases to match>, matches:[]}}

        for c_seq in search:
            for s in search[c_seq]:
                #Build Sequence from buffer
                test = ''
                for loc in s['byte_array']:
                    test += t[loc]
                if s['sequence'] == test:
                    #Found a match.
                    if entropy(t) >= min_cube_entropy:
                        #This is a keeper.
                        s['matches'].append((p, t))
                        match_count += 1


    shm.close()

    dump_json(search, outfile)
    print("Wrote results to: " + str(outfile))


if __name__ == '__main__':

    #### JUST RUN PATTERNS SHOW.. Not really any test.
    show_patterns('8x8', [0,1,2,3], [0,0,0,0])

    ## TEST get_patterns

    input_seq = 'AAAAACAGATGTTTCAGTAGCAGCGGTTGCTTAAGCAACCGCTGCTACTGAAACATCTGTTTTT' #IS A ONESSELF 8x8 0,1,2,3 0,0,0,0
    s_slice_format = '8x8'
    t_slice_format = s_slice_format
    s_slice_order = [0,1,2,3]
    t_slice_order = s_slice_order
    s_slice_rotations = [0,0,0,0]
    t_slice_rotations = s_slice_rotations


    r = get_patterns(s_slice_format, s_slice_order, s_slice_rotations, input_seq, 
                     t_slice_format, t_slice_order, t_slice_rotations)

    expected = {0: ([39, 38, 37, 36, 47, 46, 45, 44, 55, 54, 53, 52, 63, 62, 61, 60], 'CCAACATCTACATTTT'), 1: ([0, 8, 16, 24, 4, 12, 20, 28, 32, 40, 48, 56, 36, 44, 52, 60], 'AAGGATCGAGTCACAT'), 2: ([24, 25, 26, 27, 28, 29, 30, 31, 56, 57, 58, 59, 60, 61, 62, 63], 'GGTTGCTTCTGTTTTT'), 3: ([3, 2, 1, 0, 7, 6, 5, 4, 35, 34, 33, 32, 39, 38, 37, 36], 'AAAAGACACGAACCAA'), 4: ([27, 19, 11, 3, 31, 23, 15, 7, 59, 51, 43, 35, 63, 55, 47, 39], 'TGTATCAGTAGCTTCC'), 5: ([0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27], 'AAAAATGTGTAGGGTT')}

    if r != expected:
        raise Exception("TEST FAILURE: get_patterns")

    #TEST:
    name_1 = str(random.randint(99999999,999999999999)) + '.tmp'
    s_slice_format = '8x8'
    s_slice_order = [0,1,2,3]
    s_slice_rotations = [0,0,0,0]
    t_slice_format = s_slice_format
    t_slice_order = s_slice_order
    t_slice_rotations = s_slice_rotations

    test_randoms = random_seq(1024)
    find_this = test_randoms[64:128]
    and_this = test_randoms[448:448+64]


    #Generate Search patterns
    q = get_patterns(s_slice_format, s_slice_order, s_slice_rotations, find_this,
                     t_slice_format, t_slice_order, t_slice_rotations)
    r = get_patterns(s_slice_format, s_slice_order, s_slice_rotations, and_this,
                     t_slice_format, t_slice_order, t_slice_rotations)

    #get_patterns returns {0:([byte seq in ints],<pattern>), 1:(..)....}

    #Search for q face 0, and r face 3
    q0_bytes = q[0][0]
    q0_seq = q[0][1]
    r3_bytes = r[3][0]
    r3_seq = r[3][1]

    #Write to the test sequence the pattern we are looking for
    q0_randoms = list(random_seq(64))
    r3_randoms = list(random_seq(64))

    index = 0
    for q0b in q0_bytes:
        q0_randoms[q0b] = q0_seq[index]
        index += 1
    q0_randoms = ''.join(q0_randoms)

    index = 0
    for r3b in r3_bytes:
        r3_randoms[r3b] = r3_seq[index]
        index += 1
    r3_randoms = ''.join(r3_randoms)

    test_randoms += q0_randoms + random_seq(512) + r3_randoms + random_seq(512)

    #Write test sequence to file
    f = open(name_1, 'a+')
    f.write(test_randoms)
    f.close()
    shm = map_file(name_1, 0, -1)
    os.unlink(name_1)

    #    {'AAAGTACATCAGTACCCA..':[ {slice_format:<x>, 
    #                               slice_order:<y>, 
    #                               slice_rotations:<z>, 
    #                               face:<w>,  #WIll be the face of the Target Sequence.
    #                               byte_array:[ordered,int,byte,locations],
    #                               sequence:<BASES TO MATCH>
    #                               matches:[(offset, <CUBE SEQUENCE>)] #Cube sequence will be assumed to start at 0.
    #                              }, 
    #                            ]
    #    }

    search = {}
    search[find_this] = [ {'slice_format':s_slice_format,
                           'slice_order':s_slice_order,
                           'slice_rotations':s_slice_rotations,
                           'face':0,
                           'byte_array':q0_bytes,
                           'sequence':q0_seq,
                           'matches':[]
                           }
                        ]
    search[and_this] = [ {'slice_format':s_slice_format,
                           'slice_order':s_slice_order,
                           'slice_rotations':s_slice_rotations,
                           'face':0,
                           'byte_array':r3_bytes,
                           'sequence':r3_seq,
                           'matches':[]
                         }
                       ]

    proc = (0, 0, len(test_randoms))
    server_num = 0
    min_cube_entropy = 1.0
    #Search for the pattern. No return.  Just writes to file.
    pattern_extract(name_1, name_1, proc, shm.name, server_num, min_cube_entropy, search)
    shm.close()
    shm.unlink()

    f = open(name_1, 'r')
    x = f.read()
    f.close()
    os.unlink(name_1)

    x = json.loads(x)
    if search[find_this][0]['matches'][0][0] != 1024 or search[and_this][0]['matches'][0][0] != 1600:
        print("TEST FAILURE")



    fp = get_face_byte_pattern(s_slice_format, s_slice_order, s_slice_rotations, 0)
    if fp != [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27]:
        raise Exception("FAILED TEST get_face_byte_pattern")

    print("TESTS PASSED")

