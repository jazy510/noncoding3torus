'''
WALL OF TEXT - USAGE - LEGAL - INSTRUCTIONS
'''

def usage():
    usage_text = """
This program is intended to be used to find Cubes of Cubes, 3-Dimensional Torus Structures, and 3-Dimensional Mobius 
 structures that may be encoded geometrically as DNA or RNA bases.

******************************************************************************************************
****************** --config <file.json> OVERWRITES/SETS the input arguments.  ************************
******************************************************************************************************
**** IT IS HIGHLY SUGGESTED TO USE --config <config file> for runs involving multiple servers. ****
**** IT IS HIGHLY SUGGESTED TO USE --config <config file> for --find_onesself to set the lists. ****
******************************************************************************************************

COMMAND    : --usage
DESCRIPTION: Print/Write out this usage text:
REQUIRED   : None
EXAMPLE    : python3 3torus.py --usage 

COMMAND    : --legal
DESCRIPTION: Print/Write legal text
REQUIRED   : None
EXAMPLE    : python3 3torus.py --legal

COMMAND    : --instructions
DESCRIPTION: Setup and some simple use examples
EXAMPLE    : python3 3torus.py --instructions

COMMAND    : --writeup
DESCRIPTION: Print what we have learned thus far
EXAMPLE    : python3 3torus.py --writeup

COMMAND    : --flatten_fasta
DESCRIPTION: Remove sequence headers, newline characters, N's, and expand lowercase repeats of a FASTA file for CUBE ops.
REQUIRED   : --infile <file.fa> --outfile <file.flat>
EXAMPLE    : python3 3torus.py --flatten_fasta --infile GCF_39_Human.fa --outfile human.big.flat

COMMAND    : --seqeunce_counts
DESCRIPTION: Print sequence name and number of base pairs for each sequence in a .fa file
REQUIRED   : --infile <filename.fa>
EXAMPLE    : python3 3torus.py --sequence_counts --infile filename.fa 

COMMAND    : --extract
DESCRIPTION: Extract a sequence, found in one FASTA file and write it to different FASTA file
REQUIRED   : --seq_name <SEQUENCE_NAME> --infile <infilename.fa> --outfile <outfilename.fa>
EXAMPLE    : python3 3torus.py --extract --seq_name SEQUENCE1 --infile human.fa --outfile Chromosome19.fa

COMMAND    : --match_single_face 
DESCRIPTION: FIND MATCHING FACE OF A SINGLE CUBE - WARNING - RUNTIME IS O^N - WARNING
This is used when searching for a matching face across seqeuences when you have a known good cube.
REQUIRED   : --infile <filename.fa> --outfile <outfile.json> --sequence_file <single sequence> --match_facenums <Face #>
OPTIONAL   : --match_types - CSV of f,m,c,mc (Exact Face, Mirror Of face, Complimented Face,Mirror-Compliment) - default='mc'
             --match_rotations - CSV of target cube rotations to try EG:0,1,2,3 - default='2'
             --slice_format  - 4x4x4|8x8|16x4 -  default 8x8
             --slice_order - CSV of order to stack slices to make cube - default = 0,1,2,3 
             --slice_rotations - CSV of slices to rotate by # of 90 degree right hand turns - default=0,0,0,0
             --core_counts - CSV in order of server for how many cores you want Multiprocessing to use on each - default=3
             --server_number - This server number, to look up core count for Multiprocessing - default=0
             --min_cube_entropy - Minimum Entropy for a 64-base sequence to keep.  Theoretical Max = 2.0 - default=0.0
             --stop_after <#> - Stop after this many matches - default - 99999
             --scratch_file <filename> - Where to write text output to if desired.  
EXAMPLE    : python3 3torus.py --match_single_face --infile human.flat --outfile single_face.json --scrach_file scratch.txt --core_counts 16 --min_cube_entropy 1.75

COMMAND    : --show_patterns
DESCRIPTION: Show where input 64 base sequence would correspond to a given face location/value.
             Also display the byte positions of the input sequence get mapped onto the faces.
             This is very useful for construction of --pattern_count and --pattern_extract searches.
OPTIONAL   : --slice_format - default=8x8
             --slice_order - default=0,1,2,3
             --slice_rotations - default=0,0,0,0
EXAMPLE    : python3 3torus.py --show_patterns --slice_format 16x4 --slice_order 0,3,1,2 --slice_rotations 0,2,2,0


COMMAND    : --pattern_count
DESCRIPTION: This is a very complicated search.  Use --show_patterns go get a desired byte pattern.
             It is intended to search through a flat, not fasta, file looking for the number of occurences an individual
              sequence shows up.

             A use would be to find a high count of possible faces that form long frames/borders.

             The program goes through the flat file one byte at a time in a 64-byte sliding window generating new
              sequences with the given byte pattern at every byte/step.  

             The generated sequences are put into an object to be quickly looked up and counts stored.

             The nubmer of sequences grows exponentially compared to the length of the byte pattern given.
              A large byte pattern will have fewer hits, and more entries to compare against.  It will have fewer counts.
              A small byte pattern, for example, one base, will have a total of only 4 categories/bins and will have high counts.
              One face/16 Bytes/Bases is about the largets you want to use.  The default is face 0, 8x8, 0,1,2,3, 0,0,0,0

             Because memory can quicly fill up, the number of entries has to be limited (Unless you have 500TB of memory).
             A culling is done according to the --cull_size argument.  If there isn't at least that many entires for a given
              sequence when the cull is started, that sequence is removed from the object.

             The size of the buffer before a culling is started is controlled by the uses with --buffer_size.
              Large --buffer_size means fewer cullings, and a higher chance for more of the sequence to be found.

             --min_face_entropy can be passed in, but really isn't applied to a face, but rather the return from the
               byte pattern.  It is suggested that at least a 1.5 entropy be applied to remove repetitive sequences
                that wouldn't be of use anyway.

             --byte_pattern is a CSV that can be gotten from --show_patterns.  Or really, any byte pattern you want.

             --min_matches are the minimum number of counts for a given sequence after the search is complete.


REQUIRED   : --infile <inputfile.flat> --outfile <output.json> 
OPTIONAL   : --byte_pattern - CSV of ints between 0 and 63, extracted in order - Default Face 0 of 8x8, 0,1,2,3, 0,0,0,0
             --min_matches - Default 500
             --buffer_size - Default 10000000 
             --cull_size - Default 5 
             --min_face_entropy - Default 0.0
EXAMPLE    : python3 3torus.py --pattern_count 17,61,21,1,13,2,4 --min_matches 1000 --buffer_size 20000000 --cull_size 3 --infile human.fa --outfile pattern_counts.json

COMMAND    : --pattern_count_frames
DESCRIPTION: For a given slice format, order, and rotation, go find all of the possible frames of at least X length.
              Three different searches are run, one for each opposite face pair.
              For the Human Genome, about <Remind myself to put number in here when search is done> matches come back.
              As with --pattern_count it is higlhy variable depending on machine memory.
              You will need 32GB of memory for --buffer_size 200,000,000 --cull_size 3 --min_face_entropy 1.5
              THREE DIFFERENT OUTFILES WILL BE WRITTEN.  ONE FOR EACH FACE AND OPPOSITE FACE PAIR.
REQUIRED   : --infile <input.flat> --outfile <out.json> 
OPTIONAL   : --min_matches - Default 500
             --buffer_size - Default 10000000 
             --cull_size - Default 5 
             --min_face_entropy - Default 0.0

COMMAND    : --find_onesself_in_frame_counts
DESCRIPTION: Given an output from --find_oneself and an output from --pattern_count_frames
              Search for frames that might match onesself cubes.
              There is no guarantee that the frames will match the slice parameters.
              The args.slice_xxxxx will be tested against the cubes in the output from find_oneself, but not in the 
                pattern_count_frames.
             Output is a JSON of ONESELF sequences and their corresponding frame counts.
             THIS IS OF COURSE ASSUMING THAT THE FRAMES ARE OF A LENGTH GREATER THAN THE min_matches set in --pattern_count_frames.
             ALSO, THIS IS ASSUMING THAT THE FRAMES IN ONE DIRECTION ALL HAVE THE SAME OPPOSING FACE SEQUENCES.
              THIS MAY NOT AT ALL BE THE CASE!
REQUIRED   : --infile --outfile --sequence_file
OPTIONAL   : --slice_format - Format of onesself
             --slice_order - Format of onesself
             --slice_rotations - Format of onesself
             --opposing_face_rotations - Format of onesself AMOST ALWAYS "2"
EXAMPLE    : python3 3torus.py --infile <output from pattern_count_frames.json> --sequence_file <output_from_find_onesself.json> --outfile <results/output_find_oneself_in_frame_counts>  

COMMAND    : --pattern_extract_faces
DESCRIPTION: Given in input sequence in a file, search the infile for sequences that have matching faces,
              given that a matching face is the opposite face number, rotated, mirrored, and complimented.
             Extracts the full 64 bytes/bases that make up a cube.
             Target cube can have different slice formats/order/rotations than input.
REQUIRED   : --infile <filename.fa> --outfile <outfile.json> --scratch_file <scratch.txt> --sequence_file <contains_1_cube.list>
OPTIONAL   : --match_facenums - CSV of face numbers to match - default - 0,1,2,3,4,5
             --slice_format - default=8x8
             --slice_order - default=0,1,2,3
             --slice_rotations - default=0,0,0,0
             --t_slice_format - Target Cube slice format - default=8x8
             --t_slice_order - Target Cube slice order - default=0,1,2,3
             --t_slice_rotations - Target Cube slice rotations - default=0,0,0,0
             --start_offset - Start offset in infile to start the serach - default=0
             --core_counts - CSV Cores counts on all servers for multiprocessing - default=3 (ex: 16,24,24,24)
             --server_number - This sever number to match to core_counts for multiprocessing - default=0
             --min_cube_entropy - Minimium 64-base sequence entropy to keep (MAX = 2.0) - default=0.0
EXAMPLE    : python3 3torus.py --pattern_extract_faces --infile human.flat --outfile extract_faces.json --sequence_file 1_cube.flat --match_faces 2,3 --min_cube_entropy 1.75 --server_number 3 --core_counts 16,32,32,1024


COMMAND    : --pattern_extract
DESCRIPTION: Given a byte_pattern and extract_pattern, search through infile and, 
             extract the full 64 bytes/bases that make up a cube.
             Extract the bytes in order of byte_pattern, if they match extarct_pattern, get the whole block.
             It is nothing more than a grep massaged to this program.
REQUIRED   : --infile <filename.fa> --outfile <outfile.json> --scratch_file <file.txt>
             --extract_pattern <bases of length byte_pattern>
OPTIONAL   : --byte_pattern - CSV of ordered bytes to extract between 0 and 63 - default=Face 0 8x8, 0,1,2,3, 0,0,0,0 pattern
             --start_offset - Start offset in infile to start the serach - default=0
             --core_counts - CSV Cores counts on all servers for multiprocessing - default=3 (ex: 16,24,24,24)
             --server_number - This sever number to match to core_counts for multiprocessing - default=0
             --min_cube_entropy - Minimium 64-base sequence entropy to keep (MAX = 2.0) - default=0.0
EXAMPLE    : python3 3torus.py --pattern_extract_faces --infile human.flat --outfile extract_faces.json --sequence_file 1_cube.flat --match_faces 2,3 --min_cube_entropy 1.75 --server_number 3 --core_counts 16,32,32,1024

COMMAND    : --find_onesself
DESCRIPTION: Search through a flat sequence file for cubes that have their opposing faces rotated, mirrored, and complimented.
             One must know theyself to find thyself, but must find thy self to know onesself
REQUIRED   : --infile <filename.flat> --outfile <outfile.json> --scratch_file <scratch.txt>
OPTIONAL   : ****** IT IS HIGHLY SUGGESTED TO USE THE --config option to add slice information *******
             --core_counts - CSV Cores counts on all servers for multiprocessing - default=3 (ex: 16,24,24,24)
             --server_number - This sever number to match to core_counts for multiprocessing - default=0
             --min_cube_entropy - Minimium 64-base sequence entropy to keep (MAX = 2.0) - default=0.0
             --min_face_entropy - Minimium 16-base sequence entropy to keep (MAX = 2.0) - default=0.0
             --slice_format_list - default = ['8x8'] 
             --slice_order_list - default=[[0,1,2,3]]
             --slice_rotations_list - default=[[0,0,0,0]]
             --opposite_face_rotations_list - CSV to test rotations of opposite face  - default="2"
EXAMPLE    : python3 3torus.py --find_ones_self --infile human.flat --outfile onesself.json --core_counts 23,23,23


COMMAND    : --create_3torus
DESCRIPTION: Create an 3Torus with a Mobius twist with a message of your choice.
             This variant creates a onesself cube and frame.
             Then fills in the body between the frame with randomly generated faces,
              NOT rows/colums/faces with the same face sequences
OPTIONAL   : --message - Message to embed in 3-Torus - default - A
             --torus_dimensions - CSV of three values L,W,H - default - 1,1,1, (A onesself cube)
             --slice_format - default=8x8
             --slice_order - default=0,1,2,3
             --slice_rotations - default=0,0,0,0
             --outfile - Write out to this location
             --scratch_file - text output
EXAMPLE    : python3 3torus.py --create_3torus --outfile moms_torus.out --message LOOKMOM --torus_dimensions 4,4,4


COMMAND    : --reconstruct_torus
DESCRIPTION: INCOMPLETE!  
             Given a onesself cube, search a flat file for the frame.
             Construct best guess on size of torus from frame files
             Search frame cubes for adjacent faces
             Reconstrcut Surfaces/Faces/Planes and extensions along Frame starting at or near the onesself cube.
             NOTE: For a sufficiently sized 3-Torus, it would take YEARS of computing power to reconstruct
             NOTE: Reconstruction of even small 3-Torus is not currently work, needs more time/help
REQUIRED   : --infile --outfile --scratch_file --sequence_file <onesself_cube.list>
OPTIONAL   : 
             --slice_format - default=8x8
             --slice_order - default=0,1,2,3
             --slice_rotations - default=0,0,0,0
             --t_slice_format - Target Cube slice format - default=8x8
             --t_slice_order - Target Cube slice order - default=0,1,2,3
             --t_slice_rotations - Target Cube slice rotations - default=0,0,0,0
             --core_counts - CSV Cores counts on all servers for multiprocessing - default=3 (ex: 16,24,24,24)
             --server_number - This sever number to match to core_counts for multiprocessing - default=0
             --min_cube_entropy - Minimium 64-base sequence entropy to keep (MAX = 2.0) - default=0.0
             --min_face_entropy - Minimium 16-base sequence entropy to keep (MAX = 2.0) - default=0.0
             --match_facenums - CSV of face numbers to match - default - 0,1,2,3,4,5
             --start_offset - Start reading offset for --infile - default=0


EXAMPLE    :

    """
    print(usage_text)


