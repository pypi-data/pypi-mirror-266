try:

    from WASDHandle import WASDHandler
    import time
    import sys
    import string
    import gclib
    import tkinter as tk
except Exception as e:
    print(e)

class PyCoord():
    """This class handles the communication with Feinmess devices via RS232"""
    forward_limit = 2147483647
    reverse_limit = -2147483648
    range_of_motion = forward_limit - reverse_limit
    measurement_positions = []

    def __init__(self, com_port:str):
        self.galilTool = gclib.py()
        self.galilTool.GOpen(com_port)
        print(self.galilTool.GInfo())
    
    def sentCommand(self, command:str):
        """This method allows the user to send specific commands
        :param command: The command the user wants to execute
        :type command: str
        """
        self.galilTool.GCommand(command)


    def initSystem(self):
        """This method is used to put the system into an initial position which is always the same."""
        print(self.galilTool.GCommand('TP'))
        # if self.galilTool.GCommand('TP') == '0, 0, 1264':
        #     print("System in initial position!")
        #     return
        
        self.galilTool.GCommand('AB')
        self.galilTool.GCommand('CB 1')
        self.galilTool.GCommand('MO')   
        self.galilTool.GCommand('SH')
        self.galilTool.GCommand('AC 150000')
        self.galilTool.GCommand('DC 150000')
        self.galilTool.GCommand('SB 1')
        self.galilTool.GCommand('SP 5000,5000,5000')
        self.galilTool.GCommand('FE')
        print(self.galilTool.GCommand('BG '))
        self.galilTool.GMotionComplete('XYZ')
        self.galilTool.GCommand('AB')
        self.galilTool.GCommand('CB 1')
        self.galilTool.GCommand('MO')   
        self.galilTool.GCommand('SH')
        self.galilTool.GCommand('AC 150000')
        self.galilTool.GCommand('DC 150000')
        self.galilTool.GCommand('SB 1')
        self.galilTool.GCommand('JG 10000,10000,10000')
        self.galilTool.GCommand('FI')
        self.galilTool.GCommand('CB 1')
        print(self.galilTool.GCommand('BG '))
        self.galilTool.GMotionComplete('XYZ')
        print("System in initial position!")
        print(self.galilTool.GCommand('TP'))

    def relativePos(self,x = None, y = None, z = None):
        """This method moves an axis the specified amount of steps away from its current position.

        :param x: List with two elements.The first element specifies the movement speeed. The second element specifies the amount of steps you want the axis to take.
        :type x: list

        :param y: List with two elements.The first element specifies the movement speeed. The second element specifies the amount of steps you want the axis to take.
        :type x: list

        :param z: List with two elements.The first element specifies the movement speeed. The second element specifies the amount of steps you want the axis to take.
        :type x: list
        """

        self.galilTool.GCommand('AB')
        self.galilTool.GCommand('CB 1')
        self.galilTool.GCommand('MO')   
        self.galilTool.GCommand('SH')
        self.galilTool.GCommand('SB 1')
        self.galilTool.GCommand('AC 150000')
        self.galilTool.GCommand('DC 150000')
  
        active_axis = ''

        if type(x) == list:
            self.galilTool.GCommand('SPX = '+ str(x[1]))
            self.galilTool.GCommand('PRX = ' + str(x[0]))
            active_axis += 'X'

        if type(y) == list:
            self.galilTool.GCommand('SPY = '+ str(y[1]))
            self.galilTool.GCommand('PRY = ' + str(y[0]))
            active_axis += 'Y'

        if type(z) == list:
            self.galilTool.GCommand('SPZ = '+ str(z[1]))
            self.galilTool.GCommand('PRZ = ' + str(z[0]))
            self.galilTool.GCommand('SB 1')
            active_axis += 'Z'

        print("Starting movement!")
        self.galilTool.GCommand('BG ' + active_axis )
        self.galilTool.GMotionComplete(active_axis)
        self.galilTool.GCommand('CB 1')
        print("Movement complete!")
    
    def absolutePos(self,x = None, y = None, z = None):
        """This method moves an axis to an absolute position in the coordinate system of the Feinmess system.

        :param x: List with two elements.The first element specifies the movement speeed. The second element specifies the absolute position you want the axis to endup.
        :type x: list

        :param y: List with two elements.The first element specifies the movement speeed. The second element specifies the absolute position you want the axis to endup.
        :type x: list

        :param z: List with two elements.The first element specifies the movement speeed. The second element specifies the absolute position you want the axis to endup.
        :type x: list
        """


        self.galilTool.GCommand('AB')
        self.galilTool.GCommand('CB 1')
        self.galilTool.GCommand('MO')   
        self.galilTool.GCommand('SH')
        self.galilTool.GCommand('SB 1')
        self.galilTool.GCommand('AC 150000')
        self.galilTool.GCommand('DC 150000')
            
        active_axis = ''

        if x != None:
            self.galilTool.GCommand('SPX = '+ str(x[1]))
            self.galilTool.GCommand('PAX = ' + str(x[0]))
            active_axis += 'X'
        
        if y != None:
            self.galilTool.GCommand('SPY = '+ str(y[1]))
            self.galilTool.GCommand('PAY = ' + str(y[0]))
            active_axis += 'Y'

        if z != None:
            self.galilTool.GCommand('SPZ = '+ str(z[1]))
            self.galilTool.GCommand('PAZ = ' + str(z[0]))
            self.galilTool.GCommand('SB 1')
            active_axis += 'Z'

        print("Starting movement!")

    

    

        self.galilTool.GCommand('BG' + active_axis)
        self.galilTool.GMotionComplete(active_axis)
        self.galilTool.GCommand('CB 1')
        print("Movement complete!")


    def getPos(self):
        """    This method returns the current position of all connected axis.

        :return: A list every element holds the current position of an axis in alphabetical order.
        :rtype: list
        """        
        data = self.galilTool.GCommand('TP')
        data = data.split(',')
        
        for i in range(len(data)):
            data[i] = int(data[i])

        return data 

    def gridMode(self, rows, column, row_step, col_step, z_retract,rest_period, speed):
        for i in range(rows):
            time.sleep(rest_period)
            self.relativePos(z=[z_retract, speed])
            for j in range(column-1):
                if i % 2 == 0:
                    self.relativePos(x=[row_step, speed])
                else:
                    self.relativePos(x=[-1*row_step, speed])
                self.relativePos(z=[z_retract*-1, speed])
                time.sleep(rest_period)
                self.relativePos(z=[z_retract, speed])
            self.relativePos(y = [col_step, speed],z=[z_retract*-1, speed])
            
    
    def customGridMode(self, steps_per_element, mapping, rest_time):
        
        steps_to_take = 0
        positions = self.getPos()
        initial_x_position = positions[0]
        initial_y_position = positions[1]
        initial_z_position = positions[2]

        row_counter = 0

        for row in mapping:
            for point in row:
                if point == 1:
                    self.absolutePos(z = [1000, initial_z_position])
                    time.sleep(rest_time)
                    self.relativePos(z = [1000, -50000])
                self.relativePos(y = [1000, steps_per_element])
            
            self.relativePos(x = [1000, steps_per_element])
            self.absolutePos(y = [1000, initial_y_position])

    def wasdMovement(self):
        """This method opens a small GUI that allows the user to move the Feinmess-system with
        the keys "WASD". When pressing enter the current position of the Feinmess-system gets
        written to the global list measurement_positions for laater use    
        """
        root = tk.Tk()
        #self.pack(fill = "both", expand=True)
        WASDHandler(root, self).pack(fill="both", expand=True)
        root.mainloop()

    

    

