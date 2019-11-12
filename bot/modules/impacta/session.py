from requests import Session
base_url = "https://account.impacta.edu.br/"
login_url = base_url + "account/enter.php"

def getSession(user, passw):
    session = Session()
    login_body = {
        'desidentificacao': user,
        'dessenha': passw
    }
    response = session.post(login_url, data=login_body)
    return session, response.json().get('success')