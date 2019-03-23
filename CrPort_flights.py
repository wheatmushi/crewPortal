from time import localtime, strftime
import tools
import os


session = tools.authentication()

flights = tools.flights_scrabbler(session)
session.close()
print('\nextracting flights in file...')
flights_str = [(';'.join(flight) + '\n') for flight in flights]

datetime = strftime("%Y-%b-%d  %H-%M-%S", localtime())
params = ['Airline','Flight number','Departure airport','Arrival airport','Scheduled departure','Last update']

table = open(os.path.join('response','Flights '+datetime+'.csv'), 'w', newline='')
table.write(';'.join(params)+'\n')
for line in flights_str:
    table.write(line)
table.close()

print('\nflights extraction finished normally')