import sys
import time
import os
import random
import re
import json
from math import log
from collections import Counter
from multiprocessing import shared_memory
from multiprocessing import Process

def entropy(seq):
    '''
        https://stackoverflow.com/questions/1540192/fastest-way-to-compute-entropy-in-python#45091961

        INPUT: string
        ACTION: Compute the entropy of the input
        OUTPUT: Float of Measure of Entropy
    '''
    probabilities = [n_x/len(seq) for x,n_x in Counter(seq).items()]
    e_x = [-p_x*log(p_x,2) for p_x in probabilities]
    return sum(e_x)



def random_seq(count):
    '''
        INPUT: count
        ACTION: makes a byte sequence of random bases
        OUTPUT: bytes sequence of random bases of length count
    '''
    d = ''
    r = ['A','T','G','C']
    for c in range(0, count):
        d += random.choice(r)
    return d
        
def reverse_seq(seq):
    '''
        INPUT: bytes or string
        OUTPUT: reversed bytes or string sequence
    '''
    return seq[::-1]

def compliment_seq(seq):
    '''
        INPUT: bytes sequence
        OUTPUT: bytes sequence with A->T, T->A, G->C, C->G replacement
    '''
    return seq.replace('A','w').replace(
                       'T','x').replace(
                       'G','y').replace(
                       'C','z').replace(
                       'w','T').replace(
                       'x','A').replace(
                       'y','C').replace(
                       'z','G')

def mirror_seq(seq):
    '''
        INPUT: bytes sequence from mapping a 16 entry face starting with [0][0] -> [0][3]
               and ending at [3][3]
        OUTPUT: Mirrored sequence bytes of a face.  Top row reversed, second row reversed, etc.

    '''
    return seq[0:4][::-1] + seq[4:8][::-1] + seq[8:12][::-1] + seq[12:16][::-1]


def read_file(filename, offset, read_bytes):
    '''
       INPUTS: filename, offset to start reading, number of bytes to read
               read_bytes = -1 = Whole file
       ACTION: MUST be a flat sequence file, NOT FASTA
       OUTPUTS: bytes from file
    '''
    file_size = os.path.getsize(filename)
    f = open(filename, 'r')
    d = f.read(1)
    f.seek(0)
    data = ''
    if d == '>':
        f.close()
        raise Exception("read_file() does not support fasta format, flatten it")

    #IS NOT FASTA
    f.seek(offset)
    if read_bytes == -1:
        read_bytes = file_size
    data = f.read(read_bytes)
    f.close()
    return data

def map_file(filename, offset, read_bytes):
    '''
        INPUT: Filename, offset to start reading, and the number of bytes to read into memory
        ACTION: Checks if FASTA and fails if it is,
                Creates a Shared Memory space (NEEDS PYTHON 3.8+)
                Seek to file offset
                Read memory into shared memory space.
                DOES NOT CHECK TO SEE IF ENOUGH MEMORY CAN BE ALLOCATED
        OUTPUT: Returns a shared memory object that can be used to create buffers to read file
    '''
    #open a filename, in flat format
    file_size = os.path.getsize(filename)
    if read_bytes == -1:
        read_bytes = file_size
    f = open(filename, 'rb')
    d = f.read(1)
    f.seek(0)
    if d == b'>':
        f.close()
        raise Exception("map_file() does not support fasta format, flatten it")

    #IS NOT FASTA
    f.seek(offset)
    shm = shared_memory.SharedMemory(create=True, size=read_bytes)
    shm.buf[:] = f.read(read_bytes)
    f.close()
    return shm

def get_mp_split(filename, splits):
    '''
        INPUT: Filename, array representing the number of cores to run on a given survey
               EG: splits = [16,24,24] or [1] for a single core system

        ACTION: Calculates start offsets and number of bytesof the file for the process to work on
                This can also be used for memory mapped files, not just ones on disk
                This is intended for Multiprocessor.Process.
                Assumes a block size of 64 bases and an overlap of one block

        OUPUT: object of key = sever #, value = List of (process #, start byte, bytes to read)
    '''
    the_size = os.path.getsize(filename)
    f = open(filename, 'r')
    x = f.read(1)
    f.close()
    if x == '>':
        raise Exception("Function requires a flat sequence file, NOT FASTA formatted!")

    total_cores = 0
    for x in splits:
        total_cores += x

    bytes_per_core = int(the_size/total_cores)
    bytes_per_core += 64 - (bytes_per_core%64) #Round off to next evenly divisible 64 bytes

    #split input file into sizes according to number of cores.  Add 64 bytes to the size of each for overlap.
    # Last one gets any remainder from rounding errors
    location = 0
    core_locs = []
    for proc in range(0, total_cores):
        if the_size - location > bytes_per_core:
            core_locs.append((proc, location, bytes_per_core))
        else:
            #is last block
            core_locs.append((proc, location, the_size - location))
            break
        location += bytes_per_core - 64 #Go back one whole block to cover any gap between two blocks

    #Split up the processing blocks to their appropriate servers.
    the_return = {}
    the_count = 0
    for x in range(0, len(splits)):
        the_return[x] = core_locs[the_count:the_count+splits[x]]
        the_count += splits[x]

    return the_return


