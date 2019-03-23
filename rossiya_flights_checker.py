import requests
import json
import getpass
import re
import json
from time import localtime, strftime, time
import tools
import os

# authentication func
email_RE = '[^@]+@[^@]+\.[^@]+'
url_general = 'https://services-fv.crewplatform.aero/'

def authentication():
    login = ''
    password = ''
    print('\nopening session...')

    if not re.match(email_RE, login):
        login = login + '@sita.aero'

    url_login = url_general + 'j_spring_security_check'
    url_admin = url_general + 'CrewServices/adminConsole/adminData'

    ssl = 'certs_rossiya.pem'

    headers = {'j_username': login, 'j_password': password}

    session = requests.Session()
    p = session.post(url_login, headers, verify=ssl)

    if 'login_error=1' in p.url:
        print('\nincorrect login or password, try again!')
        return authentication()

    session.cookies.update({'username': login})

    admin = session.get(url_admin)
    admin = json.loads(admin.content)
    key = admin['airlines'][0]['key']

    session.headers.update({'X-apiKey': key})
    print('\nsession loaded successfully')
    return session

def flights_scrabbler(session):
    print('\nflights scrabbling in progress... (this may take a while)')
    url_flights = url_general + 'CrewServices/flightList/SU'
    flights = session.get(url_flights)
    flights = json.loads(flights.content)['crewFlights']
    print('\nflights loaded')
    return [tools.flight_info_filter(flight) for flight in flights]

'0106,svo,2017-09-27'
def url_former(flight_info):
    flight_info[1] = flight_info[1].upper()
    return url_general + 'CrewServices/flightData/SU/{}/{}/{}?filter=noforms+noseatmap+noweather'.format(*flight_info)

def flight_loader(params,session):
    url = url_former(params)
    flight = session.get(url)
    flight = json.loads(flight.content)
    return flight

t = time()
session = authentication()

flights = flights_scrabbler(session)

for i in flights:
    params = [i[1],i[2],i[4][:10]]
    fl = flight_loader(params,session)
    crews = len(fl['crewList'])
    i.append(str(crews))
    if crews < 4:
        print(i)


flights_str = [(';'.join(flight) + '\n') for flight in flights]

datetime = strftime("%Y-%b-%d  %H-%M-%S", localtime())
params = ['Airline','Flight number','Departure airport','Arrival airport','Scheduled departure','Last update','Num. of crews']

table = open(os.path.join('response','Flights '+datetime+'.csv'), 'w', newline='')
table.write(';'.join(params)+'\n')
for line in flights_str:
    table.write(line)
table.close()

print('completed in ' + str(time() - t) + 's')
