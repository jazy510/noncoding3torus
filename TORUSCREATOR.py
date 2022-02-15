from UTILS import *
from CUBE import * 

def cube_from_faces(stan, faces):
    '''
        Given an object or array of faces, create a cube from them.
        Create a sequence from the faces, then use that sequence to create a cube.
        Used for propogating changes through the block of blocks network
    '''
    seq = create_cube_seq_from_faces(stan, faces)
    return cube(seq, 0, stan[0], stan[1], stan[2])


def create_onesself_seq_old(stan, message_seq):
    '''
        ------------- WARNING --------------
            THIS DOES NOT WORK.
            SOMETHING IS WRONG THAT WAS CAUSING COLLISSIONS
            SCRAPPED IT AN UPDATED/PROPOGATED A SINGLE BASE CHANGE THROUGH
            THE WHOLE NETWORK IN THE NEW ONE.
            PROBABLY JUST DOING SOMETHING STUPID HERE. 
            GUESSTING OVERWRITING A BASE ON A CORNER OR SOMETHING.
        ------------- WARNING --------------
        Create one cube where all faces match the face opposite of it.
        This is the reverse of find_onesself()
        The opposite face will be rotated twice, complimented, and mirrored

        ---- ASSUMES A MATCH IS A MIRROR, COMPLIMENT, DOUBLE ROTATION OF THE OPPOSTITE FACE ------
        ---- IF THE STANDARD/CONVENTION IS CHANGED TO DO SLICE ROTATIONS, THEN THIS WILL NEED TO CHANGE ----

    '''
    if len(message_seq) != 8:
        raise Exception("Message to create_onesself_seq must be 8 bases long")

    #Create a reference cube.
    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fake_cube = cube(fake_cube_seq, 0, stan[0], stan[1], stan[2]) 


    cube_seq = list("."*64)
    
    for facenum in range(0,3):
        fake_seq       = fake_cube.face_to_seq(fake_cube.faces[0][facenum])
        fake_seq_orm   = fake_cube.face_to_seq(fake_cube.mirror_face(fake_cube.faces[2][5-facenum])) #opposite face rotated

        #To Define the ordering of the opposite face, mirror, rotate, compliment the original face.
        #  Then map directly onto the opposite face.
        #  Once mapping is done, find the location of the opposite face in the original fake sequence

        for i in range(0, 16):
            #Face values mapped to input sequence locations
            fake_loc     = fake_cube_seq.find(fake_seq[i])
            fake_loc_orm = fake_cube_seq.find(fake_seq_orm[i])

            if cube_seq[fake_loc] == '.' and cube_seq[fake_loc_orm] == '.':
                #Can fill in with new random sequence
                seq = random_seq(1)
                cube_seq[fake_loc] = seq
                cube_seq[fake_loc_orm] = compliment_seq(seq)

            elif cube_seq[fake_loc] != '.' and cube_seq[fake_loc_orm] == '.':
                seq = cube_seq[fake_loc]
                cube_seq[fake_loc_orm] = compliment_seq(seq)

            elif cube_seq[fake_loc] == '.' and cube_seq[fake_loc_orm] != '.':
                seq = cube_seq[fake_loc_orm]
                cube_seq[fake_loc] = compliment_seq(seq)

            else:
                continue

    s = ''.join(cube_seq)
    ms = list(message_seq)
    l = 0
    for m in ms:
        l = s.find('.', l+1)
        cube_seq[l] = m
    s = ''.join(cube_seq)
    return s


def create_cube_seq_from_faces(stan, faces):
    '''
        Create a sequence from a list of all six faces.  

        If a sequence is impossible/contradictory because the data in the faces is wrong,
         an exception is thrown.

        It does not check the validity of the data in the faces.

        It matches the location of the face element to a location to a fake, but unique input stream.

    '''
    if len(faces) != 6:
        raise Exception("create_cube_seq_from_faces must be passed 6 faces")

    #Create a reference cube.
    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fake_cube = cube(fake_cube_seq, 0, stan[0], stan[1], stan[2]) 


    cube_seq = list('.'*64)
    for facenum in range(0,6):
        fake_face_seq = list(fake_cube.face_to_seq(fake_cube.faces[0][facenum]))
        new_face_seq = list(fake_cube.face_to_seq(faces[facenum]))
        for x in range(0, 16):
            loc = fake_cube_seq.find(fake_face_seq[x])
            if new_face_seq[x] != '.':
                cube_seq[loc] = new_face_seq[x]

    return ''.join(cube_seq)

