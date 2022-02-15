from UTILS import *

class cube(object):
    """
        A 4x4x4 die/Cube will be constructed from four slices of 4x4 faces/double lists.

        --slice_format defines how the Bases are Read in and layed onto the slices.
        4x4x4 will read in and fill the first slice, then the second...
        8x8 will read in and fill in the top row of the first two slices, the second row, the third, then final row
           it will then read in and fill the top row of the next two slices.....
        16x4 will fill in the top row of all of the slices, then the second row..

        --slice_order is changed AFTER the slices have been mapped, but before any slice rotations.
          input is an array, default is [0,1,2,3]. 
          Each slice must be used ONCE and only ONCE
          BE VERY THOUGHTFUL OF THIS WHEN TRYING TO CREATE A PATTERN TO FIND A MATCH TO ANOTHER FACE.
          THE SLICES WILL HAVE TO BE PLACED BACK INTO THE ORDER THEY WERE READ IN BEFORE CREATING THE SEQUENCE.

          an input of [1,0,2,3] simply puts slice one on top as the ZERO indexed slice, and 0 and index 1.

        --slice_rotations defines how the slices will be rotated after mapping and ordering, before face construction
         it is a list with each index in the list matching the index of the slices.
         eg: slice_rotations = [3,1,0,2], will rotate slice 0 three times, slice 1 once, not rotate slice 2, and slice 3 twice


        Will use a die as a reference, but zero indexed in code insted of 1 indexed.
        Will use convention of a die, reference of looking down at a die sitting on a table:
          "1" face pointing up, "6" face down.
          "2" face will be on the right, "5" on the left.
          "4" in the "south" position, and "3" in the north.

        Faces will have to be consctructed from the various pieces of the slices, after ordering and rotations. 
        Die Face 0 is s[0] 
        Die Face 3 is s[3] 

        Reading of faces will mean orienting the face "UP" and reading from [0][0] -> [0][3] ... [3][0] -> [3][3]
           Or just changing our perspective to the appropriate face and reading as above.

        Compute all Compliments, Mirror, and Rotations of faces and edges on object creation.  
        Compliment -> A->T, T->A, C->G, G->C
        MIRROR -> ATGC -> GCTA
                  AATT -> TTAA
                  GGCC -> CCGG
                  GCTA -> ATCG

        Rotation  ->  AAAA -> CGTA -> CCCC -> ATGC -> AAAA
                      TTTT    CGTA    GGGG    ATGC    TTTT
                      GGGG    CGTA    TTTT    ATGC    GGGG
                      CCCC    CGTA    AAAA    ATGC    CCCC

        All Faces -> Normal, compliment, or Mirrored may have rotaions applied to them.
        All versions will be referenced by the number of rotations that have been applied
        faces = {0:face array, 1:face array} 
        faces_c = {0:compliment, not rotated 1:...} #You have such a lovely face. ;)
        faces_m = {0:mirrored face array not rotated, 1:mirrored and rotated once}
        faces_mc = {0:mirrored, complimented, not rotated, 1:..} #I take it back Mr. Ugly pants :p

        There will be BILLIONS and BILLIONS of comparisons.
        Runtime computations turned something that should take 1 hour into 20 hours.
        There is no need for runtime computation when it can easily be done at creation time


        Initially I was working with edges, but this is making an assumption that edges may
         be used to give orientation information if a full face is not matched.
        Instead I considered subfaces.  Subfaces are just rows, columns, and diagonals of a face.
        We may want to find the count matching subfaces to determine the strength of the match, and to see if orientation
         is possible.  Orientation is not possible if only an edge is matched because that edge could match another face.
         Any other row, column, or diagonal in addition can be used for orientation.
        But only one row or column is a pretty weak match.  Why not just use the full face?
        Even two rows of columns is still fairly weak, and at that point you are up to half of the full 16 base pairs of a face.

        Now that I think of it.  I am skipping subfaces/edges/diagonals all together.  Too prone to error, not enough specificity...

    """
    def __init__(self, rawdata, start_offset, slice_format, slice_order, slice_rotations):
        self.sequence = rawdata
        self.start_offset = start_offset
        self.slice_format = slice_format
        self.slice_order = slice_order
        self.slice_rotations = slice_rotations
        self.cube_entropy = entropy(self.sequence)
        d = self.sequence
        loc = 0
        loc1 = 1
        s = []

        #DO SLICE FORMAT
        if self.slice_format == '4x4x4':
            for x in range(0,4):
                b = [ [d[loc],    d[loc+1],  d[loc+2],  d[loc+3]],
                      [d[loc+4],  d[loc+5],  d[loc+6],  d[loc+7]],
                      [d[loc+8],  d[loc+9],  d[loc+10], d[loc+11]],
                      [d[loc+12], d[loc+13], d[loc+14], d[loc+15]] ]
                s.append(b)
                loc += 16
                loc1 += 16

        elif self.slice_format == '8x8': #probably a slick way to do this
            for x in range(0, 2):
                a = [[d[loc],    d[loc+1],  d[loc+2],  d[loc+3]],
                     [d[loc+8],  d[loc+9],  d[loc+10], d[loc+11]],
                     [d[loc+16], d[loc+17], d[loc+18], d[loc+19]],
                     [d[loc+24], d[loc+25], d[loc+26], d[loc+27]] ]
                s.append(a)

                b = [[d[loc+4],  d[loc+5],  d[loc+6],  d[loc+7]],
                     [d[loc+12], d[loc+13], d[loc+14], d[loc+15]],
                     [d[loc+20], d[loc+21], d[loc+22], d[loc+23]],
                     [d[loc+28], d[loc+29], d[loc+30], d[loc+31]] ]
                s.append(b)

                loc += 32

        elif self.slice_format == '16x4': #And this too.
                a = [[d[loc],    d[loc+1],  d[loc+2],  d[loc+3]],
                     [d[loc+16], d[loc+17], d[loc+18], d[loc+19]],
                     [d[loc+32], d[loc+33], d[loc+34], d[loc+35]],
                     [d[loc+48], d[loc+49], d[loc+50], d[loc+51]] ]
                s.append(a)

                b = [[d[loc+4],  d[loc+5],  d[loc+6],  d[loc+7]],
                     [d[loc+20], d[loc+21], d[loc+22], d[loc+23]],
                     [d[loc+36], d[loc+37], d[loc+38], d[loc+39]],
                     [d[loc+52], d[loc+53], d[loc+54], d[loc+55]] ]
                s.append(b)

                c = [[d[loc+8],  d[loc+9],  d[loc+10], d[loc+11]],
                     [d[loc+24], d[loc+25], d[loc+26], d[loc+27]],
                     [d[loc+40], d[loc+41], d[loc+42], d[loc+43]],
                     [d[loc+56], d[loc+57], d[loc+58], d[loc+59]] ]
                s.append(c)

                d = [[d[loc+12], d[loc+13], d[loc+14], d[loc+15]],
                     [d[loc+28], d[loc+29], d[loc+30], d[loc+31]],
                     [d[loc+44], d[loc+45], d[loc+46], d[loc+47]],
                     [d[loc+60], d[loc+61], d[loc+62], d[loc+63]] ]
                s.append(d)

                loc += 64

        else:
            raise Exception("Incorrect slice format: " + self.slice_format)

        #DO SLICE ORDERING
        temp = []
        for x in self.slice_order:
            temp.append(s[x])
        s = temp 


        #DO SLICE ROTATIONS
        for x in range(0,4):
            s[x] = self.rotate_face(s[x], self.slice_rotations[x])
        self.slices = s

        #CONSTRUCT CENTER 8
        self.center8 = [s[1][1][1], s[1][1][2], s[1][2][1], s[1][2][2],
                       s[2][1][1], s[2][1][2], s[2][2][1], s[2][2][2] ]

        #CONSTRUCT FACES AND VARIATIONS
        self.faces                    = {0:[], 1:[], 2:[], 3:[]} #four rotations, six faces each
        self.faces_m                  = {0:[], 1:[], 2:[], 3:[]} #mirrored
        self.faces_c                  = {0:[], 1:[], 2:[], 3:[]} #compliment - He is beautiful 
        self.faces_mc                 = {0:[], 1:[], 2:[], 3:[]} #mirrored compliment - He is such a sweet baby

      
        #This self.faces[x] is the rotation number
        self.faces[0].append(   s[0] ) #Die Face 1
        self.faces[0].append( [[s[0][3][3], s[0][2][3], s[0][1][3], s[0][0][3]], # Slice#, Row#, Column#
                               [s[1][3][3], s[1][2][3], s[1][1][3], s[1][0][3]],
                               [s[2][3][3], s[2][2][3], s[2][1][3], s[2][0][3]],
                               [s[3][3][3], s[3][2][3], s[3][1][3], s[3][0][3]]] ) #Die Face 2.. 


        self.faces[0].append( [[s[0][0][3], s[0][0][2], s[0][0][1], s[0][0][0]],
                               [s[1][0][3], s[1][0][2], s[1][0][1], s[1][0][0]],
                               [s[2][0][3], s[2][0][2], s[2][0][1], s[2][0][0]],
                               [s[3][0][3], s[3][0][2], s[3][0][1], s[3][0][0]]] ) #Die Face 3

        self.faces[0].append( [[s[0][3][0], s[0][3][1], s[0][3][2], s[0][3][3]],
                               [s[1][3][0], s[1][3][1], s[1][3][2], s[1][3][3]],
                               [s[2][3][0], s[2][3][1], s[2][3][2], s[2][3][3]],
                               [s[3][3][0], s[3][3][1], s[3][3][2], s[3][3][3]]] ) #Die Face 4

        self.faces[0].append( [[s[0][0][0], s[0][1][0], s[0][2][0], s[0][3][0]],
                               [s[1][0][0], s[1][1][0], s[1][2][0], s[1][3][0]],
                               [s[2][0][0], s[2][1][0], s[2][2][0], s[2][3][0]],
                               [s[3][0][0], s[3][1][0], s[3][2][0], s[3][3][0]]] ) #Die Face 5

        self.faces[0].append( [[s[3][0][3], s[3][0][2], s[3][0][1], s[3][0][0]],
                               [s[3][1][3], s[3][1][2], s[3][1][1], s[3][1][0]],
                               [s[3][2][3], s[3][2][2], s[3][2][1], s[3][2][0]],
                               [s[3][3][3], s[3][3][2], s[3][3][1], s[3][3][0]]] ) #Die Face 6.


        self.faces_entropy = []
        for x in range(0,6):
            self.faces_entropy.append(entropy(self.face_to_seq(self.faces[0][x])))

        #Rotate and store all faces from unrotated faces
        for rotnum in range(1,4):
            for facenum in range(0,6):
                self.faces[rotnum].append(self.rotate_face(self.faces[0][facenum], rotnum))

        #Compliment faces, rotation already done. You have such small pores!
        for rotnum in range(0,4):
            for facenum in range(0,6):
                self.faces_c[rotnum].append(self.compliment_face(self.faces[rotnum][facenum]))

        #Mirror Faces, rotation already one.  So Wow; Much Symmetry.
        for rotnum in range(0,4):
            for facenum in range(0,6):
                self.faces_m[rotnum].append(self.mirror_face(self.faces[rotnum][facenum]))

        #mirror Compliemnt.  Already mirrored and rotated, just compliment.  You have huge pores!
        for rotnum in range(0,4):
            for facenum in range(0,6):
                self.faces_mc[rotnum].append(self.compliment_face(self.faces_m[rotnum][facenum]))

    def slices_to_seq(self):
        '''
         Output the full cube input sequence that would result in this cube if no rotations of ordering were to
          be applied to the input.
         It is to be used when you built this cube with a given sequence, did slice reordering or rotations
          and want to recreate the cube from only an input sequence without any of the reordring or rotations
        '''
        s = self.slices
        ret = ''
        if self.slice_format == '4x4x4':
            ret = s[0][0][0:4] + s[0][1][0:4] + s[0][2][0:4] + s[0][3][0:4] + \
                  s[1][0][0:4] + s[1][1][0:4] + s[1][2][0:4] + s[1][3][0:4] + \
                  s[2][0][0:4] + s[2][1][0:4] + s[2][2][0:4] + s[2][3][0:4] + \
                  s[3][0][0:4] + s[3][1][0:4] + s[3][2][0:4] + s[3][3][0:4] 

        elif self.slice_format == '8x8':
            ret = s[0][0][0:4] + s[1][0][0:4] + \
                  s[0][1][0:4] + s[1][1][0:4] + \
                  s[0][2][0:4] + s[1][2][0:4] + \
                  s[0][3][0:4] + s[1][3][0:4] + \
                  s[2][0][0:4] + s[3][0][0:4] + \
                  s[2][1][0:4] + s[3][1][0:4] + \
                  s[2][2][0:4] + s[3][2][0:4] + \
                  s[2][3][0:4] + s[3][3][0:4] 

        elif self.slice_format == '16x4':
            ret = s[0][0][0:4] + s[1][0][0:4] + s[2][0][0:4] + s[3][0][0:4] + \
                  s[0][1][0:4] + s[1][1][0:4] + s[2][1][0:4] + s[3][1][0:4] + \
                  s[0][2][0:4] + s[1][2][0:4] + s[2][2][0:4] + s[3][2][0:4] + \
                  s[0][3][0:4] + s[1][3][0:4] + s[2][3][0:4] + s[3][3][0:4] 

        return ''.join(ret)

    def face_to_seq(self, f):
        s  = f[0][0] + f[0][1]+ f[0][2]+ f[0][3]
        s += f[1][0] + f[1][1]+ f[1][2]+ f[1][3]
        s += f[2][0] + f[2][1]+ f[2][2]+ f[2][3]
        s += f[3][0] + f[3][1]+ f[3][2]+ f[3][3]
        return s

    def seq_to_face(self, seq):
        f = [ list(seq[0:4]),
              list(seq[4:8]),
              list(seq[8:12]),
              list(seq[12:16])]
        return f

    def copy_face(self, f):
        r = [
                 [ f[0][0], f[0][1], f[0][2], f[0][3] ],
                 [ f[1][0], f[1][1], f[1][2], f[1][3] ],
                 [ f[2][0], f[2][1], f[2][2], f[2][3] ],
                 [ f[3][0], f[3][1], f[3][2], f[3][3] ] 
            ]
        return r

    def compliment_face(self, f):
        #you have such smooth skin
        #compliment A->T, T->A, G->C, C->G. 
        n = []
        for row in f:
            r = []
            for b in row:
                if b == 'A':
                    r.append('T')
                elif b == 'T':
                    r.append('A')
                elif b == ('G'):
                    r.append('C')
                elif b == ('C'):
                    r.append('G')
                else:
                    r.append(b) #Need this for cases where there is no compliment
            n.append(r)
        return n

    def mirror_face(self, f):
        n = []
        for row in f:
            r = [row[3], row[2], row[1], row[0]]
            n.append(r)
        return n

    def rotate_face(self, f, num):
        #Rotate face f, clockwise num times
        true_num = num %4
        if true_num == 0:
            return f
        
        r = self.copy_face(f)
        
        while true_num > 0:
            r = [
                 [ r[3][0], r[2][0], r[1][0], r[0][0] ],
                 [ r[3][1], r[2][1], r[1][1], r[0][1] ],
                 [ r[3][2], r[2][2], r[1][2], r[0][2] ],
                 [ r[3][3], r[2][3], r[1][3], r[0][3] ]
                ]
            true_num -= 1
        return r

    def rmc_face(self, f, num):
        x = self.rotate_face(f, num)
        y = self.mirror_face(x)
        z = self.compliment_face(y)
        #return self.compliment_face(self.mirror_face(self.rotate_face(f, num)))
        return z

    def cube_has_f(self, f, rotations):
        '''
            Search this cube for matching faces
            INPUT: Face Array, rotations to test list (ints), minimum_entropy
            OUTPUT: False | (facenum, rotation)
        '''
        for facenum in range(0,6):
            for rotation in range(0,4):
                if self.faces[rotation][facenum] == f:
                    return (facenum, rotation)
        return False

    def cube_has_c(self, f, rotations):
        '''
            Search this cube for matching compliment faces
            INPUT: Face Array, rotations to test list (ints), minimum_entropy
            OUTPUT: False | (facenum, rotation)
        '''
        for facenum in range(0,6):
            for rotation in rotations:
                if self.faces_c[rotation][facenum] == f:
                    return (facenum, rotation)
        return False

    def cube_has_m(self, f, rotations):
        '''
            Search this cube for matching mirror faces
            INPUT: Face Array, rotations to test list (ints), minimum_entropy
            OUTPUT: False | (facenum, rotation)
        '''
        for facenum in range(0,6):
            for rotation in rotations:
                if self.faces_m[rotation][facenum] == f:
                    return (facenum, rotation)
        return False


    def cube_has_mc(self, f, rotations):
        '''
            Search this cube for matching mirror compliment faces
            INPUT: Face Array, rotations to test list (ints), minimum_entropy
            OUTPUT: False | (facenum, rotation)
        '''
        for facenum in range(0,6):
            for rotation in rotations:
                if self.faces_mc[rotation][facenum] == f:
                    return (facenum, rotation)
        return False

    def cube_has_match(self, f, rotations, face_entropy, match_type):
        # FACE ENTROPY WILL ALWAYS BE THE SAME WHATEVER THE MATCH TYPE.
        # IF THIS CUBE DOES NOT HAVE A FACE WITH MATCHING ENTROPY RETURN FALSE
        if face_entropy not in self.faces_entropy:
            return False

        if match_type == 'f':
            return self.cube_has_f(f, rotations)
        elif match_type == 'm':
            return self.cube_has_m(f, rotations)
        elif match_type == 'c':
            return self.cube_has_c(f, rotations)
        elif match_type == 'mc':
            return self.cube_has_mc(f, rotations)
        else:
            raise Exception("Invalid Match Type: " + match_type)



    def dump(self):
        print("Start Offset: : " + str(self.start_offset))
        print("Slice format: : " + self.slice_format)
        print("Sequence Data : " + self.sequence)
        print("")
        print("Slices:")
        s0 = self.face_to_seq(self.slices[0])
        s1 = self.face_to_seq(self.slices[1])
        s2 = self.face_to_seq(self.slices[2])
        s3 = self.face_to_seq(self.slices[3])
        print("  0   1    2    3")
        print(s0[0:4] + ' ' + s1[0:4] + ' ' + s2[0:4] + ' ' + s3[0:4])
        print(s0[4:8] + ' ' + s1[4:8] + ' ' + s2[4:8] + ' ' + s3[4:8])
        print(s0[8:12] + ' ' + s1[8:12] + ' ' + s2[8:12] + ' ' + s3[8:12])
        print(s0[12:16] + ' ' + s1[12:16] + ' ' + s2[12:16] + ' ' + s3[12:16])
        print("")

        for r in [0,2]:
            print("Faces: ROTATED: " + str(r))
            f0 = self.face_to_seq(self.faces[r][0])
            f1 = self.face_to_seq(self.faces[r][1])
            f2 = self.face_to_seq(self.faces[r][2])
            f3 = self.face_to_seq(self.faces[r][3])
            f4 = self.face_to_seq(self.faces[r][4])
            f5 = self.face_to_seq(self.faces[r][5])
            print("0    1    2    3    4    5   ")
            print(f0[0:4] + ' '   + f1[0:4] + ' '   + f2[0:4] + ' '   + f3[0:4] + ' '   + f4[0:4] + ' '   + f5[0:4])
            print(f0[4:8] + ' '   + f1[4:8] + ' '   + f2[4:8] + ' '   + f3[4:8] + ' '   + f4[4:8] + ' '   + f5[4:8])
            print(f0[8:12] + ' '  + f1[8:12] + ' '  + f2[8:12] + ' '  + f3[8:12] + ' '  + f4[8:12] + ' '  + f5[8:12])
            print(f0[12:16] + ' ' + f1[12:16] + ' ' + f2[12:16] + ' ' + f3[12:16] + ' ' + f4[12:16] + ' ' + f5[12:16])
            print('='*30)

            print("Faces: MIRRORED ROTATED: " + str(r))
            f0 = self.face_to_seq(self.faces_m[r][0])
            f1 = self.face_to_seq(self.faces_m[r][1])
            f2 = self.face_to_seq(self.faces_m[r][2])
            f3 = self.face_to_seq(self.faces_m[r][3])
            f4 = self.face_to_seq(self.faces_m[r][4])
            f5 = self.face_to_seq(self.faces_m[r][5])
            print("0    1    2    3    4    5   ")
            print(f0[0:4] + ' '   + f1[0:4] + ' '   + f2[0:4] + ' '   + f3[0:4] + ' '   + f4[0:4] + ' '   + f5[0:4])
            print(f0[4:8] + ' '   + f1[4:8] + ' '   + f2[4:8] + ' '   + f3[4:8] + ' '   + f4[4:8] + ' '   + f5[4:8])
            print(f0[8:12] + ' '  + f1[8:12] + ' '  + f2[8:12] + ' '  + f3[8:12] + ' '  + f4[8:12] + ' '  + f5[8:12])
            print(f0[12:16] + ' ' + f1[12:16] + ' ' + f2[12:16] + ' ' + f3[12:16] + ' ' + f4[12:16] + ' ' + f5[12:16])
            print('='*30)

            print("Faces: COMPIMENTED ROTATED: " + str(r))
            f0 = self.face_to_seq(self.faces_c[r][0])
            f1 = self.face_to_seq(self.faces_c[r][1])
            f2 = self.face_to_seq(self.faces_c[r][2])
            f3 = self.face_to_seq(self.faces_c[r][3])
            f4 = self.face_to_seq(self.faces_c[r][4])
            f5 = self.face_to_seq(self.faces_c[r][5])
            print("0    1    2    3    4    5   ")
            print(f0[0:4] + ' '   + f1[0:4] + ' '   + f2[0:4] + ' '   + f3[0:4] + ' '   + f4[0:4] + ' '   + f5[0:4])
            print(f0[4:8] + ' '   + f1[4:8] + ' '   + f2[4:8] + ' '   + f3[4:8] + ' '   + f4[4:8] + ' '   + f5[4:8])
            print(f0[8:12] + ' '  + f1[8:12] + ' '  + f2[8:12] + ' '  + f3[8:12] + ' '  + f4[8:12] + ' '  + f5[8:12])
            print(f0[12:16] + ' ' + f1[12:16] + ' ' + f2[12:16] + ' ' + f3[12:16] + ' ' + f4[12:16] + ' ' + f5[12:16])
            print('='*30)

            print("Faces: MIRROR COMPLIMENT ROTATED: " + str(r))
            f0 = self.face_to_seq(self.faces_mc[r][0])
            f1 = self.face_to_seq(self.faces_mc[r][1])
            f2 = self.face_to_seq(self.faces_mc[r][2])
            f3 = self.face_to_seq(self.faces_mc[r][3])
            f4 = self.face_to_seq(self.faces_mc[r][4])
            f5 = self.face_to_seq(self.faces_mc[r][5])
            print("0    1    2    3    4    5   ")
            print(f0[0:4] + ' '   + f1[0:4] + ' '   + f2[0:4] + ' '   + f3[0:4] + ' '   + f4[0:4] + ' '   + f5[0:4])
            print(f0[4:8] + ' '   + f1[4:8] + ' '   + f2[4:8] + ' '   + f3[4:8] + ' '   + f4[4:8] + ' '   + f5[4:8])
            print(f0[8:12] + ' '  + f1[8:12] + ' '  + f2[8:12] + ' '  + f3[8:12] + ' '  + f4[8:12] + ' '  + f5[8:12])
            print(f0[12:16] + ' ' + f1[12:16] + ' ' + f2[12:16] + ' ' + f3[12:16] + ' ' + f4[12:16] + ' ' + f5[12:16])
            print('='*30)

        print("")

        print("Center 8:")
        print(self.center8[0] + self.center8[1] + ' ' + self.center8[2] + self.center8[3])
        print(self.center8[4] + self.center8[5] + ' ' + self.center8[6] + self.center8[7])
        print("")

if __name__ == '__main__':

    #TEST THAT ORDER OF rotations, mirrors, and compliments don't matter
        #rmc vs mrc vs crm vs
    fake_cube_seq = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$!'
    for slice_format in ['4x4x4', '8x8', '16x4']:
        fake_cube = cube(fake_cube_seq, 0, slice_format, [0,1,2,3], [0,0,0,0])
        f = fake_cube.faces[0]
        rmc = fake_cube.rmc_face(f, 2)
        mrc = fake_cube.compliment_face(fake_cube.rotate_face(fake_cube.mirror_face(f), 2))
        mcr = fake_cube.mirror_face(fake_cube.compliment_face(fake_cube.rotate_face(f,2)))
        cmr = fake_cube.compliment_face(fake_cube.mirror_face(fake_cube.rotate_face(f,2)))
        crm = fake_cube.compliment_face(fake_cube.rotate_face(fake_cube.mirror_face(f), 2))

        if rmc != mrc or rmc != mcr or rmc != cmr or rmc != crm:
            raise Exception("Failed.  Rotate, mirror, compliment operations order not equivalent.")


    print("TEST PASSED")
