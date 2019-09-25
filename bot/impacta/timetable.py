from bs4 import BeautifulSoup as bs
from requests import request as req
from requests import Session
import re

base_url = "https://account.impacta.edu.br/"
login_url = base_url + "account/enter.php"
url_timetable_aula = base_url + "aluno/horario-aula.php"
url_timetable = base_url + "aluno/quadro-horario.php?turmaid={}&produto={}"
login_body = {
    'desidentificacao': IMPACTA_USER,
    'dessenha': IMPACTA_PASS
}

def getSession():
    session = Session()
    session.post(login_url, data=login_body)
    return session

def treatRoom(room):
    split = room.split(';')
    return f'{split[0]} ({split[1]})  '

def getDisciplinesByDay(disciplinesElements, title):
    parsedWeekday = disciplinesElements \
    .replace(';', '') \
    .replace('\n', '') \
    .replace(' :', ':') \
    .replace(': ', ':') \
    .replace('Aula', '#DIV##;Aula') \
    .replace('Disciplina', ';Disciplina') \
    .replace('Prof', ';Prof') \
    .replace('Sala', ';Sala') \
    .split('#DIV##')
    dayData = [x[1:].split(';') for x in parsedWeekday[1:]]
    disciplines = dict()
    for _classRow in dayData:
        _class = _classRow[0].split('[')[0].lstrip()
        discipline = _classRow[1].split(':')[1]
        teacher = _classRow[2].split(':')[1]
        room = _classRow[3].split(':')[1]
        if discipline not in disciplines.keys():
            disciplines[discipline] = {
                'teacher': teacher,
                'rooms': [f'{room};{_class}']
            }
        else:
            if room not in [room.split(';')[0] for room in disciplines[discipline]['rooms']]:
                disciplines[discipline]['rooms'].append(f'{room};{_class}')
    response = []
    for discipline, content in disciplines.items():
        if len(content['rooms']) == 1:
            roomString = content['rooms'][0].split(';')[0]
        else:
            roomString = ''.join(treatRoom(room) for room in content['rooms'])
        response.append(f'''
                        => {title}
                        => {discipline}
                        => {content['teacher']}
                        => {roomString}
                        ========================\n
                        ''')
    return response
    
def filterDisciplinesArray(disciplinesArray):
    for data in disciplinesArray:
        return None

def getFullTimetable(bot, update):
    s = getSession()
    classes_timetable_page = bs(s.get(url_timetable_aula).text, 'html.parser')
    ids_el = classes_timetable_page.find(attrs={'data-turmaid':True})
    class_id = ids_el.get('data-turmaid')
    product_id = ids_el.get('data-produto')

    class_timetable_page = bs(s.get(url_timetable.format(class_id, product_id)).text, 'html.parser')
    timetable_wrapper = class_timetable_page.find('div', attrs={"class": "accordion"})
    days_of_week = timetable_wrapper.find_all('div', attrs={"class":"dia-semana"})

    fullResponse = []
    for weekday in days_of_week:
        title = weekday.find('h2').text
        weekday.h2.extract()
        dayData = getDisciplinesByDay(weekday.text, title)        
        fullResponse.append(dayData)
    bot.send_message(
        chat_id=update.message.chat.id,
        text=''.join(''.join(day) for day in fullResponse)
        )