def adjacent(size_list, l, w, h):
    '''
        Given a list of the 3 Dimensional size of the cube of cubes, and the location of cubes and faces
         adjacent to it, return a dict containing THIS cube's face number, and the LHW coordinates of the 
         adjacent Cube and the face number.
    '''
    adj = {}
    adj[0] = (l, w, (h+1)%size_list[2], 5)
    adj[5] = (l, w, (h-1)%size_list[2], 0)
    adj[1] = ((l+1)%size_list[0], w, h, 4)
    adj[4] = ((l-1)%size_list[0], w, h, 1)
    adj[2] = (l, (w+1)%size_list[1], h, 3)
    adj[3] = (l, (w-1)%size_list[1], h, 2)
    return adj

def update_torus_faces(stan, faces):
    '''
        NO LONGER USED
        Make a cube from the updated sequence and update the faces in torus.
    '''
    seq = create_cube_seq_from_faces(stan, faces)
    temp_cube = cube(seq, 0, stan[0], stan[1], stan[2]) 
    return list_to_dict(temp_cube.faces[0])

def create_NxNxN_seq_old(stan, size_list, message_seq):
    '''
        ------------- WARNING -------------
           THIS DOES NOT WORK! What happens is that when we fill in blanks, the blanks propogate to neighbors
            and the neighbors down the line may already have a block that doens't match...
            Need an efficient way to create a onesself block that can be propogated but doesn't conflict with itself.
        ------------- WARNING -------------
        This creates a cube of cubes of size NxNxN in a 3-Torus, 3-Mobius, 3-Mobius-Torus, whatever it is called
        size_list will be a list of three elements [L, W, H] 

        ---- Assuming ONESSELF cube is the anchor
        ---- Assuming only one ONESSELF cube
        ---- Assuming the cube is in a corner, could be in the center, but doesn't really matter, self organizing.
        ---- Assuming that the entire cube is NOT ONESSELF cubes; implies not all stright lines are the same seq/face and match.
        ---- Assuming that only the edges extending from the ONESSELF cube are connected end-to-end.
        ---- Assuming all other cubes in the cube of cubes have faces matching one other face in the cube.
        ---- Assuming No FEC or CRC/Error Detection/Correction  in either Faces or Center8 (But they could)
        ---- Assuming Faces carry no information other than ordering (But they could)


        Will have to hold cube/face information in an object.  
        The object will hold faces[]-> length of 6, message str, c->cube, seq, and adjacent cubes and faces
        The object for each will be stored in the 3D array

        L = 1-4 Right-Left/East-West
        W = 2-3 Forward-Backwards/North-South
        H = 0-5 Up-Down

        ADJACENT CUBE/FACE
        Convention - ONLY FOR THIS PROGRAM!!!:
         h = 0 (UP +1), 5(down -1)
         l = 1 (Right +1) ,4(left -1)
         w = 2 (Forward +1), 3(reverse -1)
          
          Height
               ^   Width
               |  /
               | /
               |/
                --------> Length
    '''
    final_seq_list = []

    #reference cube for building other cubes.
    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fake_cube = cube(fake_cube_seq, 0, stan[0], stan[1], stan[2]) 

    total_cubes = size_list[0] * size_list[1] * size_list[2]

    if len(message_seq) != total_cubes * 8:
        raise Exception("Message Seq must be of length: " + str(total_cubes * 8))

    #L = 1-4 Right-Left/East-West
    #W = 2-3 Forward-Backwards/North-South
    #H = 0-5 Up-Down
    #Start with a self-cube - Location = 0,0,0

    #Iterate over all and build the info object for each
    lmax = size_list[0]
    wmax = size_list[1]
    hmax = size_list[2]
    torus = []
    for l in range(0, lmax):
        torus.append([])
        for w in range(0, wmax):
            torus[l].append([])
            for h in range(0, hmax):
                torus[l][w].append([])
                adj = adjacent(size_list, l, w, h)
                f = {0:fake_cube.seq_to_face('.'*16), 
                     1:fake_cube.seq_to_face('.'*16), 
                     2:fake_cube.seq_to_face('.'*16), 
                     3:fake_cube.seq_to_face('.'*16), 
                     4:fake_cube.seq_to_face('.'*16), 
                     5:fake_cube.seq_to_face('.'*16)}

                torus[l][w][h] = {'faces':f, 'message':'.'*8, 'c':None, 'seq':None, 'adjacent':adj}

    torus = initialize_torus(size_list, stan)


    #Will have to construct faces, then from the faces construct cubes.
    onesselfseq = create_onesself_seq(stan, '.'*8)
    onesself_cube = cube(onesselfseq, 0, stan[0], stan[1], stan[2]) 
    torus[0][0][0]['faces'] = list_to_dict(onesself_cube.faces[0])
    torus[0][0][0]['seq'] = onesselfseq

    #Just like a puzzle, you have to fill in the border first.  
    #In this case, just the LHW lines extending from the onesself cube.

    #only increment L
     #l = 1 (Right +1) ,4(left -1)
    for l in range(1, size_list[0]):
        torus[l][0][0]['faces'][1] = torus[0][0][0]['faces'][1]
        torus[l][0][0]['faces'][4] = torus[0][0][0]['faces'][4]
        torus[l][0][0]['faces'] = update_torus_faces(stan, torus[l][0][0]['faces'])


    #only increment W
     #w = 2 (Forward +1), 3(reverse -1)
    for w in range(1, size_list[1]):
        torus[0][w][0]['faces'][2] = torus[0][0][0]['faces'][2]
        torus[0][w][0]['faces'][3] = torus[0][0][0]['faces'][3]
        torus[0][w][0]['faces'] = update_torus_faces(stan, torus[0][w][0]['faces'])

    #only increment H
     #h = 0 (UP +1), 5(down -1)
    for h in range(1, size_list[2]):
        torus[0][0][h]['faces'][0] = torus[0][0][0]['faces'][0]
        torus[0][0][h]['faces'][5] = torus[0][0][0]['faces'][5]
        torus[0][0][h]['faces'] = update_torus_faces(stan, torus[0][0][h]['faces'])


    #Frame built.  
    #Loop over faces filling in missing pieces with random face data
    empty_face = fake_cube.seq_to_face('.'*16)
    for l in range(0, size_list[0]):
        for w in range(0, size_list[1]):
            for h in range(0, size_list[2]):
                for f in range(0,6):
                    al, aw, ah, af = torus[l][w][h]['adjacent'][f]
                    this_face = torus[l][w][h]['faces'][f]
                    this_face_rmc = fake_cube.rmc_face(this_face,2)
                    this_face_rmc_seq = list(fake_cube.face_to_seq(this_face_rmc))

                    that_face = torus[al][aw][ah]['faces'][af]
                    that_face_seq = list(fake_cube.face_to_seq(that_face))
                    
                    #Loop over this face.  If Dot in both, generate a new one and put in place 
                    for index in range(0, 16):
                        if this_face_rmc_seq[index] == '.' and that_face_seq[index] == '.':
                            this_face_rmc_seq[index] = random_seq(1)
                            that_face_seq[index] = this_face_rmc_seq[index]
                        elif this_face_rmc_seq[index] != '.' and that_face_seq[index] == '.':
                            that_face_seq[index] = this_face_rmc_seq[index]
                        elif this_face_rmc_seq[index] == '.' and that_face_seq[index] != '.':
                            this_face_rmc_seq[index] = that_face_seq[index]
                        elif this_face_rmc_seq[index] != that_face_seq[index]:
                            raise Exception("THE ADJACENT FACES DO NOT MATCH!")

                    #rmc that rmc seq to return to normal.  Then set it equal.
                    # Then for both faces, update the torus faces for the next iteration of the loop
                    this_face_rmc_seq = ''.join(this_face_rmc_seq)
                    this_face_rmc = fake_cube.seq_to_face(this_face_rmc_seq)
                    this_face = fake_cube.rmc_face(this_face_rmc, 2)
                    torus[l][w][h]['faces'][f] = this_face
                    torus[l][w][h]['faces'] = update_torus_faces(stan, torus[l][w][h]['faces'])

                    that_face_seq = ''.join(that_face_seq)
                    that_face = fake_cube.seq_to_face(that_face_seq)
                    torus[al][aw][ah]['faces'][af] = that_face
                    torus[al][aw][ah]['faces'] = update_torus_faces(stan, torus[al][aw][ah]['faces'])


                #Fill in the Message for each block
                torus[l][w][h]['message'] = message_seq[l*w*h:(l*w*h) + 8]
                ms = torus[l][w][h]['message']

    raise Exception("INCOMPLETE FUNCTION - REVISIT IF BORED")

