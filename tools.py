import requests
import json
import getpass
import re

# authentication func
email_RE = '[^@]+@[^@]+\.[^@]+'

def authentication():
    login = input('\nenter your login as "firstname.lastname" (with or without domain)\n')
    password = getpass.getpass('\nenter your password\n')
    print('\nopening session...')

    if not re.match(email_RE, login):
        login = login + '@sita.aero'

    url_login = 'https://su-ati.crewplatform.aero/j_spring_security_check'
    url_admin = 'https://su-ati.crewplatform.aero/CrewServices/adminConsole/adminData'

    ssl = 'certs.pem'

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

# flights extraction funcs

def flight_info_filter(f):
    return [f['airline'],f['flightNumber'],f['depAirport'],f['arrAirport'],\
            f['scheduledDepDateTime'].replace('T', '  '),\
            f['lastUpdate'][:-5].replace('T', '  ')]


def flights_scrabbler(session):
    print('\nflights scrabbling in progress... (this may take a while)')
    url_flights = 'https://su-ati.crewplatform.aero/CrewServices/flightList/SU'
    flights = session.get(url_flights)
    flights = json.loads(flights.content)['crewFlights']
    print('\nflights loaded')
    return [flight_info_filter(flight) for flight in flights]


# user extraction funcs

def get_roles(username, session):
    url = 'https://su-ati.crewplatform.aero/CrewServices/crewManager/getRoles/SU/' + str(username)
    r = session.get(url)
    roles = json.loads(r.content)
    roles = ', '.join(roles['roles'])
    return roles


def flatten_users(user):
    keys = list(user.keys())
    for k in keys:
        if type(user[k]) == dict:
            user.update(user[k])
            del user[k]
    return user


def extract_all_keys(users):
    all_keys = []
    for user in users:
        all_keys += list(user.keys())
    main_keys = ['firstName', 'lastName', 'staffId', 'email', 'phone',\
                 'username', 'position', 'description', 'lastUpdate', 'airline', 'password']
    return main_keys + sorted(list(set(main_keys).symmetric_difference(set(all_keys))))


def dict_to_str(user,all_keys):
    user_string = ''
    for key in all_keys:
        if key in user.keys():
            user_string += str(user[key]) + ';'
        else:
            user_string += ' ' + ';'
    return user_string+'\n'