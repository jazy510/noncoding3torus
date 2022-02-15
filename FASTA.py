import os
import random
import re
from UTILS import *

def load_fasta(filename):
    '''
        INPUT: Filename of FASTA formatted file
        OUTPUT: Object with key = seq name, value = seq data

        FASTA Format:
         >Some Description
         A|C|G|T*50 to 80 (Could have lowercase to show repeats, and others to show combinations of possibliities)

         !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
         !THIS DOES NOT HANDLE EXPANSIONS
         !NOR DOES IT DO UPPERCASE BECAUSE IT IS JUST TO FIND THE DATA AND LOAD IT.
         !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''
    data = {}
    f = open(filename, 'r')
    d = ''
    namecount = 0
    name = ''
    try:
        while True:
            line = f.readline().strip()
            if line == '':
                data[name] = d
                break

            if line[0:1] == '>':
                data[name] = d
                d = ''
                name = line[1:]
                namecount += 1
                if namecount %1000 == 0:
                    print("Loading Sequence: " + str(namecount))
            else:
                d += line
    except:
        data[name] = d
    f.close()

    if '' in data:
        del(data[''])

    return data

def load_fasta_seq(filename, seq_name):
    '''
        INPUT: Filename of FASTA formatted file, and a sequence name to load
        OUTPUT: Object with key = seq name, value = seq data

        FASTA Format:
         >Some Description
         A|C|G|T*50 to 80 (Could have lowercase to show repeats, and others to show combinations of possibliities)

         !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
         !THIS DOES NOT HANDLE EXPANSIONS
         !NOR DOES IT DO UPPERCASE BECAUSE IT IS JUST TO FIND THE DATA AND LOAD IT.
         !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''
    if not os.path.exists(filename):
        raise Exception("File not found: " + filename)
    data = {}
    f = open(filename, 'r')
    d = ''
    namecount = 0
    try:
        #find start of seq_name
        while True:
            line = f.readline()
            if line == '':
                raise Exception(seq_name + " not found!")
            if line[0:1] != '>':
                continue
            line = line.strip()
            line = line[1:]
            if seq_name == line:
                break

        #Found start of sequence 
        while True:
            line = f.readline()
            if line[0:1] == '>' or line == '':
                data[seq_name] = d
                break
            d += line.strip()
    except:
        data[seq_name] = d

    f.close()

    if '' in data:
        del(data[''])

    return data



def write_fasta(data, outfile):
    '''
        INPUT: object with fasta header without the '>' as the key, sequence data as the value
               OUTPUT filename
        OUTPUT: fasta file (WITHOUT STUPID 50-80 char length limit)
    '''
    f = open(outfile, 'w+')
    for name in data:
        f.write('>' + name + '\n')
        f.write(data[name] + '\n')
    f.close()

def flatten_fasta(filename, outfile, repeat):
    '''
        INPUT: filename of FASTA formatted File, Output Filename, # of repeats for sequences less than 32 bases
        ACTION: Open Fasta File, and confirm FASTA FORMAT
                Generate a random temp file in the local directory
                Read in Line by line and remove FASTA headers, newlines, and N's (Any sequence) and write to temp file
                Limit read to 250MB so as not to destroy system memory
                Search for repeat sequences (lowercase atgc), UPPERCASE it and Expand 'repeat' times
                    Only repeat twice for runs greater than 32 bases long. (As this would be a whole cube and don't want doubles)
                Write to outfile and unlink temporary file
        OUTPUT: Flattened, EXPANDED, sequence written to outfile.
    '''
    f = open(filename, 'r')
    d = f.read(1)
    f.seek(0)
    if d != '>':
        f.close()
        raise Exception("Not a FASTA file! " + filename)

    #Get Rid of headers, newlines, and 'N's; write to temp file.
    rand_name = str(random.randint(1000000, 999999999)) + '.tmp'
    d = ''
    x = open(rand_name, 'a+')
    while True:
        d = f.readline()
        if d == '':
            break
        if '>' in d:
            continue
        d = d.replace('\n', '')
        d = d.replace('\r', '')
        d = d.replace('N', '')
        x.write(d)

    f.close()
    x.close()

    #EXPAND OUT LOWERCASE TO REPEATED SEQUENCES
    l = re.compile('[atgc]{1,}')
    x = open(rand_name, 'r')
    y = open(outfile, 'a+')
    final = ''
    while True:
        d = x.read(250000000)
        if d == '':
            break

        #Make sure last characters are not lowercase unless EOF
        while True:
            if d[-1] in ['a','t','g','c']:
                temp = x.read(1)
                if temp == '':
                    break
                else:
                    d += temp
            else:
                break

        start = 0
        end = 0
        last_end = 0
        while True:
            res = l.search(d, start)
            if res:
                start, end = res.span()
                y.write(d[last_end:start].upper())
                if end - start < 32:
                    y.write((d[start:end] * repeat).upper())
                else:
                    y.write((d[start:end] * 2).upper())
                last_end = end
                start = end
            else:
                y.write(d[start:].upper())
                break
    x.close()
    y.close()
    os.unlink(rand_name)

