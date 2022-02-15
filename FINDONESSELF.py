from UTILS import *
from CUBE import *
from multiprocessing import shared_memory

def find_onesself(outfile, scratch_file, proc, shm_name, min_cube_entropy, min_face_entropy, slice_formats, slice_orders, slice_rotations, opposite_face_rotations_list):

    '''
        Take in a memory-mapped file referece <shm_name> and search though it looking for palendromic-like
            cubes that are most likely the base/reference cubes to start a 3torus/3mobius.

        The proc structure: (proc#, offset, #read bytes) will give the information this process needs to work on the file

        This was originally a REGEX, but was WAAAAAYYYY TOO SLOW!
        This function searches ALL data in a flattened .fa file, or any text file byte by byte.
        It looks for 4x4x4, 8x8, and 16x4 slices all faces where the opposite face is the same pattern but
            rotated, mirrored, and complimented.  As far as the full 64base sequence goes, it is just the palendrome
             except for the center8 bases.
        
        #### NOTE #####
         Some runs may be modified to not to the rotation, mirroring, and complimenting for statistical indications
        ###############

        SLICE_FORMATS is a list of desired formats to search.  3 max - 4x4x4, 8x8, 16x4
        SLICE_ORDERS and SLICE_ROTATIONS are both LIST OF LISTS

        opposite_face_rotations_list is usually [0] or [2].  It is to test what kind of mobious twist to apply to it.
          If 2, which is what I suspect they all are, then for example Face 0 = Face 5 - mirrored, compimented and rotated twice
          If 0, Then Face 0 = Face 5 - mirrored and complimented (No Rotation)
          Both cases, maybe even 1, and 3 also need to be tested.  But most likely will be 0 and 2.
    '''
    proc_number, start_offset, datalen = proc

    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf


    #Contains the total matches for the run.
    counts = {} 
    the_return = {} ### Because now using MP_EXECUTE.. Must be { <key>:[<data>,<data>], <key2>:[<data>]}

    total_steps = len(slice_formats) * len(slice_orders) * len(slice_rotations) * len(opposite_face_rotations_list) * datalen
    steps = 0
    full_matches = 0
    for slice_format in slice_formats:
        counts[slice_format] = {}
        for slice_order in slice_orders:
            counts[slice_format][str(slice_order)] = {}
            for slice_rotation in slice_rotations:
                counts[slice_format][str(slice_order)][str(slice_rotation)] = {}
                for opposite_face_rotation in opposite_face_rotations_list:
                    counts[slice_format][str(slice_order)][str(slice_rotation)][opposite_face_rotation] = {}

                    message = "START: Slice_format: " + str(slice_format) + \
                              " Slice_order: " + str(slice_order) + \
                              " Slice_rotations: " + str(slice_rotation)

                    print(message)

                    counts[slice_format][str(slice_order)][str(slice_rotation)][opposite_face_rotation] = {'total':0, 'all':0, 'full':[]}

                    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
                    cX = cube(fake_cube_seq, 0, slice_format, slice_order, slice_rotation)

                    #Contains the byte positions to extract from the current index for each map
                    maps = {'0':[], '5':[], '1':[], '4':[], '2':[], '3':[]}

                    face_list = [0, 1, 2]#only need pattern for these three,opposite will automatically be the same
                    for this_face in face_list:
                        face_seq = cX.face_to_seq(cX.faces[0][this_face])
                        or_face_seq = cX.face_to_seq(cX.faces[opposite_face_rotation][5-this_face])#Opposite Rotated Face
                        orm_seq = mirror_seq(or_face_seq) #Rotated and mirrored.  Just reference position, Can't compliment
                        for index in range(0,16):
                            maps[str(this_face)].append(fake_cube_seq.find(face_seq[index]))
                            maps[str(5-this_face)].append(fake_cube_seq.find(orm_seq[index]))

                    p = start_offset -1
                    end = start_offset + datalen - 64
                    matches = 0
                    while p < end:
                        p = p+1
                        steps += 1
                        if steps%100000 == 0:
                            print("Proc: " + str(proc[0]) + 
                                  " At step " + str(steps) + " of  " + str(total_steps) + 
                                  " Fraction done: " + str(float(steps)/float(total_steps)) + 
                                  " Full Matches: " + str(full_matches))

                        t = bytes(buf[p:p+64]).decode()
                        face_matches = 0
                        for face in [0,1,2]: #Only first three faces
                            this_face = ''
                            opposite_face = ''
                            for index in range(0,16):
                                this_face += t[ maps[str(face)][index] ]#Index to character in 64 base sequence
                                opposite_face += t[ maps[str(5 - face)][index] ]#Index to character in 64 basesequence
                            opposite_face_compliment = compliment_seq(opposite_face)

                            if this_face == opposite_face_compliment and entropy(this_face) >= min_face_entropy and entropy(list(t)) >= min_cube_entropy:
                                # FOUND A MATCH FOR A SINGLE FACE
                                counts[slice_format][str(slice_order)][str(slice_rotation)][opposite_face_rotation]['total'] += 1 
                                matches += 1
                                face_matches += 1
                        if face_matches == 3:
                            ### FOUND A FULL ONESSELF CUBE.  ALL FACES MATCH OPPOSITE SIDE ROTATED TWICE, MIRRORED, AND COMPIMENTED
                            full_matches += 1
                            counts[slice_format][str(slice_order)][str(slice_rotation)][opposite_face_rotation]['all'] += 1 
                            counts[slice_format][str(slice_order)][str(slice_rotation)][opposite_face_rotation]['full'].append((p, t))
                            if t in the_return:
                                the_return[t].append({'offset':p,
                                                      'opposite_rotation':opposite_face_rotation,
                                                      'slice_format':slice_format,
                                                      'slice_order':slice_order,
                                                      'slice_rotations':slice_rotation})
                            else:
                                the_return[t] = [{'offset':p,
                                                  'opposite_rotation':opposite_face_rotation,
                                                  'slice_format':slice_format,
                                                  'slice_order':slice_order,
                                                  'slice_rotations':slice_rotation}]

                            message = t + '-' + str(p) + '-' + \
                                      slice_format + '-' + str(slice_order) + \
                                      '-' + str(slice_rotation) + '-' + str(opposite_face_rotation) + "\n"
                            print(message)
                            scratch(message, scratch_file)

    if outfile:
        dump_json(the_return, outfile)
        print("Wrote output to: " + outfile)
    else:
        print(json.dumps(the_return, indent=4))

if __name__ == '__main__':
    name_1 = str(random.randint(99999999,999999999999)) + '.tmp'
    #--create_3torus --torus_dimensions 1,1,1 --slice_format '8x8' --slice_order 0,1,2,3 --slice_rotations 0,0,0,0
    f = open(name_1, 'wb+')
    f.write(b'TGGCCCTCAATTACTCGCCACAAGCAAGAGGATCCTCAAGCAAGTGGCGAGTAATTGAGGGCCA')#4x4x4 0,1,2,3, 0,0,0,0
    f.write(b'GCGCTAGTCTCGGAATTGGGCAAGTGCGCACGCGTGCGCACAAGCCCAAAACCGAGACTAGCGC')#8x8 0,1,2,3 0,0,0,0
    f.write(b'ATTCCAGCGGGCATAGGAACTTAGAAATGCATAAACAGGTAAAGGCTCACAGTCCGTCTTCACG')#16x4 3,2,0,1 0,1,2,3
    f.close()

    shm = map_file(name_1, 0, -1)
    shm_name = shm.name
    os.unlink(name_1)
    
    outfile = 'crap.out'
    scratch_file = 'crap.scratch'
    proc = (0, 0, 64*3)
    min_cube_entropy = 0.0
    min_face_entropy = 0.0
    slice_formats = ['4x4x4', '8x8', '16x4']
    slice_orders = [[0,1,2,3], [3,2,0,1]]
    slice_rotations = [[0,0,0,0], [0,1,2,3]]
    find_onesself(outfile, scratch_file, proc, shm_name, min_cube_entropy, min_face_entropy, slice_formats, slice_orders, slice_rotations, [2])
    shm.close()
    shm.unlink()
    os.unlink(outfile)
    os.unlink(scratch_file)
    print("TEST PASSED")
