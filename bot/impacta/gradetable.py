from bs4 import BeautifulSoup as bs
from unidecode import unidecode
from requests import request as req
from requests import Session
from requests import codes as requestCodes
import re

from .session import getSession

base_url = 'https://account.impacta.edu.br/'
login_url = base_url + 'account/enter.php'
url_grade_faults = base_url + 'aluno/notas-faltas.php'
url_gradetable = base_url + 'aluno/{}'

def getCode(s):
    courses_grid_page = bs(s.get(url_grade_faults).text, 'html.parser')
    courses_grid = courses_grid_page.find(id='grid-cursos-notas-faltas')
    courses_rows = courses_grid.find_all('tr')
    code_url = False
    for course_row in courses_rows:
        if ('ativa' in unidecode(course_row.text).lower() and
        not 'concluida' in unidecode(course_row.text).lower()):
            code_url = course_row.find(id='btn_visualization').get('href')
            break
    return code_url

def titlesMap(row):
    span = row.find('span')
    if span:
        return span.text
    return row.text

def parseNull(nill):
    if len(nill) == 0 or not nill:
        return '-'
    return nill

def handleDisciplineTd(td):
    absolute_grade = td.find('div', attrs={'class':'td-nota-absoluta'})
    ponderate_grade = td.find('div', attrs={'class':'td-nota-ponderada'})
    if absolute_grade or ponderate_grade:
        abs_grade = parseNull(absolute_grade.text)
        pon_grade = parseNull(ponderate_grade.text)
        return f'{abs_grade} ({pon_grade})'
    return td.text.lstrip()

def disciplineMap(discipline):
    return [
        disc for disc in map(handleDisciplineTd, discipline.find_all('td'))
        ]

disc_row_template = """
{0} {1} - {2} - {3}h
Faltas: {4}
=> MAC: {5}
=> Prova: {6}
=> Substitutiva: {7}
=> PAI: {8}
----------------------------
Média Final: {9} - {10}
\n
===========================
"""

def handleDisciplineRow(disciplineList, titles):
    # 0 = Disciplina    # 1 = Turma
    # 2 = Tipo          # 3 = CH
    # 4 = MAC           # 5 = PR
    # 6 = SUB           # 7 = PAI
    # 8 = BO            # 9 = TF
    # 10 = MF           # 11 = Sit
    d = disciplineList
    t = titles
    return disc_row_template.format(
        d[0], d[1], d[2], d[3],
        d[9],
        d[4],
        d[5],
        d[6],
        d[7],
        d[10], d[11]
    )

def handleTable(s, code_url):
    student_grade_page = bs(
        s.get(url_gradetable.format(code_url)
        ).text, 'html.parser')
    grade_table_full = student_grade_page.find(id='table-boletim')
    grade_table = grade_table_full.find('tbody')
    grade_rows = grade_table.find_all('tr')

    titles = [
        title for title in map(titlesMap, grade_rows[0].find_all('th'))
        ]
    disciplines_rows = [
        dscpln_data for dscpln_data in map(disciplineMap, grade_rows[1:])
        ]
    response = ''.join(
        [handleDisciplineRow(row, titles) for row in disciplines_rows if (len(row) > 5)]
        )
    return response

def getNotes(update, context):
    # Pega os dados do usuário na mensagem
    user = context.args[0]
    passw = context.args[1]

    # Inicia a sessão na impacta
    s, success = getSession(user, passw)

    # Busca o codigo do aluno
    if not success:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text='Sinto muito, algo deu errado... Poderia tentar novamente?'
            )
        return None
    code_url = getCode(s)
    if code_url:
        response = handleTable(s, code_url)
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=response
        )
        return None
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text='Sinto muito, algo deu errado... Poderia tentar novamente?'
    )
    return None