def decode_dict(d):
    '''
        Convert the keyes of a dict to a str so json.dumps can be used to dump the object.
        use like this: json.dumps(obj, cls=decode_dict)
        Have to use recursion, only check for bytes, dict, and list to convert.  Will th
    '''
    def decode_list(l):
        tmp = []
        for x in l: #Does not do list of lists
            if isinstance(x, bytes):
                tmp.append(x.decode())
            elif isinstance(x, dict):
                tmp.append(decode_dict(x))
            elif isinstance(x, list):
                tmp.append(decode_list(x))
            else:
                tmp.append(x)
        return tmp


    result = {}
    for key, value in d.items():
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        result.update({key:value})
    return result

def dump_json(the_data, filename):
    '''
        Simple wrtapper for json.dumps that includes a recursive dict, list, byte conversion to string
    '''
    #the_data = decode_dict(the_data)
    d = json.dumps(the_data, indent=4)
    f = open(filename, 'w+')
    f.write(d)
    f.close()

def ascii_to_base(inputstring):
    '''
        Convert an ascii string to a sequence of Bases.
        A = 00
        C = 01
        G = 10
        T = 11

        Pad front with Zeros
    '''
    retstring = ''
    for x in inputstring:
        the_bin = bin(ord(x))[2:] # Binary string
        the_bin = '0'* ( 8 - (len(the_bin) %8)) + the_bin
        for y in range(0, 4):
            if the_bin[2*y:2*y+2] == '00':
                retstring += 'A'
            elif the_bin[2*y:2*y+2] == '01':
                retstring += 'C'
            elif the_bin[2*y:2*y+2] == '10':
                retstring += 'G'
            elif the_bin[2*y:2*y+2] == '11':
                retstring += 'T'
    return retstring

def base_to_ascii(inputstring):
    '''
        Convert Bases to ascii string.
        A = 00
        C = 01
        G = 10
        T = 11

        Pad tail with 0s.
    '''
    bin_string = ''
    for x in inputstring:
        if x == 'A':
            bin_string += '00'
        elif x == 'C':
            bin_string += '01'
        elif x == 'G':
            bin_string += '10'
        elif x == 'T':
            bin_string += '11'
            
    bin_string += '0'* (len(bin_string) %8)

    start = 0
    return_string = ''
    for x in range(0, int(len(bin_string)/8)):
        return_string += int(bin_string[x*8:x*8+8],2).to_bytes(1,'little').decode('ascii')

    return return_string

def list_to_dict(thelist):
    if type(thelist) == type({}):
        return thelist
    thedict = {}
    index = 0
    for x in thelist:
        thedict[index] = x
        index += 1
    return thedict

def interleave_messages(message1, message2, interleave_size):
    '''
       Given two messages, read (interleave_size) bases of first, then (interleave_size) of the second
        and combine them into a new string.
        Continue over length of both messages.
        messages must be of same length
        messages must be of % interleave_size == 0
    '''
    if len(message1) %interleave_size != 0 or len(message2) %interleave_size != 0:
        raise Exception("Message Lengths must have zero remainder compared to interleave size")

    if len(message1) != len(message2):
        raise Exception("Messages must be of same length to interleave")

    return_message = ''
    loc = -1
    while True:
        loc += 1
        return_message += message1[loc*interleave_size:loc*interleave_size+interleave_size]
        return_message += message2[loc*interleave_size:loc*interleave_size+interleave_size]
        if loc*interleave_size+interleave_size > len(message1):
            break
    return return_message
        
def scratch(message, filename):
    if filename:
        f = open(filename, 'a+')
        f.write(message)
        f.close()

