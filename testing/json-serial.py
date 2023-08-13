import serial
import time, json

serialPort = serial.Serial(
    port="/dev/ttyUSB0", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART

data = {"A": "test5"}

data = {
        "A": "moveRev",
        "M": str(int(900 * 44.44)),
        "M2": 1,
        "P": 1,
        "F":1
    }

serialPort.write(json.dumps(data).encode())
while 1:
    if serialPort.in_waiting > 0:

        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()

        # Print the contents of the serial data
        try:
           # print(serialString.decode("Ascii"))


            mystring = json.loads(str(serialString.decode("Ascii")).strip())
            print(mystring)
            print(mystring["status"])
        except:
            print("fail")
            pass
