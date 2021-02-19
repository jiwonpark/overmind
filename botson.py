#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from common import log


# In[ ]:


import requests
import asyncio

import json

botson_key = None

def load_botson_config():
    global botson_key
    file = open('config.json',mode='r')
    all_of_it = file.read()
    file.close()
    obj = json.loads(all_of_it)
    botson_key = obj['botson']['api_key']

load_botson_config()

admin_chat_id = 517995321;

import urllib

# def send(id, text):
#     res = requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(botson_key, id, urllib.parse.quote(text)));
#     body = res.json()
#     log(body)

# files = {'photo': open('./saved/{}.jpg'.format(user_id), 'rb')}
# status = requests.post('https://api.telegram.org/bot<TOKEN>/sendPhoto?chat_id={}'.format(chat_id), files=files)

async def _send_photo(id):
    async with aiohttp.ClientSession() as session:
        files = {'photo': open('sandbox.tLTCUSD.5m.png', 'rb')}
        async with session.post('https://api.telegram.org/bot{}/sendPhoto?chat_id={}'.format(botson_key, id), data=files) as res:
            data = await res.text()
            body = json.loads(data)
            log(body)


async def _send(id, text):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(botson_key, id, urllib.parse.quote(text))) as res:
            data = await res.text()
            body = json.loads(data)
            log(body)

def send(id, text):
    loop = asyncio.get_event_loop()
    loop.create_task(_send(id, text))

def send_photo(id):
    loop = asyncio.get_event_loop()
    loop.create_task(_send_photo(id))

def notify_admin(text):
    send(admin_chat_id, text)

def send_photo_to_admin():
    send_photo(admin_chat_id)

def handle_admin_chat(first_name, id, text):
    if id != admin_chat_id:
        return False
    send(id, text)
    return True

import aiohttp

async def _botson_loop():
    next_update_id = -1

    while True:

#         res = requests.get('https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=1000'.format(botson_key, next_update_id));
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=1000'.format(botson_key, next_update_id)) as res:
#                 log(res)
                data = await res.text();
#                 log(data)
                body = json.loads(data)
                log(body)

                if not body['ok']:
                    log(body)
                    continue

                log('Polled!')

                if len(body['result']) == 0:
                    next_update_id = 1;
                    continue

#                 if next_update_id == -1:
#                     next_update_id = body['result'][- 1]['update_id'] + 1
#                     log('Set last update id to {}'.format(next_update_id));
#                     continue

                for it in body['result']:

#                     log(it['update_id'], it['message'])
#                     log(it['update_id'], it['message']['chat']['id'], it['message']['from']['id'], it['message']['from']['first_name'], it['message']['date'], it['message']['text'])

                    next_update_id = it['update_id'] + 1
                    log('Set last update id to {}'.format(next_update_id))
                    log(it['message']['from']['first_name'], it['message']['from']['id'], it['message']['text'])

                    if handle_admin_chat(it['message']['from']['first_name'], it['message']['from']['id'], it['message']['text']):
                        continue

async def botson_loop():

    while True:
        
        try:
            await _botson_loop()

        except Exception as e:
            log(repr(e))
            notify_admin(repr(e))
            sleep(30)


# In[ ]:


# async def test_loop():
#     send_photo(admin_chat_id)
#     for i in range(5):
#         notify_admin(str(i))

# # if not running_in_notebook():
# loop = asyncio.get_event_loop()
# # loop.create_task(botson_loop())
# loop.create_task(test_loop())
# log('here')
# # loop.close()


# In[ ]:
