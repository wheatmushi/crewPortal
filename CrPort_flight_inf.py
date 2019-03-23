import json
from time import localtime, strftime
import tools
import os

def url_former(flight_info):
    flight_info[1] = flight_info[1].upper()
    return 'https://su-ati.crewplatform.aero/CrewServices/flightData/SU/{}/{}/{}?filter=noforms+noseatmap+noweather'.\
           format(*flight_info)


def crew_filter(crew):
    return [crew['position'],crew['name'],crew['staffId'],crew['phone']]


def passenger_filter(pas):
    ssrCode = []
    if pas['auxInfo'] and pas['auxInfo']['specialServiceRequestList']:
        path = pas['auxInfo']['specialServiceRequestList']
        for k in path:
            ssrCode.append(k['ssrcode'])
    ssrCode = ','.join(ssrCode)
    output = [pas['firstName'],pas['lastName'],pas['idPassenger'],ssrCode,pas['loyalty'],\
              pas['bookingClass'],pas['bookingReference'],pas['cabin'],pas['seat'],pas['checkedIn'],pas['boarded']]
    output = [i if type(i) == str else '' for i in output]
    return output


def inf_writer(inf,csv_file):
    titles = ['departureAirport','arrivalAirport','capacity','booked','boardedCount','checkedInCount','load']
    times = ['flightStatus', 'depScheduled', 'arrScheduled', 'depEstimated', 'depActual',\
             'arrEstimated', 'arrActual']
    csv_file.write(';'.join(times) + '\n')
    for t in times:
        csv_file.write(str(inf[t])+';')
    csv_file.write('\n\n')
    for position in titles:
        csv_file.write(position+'\n')
        keys = sorted(list(inf[position].keys()))
        csv_file.write(';'.join(keys)+'\n')
        for k in keys:
            csv_file.write(str(inf[position][k])+';')
        csv_file.write('\n\n')


def flight_loader(params,session):
    print('\nloading detailed flight info...')
    url = url_former(params)
    flight = session.get(url)
    flight = json.loads(flight.content)
    return flight


def show_flights(flights):
    title = ['airline','flight Nb','Dep.Airport','Arr.Airport','Scheduled departure date/time','Last update date/time']
    form = '{0:>8}{1:>11}{2:>13}{3:>13}{4:>34}{5:>25}'
    print(form.format(*title))
    for f in flights:
        print (form.format(*f))


def print_flight_to_csv(flight,num):
    print('\nextracting detailed flight info...')
    inf = flight['flight']
    passengers = flight['passengers']
    crews = flight['crewList']

    crews = [crew_filter(crew) for crew in crews]
    passengers = [passenger_filter(pas) for pas in passengers]

    csv_file = open(os.path.join('response','FlightInfo su'+num+'  '+strftime("%Y-%b-%d  %H-%M-%S", localtime())+'.csv'),'w')

    inf_writer(inf,csv_file)
    csv_file.write('\n\n'+'position; name; crew; staffId; phone' + '\n')

    for crew in crews:
        csv_file.write(';'.join(crew)+'\n')

    csv_file.write('\n\n'+'firstName; lastName; idPassenger; ssrCode; loyalty; bookingClass; \
                    bookingReference; cabin; seat; checkedIn; boarded'+'\n')

    for passenger in passengers:
        csv_file.write(';'.join(passenger)+'\n')

    csv_file.close()
    print('\ninfo extracted successfully')


def flights_handler(session, params=[], flights=[]):
    if not params:
        new_params = params_req()
        if new_params==['e']:
            return 0
        flights_handler(session, params=new_params)
    elif params[0] in ('arr','dep','fl'):
        if not flights:
            flights = tools.flights_scrabbler(session)
        flights_filtered = flights
        if len(params)==3 and len(params[2])==10:
            flights_filtered = [f for f in flights_filtered if f[4][:10] == params[2]]
        if params[0] == 'arr':
            flights_filtered = [f for f in flights_filtered if f[3] == params[1].upper()]
        elif params[0] == 'dep':
            flights_filtered = [f for f in flights_filtered if f[2] == params[1].upper()]
        elif params[0] == 'fl':
            flights_filtered = [f for f in flights_filtered if f[1] == params[1]]
        show_flights(flights_filtered)
        new_params = params_req()
        if new_params==['e']:
            return 0
        flights_handler(session, params=new_params, flights=flights)
    else:
        flight = flight_loader(params, session)
        print_flight_to_csv(flight, num=params[0])
        new_params = params_req()
        if new_params==['e']:
            return 0
        flights_handler(session, params=new_params, flights=flights)

def params_req():
    params = input("\nto extract particular flight info in .csv enter\n"
                   "   full flight parameters: flight Nb, dep. airport and date as '0106,svo,2017-09-27' \n"
                   "to show filtered flights in console enter\n"
                   "   whether dep/arr airport (with or without date) as 'arr,muc' or 'dep,led,2017-09-28'\n"
                   "   or flight Nb (with or without date) as 'fl,0011' or 'fl,1321,2017-10-05'\n"
                   "to exit script enter 'e'\n").split(',')
    return params


session = tools.authentication()
flights_handler(session)
session.close()