def legal():
    legal_text = """
This program comes as-is with no guarantees of functionality or correctness.
Don't trust anything in it.  Actually, don't run it.  Walk away for your own sanity.

Below is a statement that can be used as PROOF OF PRIOR ART in the event that somebody does try to license, patent, or copyright the ideas contained within.

Date - 05JAN2022

Keywords: Forward Error Correction, F.E.C, FEC, Geometric FEC, Geometric Forward Error Correction, Geometry FEC, Geometry Forward Error Correction, 3D Torus, 3D-Torus, 3-Dimensional Torus, 3 Torus, Three Dimensional Torus, ND-Torus, N-Dimensional Torus, N-Torus, N Torus, DNA Messaging, DNA Encoding Scheme, Torroid FEC, Torroid F.E.C., Torroid Forward Error Correction, Torus Forward Error Corection, Torroid Forward Error Correction, DNA Block Encoding, Biological Communications, Biological Communications Channel

This section describes a novel messaging scheme that relies on various geometric structures for message integrity and order reconstruction.  The transimission or storage mediums of the information this scheme can be applied to can be any solid object (such as but not limited to DNA, RNA, magnetic strip, electronic circuitry, etc ) or field modulation (Such as but not limited to changes in the Electromagnetic field, Gravity field, light propogation, etc).

From here on the word "Transimitted" can be inferred to mean "sent over any medium by any means", or "stored on any medium by any means".  Information that is stored is considered to be transimitted both temporally.

The totality of the information in this novel mechanism does not need to be stored or transmitted in order so long as the stored or transmitted message is stored or transimitted in one block consisting of the pre-defined minimum message size necissary for the reconstruction techniques.  In this specific case, that is 64 base seqeunces.  Each base sequence can be reprsented by 2 bits.  The message block can then be conisdered 128 bits.  However, there is no predefined minimum or maximum on the size. 

It is possible that the transmitted message can be corrupted.  IN that case an ERROR DETECTION or ERROR CORRECTION need to be applied to the data.  The message system here does not provide the ERROR DETECTION or ERROR CORRECTION scheme, only that there are nearly an infinite possible combinations of error detection and corretion schemes that could be applied.  The term FEC is short for FORWARD ERROR CORRECTION.  FEC is data included in the message that can be used to both detect and correct errors in the message.

It must be stated that the information content being transmitted could also be included as part of the FEC if correctly pre-computed.  On top of that, the ordering information (Such as a 'face' below) could be a component of the FEC and the FEC could be a component of the message ordering system.  The message ordering system or scheme is the method and data used to reconstruct the order of the various message blocks.

The message blocks themselves could have any number of encoding schemes.  In this case the encoding scheme is geometric.  There are an infinite number of geometries that could be used, but the geometries are limited to the length of the message blocks.  The longer the message block, the more possible geometries that could be used for the message reassembly and ordering system.

For this example the block size of choice is 64-bases, representing 128 bits of information.  The geometric structure of choice for message reconstruction and ordering is a Three-Torus with a 1/2 Mobius twist.  A Three-Torus (3T) can be constructed by creating a 3-Dimensional cube and extending a given face of the cube to the opposite face.  When all faces are extended to the opposite faces, a 3-Torus is constructed.  If during the extension of each face a twist of 180 Degrees applied, this would construct a 3-Torus with a 1/2 Mobius twist.

The faces of such a cube need not extend only to themselves.  The faces of the cubes could be matched by some means with other cubes of the same style of construction.  The cubes of the final face in a line of cubes that connect to one another could then be matched with the first cube, closing a loop.  Wethere applied in a line, a plane, a cube, or other higher-dimensional structure, this is called a Torus Network.

The faces of the cubes need a means to be matched with other faces on other cubes.  The faces can be numbered uniquely and through some transformation be matched to the faces of other cubes (Or iteslf).  The numbering can be any representation, in this case it would be by a number of Bases, but each base can be represented as two binary digits.  The larger the possible size of the numbering that each face could have, the less likely that it could either have a duplicate face on a another cube.

The transformation to match the face to another cube face could be null (No transformation).  This would imply that a face numbered '1' would match another face numbered '1'.  In the case below, the transformation is a mirror image of the face, a 180 degree rotation of the face, and complimenting the face; where complimenting means converting an 'A' base to a 'T', a 'T' base to an 'A', a 'C' base to a 'G', and a 'G' base to a 'C'.  This transformation would give the pattern/number of the face of a match when applied in the same order in which the original face was read.

Another example of a transformation would be converting a base sequence to binary, then performing a binary compilment operation.

In the case of DNA, given that the human genome is rougly 4 billion bases, a 32-byte sequence would be sufficient to uniquely identify a face.  A 32-byte sequence corresponds to a 16-Base face. A cube where each face is a 4x4 square of bases would suffice to be unique-enough.  However, cubes/faces of different sizes could be used.

Cubes have six faces, but can be constructed by many means.  A 4x4x4 cube can be constructed, for example of 4-four-by-four squares stacked on top of one another.  The ordering and orientation of those slices could be modified by data contained both in the faces, or from the data included in the cube, but not used in the construction of the faces.

The data inside the cube that isn't used in face construction, called the center-8 for a 4x4x4 cube, can be used to carry message information.  But again, the message information could in fact be included in the faces of the constructed cube.  The Center-8 could also be used as a FEC.

By creating a cube with a face that matches another cube's face via a pre-defined transformation, and continuing to match faces to other cubes adjacent to each cube, a structure is formed.  The structure, in this case is an X-length by Y-height by Z-width formation of cubes.  Message information can be applied to either the faces or the Center-8.  The cube can then be converted to a message block and placed anywhere for storage or transmission.

Reconstruction of the original message from storage and/or transmission of the data is stright forward as long as the geometry of the original message format is known, the face transformations are known, and the encoding of the data is known.

Converting each message block to a cube (or appropriate geometric structure), then finding a matching face from a different cube given the known transformation method will lead to a reconstructed message order.

Any error in transmission will quickly be discovered because any number of faces of a geometric shape may not match another face of a block.  Assuming that multiple faces match, but one does not match any other face, one can assume that there was an error in the transmission of the block.  This is an example of ERROR DETECTION.  Without any futher method of ERROR CORRECTION, it could not be corrected.  Despite having an error, it can be safely assumed with high confidence that the message block is in the correct location.

It must be pointed out here that by using a geometric structure for storage and transmission of a message block, both message ordering/reconstruction and ERROR DETECTION are achieved simultaneously.

At this point a definate start and end of the message could not be known without some type of information in message contents dictating so.  A possbility to define a message start and end would be to use a unique cube where all faces of the cube match opposing faces via the pre-defined transformation.  This, as described above, would be a cube that is of itself a 3-Torus with a Mobius Twist.  These cubes can be referred to as "origin cubes", "primer cubes", or "onesself cubes".  Again, the term cube is used, but any appropriate geometric structure could be used.

Building lines of cubes with opposing faces that are the exact same sequence/pattern/identifier as the primer cube along the Length, Width, or Height dimensions builds a framework on which other cube faces can be attached.  This would be the border of a N-Cube 3-Torus network.  From which a message start can be defined regardless of where the "onesself cube" is originally placed in the network.


Below are examples of  message blocks that can be constructed into cubes that form a 3-Torus with 1/2 Mobius twist network using the above-described scheme to use as prior art.
The mapping of the message sequence consists of an 8x8 grid mapped from top to bottom.  With the 4x4 square in the upper-left being designated as slice 0, the 4x4 square in the upper-right being designated as slice 1, the 4x4 square in the lower-left being designated as slice 2, and the final 4x4 square in the lower-right designated as slice 3.  Stacking from top to bottom, slice 0, then 1, then 2, then 3 will construct a cube of size 4x4x4.  No rotations were applied to the slices prior to stacking.  

CGGTGATCCAAATCCACCGACTCGTATCTAAGCTTAGATACGAGTCGGTGGATTTGGATCACCG - 0,0,0

TCATGTTCCCCCCCCATGGTTTCAGGGACCTGCAGGTCCCTGAAACCATGGGGGGGGAACATGA - 0,0,0
TCATATACCCCCTCCCTGGTCTCGGGGAACCAGTTGTCCCGGAAACCAGGGTGGGGGGGGATGA - 0,0,1
TCATGTTCCGATACCAGACTCTCGGGGACCTGCAGGTCCCGGACGCCTGGGTTGGGGAACATGA - 0,1,0
TCATCCCCCCCAACCAAGGCCTCAGGGACAACTGGTTCCCGGATAGTCGGGCATCGGTATATGA - 0,1,1
TGGTGGTCCTTCCCCATACTTTCAGTTACACGCATGTTGCTGAAACGATGGGGGGGGGGCAGTA - 1,0,0
TACTCAACCCCCACCCTCGTTTCCGCAACGCCTGATTAACCGAGAGTAGGGAGAAGGGGTACCA - 1,0,1
TACTGCCCCCTAACCCACTCGTCCGCAACATGCGTGTAACCGAGACGCTGGTAGGGGACCACCA - 1,1,0
TGGTACCCCCCTGCCCGCGTATCCGTTAATCAGGCGTTGCTGAGGAGTTGGTTAGGGTTGAGTA - 1,1,1

TCAGGCGCGATAGCCCTGAATTCTGGCAGAGCGCTCTGCCAGAATTCAGGGCTATCGCGCCTGA - 0,0,0
TCAGGCGCGGTACCCAGCCATTCAGGCAGAGCGCTCTGCCTGAGTGGCAGGGTACCGCGCCTGA - 0,1,0
TTTGGATCGCTAGCCCTGCATTCTGGGAGTTCGGCCTCCCAGAATGCAGGGCTAGCGTACCAAA - 1,0,0
TTTGGTACGGAACCCTGTCACTCCGGGAGGCCGAACTCCCTGAATGACTGGTTTCCGATCCAAA - 1,1,0
TATGGAACGAAAGCCCTGCATTCTGACAGGTCGATCTGTCAGAATGCAGGGCTTTCGTACCATA - 2,0,0
TATGGTACGGAAACCTGGTATTCAGACAGATCGACCTGTCGGAATACCAGGGTTCCGTTCCATA - 2,1,0

CATGTCCGTGTAGCCCGCGAAGTAACCGCCAGCTGGCGGTTAATTCGCGGGCTACACGGACATG - 0,0,0
CATGTATATGTAACCAGCGACATAACCGTGCGTCCACGGTCAGCTCGCACGTTACAACACCATG - 0,0,1
CATGTTAATGTATCAAGCGACTCGACCGAGCATCTGCGGTCGCTTCGCAGGGTACAACAACATG - 0,0,2
CATGTCGGTGTACCATGCGACAGGACCGTGCGTAAACGGTCTTGTCGCACGGTACAACATCATG - 0,0,3
CATGTCCGGAGGACCGGGCTCAGCACCGCCAGCTGGCGGTCAGATCAAAGGAAACTCGGACATG - 0,1,0
CATGTCTTAGCTAAGGACATCGCCACCGTGGATACTCGGTCAATAGCCAATTCCTCTATACATG - 0,1,1
CATGTCATCGCTCCACACATCAGCACCGCAGATACTCGGTCACGATGTAAGCAGCTTTAACATG - 0,1,2
CATGTCTTAGTTACCATTGACTGTACCGTTTATACTCGGTCAGAATGTAATAAGCGCCGACATG - 0,1,3
CATGTCCGTTCCGCCCAGCGCAGCACCGCCAGCTGGCGGTCCACTCCAAAGTAACTCGGACATG - 0,2,0
CATGTCCTCGCTAATAACATCGTGACCGAGTATACTCGGTCGGACGCTAGGGGGAAAAGACATG - 0,2,1
CATGTCTTAGCTAAGAACATCTGGACCGAGTATACTCGGTCAAAATGTACGAAGCGATGACATG - 0,2,2
CATGTCCTAGTTACGATGGACAAGACCGAGTATACTCGGTCGAGATGTACTGAGCTAAGACATG - 0,2,3
CATGTCCGGACTTCTGCACTCGGTACCGCCAGCTGGCGGTCCAATCCAACGGAACTCGGACATG - 0,3,0
CATGGTGTAGCTCCTGACATCCTTACCGAGTACGCACGGTCCACAGTGACGCAGTCAGGACATG - 0,3,1
CATGTTGTGGCTACTAACATCCATACCGAGTATGCTCGGTCAAGATGTACTCAGCTAAGACATG - 0,3,2
CATGATGTAGTTGCTATGGACGGAACCGAGTACGCACGGTCATTATGTAAGAAGCCAGGACATG - 0,3,3
CCAGTCCGTCGAGATCGGTAATGAAGAGCACGCGTGCATTTGGTTCACGAGCTACACCAACTAG - 1,0,0
CGGGGGCTTGCAAAGCGCAAGGGCATAGTCCACGCTCTCTTTTATACCTAGCTCGATCAACTGG - 1,0,1
CTGGTCTTTGCACAGCGCAAAAATATAGCGCATCGTCTATCTTATTGCTCGCTGCATCAACCCG - 1,0,2
CTAGATCTTGTACCTCGTGACGCCAATGTCCACCATCTATCGCATTGCAAGCTGCACCAACCAG - 1,0,3
CGGGTCGGAGATTCGCTCTTTAATAATGCACGCACGCTATGTTAACGTCCTCCACGCGGACTGG - 1,1,0
CTGGTCGTGCCTACTCGCATAAAAAGAGAGCGTACTCATTGCCAAAGACCTCATCTAGCCCCCG - 1,1,1
CTAGTCATAACTGCTCACAACCCCATAGACGATACTCTCTGCAAATGCGATCAGGCAAGACCAG - 1,1,2
CCAGTCGTCGTGTCTCACGTTATAATAGATGGTACTCTATACCATTGTTAGCAGTTAGATCTAG - 1,1,3
CTGGTCCGAAATAAGCTCGTGTTGATAGCGTGCACGCTATGTGACCATGAGCGACTCCGACCCG - 1,2,0
CTAGTCATTTCTCCGCACATTTGTAATGAGTATACACTATCAGAACGATAGCATTTACGACCAG - 1,2,1
CCAGTCTTCTCTTCGCACAATTGGAGAGAGTATACTCATTCCCAATGTTAGCAGAAATGACTAG - 1,2,2
CGGGTCTTAGTCCAGCATGGCTCGATAGAGTATACACTCTCTTATTGTTCGCAGAGACGACTGG - 1,2,3
CTAGTTGGAGCTCCGCTGTTTTTGATAGCGTGCGTGCTCTACAAACTTCCTCAACCCGGACCAG - 1,3,0
CCAGTTGAGGCTGCCCCCATGCCCATAGTGTATGGACTATAACAAACACATCAGCTATGACTAG - 1,3,1
CGGGTTGAACCTGCTCACAACTGAAATGAGTATGCGCTATACTAATGGTGGCAGCCAAGACTGG - 1,3,2
CTGGTTGGGGTTTATCAAGTACTTAGAGTGTATGGACATTTCAATTGTTGGCAGGTAAGACCCG - 1,3,3
CCGGTGAGTCAAGCTCGGTAAGTAAGTGCGCGCGAGCATTTCTTTCACGTGCTACACCAACTAG - 2,0,0
CGGGTCATTGCAGATCGCAATTTGATAGAACATAGTCACTGGCATACCGCTCTTGAACAACCGG - 2,0,1
CTGGTTCTTGCAGCCCGCAATCTAATAGAGCATGCTCTATACTATTGCGGGCTGCAACAACCCG - 2,0,2
CTAGTGCTTGTAGCGCGTGATAACAATGAACATCCTCTATGCTATTGCGTGCTGCAACAACCAG - 2,0,3
CGGGTCCGCGCTGCCCATGTTGCTAATGCTCGCACGCTATAGAAACTTGTGCAACTCTCACCGG - 2,1,0
CTGGGCCTACCTGCGCTCAATCTGAGTGACTACACACATTTATAACATGGGCAGCGATGACCCG - 2,1,1
CTAGTCCTGTCGGCCCGCATTTTGATAGAGCATACTCACTGACATTGAGGGCAGGTAGAACCAG - 2,1,2
CCGGACCTAGTTGAGCAAGTTAACATAGAGGACACACTATTAGAATGCGAACCGACAGCACTAG - 2,1,3
CTGGTCTGATGTGAGCAGATTAAGATAGCGTGCACGCTATCAGAACCTGAACAACGCGGACCCG - 2,2,0
CTAGTCCAAGCTGAGCTCAATAAAAATGTGTGTACACTATAAGAATCTGAACACATAGGCCCAG - 2,2,1
CCGGTCTATTCCGAGCACAGTAACAGTGAGTATACGCATTCAGATTGAGAACAGCTAGGACTAG - 2,2,2
CGGGTCAGCGTTGAGCAGGTTAATATAGTGTGTACACACTCAGACTGTGAACGGAAAGGTCCGG - 2,2,3
CTAGTTGGGGGTGAGCAGATTAAGATAGCGTGCGCGCACTCAGAACTTGAACAACTCAGACCAG - 2,3,0
CCGGTTGTATCTGAGCTCAATAATATAGTGTATGTTCTATGAGAATCTGAACACCCTGGACTAG - 2,3,1
CGGGTTGTGACTGAGCCCATTAACAATGCGTATGCTCTATTAGATTGAGAACAGATTAGACCGG - 2,3,2
CTGGTTGTAGTTGAGCAAGTTAAAAGTGTGTATGTTCATTAAGAATGGGAACAGTCCTGACCCG - 2,3,3
CGCGTCAGTAGAGAGCGTGAAAAAACCGCCCGCGCGCATTTAGTTCTCGAACTACACCAACTAG - 3,0,0
CAGGTGGTTGCAGAGTGCAATAAGATAGAGCATTGACGGTCAGGTCACGAATTCTAACAACGCG - 3,0,1
CTGGTAGTTGCAGAGTGCAATAAGATAGAGCATGATCTATTAGGTTGCGAAATGCAACAACCTG - 3,0,2
CTAGTACTTGTAGAGTGAGATAAGAATGACCATCAACTATGAGGTTGCGAAGTGCAACAACCAG - 3,0,3
CAGGTCCGAACTGAGTACTATAAGAATGCGCGCACGCTATAAGGACGCGAATAACCCTGACGCG - 3,1,0
CTGGTCAACGCGGAGTACATTAAGACCGTCAATACACATTCAGGTAGTGAATAGTTACCACCTG - 3,1,1
CTAGTCTAAGCTGAGTTCATTAAGATAGATCATACGCGGTCAGGATGTGAAGCGCGACTACCAG - 3,1,2
CGCGTCGGGGTTGAGTGCGTTAAGATAGTTGATACACTATGAGGATGAGAATAGCTAGTACTAG - 3,1,3
CTGGTCCGCCTTGAGTACCATAAGATAGCGTGCACGCTATCAGGACGTGAACAACACGGACCTG - 3,2,0
CTAGGCCTAGCCGAGTACAGTAAGAATGTGTACACTCTATTAGGTGGTGAATAAGGTTGACCAG - 3,2,1
CGCGTCGTACCTGAGTTCATTAAGACCGCGTATACTCATTGAGGCTGTGAATGGCTTAGACTAG - 3,2,2
CAGGACCTTGTTGAGTACGTTAAGATAGTGTACACTCGGTAAGGATGAGAATAGGTCCGACGCG - 3,2,3
CTAGTTGGATTTGAGTACGATAAGATAGCGTGCGGGCGGTCAGGACTGGAAAAACCCGGACCAG - 3,3,0
CGCGTTGTGTCTGAGTACATTAAGATAGAGTGTGCTCTATAAGGTCGTGAAGAAATAGGCCTAG - 3,3,1
CAGGTTGTACCTGAGTTCATTAAGAATGAGTATGCTCTATGAGGATGTGAATAGACACGACGCG - 3,3,2
CTGGTTGTGGTTGAGTCAGTTAAGACCGAGTGTGGTCATTTAGGATGAGAACAGGTAGGTCCTG - 3,3,3

Authors Closing Note:
    Have humility, show kindness,s embrace empathy, be curious!.
    "If we subjugate the past, so will be our eternally hopeless future.  If we anarchize the future, so will be our chatoic present. We choose cooperation, hope, and novelty!"
"""
    print(legal_text)