def has_nonstandard(data):
    '''
       Check to see if FASTA data has anything execpt ATGC.  atgc are ok.
       R = A OR G
       Y = C, T or U
       K = G, T or U
       M = A or C
       S = C or G
       W = A, T, or U
       B = C, G, T, or U .. NOT A
       D = A, G, T, or U .. NOT C
       H = A, C, T, or U .. NOT G
       V = A, C, or G, .. NOT T or U
       N = A C G T U (Nucleic Acit)
       - = Gap of inderterminate Length
    '''
    nonstandard = ['R', 'Y', 'K', 'M', 'S', 'W', 'B', 'D', 'H', 'V', 'N', '-']
    for x in nonstandard:
        if x in data:
            return True
    return False


def sequence_names_and_count(data):
    '''
         INPUT: object with keys of sequence name, value = sequence data
         OUTPUT: Print Name of Sequence and Sequence Counts.  Largest Last.

    '''
    temp = []
    for name in data:
        temp.append(len(data[name]))
    temp.sort()

    name_len = {}
    for x in temp:
        if x not in name_len:
            name_len[x] = []

    for name in data:
        name_len[len(data[name])].append(name)

    for x in name_len:
        for name in name_len[x]:
            print(name + ' ' + str(x) )


def extract(data, seq_name, outfile):
    '''
        INPUT: object with key = sequence name, value = SEQUENCE, the sequence name, and the file to write it out to
        OUTPUT: File in FASTA format of the given sequence

    '''
    if seq_name in data:
        d = {}
        d[seq_name] = data[seq_name]
        write_fasta(d, outfile)
    else:
        raise Exception(seq_name.decod() + ' not found')

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


    ### TEST 1 ####
    # FASTA.py - write_fasta, load_fasta
    #Write FASTA file with two sequences.  Read in FASTA and verify structure of 
    seq1_name = str(random.randint(99999999,999999999999)) 
    seq1 = random_seq(5)
    seq2_name = str(random.randint(99999999,999999999999))
    seq2 = random_seq(32)

    out_data = {seq1_name:seq1, seq2_name:seq2}
    write_fasta(out_data, name_2)
    in_data = load_fasta(name_2)

    if out_data != in_data:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 1")

    ###### TEST 2
    #FASTA.py -> load_fasta_seq
    in_data = load_fasta_seq(name_2, seq2_name)
    if seq2_name not in in_data or in_data[seq2_name] != out_data[seq2_name]:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 2")
    in_data = load_fasta_seq(name_2, seq1_name)
    if seq1_name not in in_data or in_data[seq1_name] != out_data[seq1_name]:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 2")


    #### TEST2.2
    #### FASTA.py - extract
    name_3 = str(random.randint(99999999,999999999999)) + '.tmp'
    extract(in_data, seq1_name, name_3)
    in_2 = load_fasta(name_3)
    if seq1_name not in in_2:
        clean(name_1, name_2, name_3)
        raise Exception('TEST 2.2 Failed: extract()')
    clean(name_1, name_2, name_3)


    ###### TEST 3
    ##### FASTA.py - write_fasta, flatten_fasta, read_file
    # Flatten a FASTA File.
    # Create a FASTA file with Random, then Lowercase, then random. Then lowercase more than 32 long., then random.
    # Ensure flattened file matches expected.
    # Repeat with read offset increase and # bytes decrease
    seq3_name = str(random.randint(99999999,999999999999)) 
    r1 = random_seq(10)
    r2 = random_seq(10)
    r3 = random_seq(10)
    if len(r1) != 10:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 3: random_seq failue")

    seq3 = r1 + 'atgc' + r2 + 'atgc'*10 + r3
    out_data = {seq3_name:seq3}
    write_fasta(out_data, name_2)
    flatten_fasta(name_2, name_1, 4)
    x = read_file(name_1, 0, -1)
    expected = r1 + 'atgc'.upper() * 4 + r2 + 'atgc'.upper() * 10 * 2 + r3
    if x == seq3:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 3: FLATTENED FASTA DID NOT EXPAND LOWERCASE")
    if x != expected:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 3: READ FLATTEND FASTA IS WRONG!")

    x = read_file(name_1, 1, len(expected) -2)
    expected = expected[1:-1]
    if x != expected:
        clean(name_1, name_2, name_3)
        raise Exception("FAILED TEST 3: READ FLATTEND FASTA WITH OFFSETS IS WRONG!")

    clean(name_1, name_2, name_3)

    print("TESTS PASSED")