def mp_execute(target, target_args_tuple, proc_info, outfile, scratchfile, server_number, core_counts):
    '''
       Wrapper around multiprocessing.Processs that handles 
       1) recombining output from multiple processes,
       2) recombining scratch files from multiple processes
       3) Keeps desired number of Processes running to fill CPU Cores

       OUTFILE MUST BE A JSON

       The value of the key in the json must be a list.

       The Arrays will be concatenated when put all together.

       The final return object will be an object with X number of keys and each key maps to a list.

    '''
    outfiles = []
    scratchfiles = []
    procs = []
    for proc in proc_info[server_number]:
        outfile_rand = outfile + str(random.randint(99999,999999999999))
        outfiles.append(outfile_rand)

        scratchfile_rand = scratchfile + str(random.randint(99999,999999999999))
        scratchfiles.append(scratchfile_rand)

        first_args = (outfile_rand, scratchfile_rand, proc)

        target_args_tuple_final = first_args + target_args_tuple
        p = Process(target=target, args=target_args_tuple_final)
        p.start()
        procs.append(p)

        #Load up X number of processes running at a time and wait for one to exit then start next.
        while len(procs) >= core_counts[server_number]:
            remove = None
            for i in range(0, len(procs)):
                proc = procs[i]
                if not proc.is_alive():
                    proc.join()
                    remove = i
                    break
            if remove is not None:
                del(procs[remove])
                remove = None
                break
            time.sleep(0.25) #SHould be good

    for p in procs:
        p.join()

    #Go through all of the separate Process Outputs and compile to one Json
    final = {}
    for filename in outfiles:
        if os.path.exists(filename):
            f = open(filename, 'r')
            x = f.read()
            y = json.loads(x)
            f.close()

            for s in y:
                if s not in final:
                    final[s] = y[s]
                else:
                    final[s] += y[s]

    dump_json(final, outfile)

    for filename in outfiles:
        if os.path.exists(filename):
            os.unlink(filename)

    #Do the same for scratch files
    scratch_data = ''
    for filename in scratchfiles:
        if os.path.exists(filename):
            f = open(filename)
            scratch_data += f.read()
            f.close()
    if len(scratch_data) > 0:
        scratch(data, scratchfile)

    for filename in scratchfiles:
        if os.path.exists(filename):
            os.unlink(filename)

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


    #### TEST ENTROPY ####
    if entropy('AAAA') != 0.0:
        raise Exception("FAILED entropy test 1: Zero Entropy")

    if entropy('AATT') != 1.0:
        raise Exception("FAILED entropy test 2: Low Entropy")

    if entropy('ATGC') != 2.0:
        raise Exception("FAILED entropy test 3: Mid Entropy")

    b = b''
    for x in range(0, 256):
        b += x.to_bytes(1,'big')
    if entropy(b) != 8.0:
        raise Exception("FAILED entropy test 4: Ludicrus Entropy")

 
    #### TEST SEQ OPS ####
    seq = 'ATGCAATTGGCATCCG'
    if reverse_seq(seq) != 'GCCTACGGTTAACGTA':
        raise Exception("FAILED TEST: reverse_seq()")
    if mirror_seq(seq) != 'CGTATTAAACGGGCCT':
        raise Exception("FAILED TEST: mirror_seq()")
    if compliment_seq(seq) != 'TACGTTAACCGTAGGC':
        raise Exception("FAILED TEST: compliment_seq()")

    #### TEST MEMORY MAPPING
    r1 = random_seq(10000)
    f = open(name_1, 'w+')
    f.write(r1)
    f.close()

    x = map_file(name_1, 1, 250)
    b = x.buf
    if bytes(b[:]).decode() != r1[1:251]:
        x.close()
        x.unlink()
        clean(name_1, name_2, name_3)
        raise Exception("TEST FAILED: Memory Mapped file")
    x.close()
    x.unlink()
    clean(name_1, name_2, name_3)


    #### TEST MP SPLIT
    r1 = random_seq(10000)
    f = open(name_1, 'w+')
    f.write(r1)
    p = get_mp_split(name_1, [1,2,1])
    #Good enough
    expected = {0: [(0, 0, 2560)], 1: [(1, 2496, 2560), (2, 4992, 2560)], 2: [(3, 7488, 2512)]}
    if p != expected:
        clean(name_1, name_2, name_3)
        raise Exception("TEST FAILED: get_mp_split ")

    clean(name_1, name_2, name_3)


    #### TEST ASCII TO BASE and BASE TO ASCII
    input_string = "THIS IS PRIOR ART"
    input_string = 'https://youtu.be/dQw4w9WgXcQ'
    a2b = ascii_to_base(input_string)
    print(a2b)
    print(len(a2b))
    b2a = base_to_ascii(a2b)
    if b2a != input_string:
        raise Exception("TEST FAILED: b2a, a2b")

    ### TEST LIST TO DICT
    l = ['a','b','c']
    d = list_to_dict(l)
    if d != {0:'a', 1:'b', 2:'c'}:
        raise Exception("TEST FAILED: list to dict")

    ### TEST INTERLEAVE MESSAGE
    message = 'TEST'
    message_bases = ascii_to_base(message)
    message_bases_rc = compliment_seq(reverse_seq(message_bases))
    message_final = interleave_messages(message_bases, message_bases_rc, 2)
    if message_final != 'CCTGCAGGCAATCCGGCCGGATTGCCTGCAGG':
        raise Exception("TEST FAILED: interleave_messages")

    print("TESTS PASSED")
