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

words = ["布団", "廊下", "教科書", "会議室",
"部屋", "トイレ", "銀行", "郵便局","図書館", "美術館", "飛行機", "刺身", "天ぷら", "うどん",
"そば", "ムー大陸", "柔道", "剣道", "サッカー", "バレー", "弓道", "野球", "スマブラ", "ポケモン", "パソコン", 
"電子レンジ", "ポテトチップス", "割りばし", "ウマ娘", "FGO", "カメラ", "CD", "おでん", "温泉", "体温計", "椅子", 
"水筒", "ビール", "日本酒", "唐揚げ", "オリンピック", "入学式", "卒業式", "マンガ", "猫", "犬"]

# Callback functions

def get_players_data():
    ret = []
    for client in clients:
        if(len(client) > 3):
            ret.append({
                'name': client['name'],
                'status': client['status'],
                'role': client['role'],
                'voted': client['voted'],
            })

    return ret

def get_player_data(index):
    ret = {}
    if(len(clients[index]) > 3):
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

def check_result():
    players_data = get_players_data()
    result_data = {}

    for player in players_data:
        result_data[player['name']] = 0

    max_num = 0
    for player in players_data:
        result_data[player['voted']] = result_data[player['voted']] + 1
        if(max_num < result_data[player['voted']]):
            max_num = max_num + 1
    
    print(result_data)

    answers = []
    for player in players_data:
        if(max_num == result_data[player['name']]):
            answers.append(player['name'])

    if(len(answers) == 1):
        if(check_insider(answers[0])):
            return True
        else:
            return False
    
    for player in players_data:
        if(player['role'] == 'master'):
            if(check_insider(player['voted'])):
                return True
            else:
                return False


    return False
        

def check_insider(name):
    players = get_players_data()
    for player in players:
        if(player['name'] == name):
            if(player['role'] == 'insider'):
                return True
    
    return False

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
        random.shuffle(words)
        answer = words[0]

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

        if(check_result()):
            ret = {
                'next_status': 'result',
                'data': get_players_data(),
                'result': True
            }
            server.send_message(client, json.dumps(ret))
        else:
            ret = {
                'next_status': 'result',
                'data': get_players_data(),
                'result': False
            }
            server.send_message(client, json.dumps(ret))

    elif(mes['status'] == 'restart'):
        for client in clients:
            client['status'] = 'ready'
            client['role'] = 'none'
            client['voted'] = 'none'
        
        role_list = []
        for i in range(len(clients)):
            if(i == 0):
                role_list.append('master')
            elif(i == 1):
                role_list.append('insider')
            else:
                role_list.append('people')
        
        random.shuffle(role_list)
        random.shuffle(words)
        answer = words[0]

        for i in range(len(clients)):
            clients[i]['role'] = role_list[i]
            ret = {
                'next_status' : 'start',
                'data': get_player_data(i),
                'answer': answer
            }
            server.send_message(clients[i], json.dumps(ret))

# Main
if __name__ == "__main__":
  server = WebsocketServer(port=12345, host='127.0.0.1', loglevel=logging.INFO)
  server.set_fn_new_client(new_client)
  server.set_fn_client_left(client_left)
  server.set_fn_message_received(message_received)
  
  server.run_forever()