def initialize_torus(size_list, stan):
    #Create a reference cube.
    fcs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fc = cube(fcs, 0, stan[0], stan[1], stan[2]) 

    #Iterate over all and build the info object for each
    lmax = size_list[0]
    wmax = size_list[1]
    hmax = size_list[2]
    torus = []
    for l in range(0, lmax):
        torus.append([])
        for w in range(0, wmax):
            torus[l].append([])
            for h in range(0, hmax):
                torus[l][w].append([])
                adj = adjacent(size_list, l, w, h)
                f = {0:fc.seq_to_face('.'*16), 
                     1:fc.seq_to_face('.'*16), 
                     2:fc.seq_to_face('.'*16), 
                     3:fc.seq_to_face('.'*16), 
                     4:fc.seq_to_face('.'*16), 
                     5:fc.seq_to_face('.'*16)}
                c = cube_from_faces(stan, f)
                torus[l][w][h] = {'faces':c.faces[0], 'message':'.'*8, 'c':c, 'seq':c.sequence, 'adjacent':adj}
    return torus


def create_3torus(stan, size_list, message_seq):
    '''
        Create one cube where all faces match the face opposite of it one base at a time.
        Then propogate the changes through the entire cube network to ensure no conflicts.


        The center 4 on each face are fair game that aren't at 0,0,0, or extending the border.
        Even though they could all be applied at the same time and propogated to the next cube,
         taking it safe this time because of failures trying to contruct the torus (See above code).
        The problem lies along the edges and in the corners; especailly the corners because they are used by 3 faces.

        If not properly accounted for the differences spread out across a network of cubes
         and eventually there is a collision when it propogates back.

        This creates a cube of cubes of size NxNxN in a 3-Torus, 3-Mobius, 3-Mobius-Torus, whatever it is called
        size_list will be a list of three elements [L, W, H] 

        ---- Assuming ONESSELF cube is the anchor
        ---- Assuming only one ONESSELF cube
        ---- Assuming The opposite face will be rotated twice, complimented, and mirrored. SLice rotations could change this
        ---- Assuming the onesself cube is in a corner, could be in the center, but doesn't really matter, self organizing.
        ---- Assuming that the entire cube is NOT ONESSELF cubes; implies not all stright lines are the same seq/face and match.
        ---- Assuming that only the faces extending out from the ONESSELF cube are connected end-to-end.
        ---- Assuming all other cubes in the cube of cubes have faces matching one other face in the cube.
        ---- Assuming No FEC or CRC/Error Detection/Correction in either Faces or Center8 (But they could)
        ---- Assuming Center 8 sequence could be a 1:X redundancy FEC that is encoded in the message sequence.
        ---- Assuming the Center 8 carry the intended message.  Could be carried in faces, just not for this test.
        ---- Assuming Faces carry no information other than ordering (But they could)
        
        For THIS EXAMPLE, and THIS EXAMPLE only, the message sequence will need to be 8 * the nubmer of cubes long.

        The message sequence FOR THIS EXAMPLE will be both forward and reversed before passing in.
        It will be mapped in order from an LWH nested for loop starting at the onesself cube. 
        The message could be read in the forward or reverse direction.  This will provide the 1:1 FEC.
        The message bases are placed in order as they appear in the sequence, NOT ANYTHING TO DO WITH SLICE/FACE ORDERING

        Will have to hold cube/face information in an dict.  
        The dict will hold faces[]-> length of 6, message str, c->cube, seq, and adjacent cubes and faces
        The object for each will be stored in the 3D array that represents the 3D cube/Torus/Mobius

        L = 1-4 Right-Left/East-West
        W = 2-3 Forward-Backwards/North-South
        H = 0-5 Up-Down

        ADJACENT CUBE/FACE
        Convention - ONLY FOR THIS PROGRAM!!! DO NOT ADOPT IT!:
         h = 0 (UP +1), 5(down -1)
         l = 1 (Right +1) ,4(left -1)
         w = 2 (Forward +1), 3(reverse -1)
          
          Height
               ^   Width
               |  /
               | /
               |/
                --------> Length
    '''
    mess_l = 8 * size_list[0] * size_list[1] * size_list[2]
    if len(message_seq) != mess_l:
        raise Exception("Message for create_3torus must be 8*L*W*H: " + str(mess_l) + " Not: " + str(len(message_seq)))

    #Create a reference cube.
    fcs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fc = cube(fcs, 0, stan[0], stan[1], stan[2]) 

    #Initialize empty torus
    torus = initialize_torus(size_list, stan)

    lmax = size_list[0]
    hmax = size_list[1]
    wmax = size_list[2]

    #TAKE CARE OF THE ONESSELF CUBE FIRST AND PROPOGATE IT THROUGH THE NETWORK.
    # THIS TAKES A LONG TIME BECAUSE WE ARE CREATING CUBES FOR EVERY SMALL CHANGE.
    #  CHANGES ARE PROPOGATED FORWARD AND BACKWARD THROUGH THE CUBE NETWORK, MAKING A LOT OF WORK!
    for l in range(0, lmax):
        for w in range(0, wmax):
            for h in range(0, hmax):
                if l == 0 and w == 0 and h == 0:
                    cs = torus[l][w][h]['seq']
                    c = torus[l][w][h]['c']
                    c_faces = c.faces[0]
                    #ONLY DO THIS FOR CUBE 0, WHICH IS ALWAYS FIRST.
                    for facenum in range(0,6):
                        print("WORKIN ON CUBE: " + str(l) + "," + str(w) + "," + str(h) + " Face: " + str(facenum))
                        o_face = c_faces[5-facenum]
                        o_face_rmc = fc.rmc_face(o_face, 2)
                        c_face = c_faces[facenum]
          
                        for x in range(0,4):
                            for y in range(0,4):
                                changed = False
                                if c_face[x][y] == '.'and o_face_rmc[x][y] == '.':
                                    c_face[x][y] = random_seq(1)
                                    changed = True
                                elif c_face[x][y] == '.' and o_face_rmc[x][y] != '.':
                                    c_face[x][y] = o_face_rmc[x][y]
                                    changed = True
                                ### NOT GOING TO DO FORWARD PROPOGATION HERE.  DO IT DOWN BELOW.
                                if not changed:
                                    continue

                                c_faces[facenum] = c_face
                                c = cube_from_faces(stan, c_faces)
                                c_faces = c.faces[0]
                                o_face = c_faces[5-facenum]
                                o_face_rmc = fc.rmc_face(o_face, 2)
                                c_face = c_faces[facenum]

                                #NEED TO REAPPLY BACK TO ONESSELF CUBE
                                torus[l][w][h]['c'] = c
                                torus[l][w][h]['seq'] = c.sequence
                                torus[l][w][h]['faces'] = c.faces

                                #COPY THIS FACENUM TO ALL CUBES IN A GIVEN ROW
                                if facenum == 1 or facenum == 4:
                                    for n in range(1, lmax):
                                        torus[n][0][0]['faces'][facenum] = c_face
                                        torus[n][0][0]['c'] = cube_from_faces(stan, torus[n][0][0]['faces'])
                                        torus[n][0][0]['seq'] = torus[n][0][0]['c'].sequence
                                elif facenum == 2 or facenum == 3:
                                    for n in range(1, wmax):
                                        torus[0][n][0]['faces'][facenum] = c_face
                                        torus[0][n][0]['c'] = cube_from_faces(stan, torus[0][n][0]['faces'])
                                        torus[0][n][0]['seq'] = torus[0][n][0]['c'].sequence
                                elif facenum == 0 or facenum ==5:
                                    for n in range(1, hmax):
                                        torus[0][0][n]['faces'][facenum] = c_face
                                        torus[0][0][n]['c'] = cube_from_faces(stan, torus[0][0][n]['faces'])
                                        torus[0][0][n]['seq'] = torus[0][0][n]['c'].sequence

                                torus = propogate(stan, size_list, torus)
                else: 
                    #ALL OTHER CUBES NOT 0,0,0
                    cs = torus[l][w][h]['seq']
                    c = torus[l][w][h]['c']
                    c_faces = c.faces[0]

                    for f in range(0,6):
                        print("WORKIN ON CUBE: " + str(l) + "," + str(w) + "," + str(h) + " Face: " + str(f))
                        al, aw, ah, af = torus[l][w][h]['adjacent'][f]
                        ac_faces = torus[al][aw][ah]['c'].faces[0]
                        a_face = ac_faces[af]
                        a_face_rmc = c.rmc_face(a_face, 2)
                        c_face = c_faces[f]
           
                        for x in range(0,4):
                            for y in range(0,4):
                                changed = False
                                if c_face[x][y] == '.'and a_face_rmc[x][y] == '.':
                                    c_face[x][y] = random_seq(1)
                                    changed = True
                                elif c_face[x][y] == '.' and o_face_rmc[x][y] != '.':
                                    c_face[x][y] = o_face_rmc[x][y]
                                    changed = True
                                ### NOT GOING TO DO FORWARD PROPOGATION HERE.  DO IT DOWN BELOW.

                                if not changed:
                                    continue

                                c_faces[f] = c_face
                                c = cube_from_faces(stan, c_faces)
                                c_faces = c.faces[0]
                                a_face = c_faces[5-f]
                                a_face_rmc = fc.rmc_face(a_face, 2)
                                c_face = c_faces[f]

                                #NEED TO REAPPLY BACK TO SELF -> Then propogate
                                torus[l][w][h]['c'] = c
                                torus[l][w][h]['seq'] = c.sequence
                                torus[l][w][h]['faces'] = c.faces

                                torus = propogate(stan, size_list, torus)
    
    #LOOP THROUGH APPLYING MESSAGE INFORMATION
    #NO ASSUMPTIONS OF MESSAGE CONTENT OR FORMAT ARE MADE HERE.
    # THEY ARE APPLIED TO THE '.' AS THEY COME, NOT FACE ORDERING.
    m_locations = []
    loc = 0
    test_seq = torus[0][0][0]['seq']

    while True:
        z = test_seq.find('.', loc)
        if z == -1:
            break
        loc = z + 1
        m_locations.append(z)
    
    cube_count = 0
    for l in range(0, lmax):
        for w in range(0, wmax):
            for h in range(0, hmax):
                s = list(torus[l][w][h]['seq'])
                for x in range(0, 8):
                    s[m_locations[x]] = message_seq[cube_count*8 + x]
                s = ''.join(s)
                torus[l][w][h]['seq'] = s
                torus[l][w][h]['c'] = cube(s, 0, stan[0], stan[1], stan[2])
                torus[l][w][h]['faces'] = c.faces[0]
                cube_count += 1

    return torus
                    
