print('\nhi there, I\'m Crew Portal script, tell me what could I do for you?\n')
print("to load list of portal users enter 'u'\n"
      "to load list of Aeroflot flights enter 'f'\n"
      "to load detailed info for flight or load flights with filters in console enter 'i'\n"
      "to exit enter 'e'\n")
handler = ''

while handler not in ('u', 'f', 'i','e'):
    handler = input()
    if handler=='u':
        import CrPort_users
    if handler=='f':
        import CrPort_flights
    if handler=='i':
        import CrPort_flight_inf
    if handler=='e':
        break

print('\nthat\'s all, bye-bye')