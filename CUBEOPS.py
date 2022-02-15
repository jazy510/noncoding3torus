from UTILS import *
from CUBE import *
from multiprocessing import shared_memory

def find_all_matches(cubes, stop_after):
    '''
        ------------------- WARNING ---------------------
        THIS SHOULD NEVER BE USED.
        IT IS A VERY SLOW GREP ON ALL FACES OVER MULTIPLE CUBES....... PROBABLY O^4 OR SOMETHING.
        THERE ARE MUCH BETTER WAYS TO DO IT USING PATTERN MATCHING
         THAT DON'T INVOLVE CREATING WHOLE CUBE OBJECTS AND INTERATING OVER THEIR FACES.
        KEEPING IF FOR MY OWN AMUSEMENT.
        ------------------- WARNING ---------------------
        cubes contains a dict of sequence names, each sequence name is a dict of offsets (from 0 to 63)
        each offsets contains an array of cube objects

        THIS FUCNTION IS WOEFULLY OUT OF DATE.  IT IS NO LONGER USED.
        IT IS WAAAAAYYY TOO SLOW AND DONE IN A VARY NAIEVE MANNER.
        DOES NOT SUPPORT MULTIPROCESSING, SHARED_MEMORY, and still uses global args.

        As with below, keeping to inspire somebody how not to do it.

        Go use patterns.
    '''
    num_cubes = 0
    for seqname in cubes:
        for offset in cubes[seqname]:
            num_cubes += len(cubes[seqname][offset])

        stop_after = args.stop_after

    total_attempts = num_cubes * num_cubes * 6 #And 3 Rotations * 6 Faces for total comparisons done in Cube 2
    total_matches = 0
    attempted = 0
    matches = {}
    for c1_seqname in cubes:
        for c2_seqname in cubes:
            for c1_offset in cubes[c1_seqname]:
                for c2_offset in cubes[c2_seqname]:
                    for c1 in cubes[c1_seqname][c1_offset]:
                        if c1.cube_entropy < args.min_cube_entropy: 
                            continue

                        for c2 in cubes[c2_seqname][c2_offset]:
                            if c2.cube_entropy < args.min_cube_entropy:
                                continue

                            if c1 != c2 or (c1.start_offset < c2.start_offset and c1_seqname == c2_seqname and c1_offset == c2_offset):
                                #Duplicate reduction.  Don't test self, and avoid double matches if same seq and offset
                                for c1num in range(0,6):
                                    attempted += 1
                                    if attempted%250000 == 0:
                                        print("Attempt: " + str(attempted) + 
                                              " of: " + str(total_attempts) + 
                                              " Fraction Done: " + str(float(attempted)/float(total_attempts)) + 
                                              " Matches: " + str(total_matches))

                                    if c1.faces_entropy[c1num] < args.min_face_entropy:
                                        continue

                                    face = c1.faces[0][c1num]
                                    resp = c2.cube_find_match(face)
                                    if resp:
                                        (the_type, the_rotation, the_face) = resp
                                        total_matches += 1
                                        location = {}
                                        location['c1_raw'] = c1.sequence
                                        location['c2_raw'] = c2.sequence
                                        location['c1_start'] = c1.start_offset
                                        location['c2_start'] = c2.start_offset
                                        location['c1_offset'] = c1_offset
                                        location['c2_offset'] = c2_offset
                                        location['c1_index'] = c1.cube_index
                                        location['c2_index'] = c2.cube_index
                                        location['c1_face_entropy'] = c1.faces_entropy[c1num]
                                        location['c2_face_entropy'] = c2.faces_entropy[the_face]
                                        location['c1_cube_entropy'] = c1.cube_entropy
                                        location['c2_cube_entropy'] = c2.cube_entropy
                                        location['c2_type'] = the_type
                                        location['c2_rotation'] = the_rotation
                                        location['c1_face_index'] = c1num
                                        location['c2_face_index'] = the_face
                                        location['c1_name'] = c1.seq_name
                                        location['c2_name'] = c2.seq_name
                                        seq = c1.face_to_seq(face)
                                        if seq in matches:
                                            matches[seq]['count'] += 1
                                            matches[seq]['info'].append(location)
                                        else:
                                            matches[seq] = {}
                                            matches[seq]['count'] = 1
                                            matches[seq]['info'] = []
                                            matches[seq]['info'].append(location)
                                    if total_matches >= stop_after:
                                        break
                                if total_matches >= stop_after:
                                    break
                            if total_matches >= stop_after:
                                break
                        if total_matches >= stop_after:
                            break
                    if total_matches >= stop_after:
                        break
                if total_matches >= stop_after:
                    break
            if total_matches >= stop_after:
                break
        if total_matches >= stop_after:
            break

    matches = remove_duplicates(matches)

    if args.outfile:
        if args.summary:
            summary(matches)
        else:
            dump_json(args.outfile, matches)
            print("DONE FINDING MATCHING FACES.  Dumped JSON to: " + args.outfile)
    else:
        if args.summary:
            summary(matches)
        else:
            print(json.dumps(matches, indent=4))

