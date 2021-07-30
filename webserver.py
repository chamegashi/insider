import random
import json
import logging
from websocket_server import WebsocketServer
 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

clients = []
answer = ""

# Callback functions

def get_players_data():
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

def get_player_data(index):
    ret = {}
    if(clients[index]['name']):
        ret = {
            'name': clients[index]['name'],
            'status': clients[index]['status'],
            'role': clients[index]['role'],
            'voted': clients[index]['voted'],
        }

    return ret

def check_all_voted():
    result = True
    clients_data = get_players_data()
    for client in clients_data:
        if(client['voted'] == 'none'):
            result = False
    
    return result

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
        clients[index]['voted'] = 'none'
        ret = {
            'next_status' : 'ready',
            'data': get_players_data(),
        }
        for c in clients:
            server.send_message(c, json.dumps(ret))
    
    elif (mes['status'] == 'ready'):
        role_list = []
        for i in range(len(clients)):
            if(i == 0):
                role_list.append('master')
            elif(i == 1):
                role_list.append('insider')
            else:
                role_list.append('people')
        
        random.shuffle(role_list)
        answer = "布団"

        for i in range(len(clients)):
            clients[i]['role'] = role_list[i]
            ret = {
                'next_status' : 'start',
                'data': get_player_data(i),
                'answer': answer
            }
            server.send_message(clients[i], json.dumps(ret))
    
    elif (mes['status'] == 'start'):
        ret = {
            'next_status': 'vote',
            'data': get_players_data(),
            'reserve': False
        }
        for i in range(len(clients)):
            server.send_message(clients[i], json.dumps(ret))

    elif (mes['status'] == 'vote'):
        index = next((index for (index, d) in enumerate(clients) if d['id'] == client['id']), None)
        clients[index]['voted'] = mes['vote']

        if(check_all_voted()):
            ret = {
                'next_status': 'waitResult',
            }
            for i in range(len(clients)):
                server.send_message(clients[i], json.dumps(ret))
        
        else:
            ret = {
                'next_status': 'vote',
                'data': get_players_data(),
                'reserve': True
            }
            server.send_message(client, json.dumps(ret))

    elif (mes['status'] == 'waitResult'):

        if(check_all_voted()):
            ret = {
                'next_status': 'waitResult',
            }
            for i in range(len(clients)):
                server.send_message(clients[i], json.dumps(ret))
        
        else:
            ret = {
                'next_status': 'vote',
                'data': get_players_data(),
                'reserve': True
            }
            server.send_message(client, json.dumps(ret))




# Main
if __name__ == "__main__":
  server = WebsocketServer(port=12345, host='127.0.0.1', loglevel=logging.INFO)
  server.set_fn_new_client(new_client)
  server.set_fn_client_left(client_left)
  server.set_fn_message_received(message_received)
  
  server.run_forever()
