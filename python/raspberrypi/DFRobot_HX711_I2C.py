# -*- coding: utf-8 -*
import serial
import time
import smbus
import struct

class DFRobot_HX711_I2C(object):


  
  ''' register configuration '''
  I2C_ADDR                   = 0x60
  REG_DATA_GET_RAM_DATA      = 0x66
  REG_DATA_GET_CALIBRATION   = 0x67
  REG_DATA_SET_CALIBRATION   = 0x68
  REG_DATA_GET_PEEL_FLAG     = 0x69
  
  
  ''' Conversion data '''
  rxbuf      = [0,0,0,0]
  _calibration = 2210.0
  _offset = 0
  #_addr      =  0x50
  #_mode      =  0
  #   idle =    0
  def __init__(self ,bus,address):
    self.i2cbus = smbus.SMBus(bus)
    self._addr = address
    self.idle =    0

  def begin(self):
    self._offset = self.average(20)
    time.sleep(0.05)

  def readWeight(self,times):
    value = self.average(times)
    time.sleep(0.05)
    if self.peelFlag() == True:
      self._offset = self.average(times)
      #Serial.println("pppppppppppppppppppppp----------------------");
    #print(value);
    #print(self._offset);
    return ((value - self._offset)/self._calibration) 

  def average(self,times):
    
    sum = 0
    for i in range(times):
        #
        data = self.getValue()
        if data == 0 :
           times = times -1
        else:
           sum = sum + data;
    #print(times)
    #print("--------------------------")
    if(times == 0):
       times =1
    return  sum/times
    
   
  ''' Read the result data of the register '''
  def getCalibration(self):
      data = self.read_reg(self.REG_DATA_GET_CALIBRATION,4);
      aa= bytearray(data) 
      
      return struct.unpack('>f', aa)
  ''' Modify i2c device number '''
  def setCalibration(self ,value):
      self._calibration = value
  def peelFlag(self):
      data = self.read_reg(self.REG_DATA_GET_PEEL_FLAG,1);
      if(data[0] == 0x01 or data[0] == 129):
        return True
      else:
        return False
  def getValue(self):
      data = self.read_reg(self.REG_DATA_GET_RAM_DATA,4);
      value = 0;
      if(data[0] == 0x12):
        value = long(data[1])
        value = long((value << 8) | data[2]);
        value = long((value << 8) | data[3]);
      else:
        return 0
      return value^0x800000
  def write_data(self, data):
    self.i2cbus.write_byte(self._addr ,data)
    
  def write_reg(self, reg, data):
    self.i2cbus.write_byte(self._addr ,reg)
    self.i2cbus.write_byte(self._addr ,data)

  def read_reg(self, reg ,len):

    self.i2cbus.write_byte(self._addr,reg)
    time.sleep(0.03)
    for i in range(len):
      #time.sleep(0.03)
      self.rxbuf[i] = self.i2cbus.read_byte(self._addr)
    #print(self.rxbuf)
    return self.rxbuf