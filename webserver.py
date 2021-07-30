import json
import logging
from websocket_server import WebsocketServer
 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

clients = []

# Callback functions

def get_player_data():
    ret = []
    for client in clients:
        if(client['name']):
            ret.append({
                'name': client['name'],
                'status': client['status'],
                'role': client['role'],
                'voted': client['voted'],
            })

    return ret

def new_client(client, server):
  logger.info('New client {}:{} has joined.'.format(client['address'][0], client['address'][1]))
  clients.append(client)
  print(clients)
 
def client_left(client, server):
    logger.info('Client {}:{} has left.'.format(client['address'][0], client['address'][1]))
    index = next((index for (index, d) in enumerate(clients) if d['id'] == client['id']), None)
    clients.pop(index)

 
def message_received(client, server, message):
  logger.info('Message "{}" has been received from {}:{}'.format(message, client['address'][0], client['address'][1]))
  mes = json.loads(message)
  if(mes['status'] == 'login'):
    index = next((index for (index, d) in enumerate(clients) if d['id'] == client['id']), None)
    clients[index]['name'] = mes['name']
    clients[index]['status'] = 'ready'
    clients[index]['role'] = 'none'
    clients[index]['voted'] = 0
    ret = {
        'next_status' : 'ready',
        'data': get_player_data(),
    }
    server.send_message(client, json.dumps(ret))

  print(client)

  # server.send_message(client, reply_message)
  # logger.info('Message "{}" has been sent to {}:{}'.format(reply_message, client['address'][0], client['address'][1]))

# Main
if __name__ == "__main__":
  server = WebsocketServer(port=12345, host='127.0.0.1', loglevel=logging.INFO)
  server.set_fn_new_client(new_client)
  server.set_fn_client_left(client_left)
  server.set_fn_message_received(message_received)
  
  server.run_forever()
