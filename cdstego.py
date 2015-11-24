#!/usr/bin/python2

from sys import stdin, stdout, argv
import array
import struct
from hashlib import md5

#### FUNCTION DEFS ####
# start embed_char -----------------------------------------
def embed_char(cover_chunk, embed_char):

    # take an 8 bit (one byte) chunk and set the LSB to 'bit' value
    def set_LSB(chunk, bit):
        if bit == 0:
            chunk &= ~(1<<0)
        if bit == 1:
            chunk |= 1<<0
        return chunk

    out_buffer = array.array('h')
    
    for i in range(8):
        bit = (ord(embed_char) >> (7-i)) & 1
        out_buffer.append(set_LSB(cover_chunk[i], bit))
    
    return out_buffer
# end embed_char --------------------------------------------

# start extract_char -----------------------------------------
def extract_char(cover_chunk):

    # take an 8 bit (one byte) chunk and extract the LSB value
    def get_LSB(chunk):
        bit = (chunk>>0) & 1;
        return bit
    
    binary_string = ''
    
    for i in cover_chunk:
        binary_string += str(get_LSB(i))

    # convert binary string (ie '01101001') to a single int:
    output_char = int(binary_string, 2)
    return output_char
# end extract_char --------------------------------------------

#### MAIN ####
# take password for checking/setting the end marker. ask for it if not given
if "-p" in argv:
    data_password = argv[(argv.index("-p"))]
else:
    data_password = raw_input("Password: ")

# set the end marker string to search for.
end_marker_hash_object = md5("ENDFILE.")
end_marker_hash_object.update(data_password)
end_marker = end_marker_hash_object.hexdigest()

# embed mode:
if "-embed" in argv:
    embed_file = argv[(argv.index("-embed")+1)]
    
    with open(embed_file, 'rb') as data_file:
        embed_data = data_file.read()
    
    # append end_marker to the end of the data:
    embed_data += end_marker
    
    # embed given data to file:
    for i in embed_data:
        input_stream = stdin.read(16)
        cover_buffer = array.array('h', input_stream)
        output_buffer = embed_char(cover_buffer, i)
        for i in output_buffer:
            stdout.write(struct.pack('<h', i))

    # write the rest of the PCM to output file.
    stdout.write(stdin.read())
    exit(0)

# extract mode (reads from stdin and writes to stdout):
if "-extract" in argv:
    input_stream = stdin.read(16)
    output_buffer = []

    while input_stream:
        cover_buffer = array.array('h', input_stream)
        newchar = chr(extract_char(cover_buffer))
        
        if len(output_buffer) < 32:
            output_buffer.append(newchar)
        else:
            out_char = output_buffer.pop(0)
            output_buffer.append(newchar)
            stdout.write(struct.pack('c', out_char))
            
            if "".join(output_buffer) == end_marker:
                break

        input_stream = stdin.read(16)
    exit(0)

else: # just exit telling correct syntax if no command is given:
    print("usage: cdstego.py -embed [file to be embedded]")
    print("       cdstego.py -extract")
    print("cdstego reads cover data from stdin and writes the modulated pcm to stdout.")
    print("examples:")
    print("cdstego -embed my_secret_data.txt < cover_file.pcm > stego_file.pcm")
    print("cdstego -extract < stego_file.pcm > my_extracted_secrets.txt")
    exit(0)