def propogate(stan, size_list, torus):
    changed = True
    while changed == True:
        changed = False
        for l in range(0,size_list[0]):
            for w in range(0,size_list[1]):
                for h in range(0,size_list[2]):
                    for f in range(0,6):
                        al, aw, ah, af = torus[l][w][h]['adjacent'][f]
                        #Get this face and adjacent face.
                        c = torus[l][w][h]['c']
                        c_faces = c.faces[0]
                        ac_faces = torus[al][aw][ah]['c'].faces[0]

                        #Rotate, mirror, and compliment opposing faces for comparison.
                        a_face = ac_faces[af]
                        a_face_rmc = c.rmc_face(a_face, 2)
                        c_face = c_faces[f]
                        for i in range(0, 4):
                            for j in range(0,4):
                                if c_face[i][j] == a_face_rmc[i][j]:
                                    #Nothing to do. No forward or reverse propogation
                                    pass
                                elif c_face[i][j] == '.' and a_face_rmc[i][j] != '.':
                                    #Backward Propogation
                                    c_face[i][j] = a_face_rmc[i][j]
                                    changed = True
                                elif c_face[i][j] != '.' and a_face_rmc[i][j] == '.':
                                    a_face_rmc[i][j] = c_face[i][j]
                                    changed = True
                                elif c_face[i][j] != a_face_rmc[i][j]:
                                    #Collision
                                    print("PROPOGATE FOUND A COLLISION")
                                    return None
                        if changed:
                            #Update FACES and TORUS 
                            c_faces[f] = c_face
                            ac_faces[af] = c.rmc_face(a_face_rmc,2) #Rotate back after changes
                            torus[l][w][h]['c'] = cube_from_faces(stan, c_faces)
                            torus[l][w][h]['seq'] = torus[l][w][h]['c'].sequence
                            torus[l][w][h]['faces'] = torus[l][w][h]['c'].faces[0]

                            torus[al][aw][ah]['c'] = cube_from_faces(stan, ac_faces)
                            torus[al][aw][ah]['seq'] = torus[al][aw][ah]['c'].sequence
                            torus[al][aw][ah]['faces'] = torus[al][aw][ah]['c'].faces[0]
    return torus


