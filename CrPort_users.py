import json
from time import localtime, strftime
import tools
import os


url_users_50 = 'https://su-ati.crewplatform.aero/CrewServices/crewManager/v1/SU/1/50'


session = tools.authentication()
print('\nloading users...')

users_counter = session.get(url_users_50)
users_counter = json.loads(users_counter.content)
users_counter = users_counter['numberOfUsers']

users = session.get(url_users_50[:-2] + str(users_counter))
users = json.loads(users.content)
users = users['airlineUsers']

handler = ''
while handler not in ('roles','n'):
    handler = input("\nto load users administrative roles for CrewPortal enter 'roles' (this may take about 5 additional minutes)\n"
                    "enter 'n' to extract only default parameters\n")


datetime = strftime("%Y-%b-%d  %H-%M-%S", localtime())
filename = 'Users ' + datetime + '.csv'

if handler == 'roles':
    print('\nloading users roles...')
    for u in users:
        u['CrewPortal Roles'] = tools.get_roles(u['username'], session)
    filename = 'Users ROLES ' + datetime + '.csv'

session.close()

print('\nusers extraction in progress...')
users = [tools.flatten_users(user) for user in users]
all_keys = tools.extract_all_keys(users)
users = [tools.dict_to_str(user,all_keys) for user in users]


table = open(os.path.join('response', filename), 'w')
table.write(';'.join(all_keys)+'\n')
for line in users:
    table.write(line)
table.close()

print('\nusers extraction finished normally')