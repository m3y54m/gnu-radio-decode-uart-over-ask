"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, samples_per_bit=1):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Decode UART Bitstream',   # will show up in GRC
            in_sig=[np.byte],
            out_sig=[np.byte]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.samples_per_bit = samples_per_bit
        self.sample_index = 0
        self.sample_sum = 0
        
        self.uart_start_bit_detected = False
        self.uart_data_byte = 0
        self.uart_data_bit_index = 0

        self.last_bit_value = 0

    def work(self, input_items, output_items):
    
        """
        | START | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | STOP |
        """

        # Get input bytes    
        # Iterarte over stream of bytes in input_items[0]
        for byte_value in input_items[0]:

            # Iterate over the bits of current byte value
            for bit_index in range(8):
                # extract the bit values from the MSB (left) side of the byte
                bit_value = (byte_value >> (7 - bit_index)) & 0x01

                # Sum of values of total samples for current bit
                self.sample_sum += bit_value
                # Index of samples for current bit
                self.sample_index += 1

                if self.sample_index >= self.samples_per_bit:
                    # Calculate the current bit value according to the sum of samples and the 1/0 threshold
                    if self.sample_sum >= (self.samples_per_bit // 2 + 1):
                        current_bit_value = 1
                    else:
                        current_bit_value = 0

                    self.sample_index = 0
                    self.sample_sum = 0

                    if not self.uart_start_bit_detected:
                        # Check the START bit in the falling edge of signal
                        if current_bit_value == 0 and self.last_bit_value == 1:
                            self.uart_start_bit_detected = True
                            self.uart_data_bit_index = 0
                            self.uart_data_byte = 0
                    else:
                        # Get bits of the DATA byte
                        if self.uart_data_bit_index < 8:
                            self.uart_data_byte = self.uart_data_byte | (
                                current_bit_value << self.uart_data_bit_index
                            )
                            self.uart_data_bit_index += 1
                        else:
                            # Check the STOP bit
                            # if STOP bit is not equal to '1' this is a corrupt frame
                            if current_bit_value == 0:
                                print("corrupt byte!")
                            else:
                                # UART frame is healthy
                                # Output the data byte
                                output_items[0][:] = self.uart_data_byte
                                print(self.uart_data_byte)

                            self.uart_start_bit_detected = False

                    self.last_bit_value = current_bit_value
                            
        return len(output_items[0])