def remove_duplicates(matches):
    #find duplicates
    removed = 0
    while True:
        delme = ()
        for seq in matches:
            for seq2 in matches:
                if seq != seq2:
                    for s1 in range(0, len(matches[seq]['info'])):
                        for s2 in range(0, len(matches[seq2]['info'])):
                            if matches[seq]['count'] == 1 and matches[seq2]['count'] == 1:
                                c1 = matches[seq]['info'][s1]['c1_start'] == matches[seq2]['info'][s2]['c2_start'] 
                                c2 = matches[seq]['info'][s1]['c1_offset'] == matches[seq2]['info'][s2]['c2_offset'] 
                                c3 = matches[seq]['info'][s1]['c1_index'] == matches[seq2]['info'][s2]['c2_index'] 
                                c4 = matches[seq]['info'][s1]['c2_type'] == matches[seq2]['info'][s2]['c2_type'] 
                                c5 = matches[seq]['info'][s1]['c1_name'] == matches[seq2]['info'][s2]['c2_name'] 
                                if c1 and c2 and c3 and c4 and c5:
                                    delme = (seq2, s2) 
                                    break
                    if len(delme) > 0:
                        break
            if len(delme) > 0:
                break
        if len(delme) > 0:
            seq2, s2 = delme
            del(matches[seq2]['info'][s2])
            removed += 1
            if len(matches[seq2]['info']) == 0:
                del(matches[seq2])
        else:
            break
    print("REMOVED " + str(removed) + " DUPLICATES")
    return matches


