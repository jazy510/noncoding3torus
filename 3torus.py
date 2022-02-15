import sys
import time
import os
import re
import argparse
import json
from UTILS import *
from WOT import *
from FASTA import *
from CUBE import *
from CUBEOPS import *
from TORUSCREATOR import *
from FINDONESSELF import *
from PATTERNCOUNT import *
from PATTERNS import *
from multiprocessing import Process
from multiprocessing import shared_memory
from multiprocessing import cpu_count


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    cmds = p.add_mutually_exclusive_group()

    #UNINTERESTING COMMANDS
    p.add_argument("--usage", help="Display usage examples", default=False, action='store_true')
    p.add_argument("--legal", help="Display legal stuff", default=False, action='store_true')
    p.add_argument("--instructions", help="Display instructions", default=False, action='store_true')
    p.add_argument("--writeup", help="Display long writeup", default=False, action='store_true')

    #FASTA RELATED COMMANDS
    cmds.add_argument("--flatten_fasta",   help="Remove headers, expand repeats x4",  default=False, action='store_true')
    cmds.add_argument("--sequence_counts", help="Print Sequence name and count of bases",   default=False, action='store_true')
    cmds.add_argument("--extract",         help="Extract a named sequence to a FASTA file", default=False, action='store_true')

    #OLD/DEPREICATED CUBE COMMANDS -> CUBEOPS.py 
    cmds.add_argument("--match_single_face",help="Depricated, but usable.  VERY SLOW CUBEOPS.", default=False, action='store_true')

    #CUBE PATTERN COMMANDS
    cmds.add_argument("--show_patterns",   help="Show patterns for manual searching", default=False, action='store_true')
    cmds.add_argument("--pattern_count",   help="Count matches of a given byte position list", default=False, action='store_true')
    cmds.add_argument("--pattern_count_frames", help="Give Counts of possible frame runs", default=False, action='store_true')
    cmds.add_argument("--pattern_extract",   help="Search for a base pattern and extract data", default=False, action='store_true')
    cmds.add_argument("--pattern_extract_faces", help="Extract cubes of matching faces", default=False, action='store_true')
    cmds.add_argument("--find_onesself",   help="Find a self-referential/orientation cube", default=False, action='store_true')
    cmds.add_argument("--find_onesself_in_frame_counts", help="Any onesself in frame counts?", default=False, action='store_true')

    #TORUS COMMANDS
    cmds.add_argument("--create_3torus", help="Create a torus from scratch.", default=False, action='store_true')
    cmds.add_argument("--reconstruct_torus", help="Build a tours from a onesself sequence", default=False, action='store_true')

    #Input/Output options
    p.add_argument("--config",          help="Config JOSN file location, overrides all arguments",         default=False)
    p.add_argument("--infile",          help="Input file",                                                 default=False)
    p.add_argument("--sequence_file",   help="FLAT File containing sequence data",                         default=False)
    p.add_argument("--scratch_file",    help="File to write important data to while doing long processes", default=False)
    p.add_argument("--outfile",         help="Output file",                                                default=False)

    #Slice Options
    p.add_argument("--slice_format",      help="4x4x4 8x8 16x4 Default: 8x8",                            default='8x8')
    p.add_argument("--slice_order",       help="Slice order to build cube default:0,1,2,3",              default='0,1,2,3')
    p.add_argument("--slice_rotations",   help="CSV of rotations for each slice default:0,0,0,0",        default='0,0,0,0')

    #Torus Options
    p.add_argument("--message",          help="ASCII Message to Encoded into the torus. Space padded.",  default='X')
    p.add_argument("--torus_dimensions", help="CSV Length, Width, Heigth",                               default='1,1,1')

    #Search and Extract options
    p.add_argument("--byte_pattern",    help="CSV of byte order to count with pattern_count",               default=None)
    p.add_argument("--extract_pattern", help="Base seq to match from byte_pattern extraction",              default=None)
    p.add_argument("--min_cube_entropy",help="Use Cubes with entropy over X. Default:0.0",                  default=0.0)
    p.add_argument("--min_face_entropy",help="Use Faces with entropy over X. Default:0.0",                  default=0.0)
    p.add_argument("--seq_name",        help="Sequence Name to use",                                        default='')
    p.add_argument("--match_types",     help="CSV of f,m,c,mc (Face,Mirror,Comp,Mirror-Compliment)",        default='mc')
    p.add_argument("--match_rotations", help="CSV of target cube rotations to try EG:0,1,2,3",              default='2')
    p.add_argument("--match_facenums",  help="CSV of faces to do matching/extraction",                      default='0,1,2,3,4,5')
    p.add_argument("--stop_after",      help="Stop Searching after X # of matches?",                        default=9999999999)
    p.add_argument("--start_offset",    help="Num Bases to start skipping when parsing",                    default=0)
    p.add_argument("--min_matches",     help="Minimum number of matches for a positive count",              default=25)
    p.add_argument("--buffer_size",     help="Size of regex buffer.  Too big causes thrashing",             default=10000000)
    p.add_argument("--cull_size",       help="When buffer full, delete items with less than this many matches.",  default=5)
    p.add_argument("--t_slice_format",    help="Pattern_extract target slice_format Default: 8x8",       default='8x8')
    p.add_argument("--t_slice_order",     help="Pattern_extract target slice_order  Default:0,1,2,3",    default='0,1,2,3')
    p.add_argument("--t_slice_rotations", help="Pattern_extract target slice_rotations Default:0,0,0,0", default='0,0,0,0')
    p.add_argument("--opposite_face_rotations",  help="CSV List of face numbers to match in search/extract",  default="2")
    p.add_argument("--slice_format_list",        help="USE --config to set",         default=['4x4x4','8x8','16x4'])
    p.add_argument("--slice_order_list",         help="USE --config to set",         default=[[0,1,2,3]])
    p.add_argument("--slice_rotations_list",     help="USE --config to set",         default=[[0,0,0,0]])

    #Multiprocessing options
    p.add_argument("--core_counts",     help="CSV of Cores on Each Server to Split jobs, EG: 4,24,16", default='1')
    p.add_argument("--server_number",   help="This server number to chose the correct job. ",  default=0)
    args = p.parse_args()


    if args.infile:
        if not os.path.exists(args.infile):
            raise Exception("--infile " + args.infile + " not found")
    if args.sequence_file:
        if not os.path.exists(args.sequence_file):
            raise Exception(args.sequence_file + " not found")
    if args.config:
        if not os.path.exists(args.config):
            raise Exception("Config file specified, but not found")
        f = open(args.config, 'r')
        d = f.read()
        f.close()
        c = json.loads(d)
        for key in c:
            if key in args:
                args.__setattr__(key, c[key])

    if len(sys.argv) == 1:
        usage()
        exit()

    if args.legal:
        legal()
        exit()

    if args.instructions:
        instructions()
        exit()

    if args.writeup:
        writeup()
        exit()

    args.min_cube_entropy = float(args.min_cube_entropy)
    args.min_face_entropy = float(args.min_face_entropy)
    args.start_offset = int(args.start_offset)
    args.stop_after = int(args.stop_after)
    args.buffer_size = int(args.buffer_size) #--pattern_count
    args.cull_size = int(args.cull_size)     #--pattern_count
    args.min_matches = int(args.min_matches) #--pattern_count
    args.server_number = int(args.server_number)
    args.slice_format = args.slice_format

    tmp = []
    for x in args.slice_rotations.split(','):
        tmp.append(int(x))
    args.slice_rotations = tmp

    tmp = []
    for x in args.slice_order.split(','):
        tmp.append(int(x))
    args.slice_order = tmp

    tmp = []
    for x in args.match_facenums.split(','):
        tmp.append(int(x))
    args.match_facenums = tmp


    tmp = []
    for x in args.torus_dimensions.split(','):
        tmp.append(int(x))
    args.torus_dimensions = tmp

    tmp = []
    for x in args.opposite_face_rotations.split(','):
        tmp.append(int(x))
    args.opposite_face_rotations = tmp

    if args.pattern_count or args.pattern_extract:
        if args.byte_pattern is None:
            ## H-Axis Faces 0 for 8x8 0,1,2,3 0,0,0,0
            args.byte_pattern = [0,1,2,3, 8,9,10,11, 16,17,18,19, 24,25,26,27]
        else:
            tmp = []
            for x in args.byte_pattern.split(','):
                tmp.append(int(x))
            args.byte_pattern = tmp

    tmp = []
    for core in args.core_counts.split(','):
        tmp.append(int(core))
    args.core_counts = tmp

    tmp = []
    for x in args.match_types.split(','):
        tmp.append(x) 
    args.match_types = tmp

    tmp = []
    for x in args.match_rotations.split(','):
       tmp.append(int(x)) 
    args.match_rotations = tmp

    if args.usage:
        usage()
        exit()

    if args.sequence_counts:
        if not args.infile:
            raise Exception("--infile is required")
        data = load_fasta(args.infile)
        sequence_names_and_count(data)
        exit()

    if args.extract:
        if not args.infile or not args.outfile or len(args.seq_name) == 0:
            raise Exception("--infile, --outfile, and --seq_name are required")
        data = load_fasta_seq(args.infile, args.seq_name)
        extract(data, args.seq_name, args.outfile)
        exit()

    if args.match_single_face:
        if not args.infile or not args.sequence_file or not args.outfile:
            raise Exception("--infile, --outfile, and --sequence_file are required")
        #match_types = ['f', 'm', 'c', 'mc'] #Face, Mirror, Mirror Compliment 
        #match_rotations = [0,1,2,3]

        if len(args.match_facenums) > 1:
            raise Exception("Can only match one face.  Set --match_facenums to one value")
        face_num = args.match_facenums[0]

        #Open A file with a single cube
        cube_data = read_file(args.sequence_file, 0, -1).strip()
        c1 = cube(cube_data, 0, args.slice_format, args.slice_order, args.slice_rotations)

        #Memory map the big file
        shm = map_file(args.infile, 0, -1) 

        #Get multiprocessing information
        procs = get_mp_split(args.infile, args.core_counts) #{server#:[(proc, start_offset, bytes_to_read)...}

        #Do the Processing
        target_args_tuple = (shm.name, c1, args.slice_format, args.slice_order, args.slice_rotations,
                             face_num, args.match_types, args.match_rotations,
                             args.min_cube_entropy, args.stop_after)
        mp_execute(match_single_face, target_args_tuple,
                   proc_info, args.outfile, arsg.scratchfile, args.server_number, args.core_counts)

        shm.close()
        shm.unlink()
        exit()

        
    if args.pattern_count:
        if not args.infile:
            raise Exception("--infile required")

        pattern_count(args.infile, args.outfile, args.min_matches, 
                      args.min_face_entropy, args.buffer_size, args.cull_size, args.byte_pattern)

        exit()

    if args.pattern_count_frames:
        if not args.infile or not args.outfile:
            raise Exception("--infile and --outfile required")
        print("This takes about 6 hours and 32GB of memory for buffer_size = 200000000 & cull_size = 3")
        print("If it dies you probably ran out of memory, decrease buffer_size, increase cull_size")

        outfiles = []
        for faces in [[0,5], [1,4], [2,3]]:

            pattern = get_face_byte_pattern(args.slice_format, args.slice_order, args.slice_rotations, faces[0])
            pattern += get_face_byte_pattern(args.slice_format, args.slice_order, args.slice_rotations, faces[1])
            outfile = args.outfile + str(faces[0]) + '_' + str(faces[1])
            pattern_count(args.infile, outfile, args.min_matches, 
                          args.min_face_entropy, args.buffer_size, args.cull_size, pattern)
            outfiles.append(outfile)

        #Reconstruct the outfiles into one.  Will be in one order.
        output = {}
        for i in range(0, 3):
            f = open(outfiles[0], 'r')
            x = f.read()
            f.close()
            y = json.loads(x)
            output[str(i) + '-' + str(5-i)] = y

        dump_json(output, args.outfile)

        exit()

    if args.find_onesself_in_frame_counts:
        if not args.infile or not args.outfile or not args.sequence_file:
            raise Exception("--infile, --outfile, --sequence_file required")
        #--infile = pattern_count_frames output -> JSON , { '0-5':{"AAT.":4449, "GGTA...":502...}, '1-4':.., '2-3' }
        #--sequence_file = find_onesself output -> JSON, {"AATGCTAAA...":{offset, slice stuff}
        #Loop throught the sequence file and extract face pairs.  Find if face-pairs byte patters are in --infile
         #If they are, save off the sequence, and the count of each. {"AATAAGCC...":{'0-5':3484, '1-4':424, '2-3':424}}

        f = open(args.infile, 'r')
        x = f.read()
        f.close()
        frame_counts = json.loads(x)
        
        f = open(args.sequence_file, 'r')
        x = f.read()
        f.close()
        onesself_files = json.loads(x)

        output = {}
        for seq in onesself_files:
            #TEST TO MAKE SURE onesself cube matches the given slice information
            if onesself_files[seq][0]['slice_format'] != args.slice_format:
                continue
            if onesself_files[seq][0]['slice_order'] != json.dumps(args.slice_order):
                continue
            if onesself_files[seq][0]['slice_rotations'] != json.dumps(args.slice_rotations):
                continue
            if onesself_files[seq][0]['opposite_rotation'] != str(args.opposite_face_rotations[0]):
                continue

            print("TESTING ONESSELF SEQ: " + seq)

            face_count = 0
            counts = []
            for face in range(0,3):
                #Generage a pattern for each face pair
                pattern = get_face_byte_pattern(args.slice_format, args.slice_order, args.slice_rotations, face)
                pattern += get_face_byte_pattern(args.slice_format, args.slice_order, args.slice_rotations, 5-face)
                ps = ''
                for b in pattern:
                    ps += seq[b]
                name = str(face) + '-' + str(5-face)

                ### IGORNING ORIENTATION
                for name in frame_counts:
                    found = False
                    for us in frame_counts[name]:
                        if ps == us:
                            found = True
                            break
                    if found:
                        if ps in output:
                            output[ps].append(frame_counts[name][us])
                            print("FOUND MATCH: " + str(ps) + " " + str(counts))

        if len(output) <= 0:
            print("No matches found")
            exit()

        dump_json(output, args.outfile)
        print("Wrote: " + str(len(output)) + " to: " + args.outfile)



    if args.pattern_extract_faces:
        if not args.infile or not args.outfile or not args.sequence_file:
            raise Exception("--infile, --outfile, --sequence_file required")

        #Read in the sequences to find matches for
        seqs = []
        f = open(args.sequence_file, 'r')
        x = f.readline()
        while True:
            seqs.append(x.strip())
            x = f.readline()
            if x == '':
                break

        #Build the search for the sequences you want to look for.
        search = {}
        for seq in seqs:
            patterns = get_patterns(args.slice_format, args.slice_order, args.slice_rotations, seq,
                                   args.t_slice_format, args.t_slice_order, args.t_slice_rotations)
            search[seq] = []
            for facenum in patterns:
                if facenum in args.match_facenums: #OR'ed Not AND'ed
                    s = {'slice_format':args.slice_format,
                         'slice_order':args.slice_order,
                         'slice_rotations':args.slice_rotations,
                         't_slice_format':args.t_slice_format,
                         't_slice_order':args.t_slice_order,
                         't_slice_rotations':args.t_slice_rotations,
                         'face':facenum, #NEED TO CONFIRM THIS IS FACE OF TARGET SEQ
                         'byte_array':patterns[facenum][0],
                         'sequence':patterns[facenum][1],
                         'matches':[]
                        }
                    search[seq].append(s)

        #Setup Multiprocessing
        shm = map_file(args.infile, args.start_offset, -1)
        proc_info = get_mp_split(arsg.infile, args.core_counts) ### TEST SERVER

        #Do the Processing
        target_args_tuple = (shm.name, args.server_number, args.min_cube_entropy, search)
        mp_execute(pattern_extract, target_args_tuple, 
                   proc_info, args.outfile, args.scratch_file, args.server_number, args.core_counts)

        shm.close()
        shm.unlink()


    if args.pattern_extract:
        if not args.infile or not args.outfile or not args.extract_pattern or not args.scratch_file:
            raise Exception("--infile, --outfile, --scratch_file --extract_pattern required")
        if len(args.extract_pattern) != len(args.byte_pattern):
            raise Exception("Extract_pattern and byte_pattern lengths differ.")

        #{'<SEQ>':[ { byte_array:[], sequence:<bases to match>, matches:[]}}
        #Build the search for the sequences you want to look for.
        search = {}
        search[0] = [{'byte_array':args.byte_pattern,
                        'sequence':args.extract_pattern,
                        'matches':[]
                      }]

        #Setup Multiprocessing
        shm = map_file(args.infile, args.start_offset, -1)
        proc_info = get_mp_split(args.infile, args.core_counts) ### TEST SERVER

        #Do the Processing
        target_args_tuple = (shm.name, args.server_number, args.min_cube_entropy, search)
        mp_execute(pattern_extract, target_args_tuple, 
                   proc_info, args.outfile, args.scratch_file, args.server_number, args.core_counts)

        shm.close()
        shm.unlink()


    if args.pattern_extract_faces:
        if not args.infile or not args.outfile or not args.sequence_file:
            raise Exception("--infile, --outfile, --sequence_file required")

        #Read in the sequences to find matches for
        seqs = []
        f = open(args.sequence_file, 'r')
        x = f.readline()
        while True:
            seqs.append(x.strip())
            x = f.readline()
            if x == '':
                break

        #Build the search for the sequences you want to look for.
        search = {}
        for seq in seqs:
            patterns = get_patterns(args.slice_format, args.slice_order, args.slice_rotations, seq,
                                   args.t_slice_format, args.t_slice_order, args.t_slice_rotations)
            search[seq] = []
            for facenum in patterns:
                if facenum in args.match_facenums: #OR'ed Not AND'ed
                    s = {'slice_format':args.slice_format,
                         'slice_order':args.slice_order,
                         'slice_rotations':args.slice_rotations,
                         't_slice_format':args.t_slice_format,
                         't_slice_order':args.t_slice_order,
                         't_slice_rotations':args.t_slice_rotations,
                         'face':facenum, #NEED TO CONFIRM THIS IS FACE OF TARGET SEQ
                         'byte_array':patterns[facenum][0],
                         'sequence':patterns[facenum][1],
                         'matches':[]
                        }
                    search[seq].append(s)

        #Setup Multiprocessing
        shm = map_file(args.infile, args.start_offset, -1)
        proc_info = get_mp_split(arsg.infile, args.core_counts) ### TEST SERVER

        #Do the Processing
        target_args_tuple = (shm.name, args.server_number, args.min_cube_entropy, search)
        mp_execute(pattern_extract, target_args_tuple, 
                   proc_info, args.outfile, args.scratch_file, args.server_number, args.core_counts)

        shm.close()
        shm.unlink()


    if args.flatten_fasta:
        if not args.infile or not args.outfile:
            raise Exception("--infile and --outfile required")
        flatten_fasta(args.infile, args.outfile, 4)

    if args.flatten_fasta:
        if not args.infile or not args.outfile:
            raise Exception("--infile and --outfile required")
        flatten_fasta(args.infile, args.outfile, 4)
        print("Wrote flattened raw base sequences to : " + args.outfile)

    if args.show_patterns:
        show_patterns(args.slice_format, args.slice_order, args.slice_rotations)
        exit()


    if args.find_onesself:
        '''
            FIND ALL POSSILBE ONESSELF CUBES.
            A onesself cube is where one face matches the opposite-side face.
              The opposite side face is complimented, mirrored, and possibly rotated.
            This call can be modified to change the number of rotations applied.
          
            If all options are used, then it only ever needs to be run ONCE against a gnome :).
             But you will need some serious computing power, or a VERY long time to do it.

            Unfortunately there isn't an easy way to program this one with multiple options for slice ordering.
            Just going to have to manually change it.
        '''
        if not args.infile or not args.outfile or not args.scratch_file:
            raise Exception("--infile, --outfile, --scratch_file required")

        proc_info = get_mp_split(args.infile, args.core_counts) #Returns {<server#>: (proc#, offset, #read bytes), ..}
        procs = []
        shm = map_file(args.infile, 0, -1)

        #Do the Processing / FIND THE FRAME
        target_args_tuple = (shm.name, args.min_cube_entropy, args.min_face_entropy,
                             args.slice_format_list, args.slice_order_list, args.slice_rotations_list, args.opposite_face_rotations)
        mp_execute(find_onesself, target_args_tuple, proc_info, 
                   args.outfile, args.scratch_file, args.server_number, args.core_counts)

        shm.close()
        shm.unlink()

        
        f = open(outfile, 'r')
        thejson = f.read()
        f.close()
        data = json.loads(thejson)

        #DATA FORMAT:
        #data[sequence] = [{'offset':position,
        #                  'opposite_rotation':op_rot,
        #                  'slice_format':slice_format, 
        #                  'slice_order':slice_order,
        #                  'slice_rotation':slice_rotation}]
        print("FOUND: " + str(len(data)) + " ONESELF CUBES ")
        exit()

    if args.create_3torus:
        '''
            Assuming user wants to make palendromic 1:1 FEC for message unless they are making a onesself cube.
        '''
        td = args.torus_dimensions
        num_cubes = td[0] * td[1] * td[2]
        message_final = 'AAAAAAAA' #NULL 16 bits of 0's
        if num_cubes > 1:
            message_bases = ascii_to_base(args.message)
            message_bases_rc = compliment_seq(reverse_seq(message_bases))
            message_final = interleave_messages(message_bases, message_bases_rc, 2)
        
        while len(message_final) < num_cubes * 8:
            message_final += ascii_to_base(' ')

        if len(message_final) > 8 * num_cubes:
            raise Exception("Message sequence length is: " + str(len(message_seq)) + " MAX: " + str(8*num_cubes)) 

        stan = (args.slice_format, args.slice_order, args.slice_rotations)
                    
        torus = create_3torus(stan, td, message_final)

        if args.outfile:
            f = open(args.outfile, 'w+')
            for l in range(0, td[0]):
                for w in range(0, td[1]):
                    for h in range(0, td[2]):
                        f.write(torus[l][w][h]['seq'] + " - " + str(l) + "," + str(w) + "," + str(h))
            f.close()
            print("Wrote: " + args.outfile)
        else:
            for l in range(0, td[0]):
                for w in range(0, td[1]):
                    for h in range(0, td[2]):
                        message = torus[l][w][h]['seq'] + " - " + str(l) + "," + str(w) + "," + str(h)
                        print(message)
                        scratch(message, args.scratch_file)

    if args.reconstruct_torus:
        if not args.infile or not args.outfile or not args.scratch_file or not args.sequence_file:
            raise Exception("--infile and --sequence_file required")

        #NOT handling possibility that adjacent cubes may have a different orientation or SLICE info, ALL MUST MATCH.

        #Search A onesself sequence/cube for faces in a gnome :) using a pattern extract.
        #Unfortunately, without shared storage it becomes very difficult to correlate all results across an MP cluster.
        # So, each onesself sequence will have to be processed on a given cluster machine.

        #Once results come back, ensure that there are X number of cubes that extend in the L W H directions.
        # 0-5, 1-4, 2-3 must all match across the X nubmer of cubes.
        # Discard any cubes that do not match this pattern.
        # Bin these cubes into Level 0: Face(0, 1, 2) bins for later matching.

        #Generage a Search pattern for all Non-LWH faces and execute. THIS COULD BE VERY, VERY LARGE.

        #Construct a blank torus object of the best-guess size
        # and place the onesself cube in the 0,0,0 location

        onesself = read_file(args.sequence_file, 0, -1).strip()
        seqs = [onesself]

        search = {}
        for seq in seqs:
            patterns = get_patterns(args.slice_format, args.slice_order, args.slice_rotations, seq,
                                   args.t_slice_format, args.t_slice_order, args.t_slice_rotations)
            search[seq] = []
            for facenum in patterns:
                if facenum in args.match_facenums: #OR'ed Not AND'ed
                    s = {'full_sequence':seq, #So we can match it up later if needed
                         'slice_format':args.slice_format,
                         'slice_order':args.slice_order,
                         'slice_rotations':args.slice_rotations,
                         't_slice_format':args.t_slice_format,
                         't_slice_order':args.t_slice_order,
                         't_slice_rotations':args.t_slice_rotations,
                         'face':facenum,
                         'byte_array':patterns[facenum][0],
                         'sequence':patterns[facenum][1],
                         'matches':[]
                        }
                    search[seq].append(s)


        #Setup Multiprocessing
        shm = map_file(args.infile, args.start_offset, -1)
        proc_info = get_mp_split(args.infile, args.core_counts) ### TEST SERVER

        #Do the Processing / FIND THE FRAME
        target_args_tuple = (shm.name, args.server_number, args.min_cube_entropy, search)
        mp_execute(pattern_extract, target_args_tuple, proc_info, 
                   args.outfile, args.scratch_file, args.server_number, args.core_counts)

        #Open up the final output json and parse.
        f = open(args.outfile, 'r')
        data = f.read()
        f.close()
        os.unlink(args.outfile)
        pattern_json = json.loads(data)

        #print(pattern_json)
        print("THIS IS THE LENGTH OF THE JSON: " + len(pattern_json))
        print("THIS IS THE LENGTH WITH SEQ:" + len(pattern_json[onesself]))

        #### WE HAVE OUR LIST OF POSSIBLE LWH Frames
        ### Clean it up and throw them into face bins.
        bin0 = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}}
        for onesself in pattern_json:
            for ahit in pattern_json[onesself]:
                face = ahit['face']
                for amatch in ahit['matches']:
                    bin0[face][amatch[1]] = amatch[0]
        '''
        L = 1-4 Right-Left/East-West
        W = 2-3 Forward-Backwards/North-South
        H = 0-5 Up-Down

        ADJACENT CUBE/FACE
        Convention - ONLY FOR THIS PROGRAM!!! DO NOT ADOPT IT! 
        We don't want another Electron with a negative charge convention! SERIOUSLY! THAT SHOULD NEVER HAVE HAPPENED!
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

        #Bin the Frame pieces.
        binL = {}
        binW = {}
        binH = {}
        for face in bin0:
            for seq in bin0[face]:
                if seq in bin0[5-face]:
                    #This is a frame piece.
                    if face == 0 or face == 5:
                        #This is an H piece
                        binH[seq] = {}
                    if face == 1 or face ==4:
                        #this is an L piece
                        binL[seq] = {}
                    if face == 2 or face == 3:
                        #This is a W piece
                        binW[seq] = {}
 
        #Now we know enough to construct a dummy Torus framework.
        # This framwork will be useful because we can use it to get the Adjacency information to 
        #  start construction closes to the onesself cube and work outward.
        #  For this first example, we are going to just have to assume clean data.
        size_list = [len(binL), len(binW), len(binH)]
        stan = (args.slice_format, args.slice_order, args.slice_rotations)
        torus = initialize_torus(size_list, stan)

        lmax = size_list[0]
        wmax = size_list[1]
        hmax = size_list[2]
        ### GO THROUGH AND CLEAR OUT DATA IN THE TORUS THAT WE DON'T WANT
        #'matches' is a key of face#'s, value is an object. with Key of 64base seq of matches, value None or LWH location.
        for l in range(0, lmax):
            for w in range(0, wmax):
                for h in range(0, hmax): #seq, message, c, faces, adjacent[<face#>] = (l,w,h,Face# of adjacent cube)
                    torus[l][w][h]['seq'] = None
                    torus[l][w][h]['message'] = None
                    torus[l][w][h]['c'] = None
                    torus[l][w][h]['faces'] = {0:None, 1:None, 2:None, 3:None, 4:None, 5:None}
                    torus[l][w][h]['matches'] = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}}

        #SET ONESELF cube to 0,0,0
        torus[0][0][0]['seq'] = onesself
        torus[0][0][0]['c'] = cube(onesself, 0, args.slice_format, args.slice_order, args.slice_rotations)
        torus[0][0][0]['faces'] = torus[0][0][0]['c'].faces[0]

        #pattern_json holds the search results from the onesself cube
        #Load up the torus maches results
        for x in pattern_json[onesself]:
            face = x['face']
            matches = x['matches']
            for match in matches:
                torus[0][0][0]['matches'][face][match[1]] = {'loc':None, #this will hold LWH location if found
                                                             'matches':{0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}}}


        #From Here we don't have enough information to start filling in the cube/torus.
        # We have to search on each of the sequences in the matches of the onesself torus.
        # For every search we do, check to see if it sequence exists in the oneself matches and duplicate the info.
        #If we consistently get back multiple paris for the different planes, then we know that
        # the planes either:
        # 1) All cubes in a plane have the same opposing face information 
        #      - But one face pair must be different from its opposite, otherwise they would all be onesself cubes
        # 2) Either a row or a column of faces have matching opposite faces.
        # IF we consistently get one or few matches, then all of the cubes (Like in the create_3torus function)
        #  have different faces (besides the one that attaches to the LHW frame)

        # THIS WILL BE BY FAR THE MOST EXPENSIVE LOOP TO START WITH.  WE NEED A GOOD BASE OF DATA TO WORK WITH.
        #print(torus[0][0][0]['matches'])
        for face in torus[0][0][0]['matches']:
            for seq in torus[0][0][0]['matches'][face]:
                patterns = get_patterns(args.slice_format, args.slice_order, args.slice_rotations, seq,
                                       args.t_slice_format, args.t_slice_order, args.t_slice_rotations)

                search = {} #Move this out of loop if change to big search instead of multiple small
                search[seq] = []

                for facenum in patterns:
                    if facenum in range(0,6): #OR'ed Not AND'ed
                        s = {'full_sequence':seq, #for matching later
                             'slice_format':args.slice_format,
                             'slice_order':args.slice_order,
                             'slice_rotations':args.slice_rotations,
                             't_slice_format':args.t_slice_format,
                             't_slice_order':args.t_slice_order,
                             't_slice_rotations':args.t_slice_rotations,
                             'face':facenum, #NEED TO CONFIRM THIS IS FACE OF TARGET SEQ
                             'byte_array':patterns[facenum][0],
                             'sequence':patterns[facenum][1],
                             'matches':[]
                            }
                        search[seq].append(s)

                #HERE WE HAVE A CHOICE.  MULTIPLE MP_EXECUTES.  ONE FOR EACH SEQ, OR ONE BIG ONE.
                # I think the ONE BIG ONE WOULD END UP GOING FASTER. But have to reloop to find where the matches go.
                #Will do multiple searches for now for simplicity.

                print("SEARCHING FACE: " + str(face) + " SEQ: " + seq)

                #Do the Processing / FIND THE SEQUENCES ADJACENT TO THE FRAME
                target_args_tuple = (shm.name, args.server_number, args.min_cube_entropy, search)
                mp_execute(pattern_extract, target_args_tuple, proc_info, 
                           args.outfile, args.scratch_file, args.server_number, args.core_counts)


                #Open up the final output json and parse.
                f = open(args.outfile, 'r')
                data = f.read()
                f.close()
                pattern_json = json.loads(data)
                os.unlink(args.outfile)
                for x in pattern_json[seq]:
                    face2 = x['face']
                    matches2 = x['matches']
                    for match in matches2:
                        blank = {'loc':None, #this will hold LWH location if found
                                 'matches':{0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}}}
                        torus[0][0][0]['matches'][face][seq]['matches'][face2][match[1]] = blank
                                                                                          

        #torus onesself now holds all of the LWH cubes, as well as all of the cubes that are adjacent to those.
        # If this was a human gnome :), it would have taken about 160 days of core time.
      
        #TORUS LOOKS LIKE THIS:
        #print(torus[0][0][0]['matches'])
        '''
        {'matches':{0:{<MATCHING SEQUENCE>:{'loc':None, 
                                            'matches': { 0:{<MATCHING SEQ2>:{'loc':None,
                                                                             'matches':{0:{}, 1:{}..}
                                                                            }
                                                           }
                                                         1:{<MATCHING SEQ3>:{'loc':None,
                                                                             'matches':{0:{}, 1:{}..}
                                                                             }
                                                           }....
                                                        }
                                           }
                      },
                    1: ......
        }
   
            The Top level 0, 1, etc, represent the immediate faces of the ONESSELF cube.
              Twill be multiple 
        '''

        #LOOP and find L-H, L-W, W-H Frames that have cubes with faces of second level cubes that match the frame
        #for face in torus[0][0][0]['matches']:
        print("INCOMPLETE")

        shm.close()
        shm.unlink()
