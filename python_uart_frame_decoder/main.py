import os

SAMPLES_PER_BIT = 10

BINARY_FILE_NAME = "10-samples-per-bit.bin"
# Get the path of the Python source file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the relative path to the binary file
FILE_PATH = os.path.join(CURRENT_DIR, BINARY_FILE_NAME)

"""
| START | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | STOP |

"""
try:
    with open(FILE_PATH, "rb") as file:
        is_start_bit_detected = False
        data_bit_index = 0
        current_byte = 0
        last_bit = "0"

        sample_index = 0
        sample_bits_sum = 0

        while True:
            # Read 1 byte from the file
            byte_value = file.read(1)

            if not byte_value:
                break

            binary_string = bin(int.from_bytes(byte_value, byteorder="big"))[2:].zfill(
                8
            )

            for i, bit_char in enumerate(binary_string):
                
                sample_bits_sum += int(bit_char)
                sample_index += 1
                
                if sample_index >= SAMPLES_PER_BIT:
                    
                    if sample_bits_sum >= (SAMPLES_PER_BIT // 2 + 1):
                        current_bit = "1"
                    else:
                        current_bit = "0"

                    sample_index = 0
                    sample_bits_sum = 0

                    if not is_start_bit_detected:
                        if current_bit == "0" and last_bit == "1":
                            is_start_bit_detected = True
                            data_bit_index = 0
                            current_byte = 0
                            last_bit = current_bit
                        else:
                            last_bit = current_bit
                            continue
                    else:
                        last_bit = current_bit
                        if data_bit_index < 8:
                            current_byte = current_byte | (
                                int(current_bit) << data_bit_index
                            )
                            data_bit_index += 1
                        else:
                            is_start_bit_detected = False

                            if current_bit == "0":
                                current_byte = None

                            print(current_byte)
except IOError:
    print("Error opening file.")
