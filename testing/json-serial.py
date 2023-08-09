import serial
import time, json

serialPort = serial.Serial(
    port="COM3", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
while 1:
    # Wait until there is data waiting in the serial buffer
    if serialPort.in_waiting > 0:

        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()

        # Print the contents of the serial data
        try:
           # print(serialString.decode("Ascii"))
            mystring = json.loads(str(serialString.decode("Ascii")).strip())
            print(mystring)
            print(mystring["sensor"])
        except:
            pass