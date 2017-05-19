import vk
import time
import re

token = ''
session = vk.Session(access_token = token)
api = vk.API(session)
 
 
fLink = input('Ссылка на пост: ')
res = re.search(r'-\d*_\d*', fLink)
link = res.group(0)
ownerId, wallId = link.split('_')

# Если впереди стоит минус, то это паблос, для использования нам нужна переменная с минусом (ownerId) и без (groupId)
if ownerId[0] == '-':
	groupId = ownerId[1:]
 
# Забираем ID опроса 
wall = api.wall.getById(posts = link, v = 5.64)
attachments = wall[0]['attachments']
for attachment in attachments:
	if attachment['type'] == 'poll':
		pollId = attachment['poll']['id']
		members = attachment['poll']['answers'] # участники опроса

dataOfPolls = api.polls.getById(owner_id = ownerId, poll_id = pollId, v = 5.64)
question = dataOfPolls['question']
answers = []
for answer in dataOfPolls['answers']:
	answers.append(answer['text'])


# Создаем массив подписоты
offset = 0
usersOfGroup = []
print('Обрабатываем подписчиков: ')
while True:
	res = api.groups.getMembers(group_id = groupId, offset = offset, v = 5.64)
	usersOfGroup.extend(res['items'])
	if offset % 10000 == 0:
		print(len(usersOfGroup))
	offset += 1000
	time.sleep(0.4)
	if res['count'] == len(usersOfGroup):
		break
print(len(usersOfGroup))

# Создаем массив участников (id)
memberIds = []
for member in members:
	memberIds.append(member['id'])
membersCount = len(memberIds)

answerIds = ','.join(map(str, memberIds))

# Создаем массив проголосовавших
votersIds = [[] for i in range(membersCount)]
isEmpty = False
offset = 0
while not isEmpty:
	voters = api.polls.getVoters(owner_id = ownerId, poll_id = pollId, count = 1000, offset = offset, answer_ids = answerIds, v = 5.64)
	empty = 0
	for i in range(membersCount):
		if len(voters[i]['users']['items']) == 0:
			empty += 1
		else:
			votersIds[i].extend(voters[i]['users']['items'])
	if empty == membersCount:
 		isEmpty = True
	offset += 1000
	time.sleep(0.4)

print(question)
print('--------------------------------')
for i in range(membersCount):
	print('{0}. {1}'.format(i+1, answers[i]))
	print('Количество проголосовавших - ', len(votersIds[i]))
	tmp = 0
	for voter in votersIds[i]:
		if voter in usersOfGroup:
			tmp += 1
	print('Из них состоят в группе - ', tmp)
	print('--------------------------------')