def match_single_face(outfile, scratch_file, proc, 
                      map_name, c1, 
                      slice_format, slice_order, slice_rotations,
                      face_num, match_types, match_rotations,
                      min_cube_entropy, stop_after): 
    '''
         ------------ WARNING --------------
         THIS IS BASICALLY A VERY, VERY SLOW GREP
         IT WAS ONE OF THE STEPPING-STONES TO UNDERSTAND HOW THIS WAS ALL CONSTRUCTED.
         YOU SHOULD NEVER NEED TO USE THIS.
         PATTERN MATCHING IS MUCH, MUCH FASTER.
         USE PATTERN MATCHING ONCE YOU UNDERSTAND HOW THE PATTERNS WORK.
         ----------- WARNING --------------

        INPUT: A WHOLE BUNCH
        OUTPUT: A JSON FILE OF LOCATIONS OF CUBES THAT HAVE A MATCHING FACE

        Takes in a single cube, and a specified face number, then creates cubes from start_offset to start_offset + bytes_to_read
           comparing all of the types of rotions, match types, etc, looking for a matching face.
    '''
    proc_num, start_offset, bytes_to_read = proc
    matches = {}
    attempted = 0
    total_matches = 0
    #CREATE BUFFER TO MEMORY MAPPED FILE
    shm = shared_memory.SharedMemory(name=map_name)
    buf = shm.buf

    loc = start_offset -1
    end_offset = start_offset + bytes_to_read

    face_entropy = c1.faces_entropy[face_num]
    face = c1.faces[0][face_num]

    while loc < end_offset - 64:
        loc += 1
        attempted += 1
        if attempted%5000 == 0:
            print("PROC: " + str(proc_num) + 
                  " Attempt: " + str(attempted) + 
                  " OF: " + str(bytes_to_read) + 
                  " FRAC: " + str(attempted/bytes_to_read) + 
                  " Matches: " + str(total_matches))

        #Create a cube after checking minimum entropy of sequence string.
        seq = bytes(buf[loc:loc+64]).decode()
        if entropy(seq) < min_cube_entropy:
            continue
        c2 = cube(seq, loc, slice_format, slice_order, slice_rotations)

        ### TYPES OF SEARCHES TO RUN ON C2 dependd on the match_types f,m,c,mc cube_has_x(face, match_rotations, face_entropy)
        for match_type in match_types:
            resp = c2.cube_has_match(face, match_rotations, face_entropy, match_type)
            if resp:
                (the_face_num, the_rotation) = resp
                m = {}
                m['offset'] = c2.start_offset
                m['match_type'] = match_type
                m['rotation'] = the_rotation
                m['face_index'] = the_face_num
                m['slice_format'] = slice_format
                m['slice_order'] = slice_order
                m['slice_rotations'] = slice_rotations
                if scratch_file:
                    f = open(scratch_file, 'w+')
                    f.write('Offset: ' + str(c2.start_offset) + ' ' +
                            'Type: ' + match_type + ' ' +
                            'Rotation: ' + str(the_rotation) + ' ' +
                            'Face #: ' + str(the_face_num) )
                    f.close()
                matches[c2.sequence] = m
                total_matches += 1

            if total_matches >= stop_after:
                break

    shm.close()

    if total_matches > 0:
        dump_json(matches, outfile)
        print("DONE FINDING MATCHING FACES.  Dumped TOTAL " + str(total_matches) + " matches to: " + outfile)
    else:
        print("NO matches")

