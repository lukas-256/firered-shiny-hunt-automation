import serial

ser = serial.Serial("/dev/cu.usbserial-BG03S8AW", 19200, timeout=1)
print("opened")
ser.close()
