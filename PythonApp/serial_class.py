'''
@brief

This file is used to provide the functionality for a tkinter GUI controlling 
the UART interface to the backscatter test platform. This performs two 
functions:

    1: initiate transmissions by transmitting 's'
    2: write data by transmitting 'a' + [data]

This is just a test platform and not necessarily fully functional. Additional 
functionality may be added in the future to write to registers within the RTL.

@author Cameron Castillo

@note See gui.py to load the GUI made from tkinter

'''
import serial as ser

class zynq_interface:
    """
    @brief 

    This class acts as an interface to the zynq using the serial port.
    It sets up a com port, and will eventually include a register map 
    and functions to integrate with the RTL. 

    @author Cameron Castillo

    """

    def __init__(self, baud=115200, timeout=0.5):
        """
        @brief

        init function for zynq_interface class

        @author Cameron Castillo

        @param baud: baud rate for zynq board (default 115200)
        @param timeout: timeout time between transmissions (default 1s)

        @note Do not create an instance of the Uart in the init function as
        there is not a COM port initialized in the gui....

        """
        #Setup Serial variables 
        self.baud = baud
        self.timeout = timeout
        self.uart = None
        self.port = None
    
    def send_data(self, cmd, data=None):
        """
        @brief 

        transmit data over UART terminal depending on command received in
        cmd argument. Characters should either be 's' or 'a' for initiating
        transmissions or sending data respectively.

        @author Cameron Castillo

        @param self: class variables
        @param cmd: command argument, either 's'=initiate backscatter or
        'a'=send data to input fifo
        @param data: data to transmit to input fifo (max size 1024 bytes)
        
        @return number of bytes written via UART 

        """
        #Check that Uart is actually connected
        if (self.uart == None):
            print("Invalid call: no UART object defined")
            raise NameError

        #organize data and cmd into bytearray
        if (data != None):
            uart_tx = bytes((cmd + data), 'utf-8')
        else:
            uart_tx = bytes(cmd, 'utf-8')

        #Send command over uart
        return self.uart.write(uart_tx)

    def connect(self, com):
        """
        @brief

        This function handles a connection to the UART port. Called at class 
        init in a "try-except" capacity. Call again each time user inputs a 
        new COM port. 

        @author Cameron Castillo

        @param new_com: COM port to be connected to.
        @param baud: define the baud rate for the port.
        @param timeout: define timeout between transmissions

        @return boolean true for good connection

        @note Since this function is taking user input, the "try-catch" method
        is really important. Without it, the user might connect to an invalid
        COM port and the program will crash without error handling.

        """
        try:
            self.uart = ser.Serial(com, baudrate=self.baud, timeout=self.timeout)
        except SerialException: 
            print(f'{com} is an invalid COM port. Check device manager again to \
                    ensure the zynq is connected to the correct port.\n' )
            return False
        finally:
            self.port = com
        print(f'Successfully connected to {com}')
        return True
        



    