def match_known_cubes(): 
    '''
        ------------------- WARNING ---------------------
        THIS SHOULD NEVER BE USED.
        IT IS A VERY SLOW GREP ON ALL FACES.
        THERE ARE MUCH BETTER WAYS TO DO IT USING PATTERN MATCHING
         THAT DON'T INVOLVE CREATING WHOLE CUBE OBJECTS AND INTERATING OVER THEIR FACES.
        KEEPING IF FOR MY OWN AMUSEMENT.
        ------------------- WARNING ---------------------
       
        Read in a flat file that contains known cube sequeces.
        Iterate over all cubes in the known cube file, then iterate byte-by-byte over a larger FLAT file
         looking for matches.

        It needs all of the args references removed, insted use passed in variables.
        It nees to memory map the large file so each process doesn't have to map it.
        Changing from the original FASTA format to the FLATTENED sequence.
        Called functions have changed.  Everything has changed.

        I am not even going to try and update this one; it is not worth the effort. 
        Keeping it for prosperity to hopefully inspire somebody to do it better.

        Now go use patterns.

    '''
    stop_after = 999999999
    if args.stop_after:
        stop_after = args.stop_after

    matches = {}
    attempted = 0
    total_matches = 0
    sequences_loaded = 0
    cube_data = load_fasta(args.cube_file)
    big_data = load_fasta_seq(args.infile, args.seq_name) #Search this data

    for c2_seqname in big_data:
        data_to_process = {}
        data_to_process[c2_seqname] = big_data[c2_seqname]
        sequences_loaded += 1
        if sequences_loaded % 100 == 0:
            print("Named Sequences Processed " + str(sequences_loaded) + " Matches: " + str(total_matches))

        for known_cube_seq in known_cubes:
            c1_index = -1
            for c1 in known_cubes[known_cube_seq][0]:
                #for faces in c1.faces[0]: 
                if True:
                    for c2_offset in cubes[c2_seqname]:
                        for c2 in cubes[c2_seqname][c2_offset]:
                            if c2.cube_entropy < args.min_cube_entropy:
                                continue
                            attempted += 1
                            if attempted%250000 == 0:
                                print("Attempt: " + str(attempted) + 
                                      " Matches: " + str(total_matches))
                            facenum = -1
                            for face in c1.faces[0]:
                                facenum += 1
                                resp = c2.cube_find_match(face)
                                if resp:
                                    (the_type, the_rotation, the_face) = resp
                                    total_matches += 1
                                    location = {}
                                    location['c1_face_index'] = facenum
                                    location['c1_start'] = c1.start_offset
                                    location['c2_start'] = c2.start_offset
                                    location['c2_offset'] = c2_offset
                                    location['c1_index'] = c1.cube_index
                                    location['c2_index'] = c2.cube_index
                                    location['c2_face_entropy'] = c2.faces_entropy[the_face]
                                    location['c2_cube_entropy'] = c2.cube_entropy
                                    location['c2_type'] = the_type
                                    location['c2_rotation'] = the_rotation
                                    location['c2_face_index'] = the_face
                                    location['c2_name'] = c2.seq_name
                                    location['c1_raw'] = c1.sequence
                                    location['c2_raw'] = c2.sequence
                                    seq = c2.face_to_seq(face)
                                    if seq in matches:
                                        matches[seq]['count'] += 1
                                        matches[seq]['info'].append(location)
                                    else:
                                        matches[seq] = {}
                                        matches[seq]['count'] = 1
                                        matches[seq]['info'] = []
                                        matches[seq]['info'].append(location)

                                if total_matches >= stop_after:
                                    break
                            if total_matches >= stop_after:
                                break
                        if total_matches >= stop_after:
                            break
                    if total_matches >= stop_after:
                        break
                if total_matches >= stop_after:
                    break
            if total_matches >= stop_after:
                break
        if total_matches >= stop_after:
            break

    if args.outfile:
        if args.summary:
            summary(matches)
        else:
            f = open(args.outfile, 'w+')
            f.write(json.dumps(matches, indent=4))
            f.close()
            print("DONE FINDING MATCHING FACES.  Dumped JSON to: " + args.outfile)
    else:
        if args.summary:
            summary(matches)
        else:
            print(json.dumps(matches, indent=4))
if __name__ == '__main__':
    def clean(name_1, name_2, name_3):
        if os.path.exists(name_1):
            os.unlink(name_1)
        if os.path.exists(name_2):
            os.unlink(name_2)
        if os.path.exists(name_3):
            os.unlink(name_3)

    name_1 = str(random.randint(99999999,999999999999)) + '.tmp'
    name_2 = str(random.randint(99999999,999999999999)) + '.tmp'
    name_3 = str(random.randint(99999999,999999999999)) + '.tmp'




    #### match_single_face.  Use known self-referencial cube
    #Open A file with a single cube -> onesself cube:
    cube_data = "GTTAAATAAATCATGGCTCTAAGACGACTCCATGGAGTCGTCTTAGAGCCATGATTTATTTAAC"
    f = open(name_1, 'w+')
    f.write(cube_data*2)
    f.close()
    c1 = cube(cube_data, 0, '8x8', [0,1,2,3], [0,0,0,0])

    #Memory map the big file
    shm = map_file(name_1, 0, -1)
    map_name = shm.name
    match_single_face(  map_name, c1, name_2, name_3,
                        0, 0, len(cube_data) * 2,
                        '8x8', [0,1,2,3], [0,0,0,0],
                        0, ['mc','c','m'], [0,1,2,3],
                        1.25, 9999 )
    shm.close()
    shm.unlink()
    f = open(name_2, 'r')
    d = f.read()
    f.close()
    d = json.loads(d)
    if len(d) < 3:
        clean(name_1, name_2, name_3)
        raise Exception("TEST FAILURE; match_single_face")
    clean(name_1, name_2, name_3)
    
    print("TESTS PASSED")
        
