import sys
import socket
import struct
import datetime, time

def get_operational_state(host, port):
  array_calculated = []

  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((host, port))
      s.send(struct.pack('!i', 3004))
      s.send(struct.pack('!i', 0))

      if struct.unpack('!i', s.recv(4))[0] != 3004:
        print('Error: REQ_CALCULATED CMD')
        exit()

      stat = struct.unpack('!i', s.recv(4))[0]
      len = struct.unpack('!i', s.recv(4))[0]

      for i in range(len):
        array_calculated.append(struct.unpack('!i', s.recv(4))[0])
  finally:
    s.close ()

  return int(array_calculated[80])
  # return 1 # TUV

def get_state_name(state_number):
    state_names = {
        0: 'Topeni',
        1: 'TUV',
        2: 'Bazen / fotovoltaika',
        3: 'Pomocny zamek',
        4: 'Odmrazovani',
        5: 'Zadny pozadavek',
        6: 'Topeni (ext. zdroj)',
        7: 'Chlazeni'
    }

    return state_names.get(state_number, 'Unknown')