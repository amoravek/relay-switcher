import sys
import socket
import struct
import datetime, time

def get_operational_state(host, port):
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
      array_calculated = []

      for i in range(len):
        array_calculated.append(struct.unpack('!i', s.recv(4))[0])
  except Exception as e:
    print(f"Connection error: {e}")
  finally:
    try:
      s.close ()
    except Exception as e:
      print(f"Disconnect error: {e}")
      pass

  return int(array_calculated[80])

def get_state_name(state_number):
    state_names = {
        0: 'Topení',
        1: 'TUV',
        2: 'Bazén / fotovoltaika',
        3: 'Pomocný zámek',
        4: 'Odmrazování',
        5: 'Žádný požadavek',
        6: 'Topení (ext. zdroj)',
        7: 'Chlazení'
    }

    return state_names.get(state_number, 'Unknown')