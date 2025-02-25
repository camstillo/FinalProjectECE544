'''
Gui Class

@author Cameron Castillo
@author Kim Steiner

@brief

A python file which creates a class to setup a GUI for 
the ECE544 final project. The gui is used along with
the serial_comm.py class which sends and recieves data
from the Nexys7 FPGA board. The purpose of the GUI is 
to allow the user to perform several actions:

    1: Set a water percentage threshold
    2: View the moisture data graphically over time
    3: Toggle the watering system on and off

Moisture values are returned as a percentage of the max
range of values from the sensor maximum. This allows 
the UART to only send and recieve a byte for watering
values. All data on the plot will be displayed in terms 
of percentages. The plot should make requests over a 
user-specified period back to the watering system.

@note Will be packaged into an executable application
and designed via tkinter

'''
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np

#for plotting functions in tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 

from serial_class import uart

class gui:
    '''
    gui

    @brief

    A class to hold GUI functionality and allows 
    main to only instantiate to start operation.

    '''


    def __init__(root, data_interval, uart_obj=None, passed_points=None):
        '''
        init

        @brief

        Called at gui instantiation. Use to setup object for 
        serial communication instantaneously as part of self.

        @param self instantiated class object
        @param data_interval variable holding value of time 
        between data points
        @param uart_obj Offers override for self-created 
        uart; default None
        @param passed_points a list of duples representing 
        points in watering map; default None
        
        @return nothing -- run GUI output function by default

        '''
        #create tkinter object
        self.root = tk.Tk()

        #create uart object
        if (uart_obj != None):
            self.uart = uart_obj
        else:
            self.uart = uart()

        #create class param for data points
        if(passed_points != None):
            #TODO: Create a function to parse passed_points
            #from txt file or some other format.
            print("WARNING: Passed point functionality is not currently
                  supportted. Starting blank data")
            self.data = np.zeros((1,2))
        else:
            self.data = np.zeros((1,2))

        #create class-wide vars
        self.threshold = 50         #start at half percentage value
        self.watering_state = False #boolean expression for on/off watering
        self.data_interval = data_interval

        #start gui @ end
        self.start_gui()

    def start_gui(self):
        '''
        start_gui

        @brief

        Setup and start tkinter gui. Use this at the 
        end of init function to run function as main.

        @return should only return at pgm close

        '''
        #initialize gui layout
        self.gui_layout()

        #start gui
        self.root.mainloop()

        #file collected datapoints as .txt file
        #TODO: Create function to do this....
        
    def gui_layout(self):
        '''
        gui_layout

        @brief

        Use this function to define the structure of
        the GUI before starting.

        @note Created with assistance from ChatGPT

        '''
        #setup window and window size
        self.root.Title("Microblaze Watering system")
        self.root.geometry("500x500")
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)        

        #create plot
        fig = self.plot_window()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.grid(row=0, col=0, rowspan=5, padx=10, pady=10)

        #create buttons
        #   send command over uart
        self.cmd_input = tk.Entry(
                self.root
                ).grid(row=0, col=2, padx=10, pady=10)
        self.cmd_button = tk.Button(
                self.root,
                text="Send Cmd",
                command=self.handle_send_cmd
                ).grid(row=0, col=3, padx=10, pady=10)

        #   override watering threshold
        self.override_button = tk.Button(
                self.root,
                text="Force Toggle",
                command=self.handle_override
                ).grid(row=1, col=3, padx=10, pady=10)
        
        #   set water check time
        tk.Label(
                self.root,
                text="Measurment Interval[min]:"
                ).grid(row=2, col=2, padx=10, pady=10)
        self.time_interval = tk.Entry(
                self.root
                ).grid(row=2, col=3, padx=10, pady=10)
        self.interval_check = tk.Button(
                self.root,
                text="Update",
                command=self.handle_interval
                ).grid(row=3, col=3, padx=10, pady=10)
        
        #create slider for value of threshold
        tk.Scale(
                self.root,
                variable=self.threshold
                ).grid(row=0, col=1, padx=10, pady=10)

    def plot_window(self):
        '''
        plot_window

        @brief

        Create a figure object from matplotlib which can
        be added to the canvas in the GUI. Passed in point
        tuple values in self.data. Threshold plot value
        is also passed in with self.water_threshold.

        @return figure object

        @note Created with assistance from ChatGPT

        '''
        # Create a figure and axis
        fig, ax = plt.subplots(facecolor='black')

        #Pull point values from tuples in list
        t = self.data[:][0]
        water_val = self.data[:][1]

        #Plot available
        ax.plot(t, water_val, 'wo',
                markersize=4, label="Data Points")
        
        #create threshold line
        ax.axhline(y=self.water_threshold, color='w',
                   linestyle='--', label='Threshold')

        #create background and plotting colors
        ax.set_facecolor('black')

        #create axis labels and name
        ax.set_xlabel("Time [Minutes]", color='white')
        ax.set_ylabel("Moisture Percentage", color='white')
        ax.legend()

        #determine max plot xdim
        x_ticks = self.determine_xdim(t)

        #create plot dimensions
        if (x_ticks[-1] < 60):
            ax.set_xticks([10*i for i in range(7)])
            ax.xlim(-2,60)
        else:
            ax.set_xticks(x_ticks)
            ax.xlim(-2,x_ticks[-1])
        ax.ylim(-2,110)
        ax.yticks([0, 25, 50, 75, 100], 
                   ['0%', '25%', '50%', '75%', '100%'])

        return fig

    def determine_xdim(self, t):
        '''
        determine xdim

        @brief

        Use this function to create a list of tick values
        for plotting function. Goes from 0 to the largest
        multiple of 10 in the x_ticks.
        
        @param t numpy array of time values

        @return list of x_ticks

        '''
        #get multiple number
        ten_mult = t[-1]//10
        remainder = t[-1]%10
        
        x_ticks = [10*i for i in range(ten_mult+1)]

        #check whether remainder is > 0
        if(remainder > 0):
            x_ticks.append(x_ticks[-1]+10)

        return x_ticks

    #button functions:

    def handle_send_cmd(self):
        '''
        handle send command

        @brief

        button handling function for send command. Use
        to send data from the command box to the uart.

        '''
        #parse command ('cmd[0]' + 'data[1:]')
        box_in = self.cmd_input.get()


        #send over uart
        if(len(box_in) > 1):
            self.uart.send(box_in[0], data=box_in[1:])
        else:
            self.uart.send(box_in[0])


    def handle_override(self):
        '''
        handle override

        @brief

        Button handling for override function. Use to 
        toggle the watering system on and off automatically

        '''
        #set uart state opposite as previous
        self.watering_state = not(self.watering_state) 

        #send change in state
        self.uart.send(
                self.uart.cmd_dict['STATE_OVERRIDE'],
                data=self.watering_state, 
                )

    def handle_interval(self):
        '''
        handle interval

        @brief

        Button handling for interval override. Use to 
        write a new value for the time interval from 
        the user input box.

        '''
        #write value of interval from box
        self.data_variable = self.time_interval.get()




