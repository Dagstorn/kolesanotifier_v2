import schedule, time, telebot, requests
from bs4 import BeautifulSoup as bs4

# telegram bot initialization
bot = telebot.TeleBot('')
client = ''


# Specification
filters_url = "http://127.0.0.1:8000/kolesafilters/"
update_lc_url = "http://127.0.0.1:8000/updatelastcar/"

car_page_url = "https://kolesa.kz/a/show/"
price_url = "https://kolesa.kz/a/average-price/"
num_of_views_url = "https://kolesa.kz/ms/views/kolesa/live/"

cars_url = "http://127.0.0.1:8000/cars/"
add_car_url = "http://127.0.0.1:8000/addcar/"



def add_car(key, filter_key):
    print('adding car to database...')
    s = requests.Session()
    r_lc = s.get(add_car_url + filter_key + '/')
    lchtml = bs4(r_lc.content, 'html.parser')
    csrf = lchtml.select('input[name=csrfmiddlewaretoken]')[0]['value']
    payload = {
        'csrfmiddlewaretoken': csrf,
        'key': key,
    }
    s.post(add_car_url + filter_key + '/', data=payload)
    print('------------- car added successfully ------------')



def send_message(car_key, title, diffInPercents, num_of_views, c_f_title, filter_key):
    print(diffInPercents)
    print('sending message to client')
    car_url = car_page_url + car_key + '/'
    mes = 'По фильтру: ' + c_f_title + '\n' + title + '\n' + 'Дешевле на ' + str(diffInPercents) + '%, просмотрено ' + str(num_of_views) + ' раз' + '\n' + car_url
    bot.send_message(client, mes)
    
    print('updating database...')
    s = requests.Session()
    r_lc = s.get(update_lc_url)
    lchtml = bs4(r_lc.content, 'html.parser')
    csrf = lchtml.select('input[name=csrfmiddlewaretoken]')[0]['value']
    payload = {
        'csrfmiddlewaretoken': csrf,
        'lcid': car_key,
        'fid': filter_key
    }
    s.post(update_lc_url, data=payload)
    print('------------- database updated successfully ------------')


def process_car(cars, el, cf_viewcount, cf_perc, c_f_title, filter_key):
    uri = "https://kolesa.kz" + str(el.select('.a-card__link')[0]['href'])
    title = el.select('.a-card__link')[0].text.strip()
    car_key = uri.split('/')[-1]
    print(f"Pocessing car {title}")
    print(f"{car_key}")

    if car_key in cars:
        return

    print('new car')
    print('getting views number...')
    views_url = num_of_views_url + car_key + '/'

    r = requests.get(views_url)
    try:
        json_data = r.json()
    except:
        json_data = None
        return
    
    num_of_views = json_data['data'][car_key]['nb_views']
    num_of_views_phone = json_data['data'][car_key]['nb_phone_views']
    num_of_views = num_of_views + num_of_views_phone
    print(f'views number = {num_of_views}')

    if num_of_views < cf_viewcount:
        print('getting cheap percentage...')
        car_price_url = price_url + car_key + '/'
        r = requests.get(car_price_url)
        try:
            price_data = r.json()
        except:
            price_data = None
        
        if price_data and price_data["type"] == "success":
            print('got price data!')
            diffInPercents = price_data['data']["diffInPercents"]
            print(f'diffInPercents = {diffInPercents}%')

            if diffInPercents < 0 and float(diffInPercents) <= float(cf_perc):
                diffInPercents = abs(diffInPercents)
                print(f'cheaper = {diffInPercents}%')
    
                send_message(car_key, title, diffInPercents, num_of_views, c_f_title, filter_key)
                add_car(car_key, filter_key)



def process_filter(filters_json_data, filter_key):
    cars_r = requests.get(cars_url + filter_key + '/')
    try:
        cars = cars_r.json()
    except:
        cars = []



    print(f"processing filter #{filter_key}")
    current_filter_url = filters_json_data[filter_key]['url']
    c_f_title = filters_json_data[filter_key]['title']
    cf_perc = filters_json_data[filter_key]['cheap_perc']
    cf_viewcount = filters_json_data[filter_key]['view_count']

    print('CURRENT FILTER ===========')
    print(c_f_title)
    print(current_filter_url)
    print(cf_perc)
    print(cf_viewcount)
    print(f"saved cars: {cars}")

    r = requests.get(current_filter_url)
    print("got r")
    html = bs4(r.content, 'html.parser')
    print("got html")
    data = html.select('.a-card__info')
    print("got data")

    if data:
        print('filters page approached')
        for el in data:
            process_car(cars, el, cf_viewcount, cf_perc, c_f_title, filter_key)

        
def job():
    print('getting filters from website...')
    filters_r = requests.get(filters_url)

    try:
        filters_json_data = filters_r.json()
    except:
        filters_json_data = None

    if filters_json_data:
        print(f'{len(filters_json_data)} filters received successfully!')
        for filter_key in filters_json_data:
            process_filter(filters_json_data, filter_key)
    else:
        print('cant get filters')
    print('waiting.......')

print('Starting bot...')
schedule.every(10).seconds.do(job)
print('** tasks scheduled **')
while True:
    schedule.run_pending()
    time.sleep(1)