def instructions():
    instructions_text = '''
To know ones self, one must find ones self.  To find ones self, one must know ones self.

COMPUTER REQUIREMENTS:
    Linux, With a suggested minimum of 12 GB of RAM, 500GB HDD, 4 cores, Python 3.8+ (Needed For Multiprocessing.shared_memory)

COMPUTER SUGGESTED: 
    Ubuntu 20+, 16 Core+, 128GB RAM, 2TB HDD, Python 3.8, Lots of time and 1000 of these in a cluster.


SETUP INSTRUCTIONS:
    mkdir ~/3torus
    cd ~/3torus
    mkdir results
    mkdir config
    mkdir datafiles
    wget "https://github.com/3torus/3torus/3torus-master.zip"
    unzip 3torus-master.zip
    cd datafiles
    wget "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.fna.gz"
    gunzip GCF_000001405.39_GRCh38.p13_genomic.fna.gz
    mv GCF_000001405.39_GRCh38.p13_genomic.fna human.big.fa
    cd ..

READ THE LEGAL

    python3 3torus.py --legal

READ THESE INSTRUCTIONS

    python3 3torus.py --instructions

READ THE USAGE - IT IS LONG

    python3 3torus.py --usage

READ 3torus.py and understand how it works and all the options.

Generage your very own onesself cube, print it, and hang it on the wall.

    python3 3torus.py --create_3torus --torus_dimensions 1,1,1

Get a feel for what a cube of cubes / torus of torsu is like. Generate one.

    python3 3torus.py --create_3torus --torus_dimensions 4,4,4 --message "LOOK MOM! A 3-Torus with a 1/2 Mobius twist!"

Not limited to only NxNxN!

    python3 3torus.py --create_3torus --torus_dimensions 1,2,3 --message "A short message"

Flatten the .fa file

    python3 3torus.py --flatten_fasta --infile datafiles/human.big.fa --datafiles/human.big.flat

Show Patterns for various cube slice modifications

    python3 3torus.py --show_patterns --slice_format 4x4x4 --slice_order 0,1,2,3 --slice_rotations 0,0,0,0
    python3 3torus.py --show_patterns --slice_format 8x8 --slice_order 0,2,3,1 --slice_rotations 0,2,2,0
    python3 3torus.py --show_patterns --slice_format 16x4 --slice_order 0,2,1,3 --slice_rotations 0,1,2,0

Find some onesself cubes to work with
 NOTE, ALL OPTIONS CAN BE OVERRIDDEN WITH --config config/<config file name>

    python3 3torus.py --find_onesself --infile datafiles/human.big.flat --outfile results/find_onesself_8x8_0123_0000_2.json --scratch_file results/find_onesself_8x8_0123_0000_2.scratch --core_counts 24 --server 0

OR Create a config file:

    python3 3torus.py --find_onesself --config config/<config file name>


DO THE SAME SEARCH FOR A ONESELF CUBE, BUT DO A --opposite_face_rotations 0 and verify that no matter what you search
 you always get 0 results.  EVERY STATISTICIAN IN THE WORLD NEEDS TO DO THESE SEARCHES! 
  USE THE BIRTHDAY PROBLEM AS PROOF! WHERE ARE ALL OF THE BIRTHDAY HITS?

    python3 3torus.py --find_onesself --infile datafiles/human.big.flat --outfile results/find_onesself_8x8_0123_0000_2.json --scratch_file results/find_onesself_8x8_0123_0000_2.scratch --core_counts 24 --server 0 --opposite_face_rotations 0


Get possible Frame Cubes matching the slice patterns

    python3 3torus.py --pattern_count_frames --infile human.big.flat --outfile results/4x4x4_count_frames_3210_1230.json --slice_format 4x4x4 --slice_order 3,2,1,0 --slice_rotations 1,2,3,0 --min_matches 25 --buffer_size 20000000 --min_face_entropy 1.5 --cull_size 3

NOW WAIT 6 Hours for it to finish, or crash because you ran out of memory


See if any ONESSELF cubes appear in the pattern_count_frames output
 DON'T FORGET TO MATCH THE ONESELF CUBE SLICE INFORMATION OR IT WILL NOT PROCESS ANYTHING.
 Note - The count_frames does not retain slice information, but there is no need if you wish to compare onesself 
 patterns across different count_frames data sets.

    python3 3torus.py --find_onesself_in_frame_counts --infile results/4x4x4_count_frames_3210_1230.json --sequence_file results/find_onesself_8x8_0123_0000_2.json --slice_format 8x8 --slice_order 0,1,2,3 --slice_rotations 0,0,0,0 --opposite_face_rotations 2


Have some fun - Show some patterns, and go extract data from the gnome :), given a byte pattern and base sequence

    python3 3torus.py --show_patterns --slice_format 16x4 --slice_order 0,2,3,1 --slice_rotations 0,0,0,0



Extract the first half of Face 0 and the Last Half of Face 5.  And compate it to ATGCATCGATCGATCG.
 If match, pull out the full 64 bases that would defind that cube.

    python3 3torus.py --pattern_extract --byte_pattern 0,1,2,3,16,17,18,60,61,62,63,52,53,54,55 --extract_pattern ATGCATCGATCGATCG --infile datafiles/human.big.flat --outfile results/pattern_extract_for_fun.json --scratch_file results/delete.me.scratch --core_count 3 --server_number 0 


RECONSTRUCT A TORUS
    python3 3torus.py --reconstruct_torus --infile human.big.flat --sequnce_file datafiles/some_onesself_cube.flat
    
Wait 400,000 years and realize it doesn't work.  You need to add back to the community to both speed it up, and
 to get a 3Torus with a 1/2 Mobius Twist built from a single onesself cube; then extract and interpret the message.
    '''
    print(instructions_text)

