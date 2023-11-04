import numpy as np
import os

# In order to reduce effect of noise in the samples data,
# each bit of the UART bit-stream may be sampled more than once
SAMPLES_PER_BIT = 10

# The UART bit-stream samples
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
        uart_start_bit_detected = False
        uart_data_byte = 0
        uart_data_bit_index = 0

        last_bit_value = 0

        sample_index = 0
        sample_sum = 0

        while True:
            # Read 1 byte from the file
            read_byte = file.read(1)

            if not read_byte:
                break

            # convert file byte to numpy byte
            byte_value = np.uint8(read_byte[0])

            # Iterate over the bits of current byte value
            for bit_index in range(8):
                # extract the bit values from the MSB (left) side of the byte
                bit_value = (byte_value >> (7 - bit_index)) & 0x01

                # Sum of values of total samples for current bit
                sample_sum += bit_value
                # Index of samples for current bit
                sample_index += 1

                if sample_index >= SAMPLES_PER_BIT:
                    # Calculate the current bit value according to the sum of samples and the threshold
                    if sample_sum >= (SAMPLES_PER_BIT // 2 + 1):
                        current_bit_value = 1
                    else:
                        current_bit_value = 0

                    sample_index = 0
                    sample_sum = 0

                    if not uart_start_bit_detected:
                        # Check the START bit in the falling edge of signal
                        if current_bit_value == 0 and last_bit_value == 1:
                            uart_start_bit_detected = True
                            uart_data_bit_index = 0
                            uart_data_byte = 0
                    else:
                        # Get bits of the DATA byte
                        if uart_data_bit_index < 8:
                            uart_data_byte = uart_data_byte | (
                                current_bit_value << uart_data_bit_index
                            )
                            uart_data_bit_index += 1
                        else:
                            # Check the STOP bit
                            # if STOP bit is not equal to '1' this is a corrupt frame
                            if current_bit_value == 0:
                                print("corrupt byte!")
                            else:
                                # UART frame is healthy
                                # Output the data byte
                                print(uart_data_byte)

                            uart_start_bit_detected = False

                    last_bit_value = current_bit_value
except IOError:
    print("Error opening file.")
