import uuid
from datetime import datetime as dt
import datetime
import time
import requests
from jsonpath_ng.ext import parse
import json
import beepy


def print_center_information(centers_matched,body):
    print(f'{dt.now().strftime("%H:%M:%S")} :List of centers matched :')
    for center in centers_matched:
        data = parse(f'$..centers[?(@.name=="{center.value}")]').find(body)[0].value
        print(f"Center Name: {center.value}  , Block Name: {data['block_name']}  ,  Pin Code: {data['pincode']} ")
        send_message(f"Center Name: {center.value}  , Block Name: {data['block_name']}  ,  Pin Code: {data['pincode']} ")
        for session in data['sessions']:
            print(f"Date: {session['date']} ,  Slots Available: {session['available_capacity']}")


def search_slots_by_district(date_delta, timeout_in_seconds, number_of_times):
    for i in range(number_of_times):
        date_to_search = dt.now() + datetime.timedelta(days=date_delta)
        date_to_search = date_to_search.strftime('%d-%m-%Y')
        u_id = f'{uuid.uuid1()}'
        try:
            #Date format:  09-05-2021
            headers = {'Cache-Control': 'no-cache', 'random-Token': u_id, 'host': 'cdn-api.co-vin.in',
                       'user-agent': 'GenericBrowser/1.1.1'}
            r = requests.get(f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=363&date={date_to_search}',headers=headers)
        except Exception as e:
            print("Could not reach website")
            print(e)
            beepy.beep(sound=3)
            continue

        if r.status_code == 200:
            body = json.loads(r.text)
            centers_matched = parse(
                '$..sessions[?(@.min_age_limit=18 & available_capacity>0)].`parent`.`parent`.name').find(body)
            if len(centers_matched) > 0:
                print(f'!!Slots available at "{len(centers_matched)}" centers')
                print_center_information(centers_matched,body)
                for j in range(10):
                    beepy.beep(sound=6)
                break   # Break out of loop
            else:
                print(
                    f'{date_to_search}: {dt.now().strftime("%H:%M:%S")} :No centers with free slots available for 18+. Rechecking after {timeout_in_seconds / 60} minutes.')
                # beepy.beep(sound=1)
        time.sleep(timeout_in_seconds)


def search_slots_by_pin(pin_codes={'412115': 'Pirangut','411038': 'Kothrud','411027': 'Aundh',},date_delta=0, timeout_in_seconds=10, number_of_times=30):
    for i in range(number_of_times):
        date_to_search = dt.now() + datetime.timedelta(days=date_delta)
        date_to_search = date_to_search.strftime('%d-%m-%Y') # Date format:  09-05-2021
        locations_checked = ' :'
        for pin,loc in pin_codes.items():
            u_id = f'{uuid.uuid1()}'
            try:
                headers = {'Cache-Control': 'no-cache', 'random-Token': u_id, 'host': 'cdn-api.co-vin.in',
                           'user-agent': 'GenericBrowser/1.1.1'}
                r = requests.get(
                    f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pin}&date={date_to_search}',
                    headers=headers)
            except Exception as e:
                print("Could not reach website")
                print(e)
                beepy.beep(sound=3)
                continue

            if r.status_code == 200:
                body = json.loads(r.text)
                centers_matched = parse(
                    '$..sessions[?(@.min_age_limit=18 & available_capacity>0)].`parent`.`parent`.name').find(body)
                if len(centers_matched) > 0:
                    print(f'!!Slots available at {loc} center')
                    print_center_information(centers_matched, body)
                    for j in range(10):
                        beepy.beep(sound=6)
                    break  # Break out of loop
                else:
                    locations_checked = locations_checked +' '+ loc
        print(f'{date_to_search}: {dt.now().strftime("%H:%M:%S")} :No slots available for 18+ at{locations_checked}.')
        print(f'Rechecking after {timeout_in_seconds / 60} minutes.')
        time.sleep(timeout_in_seconds)

def send_message(message):
    token='1623998930:AAFP5sNGYbxHo_69SDS0SM6eniBY6ggpMh8'
    chat_id = -518604433
    r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}')
    print(f'Message Sent: {message}')

p1_pin_codes = {'412115': 'Pirangut',
                    '411038': 'Kothrud',
                    '411027': 'Aundh',
                    '411001': 'Sassoon',
                    '411028':'Magarpatta',
                    '411041': 'Dhayri',
                    '411026':'Bhosari',
                    '411035': 'Akurdi',
                    '411017':'Shastri_Nagar_Pimpri',
                    '411033':'Chinchwad',
                    '411044':'Nigidi'}


if __name__ == '__main__':

    # run for x times where 0.5x = 1 hr
    for i in range(6):
        # Search for tomorrows slots every 5 minutes for the next 0.5 hrs
        beepy.beep(sound=1)
        # search_slots_by_district(0, 30, 60)
        search_slots_by_pin(pin_codes=p1_pin_codes,date_delta=0, timeout_in_seconds=30, number_of_times=60)
        send_message('Cowin Slot alert utility running. Will Alert when free slot is available....')