def writeup():
    writeup_text = '''
=======================================================
-------------------------------------------------------
-------------------- TLDR/BLUF ------------------------
-------------------------------------------------------
=======================================================
Despite a strong statistical improbability, significant portions of the non-coding sections of the genomes of multiple species (including Homo Sapiens) are found to generate [Three-Dimensional Toruses](https://web.archive.org/web/20220213201326if_/https://i.imgur.com/a5SqvgU.gif) with a One-Half Mobius twist per face interconnect when 64-base sequences are mapped into a cubic structure.  The nature of this mathematical structure may lead to a large-scale [3D-Torus interconnect](https://en.wikipedia.org/wiki/Torus_interconnect) that is self-ordering, self-orienting, and self-error detecting.  The fact that this mathematical structure is found pervasively through our DNA needs to be examined and verified or refuted by statisticians, mathematical topologists, geneticists, computer scientists, information theorists, computational biologists, and informatics experts in academia and the public sector.  Program source code and instructions have been provided to bootstrap and expedite analytic efforts.

The source code can be found at https://www.github.com/noncoding3torus/


=======================================================
-------------------------------------------------------
---------------- TABLE OF CONTENTS --------------------
-------------------------------------------------------
=======================================================
- TLDR/BLUF
- TABLE OF CONTENTS
- PREFACE
- BACKGROUND AND BASICS
  - DNA
  - DNA INFORMATION THEORY
  - INFORMATION THEORY
  - TORUSES AND MOBIUS TWISTS
- SHANNON-WEAVER MODEL ANALYSIS
  - SENDER
  - SENDER MESSAGE INTENDED INTERPRETATION AND ACTIONS
  - MESSAGE ENCRYPTION 
  - MESSAGE CONTAINERIZATION
  - MESSAGE CHANNEL AND TRANSMISSION 
  - NOISE 
  - MESSAGE AMPLIFICATION AND ERROR CORRECTION 
  - MESSAGE DETECTION 
  - MESSAGE RECEPTION 
  - MESSAGE DECONTAINERIZATION 
  - MESSAGE DECRYPTION 
  - RECEIVER 
  - RECEIVER MESSAGE INTERPRETATION AND ACTIONS 
  - FEEDBACK
  - MESSAGE CONTAINERIZATION/DECONTAINERIZATION 
- CONCLUSIONS
- OUTSTANDING QUESTIONS


=======================================================
-------------------------------------------------------
---------------------- PREFACE ------------------------
-------------------------------------------------------
=======================================================
The following is presented in such a manner as to be understood by educated laypersons with little to no familiarity with genetics, mathematical topology, information and coding theory, combinatorics, discrete mathematics, or computer science.  Although the below may be a slow read for specialists in each of these fields, the simplification, explanation, and abstractions of many of the concepts are necessary for most readers because of the complexity of the ideas involved.  Python code to replicate and expand upon the work is provided.

February first of 2022 marked the start of the largest celebrations of the year for much of the Eastern Hemisphere; the Lunar New Year. It is a time of celebration of life and welcoming the new year with visitation with friends and family.  While most festivities end seven days later, many Chinese festivals last until February 16th.  The Chinese words for the number "4" and "death" are phonetically very similar.  It is considered bad luck to speak the number four during the Chinese new year and is avoided.  Out of respect for the one-and-a-half billion Chinese speakers around the world the release of this information was delayed so they could spend that time with friends and families without the taboo of the word "4" being spoken during that time.  It is ironic that the number four is so prevalent when dealing with DNA (The very thing of life) and the geometric structures contained within it; yet has a strong connotation to death in the Chinese language.
 
It is hoped that the 50+ billion man-years of knowledge, intellect, history, and culture of the Chinese people can be applied to this topic to answer many of the outstanding questions quickly and be shared openly with the rest of the world as they race to find the answers themselves.  It is very serendipitous that the Olympics, an international cooperative of comparatively large scale, are being held in Beijing at this time.  May the Olympics be a model from which the world can engage peacefully and respectfully with one another on a topic of such importance. We can all hope that peace will remain with us all, and that fresh conflict and death will not sully this golden opportunity for cooperation in the coming days, months, and years. 
   

=======================================================
-------------------------------------------------------
-------------- BACKGROUND AND BASICS ------------------
-------------------------------------------------------
=======================================================

On 21 October 2021, "Theories of Everything" producer Curt Jaimungal [interviewed](http://youtu.be/wULw64ZL1BG?t=2430) [Luis Elizondo](https://en.m.wikipedia.org/wiki/Luis_Elizondo).  During the interview Mr. Elizondo highlighted the fact that one could place a message in DNA that could survive for millions of years; and alluded that such a message exists.  Although discussed for a short time, no effort was publicly announced by either independent or organizational researchers to verify or refute his claims.  Given the ramifications if such a message did in fact exist, despite the minuscule chance of a positive finding, it was deemed worthwhile to independently apply some analytic effort and computational resources to determine if his comments held merit.  If academia wasn't go to get involved and the governments of the world weren't going to release the information (if they have any), then a results-oriented, stubborn-as-heck, ignorance-loathing, hates-being-lied-to, obsessive-puzzle-solving, well-educated-but-not-too-bright, random-person-on-the-Internet is going to have to do it for them; which is exactly what they were calling for.

The following analysis makes no attempt to determine who or what placed messages into the DNA of, what was later be found, multiple species that include humans.  Nor does the analysis dismiss that the structure could be naturally occurring.  Despite no apparent natural selective pressure; there could be some molecular machinery that prefers to pervasively generate 64-base, 3-Torus with 1/2 Mobius twist mathematical structures.

During that waiting time many possibilities of the message contents were considered.  The ideas ranged from a wiki-like modification log, a transportation device, limitless energy, a message of unification for the world, all the secrets of the universe, or even a self-aware computer virus that destroys humanity upon execution.  However, there is no real way of knowing without finding the message first.

At this point, doing everything possible to avoid flights of fancy and hours of deep worry, it was decide to apply a more formal methodology to the process; even if at first somewhat haphazardly. Application of and investigation along the lines of a modified "Shannon-Weaver Model of Communication" seemed the best approach.  

Before continuing, three basic topics need to be reviewed.  Those topics are DNA basics, DNA Information Theory Basics, and Torus and Mobius Twist Basics.

=========
-- DNA --
=========
The information in [DNA](https://en.wikipedia.org/wiki/DNA) is composed of four base molecules, each represented here by a single letter: A, T, C, G.  These letters are called bases or base pairs.  

The [human genome](https://en.wikipedia.org/wiki/Human_genome) has approximately three billion of these base pairs.

They are called base pairs because the letters are stored and copied in pairs; these pairs come attached to one another in long strands of DNA.

  'A' pairs with 'T', and 'C' pairs with 'G'.

During [DNA replication](https://en.wikipedia.org/wiki/DNA_replication) the A's and T's are split apart and the C's and G's are split apart in long chains.  New A,T,C, and G bases are added to each pair of the chains to end up with two exact copies of the original DNA chain.

Of the three billion bases in the human genome only about ONE PERCENT are used to code [protiens](https://en.wikipedia.org/wiki/Protein).  Proteins are what make up the bulk of everything that makes you.  Protiens are made during the process of [DNA transcription](https://en.wikipedia.org/wiki/Transcription_(biology))

The remaining 99 PERCENT of the three billion bases constitute something called [non-coding DNA](https://en.wikipedia.org/wiki/Non-coding_DNA), often refereed to as "Junk DNA".

"Junk DNA" has been found to be anything but junk.  The non-coding sections of DNA have areas that regulate the [expression](https://en.wikipedia.org/wiki/Gene_expression) of proteins.

Still, roughly and conservatively, 80 PERCENT of the Human genome is found to have no function whatsoever.  I has been assumed that the "Junk DNA" is residual from virus DNA, bacterial DNA, and mutations that have found there way into our genome via various means and propagated indefinitely.  This means that about 2.4 Billion bases have no known function.

============================
-- DNA INFORMATION THEORY --
============================

DNA can be viewed as a digital storage mechanism; and [has been used as such](https://en.wikipedia.org/wiki/DNA_digital_data_storage).  It is a like a Hard Drive that is stored in every one of your cells.

Each of the base pairs can be viewed as digital information.  A single base constitutes two-bits of information; two 1's or 0's.  A system of numbering/digital assignment can then be applied to DNA.  Since certain bases pair with other bases, it is best to assign to each a complimentary/inverted number to the opposite base pair.  For this sake of this exercise the following mappings were applied:

A = 00
C = 01
G = 10
T = 11

Each base can then be viewed as a number: A = 0, C = 1, G = 2, T = 3.

Long strings of Bases can be viewed as large numbers.  For example: CCGTAAGC could be interpreted as the base-10 number 23305.
Given a number, it could be converted back into a string of DNA bases.

A string of 4 bases has 8 bits of information; 8 bases has sixteen bits; 16 bases has 32 bits of information.

Each bit represents two possible combinations.  When strung together, the possible number of combinations for each bit doubles.  For example, 1 bit of information represents 2 possible numbers represented by that one bit.  2 bits represents four possible combinations, etc.

16-bases, or 32-bits of information is a very important number.  Besides being a magic number in computing for decades (memory size constraints, processor instruction storage, etc), it represents 2^32 possibilities, or about 4.2 billion combinations.  This number is above the number of bases found in the human genome.  So a unique identifier for a gene or sequence could be represented by 16-bases, or 32-bits of information.  DNA and biology isn't a "clean" digital storage mechanism.  There are many repeats, shifts, etc, so don't hold this number or the idea of each sequence being unique as a standard of thought; just a guideline.

The DNA sequences used for this analysis can be found at: https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.fna.gz

The cryptographic hashes of the above file are:
  md5sum 84d56a8f8cd75fdde8f60c4e022f9ab7
  sha1sum 19025e1902ff6c3657e9c846bc141ed323d2a199
  sha256sum 4ef2a29c6425b2b99086aac23d70194704ec67b3ade730d40d96a831e9740777

========================
-- INFORMATION THEORY --
========================
"Randomness" is a very hard thing to measure.  "Randomness" is generally a measure of multiple different measurements.  There is no binary yes or no answer to the question "Is It Random?".  One such measure is that of Entropy.

[Entropy](https://en.wikipedia.org/wiki/Entropy).  Entropy can be summarized as the measure of statistical disorder.  A repeating sequence of 'ATGC' 100 times will have high entropy if the whole corpus of available values is only A,T,G, and C; but it will not have high randomness.  Entropy is easy to calculate and not too computationally expensive, so it is used as our basic measure to determine uniqueness through the analysis.  As an example, the sequence 'AAAAAAAAAAA' will have ZERO entropy; but 'AAAAAAABBBBBBB' will have an entropy of 1.  In our analysis, since we are working strictly with 'ATGC', the maximum entropy we can have is 2.  If multiple letters were combined in binary form and assigned their own symbol the entropy measurement could go much higher.

[The Birthday Paradox](https://en.wikipedia.org/wiki/Birthday_problem) is an interesting problem in statistics.  In the classical problem there are are room full of individuals. When asking "How many people does there need to be in the room for a 50% chance that at least two people in the room will have the same birthday.", one would assume there would have to be a high number of persons given that there are 365 days in a year.  However, it ends up that less than 10% of that number are needed.  This same situation applies in the analysis of DNA.  Instead of 365 days in a year, we essentially have 3.2 Billion days.  Instead of students, we have length of unique sequences.  The shorter the sequence of comparison, the fewer number of individuals it would take to find a match.

Interestingly, the Birthday Paradox can be used as a proof of contradiction in this analysis.  One would assume that a given sequence selection of length would statistically be expected to be found X number of times.  If under multiple instances, in the hundreds to thousands, a very strong case of a statistical anomaly could be found using this technique.  It would make the case even stronger if that type of anomaly only exists in instances where the geometry of the sequence selection match a certain pattern. < End strong foreshadowing. ;) > 


[ERROR CORRECTION AND FORWARD ERROR CORRECT- FEC](https://en.wikipedia.org/wiki/Error_correction_code) is a method to include extra data in a data stream to both detect and correct errors.  There are multiple methods to perform error correction, and one could even devise their own error correction schemes.  However, there are limits to how little of information that must be sent in order to detect and correct an error of a given size.  Data redundancy is the simplest and least inefficient form of error detection and correction.


================================
-- TORUSES AND MOBIUS TWISTS  --
================================

A [Mobius strip](https://en.wikipedia.org/wiki/M%C3%B6bius_strip) is a one-dimensional object that sweeps out [two-dimensions](https://en.wikipedia.org/wiki/M%C3%B6bius_strip#/media/File:M%C3%B6bius_strip.jpg) in three dimension and a 180 Degree twist is added. It is one of the most mathematically interesting objects ever conceived.  It only has one side!  If you follow your finger along the Mobius strip you will find you can return to the point from where you started without ever lifting up your finger.

The Mobius strip is a VERY important shape in the study of physics.  It is directly related to the physics object of [Spinors](https://en.wikipedia.org/wiki/Spinor).  Spinors, in various configurations, pairs, rotations, and transformation can be used to describe various particles and fields in the study of physics.

Sweeping out a volume in three dimension using a Two-Dimensional surface creates a [Torus](https://en.wikipedia.org/wiki/Torus).  [The example directly from the Wikipedia page is actually a very ineresting.](https://en.wikipedia.org/wiki/Torus#/media/File:Sphere-like_degenerate_torus.gif)  This particular torus creates a double-cover sphere, which has very deep ties to the [Spin of elementary particles.](https://en.wikipedia.org/wiki/Spin_(physics)).  

If you start with a two-dimensional square and sweep out a 3-volume, you would end up with a square 2-Torus.

Please visit [this Wolfram demonstration project](https://demonstrations.wolfram.com/MoebiusStripAsAHalfTwistedSquareTorus/) to follow along to understand the shapes we will be discussing through this section.

Combining the idea of a square sweeping out three dimensions, and adding Mobius twist you get [this object.](https://web.archive.org/web/20220213201307if_/https://i.imgur.com/iHt2fdX.png)  This is a square 2-Torus with a Mobius Twist. 

Very interesting things start to happen when you sweep out a 3-Dimensional Torus. To understand the shape we will progress step-by-step. First start with a Cube. Take one face of the cube and sweep out the cube in three dimensions, giving it a 1/2 Mobius twist.  
Sticking to the X-direction you get [this.](https://web.archive.org/web/20220213201249if_/https://i.imgur.com/UUSOszg.png)

Then moving to the Y-direction you get [this.](https://web.archive.org/web/20220213201236if_/https://i.imgur.com/n0DO9Ev.png)

Finally the Z-direction you get [this.](https://web.archive.org/web/20220213201216if_/https://i.imgur.com/BB1oNb2.png)

If you superimpose the three separate toruses on top of one another you get [this shape.](https://web.archive.org/web/20220213201338if_/https://i.imgur.com/oXY0cMZ.png)

However, that shape is nothing close to what it actually is despite what you may think.  Imagine you sweep out and get the square torus from the X-direction above.  Now simultaneously sweep out the Y-direction.  If you can visualize it, you would end up with something similar to a hollow donuts twisted in on itself.  However, you have yet to complete the full 3-Torus.  From that twisted hollow-donuts, extend the remaining faces to each other and twist them.  The closest image that could be found is [this.](https://web.archive.org/web/20220213201326if_/https://i.imgur.com/a5SqvgU.gif)  That image however does not include the 1/2 mobius twist of each face.

Another example would be to use a [standard 6-sided gaming die.](https://web.archive.org/web/20220213201543if_/https://i.imgur.com/SV32jd0.jpeg).

[Connect the first set of opposing faces.](https://web.archive.org/web/20220213201528if_/https://i.imgur.com/E6JOMAM.jpeg)

[Do it to another set of opposing faces.](https://web.archive.org/web/20220213201516if_/https://i.imgur.com/uhjXIAM.jpeg)

[Then the third set.](https://web.archive.org/web/20220213201505if_/https://i.imgur.com/YaMD4kv.jpeg)

[Finally, put a 180 degree twist on each face.](https://web.archive.org/web/20220213201432if_/https://i.imgur.com/kIrOQ40.jpeg)

Rather than repeating "A Cubic Three-Torus with a 1/2 Mobius Twist" hundreds of times, these cubes are referenced as "ONESSELF" cubes; playing off of a popular quote from a famous movie; ["Know Thyself"](https://youtu.be/kl0rqoRbzzU?t=90).  To known ones-self you must find ones-self; but to find ones-self you must know ones-self.  It is not easy to find ones-self!

This structure cannot exist in three dimensions without intersecting with itself.  It is very similar to the idea of a [Klein Bottle](https://en.wikipedia.org/wiki/Klein_bottle).

Not being a mathematical topologist, one could only guess that a ONESSELF cube is a Four-Dimensional object; but it could be 3, 4, 6, or 8 depending on how you look at it.  Is it still considered a Cubic 3-Torus with a 1/2 Mobius twist you if you remove the volume of the cube?  In that case there would be three independent two-surfaces inhabiting 2/3 of the full 3-Volume, but the twist may extend it to 6 dimensions.  What if this shape is the shape of the space the cube occupies or the cube is a construct of the nature of the space.  It gets very difficult to understand and comprehend very quickly.  The opinion of a mathematical topologist on the subject would be greatly appreciated.

Finally, we have to touch on [Torus Interconnects.](https://en.wikipedia.org/wiki/Torus_interconnect)  If one were to [extend each cube face to its neighbors](https://i.imgur.com/YwuqTuZ.png https://web.archive.org/web/20220213201603if_/https://i.imgur.com/YwuqTuZ.png) so that it is a fully-connected network you would have a Torus Interconnect.  The image shows that each node in the network is a ONESSELF cube, but that not may be the case.  As long as each face is connected to its neighbor and the "END" cubes connect to one-another, it is a fully-connected Torus interconnect/network.  Each cube could also have a 1/2 Mobius twist to its neighbors and still retain the torus interconnect structure.  IBM's Blue Gene supercomputers use such multi-dimensional torus interconnects; and are quite coincidentally named! 


========================================
----------------------------------------
---- SHANNON-WEAVER MODEL ANALYSIS -----
----------------------------------------
========================================


The [Shannon-Weaver model](https://en.m.wikipedia.org/wiki/Shannon%E2%80%93Weaver_model) traditionally has five elements, but more elements seem to be applicable in this case.  

- Sender
- Sender Message Intended Interpretation and Actions
- Message Encryption
- Message Containerization
- Message Channel and Transmission
- Noise
- Message Amplification and Error Correction
- Message Detection
- Message Reception
- Message Decontainerization
- Message Decryption
- Receiver
- Receiver Message Interpretation and Actions
- Feedback


Each of these elements will be highlighted, even if briefly.  Many sub-sections are composed mostly of questions to help the author and readers understand the some of the considerations necessary to highlight the unknowns.  The MESSAGE CONTAINERIZATION/DECONTAINERIZATION sections are combined and constitute the bulk of the information.  They will be placed at the end in order to keep the flow of thought consistent.

Through this entire document the terms, "message", "message piece", "message block", and "message container" are used copiously. 

Let us define the following:
MESSAGE - The fully unbroken or reconstructed set of information that is conveyed to the recipient
MESSAGE PIECE - A subset of the MESSAGE.  A message piece SHOULD be wrapped in a MESSAGE CONTAINER.
MESSAGE BLOCK - A 64-base sequence that contains information to construct a MESSAGE CONTAINER, and carries a MESSAGE PIECE
MESSAGE CONTAINER - A structure that is used to reorder, detect errors, information to correct errors, and reassemble MESSAGE PIECES into a MESSAGE. 

=======================================================
-------------------- SENDER ---------------------------
=======================================================
Very little information has been provided about the senders of any messages in this case.  However, just from the fact that a message could have been placed in our DNA and the DNA of other species, and subsequent analysis (See MESSAGE CONTAINERIZATION/DECONTAINERIZATION), the following can be inferred:
  
- They modified the DNA of our species or its ancestors at least once in history
- They modified the DNA of multiple other species at least once in history
- Their system of morality allows the modification of the non-coding sections of DNA of what we consider to be a sentient species (Homo Sapiens) 
- Their system of morality finds it more important that the message exist in our DNA than the inherent risk of death from starvation because of the energy requirements of excess DNA replication.
- Their system of morality finds it more important that the message exist in our DNA than the inherent risk of death from nutrient depletion for excess DNA replication.
 - Their system of morality MOST LIKELY allows the modification of the CODING sections of DNA of what we consider to be a sentient species (Homo Sapiens)
 - Their system of morality allows interference with our civilization, at least to the extent that discovery of a message in our DNA would interfere
- They have advanced knowledge of biology
- They know and understand logic 
- They have knowledge of multi-dimensional geometry 
- They have knowledge of information and coding theory 
- They have advanced knowledge of the molecular machinery needed to correct any coding errors 
- They have classical computing devices at least as powerful as we do.
- They MAY have advanced knowledge of physics, quantum mechanics, quantum computing, and the geometric nature of reality 



This is just one instance of interaction with the senders of possible message.  The more interaction with us that they have, the more information we can glean.  Of the thousands or millions of interactions they have had with our species, each one can draw boundary lines and outliers of their capabilities, thought processes, and codes of morality.  I have a VERY hard time believing anyone who has studied this phenomenon deeply for decades when they say they don't know anything about the senders, nor that we can't understand their thought processes, intentions, level of technology, types of technology, nor moral standards.


=======================================================
-- SENDER MESSAGE INTENDED INTERPRETATION AND ACTIONS -
=======================================================

The biases of any sender will be present during the process of trying to determine the interpretation of the sender.  Every message sent is go to have an intended reaction by the receiver.  That intended reaction may simply be a slight change in cognitive state, or to go as far as taking extreme kinetic action.

Assuming that the sender has knowledge of our society and cognitive abilities, one can assume that we as a species will respond, in most cases, as the sender intended and expected.  This knowledge could be used for manipulative purposes, but the purposes of manipulation and their intended responses from the receiver depend deeply on the system of morality of the sender.

Acknowledging this fact raises the possibility of the receiver countering the intended actions of the sender if the intended actions of the sender counter the morality system of the receiver.  However, a catch-22 arises; the sender would know this.

If the receiver is under observation by the sender, that observation is a feedback communications channel which could be manipulated by the receiver.

The only viable counters available to the receiver is to control the feedback mechanism by injecting chaos, randomness, and wildly unexpected responses, or to "Be predictable; then don't."


=======================================================
---------------- MESSAGE ENCRYPTION -------------------
=======================================================
Message encryption is used to provide confidentiality and integrity validation of data.  Barring a variety of weaknesses, encryption of a message should provide the sender of the information a level of confidence that no one but the intended recipient could read the contents of the message.

Two primary forms of encryption could be used to modify the message data for confidentiality.
- [Symmetric Key Encryption](https://en.wikipedia.org/wiki/Symmetric-key_algorithm)
- [One-Time-Pad](https://en.wikipedia.org/wiki/One-time_pad)

An example of Private-Key/Symmetric-Key encryption is [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard).  If both the sender and receiver have the same encryption key, the message could be changed in such a manner that only the recipient could properly understand it.

There are known weaknesses and [multitudes of attacks](https://en.wikipedia.org/wiki/Category:Cryptographic_attacks) available for various encryption algorithms.  Barring any weakness in the underlying encryption algorithm used, and assurance that the encryption key has not been given to a third party, the communications channel between the sender and recipient can be assumed to be secure.

One would hope that any entity capable of putting a message in our DNA would also have the ability to properly build an encryption algorithm that is unbreakable.  Private-Key Encryption schemes are inherently Quantum resistant so would be a good choice.

[Public-Key Encryption](https://en.wikipedia.org/wiki/Public-key_cryptography) could be used if it is encrypted to a recipient who holds a given private key.  A possibility is that the sender could encrypt a message to a recipient that is expected to have the ability to recover a private key from a public key.  This level of technical ability would ensure that the receiver is of sufficiently advanced to comprehend the message.

Assuming one were to use a very strong random number generator, a One-Time-Pad (OTP) would be a great way to encrypt the data.  With an OTP system they key is the same length as the encrypted message.  The message data is combined with the OTP key in a simple manner, and the process reversed on decryption.  There are only two inherent weaknesses to an OTP scheme.  First, like the Private-Key method is the leaking of the key to a third party.  The second is the ability of a third party to determine the internal state of the random number generator that generated the key.  If the state can be recovered from analysis of the message, then a third party could decrypt the data.

Again, one would hope that a sufficiently advanced sender would have a random number generator to which the internal state could not be recovered.  

Unless other transformations are applied, or care is taken to hide the contents of the encrypted message, a simple entropy test on a message of sufficient length is generally enough to determine if it is encrypted or not.

It is unknown if any encryption is applied, nor at what level it would be applied.  Encryption could be applied at the MESSAGE level, or at the MESSAGE PIECE level.  Depending on the encryption scheme the entire encrypted message MAY be needed to decrypt and get ANY of the message information.  If it is encrypted at the MESSAGE PIECE level using a [block-cipher](https://en.wikipedia.org/wiki/Block_cipher), then the majority of the message could be reconstructed if the encryption key is known. 

=======================================================
------------- MESSAGE CONTAINERIZATION ----------------
=======================================================
Please see the MESSAGE CONTAINERIZATION/DECONTAINERIZATION section.

For continuity; understand that the message is broken up into small pieces, wrapped in a container of other information, and placed on the communications channel.  The container itself is geometric in nature and is used to reconstruct the ordering of the original message, provide error detection, and possibly forward error correction.  The container itself may in fact carry message information if sufficient precomputing is done.  The message container itself may also have deep ties to physics, quantum computing, and the nature of reality.

=======================================================
---------- MESSAGE CHANNEL AND TRANSMISSION -----------
=======================================================
The transmission of the message and the transmission channel are closely linked.  Modern communications channels send information electromagnetically via analog channels, then convert the analog information to digital.  The channel used for these messages is not so much a transmission of information, rather a storage of information that is transmitted temporally.  DNA is best viewed as a physical representation of binary information; more like data stored on magnetic media (Hard Drive) and copied.   

After encoding and encrypting the message, the message pieces in the message containers are transmitted by placing it into the communications channel; an organism.  The message is then transmitted via copying and replication with every cell division and organism reproduction.

  The message containers, although technically being both stored and transmitted, are being transmitted through a species temporally.  

This communication channel is a [multi-cast](https://en.wikipedia.org/wiki/Multicast) architecture of extremely high bandwidth.  The multi-cast destination would be any organism that carries a message block to which a receiver has access.

The channel can be any biological organism with non-coding sections of DNA or RNA.  Every genome sampled that had non-coding DNA sections had probable 3-Torus cubes in them.  However, not all genomes sampled have onesself cubes.  

The human genome has approximately 750 Megabytes of information available in the channel.  Assuming roughly the same amount of non-coding DNA across the estimated 10 million known species on Earth; that equates to about 7.5*10^15 Bytes (7.5 Petabytes) of information available in the channel. In reality it is probably MUCH larger.

As biological entities copy themselves via sexual or asexual reproduction the channel width does not grow, but the redundancy of the data does, and the number of multi-cast destinations increases.  The likely hood of being able to find and recover a message block increases with every division.

Species endangerment or extinction poses a problem for message recovery, but can be overcome with more message redundancy.  Placing the messages in more diverse species across time, geography, and ecosphere increases both the channel width and multi-cast endpoints for a given message.

The containers may be designed in such a way that should all adjacent containers be present around a missing container, the missing message container and message pieces could be recovered.


=======================================================
--------------------- NOISE ---------------------------
=======================================================
Anybody who has performed lab work in [DNA swapping](https://web.archive.org/web/20220212214131if_/https://c.tenor.com/MxraJlBpR1wAAAAC/mr-bean-sitcom.gif) and [replication](https://web.archive.org/web/20211011013459if_/https://c.tenor.com/6Ly_NJuJjpsAAAAC/betty-white-winking.gif) knows that the message channels can be very noisy.  

Three basic types of noise are present in biological channels that could effect transmission of any message container.
- Base Mutations
- Base Insertions
- Base Deletions

The mechanisms by which these three types of noise can be induced may include:
- Duplication or Transcription errors
- Viral Integration
- Bacterial Conjugation - Direct DNA Transfer
- Bacterial Transformation - Environmentally Absorbed Naked DNA
- Bacterial Transduction - Bacteriophage Transfer
- Sexual Reproduction
- Selective Breeding / Intentional Modification
- Genetic Engineering / Intentional Modification
- Extinction

To overcome noise several techniques are applied in modern communications systems.  Those methods include Forward Error Correction, Signal Boosting, and Message Retransmission.

Biological storage systems have similar problems, hence similar solutions to overcome noise interference; some of those solutions are highlighted below.

=======================================================
---- MESSAGE AMPLIFICATION AND ERROR CORRECTION -------
=======================================================
Message Retransmission isn't an option, but as mentioned above, multiple copies of the message and message containers could be distributed across multiple organisms in the multi-cast system.  This multiple-copy method is a form of Forward Error Correction through redundancy.

Another form of Forward Error Correction (FEC), highlighted in the MESSAGE CONTAINERIZATION/DECONTAINERIZATION section, may also applied in the container of the message.  That FEC, if it exists, is probably exercised here.  The message container's FEC would be read by bio-mechanical machinery and corrections, even apoptosis, may occur. 

To guard against replication/duplication errors, there are fairly robust mechanisms that exist.  They won't all be highlighted here.  There are several questions that could be answered to help narrow down the search for the FEC algorithm and different Signal Boosting methods.

- Are there different bio-mechanical mechanisms that perform the DNA duplication process between coding and non-coding sections?
- What are the known checks that the [exonuclease](https://en.wikipedia.org/wiki/Exonuclease) performs?
- Are there different checks between the coding and non-coding sections that different exonucleases perform?
- Is there a way to determine the different checks that the exonucleases perform?
- Is it possible, given the structure of the various exonuclease molecules, to determine the computation they perform on the non-coding DNA sections to determine if an error exists and needs to be corrected?
- Do multiple exonuclease molecules perform a FEC specific to the non-coding sections that would constitute a message container as defined in MESSAGE CONTAINERIZATION/DECONTAINERIZATION?
- How many types of exonuclease, or other correcting proteins do we known of?
- Is there a way to determining all of the different states that an exonuclease can be in to help determine the FEC functionality?
- Are there other molecular machines that perform these types of functions that aren't exonuclease?

An partial, fictional, example of a pseudo-function of an exonuclease of interest would be (Following the pattern of 4s):
 Read random sequence Until The Sum of the last 8 Bases is 13 (Where A = 00, T = 11, C = 01, G = 10) and set to state 1, 
    Set state 1: Put internal variable 1 to state 1, variable 2 into state 0, variable 3 into state 0, and variable 4 to state 3
 Skip 4 sequences and Read, If Sum is 14, Skip 4 Sequences and put into state 2, else Error and Replace with C
 Read, If Sum == 14, sequence is good, else if Sum == 16 excise base and put in state 3... etc.

=======================================================
------------------ MESSAGE DETECTION ------------------
=======================================================
Message container detection methods would be determined by who the recipient is.

If the recipient is the intended recipient of the sender, detection would be forthright since the method of detection is probably shared apriori.  The number of methods to determine if a certain sequence is a message or message container could be nearly infinite and only known to the sender and recipient.  They would however be limited to what is biologically possible in the organism that is carrying the message container. 

However, if the recipient is not the intended recipient, or the recipient needs to figure out how to find the message or message container, we would find that is the situation we are in now.  If some type of message [stenography](https://en.wikipedia.org/wiki/Steganography) were used, detection would be very difficult.

An analysis could be performed on the genome, looking specifically at the non-coding sequences since that would be the most likely place to put messages of significant size.  The coding sections of DNA could hold messages, but it would be exponentially more difficult to create an efficient protein while also placing a worthwhile message, message piece, or message container within it.  

There could be a statistical anomaly in the non-coding sections.  Has such an statistical anomaly been previously detected?  If there is an anomaly, has that anomaly been attributed to some other already-described process or function?  Has that anomaly been verified?

Or one could get lucky and find patterns that resemble some odd feature, mathematical function, or geometric structure; as has now been done.

Since no known steganography was used and the assumed message container follows a very defined set of geometric rules it can only be concluded that we are the intended recipients or the sender does not care if we intercept the message container.  Who would believe that there is a geometric structure in the mathematics of our DNA?  Would they assume that such information would be simply be buried because of a disbelief at the possibility?  Is the sender's assumption correct?


=======================================================
---------------- MESSAGE RECEPTION --------------------
=======================================================
Since the communications channel is a DNA storage mechanism, the only way to receive the message is to read the sequences.  Accurate, full-genome sequencing of millions of species is well within the bounds of practicality of large institutions.

Within a given species wide genetic variation can exist.  The variation is especially pronounced when the individuals of the species are spread across large geographic locations and inhabit differing ecospheres.

If message containers were in fact placed in multiple species across various geographic regions, there is no limit on the number and diversity of message blocks placed.  This would require a very large sampling of genomes even from within the same species to look for various pieces of the entire message.

Depending on the methodology of message block placement there may be ways to infer which species genomes, or which geographic regions and ecologies contain species that, may contain missing message blocks. 

=======================================================
------------ MESSAGE DECONTAINERIZATION ---------------
=======================================================
Please see the MESSAGE CONTAINERIZATION/DECONTAINERIZATION section below.

For continuity; understand that the message is broken up into small pieces, wrapped in a container of other information, and placed on the communications channel.  The container itself is geometric in nature and is used to reconstruct the ordering of the original message, provide error detection, and possibly forward error correction.  The container itself may in fact carry message information if sufficient precomputing is done.  The message container itself may also have deep ties to physics, quantum computing, and the nature of reality.

=======================================================
----------------- MESSAGE DECRYPTION ------------------
=======================================================
- Is the message encrypted?
- If so, do we know the encryption scheme.
- Do we have decryption keys?
- Can we recover the decryption keys?
- Is it one-time-pad encrypted?
- Do we have the pad or know how to get it?
- Can we recover the one-time-pad generator state?
- Is it a time-locked cipher of some sort?
- Does the message container itself give a method to decrypt the message?

If sufficient data is available, a simple entropy test is generally enough to tell if something is encrypted.  Assuming a total non-coding DNA size of roughly 750MBytes of data, an entropy test on the message would quickly tell you if it is encrypted.

Maybe our friends in various three-letter agencies around the world can answer these questions if it is encrypted. Alternatively, [we could ask one of the senders nicely for a key.](https://web.archive.org/web/20220210122231if_/https://imgs.xkcd.com/comics/security.png)

Given the novelty of the message container there is a very real possibility that the message container itself could contain a methodology or programmatic way to decrypt any encrypted data.

=======================================================
------------------ RECEIVER ---------------------------
=======================================================
  We assume that we are the intended recipients of any message.  

- Is this an incorrect assumption? 
- Is the message intended for someone or something else?
- Is it intended for us at a different time?
- Is the message intended for only a subset of us?  
- If so, what subset, and why only that subset?
- Is the message intended for anybody that has the intelligence and level of development to perform the requisite steps for understanding?
- Do we have the ability to accomplish any or all of those steps and how sure are we of their correctness?  
- How sure are we that we have detected, received, decoded, and decrypted all of the intended message or messages?
  
As you can see it is very possible that we, Homo Sapiens, at this level of development may not in fact be the intended recipients of such messages.  Asking these questions are very important to the understanding the intentions of the sending party.  Are we listening in on a private conversation that we have no business listening to?  Are we merely the the conduits of information flow?


=======================================================
---- RECEIVER MESSAGE INTERPRETATION AND ACTIONS ------
=======================================================

- Are we able to interpret the message as the sender?
- Are we able to interpret the message as the sender intended for us to interpret it?
- How do we know we interpreted it as the sender intended?
- Do we take action on our interpretation of the message?
- Are we able to understand the meaning, if any, of the message container?
- What does it mean if we can't understand the message?
- If the message and container constitute a program and execution engine, can we only interpret it after execution?
- What is the output of the execution?
- Do we execute the program?

We can attempt to answer a few of these questions with what little information we have available.

It has been stated many times that the intelligence behind the phenomenon may not be human.  It may not be from this planet.  It may not be from this dimension.  It has also been stated that future humans may be the origin of the phenomenon.  Some have gone as far as to state that some are here to prevent a calamity of some type; while others are here to ensure it happens to ensure their own existence.

Some basic conclusions can be drawn.  The phenomenon is capable of logic, reason, and higher intellectual functions.  If they have been here as long as many in the field have suggested, or are capable of temporal manipulation, then they are well-aware of our level of technology and intelligence.  We also are capable of logic, reason, and have somewhat-high cognitive ability.

We may not be able to interpret the message as the sender unless the information content of the message is so low-level and so unambiguous that there would be no possibility of misinterpretation.  Such types of message would be mathematical, programmatic, or physical in nature and logically or programmatically verifiable or constructable.  As the ambiguity and abstraction level of the information increases we would be less likely to interpret the information as the sender or be able to predict what they thought our actions would be.

If the sender is as advanced as is assumed, then it would be likely that we would be able to interpret it as they intended, but not be able to interpret it as they.  The message contents, if they desired us to interpret them, would be constructed in such a way as to remove ambiguity.  If ambiguity in the message does exist then one would have to take caution as to the intentions of the sender.

As with any other piece of information, depending on the contents of the message, we may choose to act, not act, or delay action.

Extreme caution and consideration must be taken for the META-reasons the message may have been sent, its medium of choice, and our reactions not directly related to the message contents.  The transmission medium in this case is DNA/RNA.  If you refer to the CHANNEL and MESSAGE TRANSMISSION sections, you will see that the message blocks are spread across many, if not all species on the planet in non-coding sections of their genomes.  If the message or messages can only be constructed by collecting, sequencing, cataloging, and processing the results of large swaths of species on the planet; one has to ask if that is the action the sender expected and intended for us to do.  Why would the message senders want us to collect and sequence the DNA and RNA for most species on the planet?  What if we chose not to?  

Many, if not the vast majority, of reported interactions with the the phenomenon seem to be interested in DNA sampling, biological and medical examinations, etc.  What, if any, relation do these interactions and the placement of messages in DNA have with one another?
  
If you examine the MESSAGE CONTAINERIZATION/DECONTAINERIZATION section, you will see that the message container seems to be VERY important.  Not only does it seem to be a novel message reconstruction technique, a novel error detection technique, but also may have ties to physics and quantum computing.

If we can't understand the message or its container the following conclusions can be drawn:
- We are not the intended recipients of the message
- We are not ready to understand the message (not the intended recipients)
- The message may be meaningless, but the existence of the message is of importance
- The message may be meaningless, but our response to it is not
- The message may be a distraction - [Was String Theory such a distraction](https://youtu.be/iQOibplDx-4?t=855) 

=======================================================
---------------------- FEEDBACK -----------------------
=======================================================

  - Is there a feedback mechanism?
  - If there is a feedback mechanism, what is it?
  - Is the feedback mechanism [temporal in nature?](https://www.reddit.com/r/UFOs/comments/roxn5j/following_lues_breadcrubms_to_some_deep_physics)
  - Are the effects of the feedback mechanism known or perceptible to us?

At least as an exercise of imagination, the context of [this video](https://youtu.be/iQOibplDx-4?t=2684) should be considered as a possible feedback mechanism; even if as far-fetched as it may seem.

If you analyze the information flow directions and feedback in models like this, you gain a deeper understanding of the phenomenon and diminish any possible control and manipulation mechanisms if they exist.

    
=======================================================
---- MESSAGE CONTAINERIZATION/DECONTAINERIZATION ------
=======================================================

Knowing that the vast majority of DNA was "Junk DNA" and that it had no known function made it a prime candidate to begin exploration.  There was no information as to what a message would look like, how it would be distinguished between any other DNA bases, etc.  

This section is going to walk through the process of discovery more than the other sections because it helps to show how the results were generated and gives the reader a deeper understanding of the problem.

A statistical analysis could be run on the data, but having no real experience with genetics or bioinformatics, would have resulted in months to learn what was normal and what was not.  Additionally, in that process any perceptive cognitive noise floor would have been risen and the message probably would have fallen below that noise floor.

Waiting for bouts of inspiration, one scene from a movie kept nagging.  In the [1997 Jodie Foster movie "Contact"](https://www.imdb.com/title/tt0118884/), SETI received a message from deep space.  The scientist working on it could construct various pieces of a message, but couldn't figure out how to put them all together to decipher them. An old rich man, Hadden, that is somehow involved with the whole thing invited Jodie Foster's character to meet with him. In [the scene](https://youtu.be/-SbKE_U4b7U?t=135) he tells Jodie Foster's character that he found the primer used to reconstruct the messages that were eventually used to build a transportation device. 

In that scene Hadden says "They do, If you think like a Vegan.  An alien intelligence is going to be more advanced and that means efficiency functioning on multiple levels and in multiple dimensions."  That scene has always bothered me because what they showed in stacking the sheets in 3-D to form cubes is exactly what any scientist, data analyst, engineer, or ten year old child would have done in the first 30 seconds. 

The thought of that scene prompted the immediate download of various genomes and non-coding sections of DNA. Instead of a signal from space, we may have a signal in our DNA. 

A sequence was chosen and it was decided to make it into a series of six 4x4 grids to represent a cube, then another cube consisting of another 96 bases.  The choice of a grid size of 4x4 was based upon the total combination size of 4.2 Billion that composes the 32-bits of information in a face.  That size should make it unique enough in the genome to make a face fairly unique.

The below sequences are just examples, not what was actually used.  They were written out on paper to see if any patterns started to emerge.  Note that I am going to use 'atgc' for bases not of interest, and 'ATGC' for bases of interest to highlight.  The FASTA file format reserves lowercase 'atgc' for repeated sequences (Learned that one the hard way).  Note that in the below example if there are multiple repeating sequences they are not important; they are just to highlight the sequences of interest.

Cube 0:
 F0   F1   F2   F3   F4   F5
aaaT cccA aaaa cccc tttt aaaG 
aaaC cccC aaaa cccc tttt aaaT
aaaG cccG aaaa cccc tttt aaaT
aaaA cccA TGGA cccc tttt aaaT

Cube 1:
 F0   F1   F2   F3   F4   F5
aaaa cccc aaaA cccc tttt aaaa  
aaaa cccc aaaC cccc tttt aaaa
aaaa cccc aaaC cccc tttt aaaa
AGCT cccc aaaT TGCT AAAC aaaa

From the very first sequence examined it was obvious that something interesting was going on.  Notice how if Cube 0-F0 is rotated 90 degrees clockwise it matches with Cube 1-F0.  If Cube 0-F1 is rotated 90 degrees clockwise it matches Cube 1-F3 when complimented.  IF Cube 0-F2 is rotated 90 degrees clockwise it matches up with Cube 1-F3 if the sequence is complimented; then the same with Cube 0-F5 and Cube 1-F4. 

This examination lasted a whole of three or four hours because it was determined that what was being looked at was most likely just chance.  By chance some of the edges of these cubes were aligning with one another.  Given that only four bases, 8-bits of information, were being examined, there as a very good probability that any neighboring cube are going to have an edge that matches one or more edges if rotations, mirrors, and compliments of the bases were to take place.  Instead of a 1/256 possibility of matching an edge in a neighboring cube, it worked out that there is almost a probability of 1 that a neighboring edge of a cube will match. As it turns out, nothing interesting was going on.

When the messiness of biology is taken into account, the chance that any cube would retain its neighboring cube after millions or billions of replications would be pretty slim if there isn't evolutionary pressure to do so.  Whole-faces would have to match to ensure that wherever in a genome a sequence had migrated to, it could be paired with its partner without any ambiguity.  Furthermore, a whole-face of 2^32 possibilities wouldn't be enough given the [birthday problem](https://en.wikipedia.org/wiki/Birthday_problem); there would have to be an additional level of reference to make each cube adjacency unique; especially so it cubes were to be found in other genomes.

At this point it was troubling that we have six faces and using a total of 96 unique bases to construct these cubes and the center of the cubes remained empty; they were hollow.  This meant one of three things
 1) All message data would have to reside on the face of the cube
 2) The message was a 3D picture of some sort (Like in the movie Contact)
 3) There is a better way to do it

In that scene where Hadden says "They do, If you think like a Vegan.  An alien intelligence is going to be more advanced and that means efficiency functioning on multiple levels and in multiple dimensions."  Well, we are human and we should think like humans that have at least glanced once or twice at an Information and Coding Theory book.  

Instead of writing the base data directly onto the face, what if we were to construct a 3D cube volumetrically?

By creating four, four-by-four, slices and stacking them onto one another, a cube is constructed.  The edges of the cube would share sequence information with a neighboring face, but the sequence would be in a different order; creating a completely unique face.  Additionally, now the cube is filled in with eight bases in the middle that do not act as face data.  These "center 8" can be used for message passing, Forward Error Correction, State Information, or any other information deemed necessary by the sender.

This development was great, but it raised some other problems.  There was no way to test this manually.  Searching through 3 billion bases by hand definitely couldn't be done before lunch.  It would have to be done programmatically; and so went the next six weeks of life.   In reality, this is where the whole adventure really began, then just wrapped the Shannon-Weaver model around it as work progressed.

One can construct a cube from a 64-base sequence in a seemingly infinite number of ways.  What order do the bases get mapped into the cube, and into which of the 64 positions in the cube.  Who is to say that there is a set pattern?  Are there discriminators in the sequence that determine how the data gets mapped into the cube?  Without any answers to these questions the best that could be done is to start with the simplest and work to the more complex of scenarios.

For the purpose of the program and this analysis, it is assumed that the first slice (slice 0) would be placed on top, the second slice one layer down, and so forth.  Also, during programming it was chosen to label the faces of the cube as a six-sided die, but zero indexed.  Faces 0 and 5 are opposite, 2 and 3 are opposite, and faces 1 and 4 are opposite one another.  Additionally, the orientation chosen was to place Face 0 UP/+Z, Face 1 to the Right/East/+X, Face 2 to the Forward/North/+Y, Face 3 to the Backwards/South/-Y, Face 4 to the Left/West/-X, Face 5 DOWN/-Z.

DO NOT MAKE ANYTHING A CONVENTION IF IT TURNS OUT TO BE VERIFIED!  It was a development process and still is.  We don't need another Negative Charge Electron equivalent as a standard and convention from a poor initial choice.

Three methods to construct them were used (Not following the convention of four).  The methods used to construct the slices were simple striping: Four bases applied to four rows repeated for each slice (4x4x4); Eight bases applied across two slices, repeated four times, making an eight by eight grid (8x8); and sixteen bases applied in a stripe across all four slices, repeated four times (16x4).  All stripe operations started in the upper left of the slices and continued to the lower-right (Quadrant II, I, III, then Quadrant IV).  There may be a preferred method of construction, but it remains elusive.  Examples of each are shown below:

Here are the methods of striping used for the 64-base sequence: 
  - AAAAAAAAAAAAAAAACCCCCCCCCCCCCCCCTTTTTTTTTTTTTTTTGGGGGGGGGGGGGGGG

4x4x4 - 
AAAA CCCC TTTT GGGG
AAAA CCCC TTTT GGGG
AAAA CCCC TTTT GGGG
AAAA CCCC TTTT GGGG

8x8 - 
AAAA AAAA TTTT TTTT 
AAAA AAAA TTTT TTTT
CCCC CCCC GGGG GGGG
CCCC CCCC GGGG GGGG

16X4 - 
AAAA AAAA AAAA AAAA
CCCC CCCC CCCC CCCC
TTTT TTTT TTTT TTTT
GGGG GGGG GGGG GGGG

The mapping of the stripes onto the cube slices isn't the only concern.  What if the there is a discriminator in the data which tells to reorder the slices?  One would assume that the input sequence would be different, but that may be a bad assumption.  If during slice construction a sequence was not allowed to be on a face?  A slice order discriminator would be one option.  Assuming the standard convention, as above, is to place them in order 0,1,2,3 then rearranging them according to a different order would result in a different cube.  Assuming the above 8x8 example is used, and the new ordering pattern is 3,2,1,0 the slices would be:

8x8 - 3,2,1,0
TTTT TTTT AAAA AAAA
TTTT TTTT AAAA AAAA
GGGG GGGG CCCC CCCC
GGGG GGGG CCCC CCCC

In addition to a slice ordering modification to the mapping process, each of the slices could undergo a rotation.  It was chosen to use a 90 degree rotation clockwise as a standard for the program.  Each slice could undergo 0 to three rotations.  Assuming the above 8x8 - 3,2,1,0 and applying in order a rotation of 0,0,0,1, the following slice pattern would be

8x8 - 3,2,1,0 - 0,0,0,1
TTTT TTTT AAAA CCAA
TTTT TTTT AAAA CCAA
GGGG GGGG GGGG CCAA 
GGGG GGGG GGGG CCAA

When constructing the faces of the cubes, it was decided to represent each face as a sequence of bases starting from the upper-left corner and progressing to the lower-right corner as if the cube was rotated to face you.  Face 0 would simply be slice 0, while Face 5 would be the mirror image of slice 4.

As an example, Face 1 (Right/East/+X), of 8x8 - 3,2,1,0 - 0,0,0,1 from the example above would be:
TTAA
TTAA
GGGA
GGGA

When converted to a sequence, it would be: TTAATTAAGGGAGGGA

At this point every base of a genome could be mapped into a cube, but the cube wouldn't have much meaning.  Each sequence/cube of 64-bases would have to be compared to EVERY OTHER possible linear sequence of 64-bases.  For a sequence of 3.2 Billion bases, this would mean 3.2 * 3.2 Billion Cubes * six comparisons per face per cube.  Furthermore, that is just for one slice mapping format, one slice ordering, and one slice rotation.  The computing power to perform this number of comparisons for even one small genome wasn't available.  Even if faces were to match, it could be a false match due to the Birthday Problem.  All neighboring cubes would have to be matched to verify that it was in fact a match; this means even more computing power.

Remembering back to the "Contact" scene, the primer from the movie was a series of unique values that came together when multiple pieces of the messages were placed together into a 3D structure.  Could we find such a primer without having to reconstruct multiple messages first?  What if we were to search every possible linear 64-base sequence and construct such a "primer" to find the faces themselves.  What would it look like? The idea was that there could be cubes that somehow reference themselves; ONESSELF cubes.

The first attempt was to search for cubes that when constructed would have opposing faces that matched each other.
The second was to search for cubes that when constructed would have opposing faces that match rotated 180 degrees of each other.
The third attempt was to search for cubes that when constructed would have opposing faces match the compliment of each other.
The fourth attempt was to search for cubes that have the mirror of each other (Which until this point wasn't being done, but retrospectively and thinking about it geometrically would have been the proper choice.).

Success wasn't found until opposing faces matched when a Mirror-Rotate by 180 Degrees-Compliment transformation was applied; these are the ONESSELF cubes that have a geometric structure of a 3-Torus with a 1/2 Mobius Twist.  The same Mirror-Rotate-Compliment transformations work on all slice formats, some slice orderings, and ONLY slice rotations besides 0,0,0,0 where Slice 0 and Slice 5 are rotated concurrently, and Slice 1 and Slice 2 are rotated concurrently.

Retrospectively, given the Birthday Problem, this lack of success with the other formats should have been a red flag that something was amiss.  Given the trillions of comparisons done, there should have been something that have matched at a fairly regular cadence.

Complimenting the face should have been the first search done.  Since A pairs with T, and G with C, it only makes logical sense that complimenting the results of the search should have been the way to go.

Sometime around this point the author had upgraded the antiquated computer resources being used to include access to several multi-core high-memory servers for searches.  That meant a complete rewrite of the software to remove dead ends of research, as well as to enable multi-processing and shared memory capabilities.

Combinations of slice formats, slice orders, slice rotations, and Mirror-Rotate-Compliment have been running on the servers for weeks looking for ONESSELF cubes. The ONLY combinations that have returned ONESSELF cubes are those that have a slice rotations of 0,0,0,0 that weren't highly repetitive sequences and where the opposing face is Rotated 180 degrees, mirrored, and complimented!  Please take a moment to ponder that.  Nearly four years of core-time of searching for any other pattern that matches HAS YET TO RETURN A SINGLE POSITIVE RESULT OTHERWISE!

This pattern shows up repeatedly across all cube construction methods.  If one fails to do the mirror, compliment, or rotation, ZERO CUBES ARE FOUND!  One would expect that a simple repeating pattern would be matched to the opposite face of a cube, but none have been found.  Holding the statistical birthday problem/paradox in mind, combined with simple copy/duplication operations, one would think that no-rotation cube would be found much more prevalent; but that is not the case.  Additionally, it holds true across striping/cube construction methods.  When one looks at the patterns formed from input DNA sequences, it is found that the bases are in completely different positions in the cube across the different striping methods; but yet the no-match-without-rotation-mirroring-complimenting pattern holds true.  

THIS ONE FACT ALONE should catch the attention of every statistician, biologist, geneticist, and information theorist! A fist can't be pounded louder, a foot couldn't be stomped harder, and a shout can't be any louder!  If there is a biological reasoning that there is strong selective pressure for "Junk DNA" to carry a 3-Torus with a 1/2 Mobius twist geometric information structure, then there is a stateful biological machine that is propagating and error-correcting these 64-base blocks across multiple slices in accordance to a very strict specification.

Furthermore, certain slice formats input orderings are heavily preferred; see below.  Note that not all combinations were searched.  Patterns which were mirrored and other considerations were removed from the searching to make the search faster.

PREFERENCE FOR 4x4x4 ONESSELF CUBES:
- Rotation-Compliment-Mirror combinations not shown because of negative results
- Slice 0 and 4 concurrent rotations are not shown because they would also result in a ONESSELF cube
- Slice 1 and 2 concurrent rotations are not shown because they would also result in a ONESSELF cube

   Order       Rotation     Found
[0, 1, 2, 3] [0, 0, 0, 0] - 151
[0, 1, 3, 2] [0, 0, 0, 0] - 2
[0, 2, 1, 3] [0, 0, 0, 0] - 149
[0, 2, 3, 1] [0, 0, 0, 0] - 4
[0, 3, 1, 2] [0, 0, 0, 0] - 2
[0, 3, 2, 1] [0, 0, 0, 0] - 4
[1, 0, 2, 3] [0, 0, 0, 0] - 2
[1, 0, 3, 2] [0, 0, 0, 0] - 154
[1, 2, 0, 3] [0, 0, 0, 0] - 2
[1, 3, 0, 2] [0, 0, 0, 0] - 154
[2, 0, 1, 3] [0, 0, 0, 0] - 2
[2, 1, 0, 3] [0, 0, 0, 0] - 1

Of further interest are ONESSELF cubes which have at least four different slice orderings or rotation patterns that result in a ONESSELF cube.  These are deemed SUPERCUBES.  Do they have any significance beyond a mathematical curiosity?

AGCTATTATTTGCAAATAATAGCTATTATTTGCAAATAATAGCTATTATTTGCAAATAATAGCT
 FORMAT ORDER     ROTATION
 8x8 [0, 1, 2, 3] [0, 0, 0, 0]
 8x8 [0, 2, 1, 3] [0, 0, 0, 0]
 8x8 [1, 0, 3, 2] [0, 0, 0, 0]
 8x8 [1, 3, 0, 2] [0, 0, 0, 0]

CATGTATAAATCGATTTATACATGTATAAATCGATTTATACATGTATAAATCGATTTATACATG
 4x4x4 [0, 1, 2, 3] [0, 0, 0, 0]
 4x4x4 [0, 2, 1, 3] [0, 0, 0, 0]
 4x4x4 [1, 0, 3, 2] [0, 0, 0, 0]
 4x4x4 [1, 3, 0, 2] [0, 0, 0, 0]


Once multiple ONESSELF cubes were found it was a matter of finding faces of other cubes that matched the rotate-mirror-compliment pattern.  Finding sequences that match that pattern were quite fruitful.  However, some of the faces matched hundreds to thousands of times; as one would expect with the Birthday Problem.  Quite interestingly many of the cubes that had the matching pattern had one set of face pairs that match the ONESELF pattern.

If you recall the image of the [Torus Interconnects](https://en.wikipedia.org/wiki/Torus_interconnect), these face pairs would extend in a network along one direction.  Could these multiple copies of the same face pairs as a ONESSELF cube be the framework that extend from an origin of a ONESSELF cube?  Could then the reset of the Torus Interconnect network be filled in?

Unfortunately, of the searches completed on the sets of ONESSELF cubes discovered, three matching "framework" directions could not be found for a given ONESSELF cube.  The searches only included a small subset of possible ONESSELF cube orientations and slice information compared to a small subset of orientation and slice information for the matching "framework" cubes.  This area of research could use the benefit of organization-level computing power.

Even if a "framework" isn't to be extended from a given ONESSELF cube, individual cubes could be attached to the matching face of the ONESSELF cube and the network built from there.  This search would also need an organizational-level of computing power.  Of the thousands of cubes that could be attached, each of them would need searches on their faces for matching cubes, each of those could turn up from zero to thousands of possible face matches.  Each of the cubes to which a matching face has been found has no guarantee of being a valid cube.  It is only after multiple faces of a cube has been matched that you can have assurance that the cube is in fact a valid cube.

As the network of cubes is built, their matching faces and location relative to one another perform not only the function of self-organization, but also that of error detection.  Assuming multiple cubes surround a given area that has no fully-matched cube, but one cube matches all but one face, then it is apparent that either that one cube, or the one adjacent that does not have a matching face must have an error.  Then it would be possible to find via a redundant FEC cube of a close sequence match to replace one of the two cubes.  There may be another mechanism that operates as a FEC.

This fact-of-error provides an opportunity.  Performing differential analysis across cubes with and without errors could be used to determine components of the error detection and correction scheme at the molecular level faster than would otherwise be possible.  Using nearly identical copies of cubes, one with errors and one without would further speed the analysis.  Analysis of known-good cubes alone should provide some deep insight into the error detection and correction machinery if some basic assumptions are made about the complexity of the biological state machine and/or apriori knowledge of the replication machinery.

There must exist some biological mechanism which does verification on the non-coding sections of DNA to propagate these message containers.  If that mechanism could be discovered, and the algorithm which it employs to verify the DNA can be reverse engineered, it would be entirely possible to run a single search and extract all valid message containers.  The different exonuclease molecules seem to be exactly what would perform that function.  Testing of the various exonuclease molecules against known sequences and seeing the changes that the exonuclease molecules induce could in short order be used to determine their algorithm of choice, as well as internal state mechanisms. 

Inside the center of the cube are eight bases, 16-bits of information, that are not used for any known purpose.  These eight bases could be the basis for a contained message.  These "center 8" could also be used solely for error detection, correction, cube construction, or container modification for message interpretation. The purpose of the center 8 can only be guessed at this point.

This also raises the possibility that the faces themselves may have useful information encoded in them; message data, FEC, or slice construction information.  Is their sole purpose not only to perform error detection and message reconstruction, but contain message information themselves? With significant preprocessing it is entirely feasible that the faces themselves carry meaningful information.  It would seem quite a waste of bandwidth to not encode the message into the faces of the cubes if it is at all possible.  Finally, is there something in the DNA sequence that maps to either the center 8 or the faces that can be used to determine the method to construct the cube; slice information?  This information could be used to very quickly pick out 64-base blocks without face comparisons to billions of other possible blocks. 

Current techniques to find and reconstruct the cubes and cube networks push the limits of computability.  Algorithms could be constructed that speed up the process hundreds of times faster than what have been developed during the discovery process.  There are thousands of possible combinations that must be tried per cube, with thousands or tens of thousands of combinations to reconstruct just one pair of cube faces.  The problem is further compounded by the fact that this geometric structure isn't just found in Homo Sapiens.  Millions of species of very different organisms could all carry pieces of the puzzle.  As the corpus of data available grows, so does the computational intractability of network reconstruction.  Although not implemented in the referenced program, each face could be reduced to a single integer value, then a simple transformation could be applied to find a matching face value.  Other such optimizations could speed processing significantly.

A command to generate a 3 Torus network of given dimensions is included in the program.  A function was started to perform the reconstruction of a 3 Torus network  but abandoned once it was realized it would be well beyond the computational abilities of the servers in use.

In summary, there are strong statistical indications that at least hundreds of ONESSELF cubes have been placed in the human genome.  Furthermore, hundreds of thousands of cubes of a 3-Torus with a 1/2 Mobius twist geometry exist in the human genome.  The cubes may represent a network of interconnected cubes.  The interconnected cubes may act not only as a message ordering mechanism, but also as an error-detection system.   


======================================
--------------------------------------
------------ CONCLUSIONS -------------
--------------------------------------
======================================


There exists in multiple genomes a significant number of mathematical structures that would be considered a 3-Torus with a 1/2 Mobius twist.  The structures may map themselves into large structures called a Torus Interconnect.  These structures would have the benefit of self-ordering and self-error detecting.

As with any interesting discovery it raises more questions that it answers.  Connection to many other fields of study can be spotted throughout the analysis of the structure that will undoubtedly be interesting to follow. 

The choice of format of message container is of utmost curiosity.  It was difficult, but not too difficult to find.  Was it chosen so that it would be found?   If a higher-dimensional geometric construct were used it may never have been found.  A higher-dimensional construct could also be more efficient at carrying information.  Is what was found only a subset of a higher-dimensional object?  Why was this message container chosen?   Was it chosen because the geometric shape has some other significance?

The geometric structure has a close resemblance to a higher-order Bloch Sphere in Quantum computing, but incorporates more information.  Is it related?  Does it have something to do with spinors? The 1/2 Mobius twist is reminiscent of spinor geometry.  Does the 3-Torus network have something to do with quantum computing or networks of quantum systems?  Could the center 8 represent state information and the containers the hardware of a virtual machine?  

What algebras describe the ONESSELF cube?  Lie and Clifford algebras usually describe circles and spheres of various dimensions even with spinor structures, but does it really apply in this case?  Can Lie or Clifford algebras accurately describe a 3-Torus with a 1/2 Mobius Twist even if it is degenerated to a double-cover sphere (with a 1/2 Mobius twist)? Can Lie and Clifford algebras describe the system if the volume of the cube is removed and the toruses are basically glued together via some strange multi-dimensional connection?  Should we be looking for something else?  Some other algebra that may be even more basic?  

Does this format have something to do with deeper physics and the construction of reality? The assumption thus far was that the cube has a volume.  If the volume is removed and the three faces each construct two of three dimensions, does their interaction give rise to our perception of a three dimensional reality?  Finally, when constructing the cube, the assignment and modification of values gives one an eerie sense of field tensor change propagation.

  While the message itself was not found, strong candidates for a message container, message reconstruction technique, and message error-detection scheme have been identified.  After verification by independent sources, fact-of-existence and the format of the message container may actually be MORE important than the actual contents of any message itself.  The ramifications from a purely scientific perspective are astounding, the theological and philosophical ramifications are unnerving, but the real question is why?  Why place it there?  Why this container geometry?  Why in so many species?

How did we know that a message was placed in our DNA to go looking for it in the first place?

What are we supposed to do with this information and should we act on it?

=============================================================
-------------------------------------------------------------
------------------- OUTSTANDING QUESTIONS -------------------
-------------------------------------------------------------
=============================================================

- Is there a computationally fast way to identify valid 64-base message blocks?
- What is the Forward Error Correction scheme?
- Is slice construction and orientation information built into the 64-base message blocks?
- Is there a preferred slice format (or cube construction) that isn't 4x4x4, 8x8, or 16x4?
- What are the purpose and use of the contents of the center 8?
- Why was this message container chosen?
- What is the molecular mechanism that performs error correction on these blocks and what are their algorithms?
- Is there a computationally fast way to reconstruct a torus?
- Are the blocks only a part of a higher-dimensional structure?
- Are there other geometric structures present? (A tetrahedron, double-tetrahedron, pyramidal or double-pyramidal prism?)
- Do long chains of copied opposing-faces constitute a border for a 3-Torus Network?
- Does a onesself cube correspond to a primer or origin cube in the network?
- Do onesself SUPERBLOCKS have any significance?
- Is there an origin in these 3-Torus networks?
- Is the 3-Torus with a 1/2 Mobius twist related to a Bloch Sphere or other models of physical processes?
- Does the 3-Torus with a 1/2 Mobius twist have something to do with spinor geometry and physics?
- Does this shape describe a space, or what is the nature of the space it occupies?
- What algebras describe such a space, cube, system, and these structures?
- Do Lie and Clifford algebras really cut it for ONESSELF cubes?  Are there other algebras that more readily describe them?
- What finite groups compose those algebras?
- Is there a discrete form of these algebras?
- Is a 3-Torus network related to the computability of quantum systems?
- Does the container have a deeper tie to physics and reality?
- Why put the message in DNA/RNA instead of some other format?
- Why spread the containers across multiple species?
- Is placing the 64-base containers in multiple species to encourage us to collect and catalog a wide range of species? If so, why?
- Is there a message?
- What is the content of the message, if any?
- How would we interpret the message?
- Is the message a program?
- What is the nature of the underlying instruction architecture and hardware if it is a program?
- Is the container a part of the instruction architecture or hardware?
- Is the container a virtual machine to execute a message-program on?
- If it is a program, is the underlying hardware quantum mechanical or classical?
- If so, should we execute that program?
- Does the cubic network define the hardware or provide a method of classical simulation of a quantum mechanical system?
- Are the FEC or message verification algorithms somehow related to the processing of a system of computation?
- Are the FEC or message verification algorithms somehow related to state tracking of such a system of computation? 
- Is the message a biological wiki of some sort?
- Is the message instructions of some type?
- Is the message the construction of a biological entity or machine of some sort?
- How do we decode and interpret any message?
- Is the message like a "movie" in the 3-Torus Network (Turning Cubes on and off)?
- Is the message a modification of the 3-Torus Network structure to create a 3-Dimensional shape or shapes?
- Is there a feedback mechanism and what is it?
- WHO OR WHAT PUT THE MESSAGE THERE, AND WHY?
'''
    print(writeup_text)