if __name__ == '__main__':
    stan = ('8x8', [0,1,2,3], [0,0,0,0])

    #SEQ FROM FACES
    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    fake_cube = cube(fake_cube_seq, 0, stan[0], stan[1], stan[2]) 
    faces = fake_cube.faces[0]
    seq = create_cube_seq_from_faces(stan, faces)
    expected = 'abcdefghijklm..pqrstu..xyzABCDEFGHIJKLMNO..RSTUVW..Z0123456789$!'
    if seq != expected:
        print(seq)
        print(expected)
        raise Exception("SEQ FROM FACES FAILURE")

    #ADJACENT
    adj = adjacent([4,4,4], 0,3,1)
    if adj != {0: (0, 3, 2, 5), 5: (0, 3, 0, 0), 1: (1, 3, 1, 4), 4: (3, 3, 1, 1), 2: (0, 0, 1, 3), 3: (0, 2, 1, 2)}:
        raise Exception("ADJACENT FAILURE")

    runs = []
    message = 'X'
    message_bases = ascii_to_base(message)
    message_bases_rc = compliment_seq(reverse_seq(message_bases))
    message_final = interleave_messages(message_bases, message_bases_rc, 2)
    runs.append(([1,1,1], message_final))

    message = 'X'*2*2*2
    message_bases = ascii_to_base(message)
    message_bases_rc = compliment_seq(reverse_seq(message_bases))
    message_final = interleave_messages(message_bases, message_bases_rc, 2)
    runs.append(([2,2,2], message_final))

    message = 'X'*3*2*1
    message_bases = ascii_to_base(message)
    message_bases_rc = compliment_seq(reverse_seq(message_bases))
    message_final = interleave_messages(message_bases, message_bases_rc, 2)
    runs.append(([3,2,1], message_final))

    message = 'THIS IS PRIOR ART! THIS IS NOT YOURS! I DO NOT CLAIM IT AS MINE!'
    message_bases = ascii_to_base(message)
    message_bases_rc = compliment_seq(reverse_seq(message_bases))
    message_final = interleave_messages(message_bases, message_bases_rc, 2)

    runs.append(([4,4,4], message_final))

    for size_list, message_final in runs:
        #CREATE A 3TORUS
        torus = create_3torus(stan, size_list, message_final)    
        print("="*80)
        for l in range(0, size_list[0]):
           for w in range(0, size_list[1]):
              for h in range(0, size_list[2]):
                  print(torus[l][w][h]['seq'] + " - " + str(l) + "," + str(w) + "," + str(h))

