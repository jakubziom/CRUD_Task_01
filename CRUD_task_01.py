from datetime import date
import sqlite3
from sqlite3 import Error

#funkcja nawiązująca połączenie z plikiem bazy danych
def create_connection(db_file):
    conn=None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Połączono z bazą danych {db_file}")
    except Error as e:
        print(e)    
    return conn

#funkcja wykonująca skrypt sql dla tworzenia tabel
def execute_sql(conn,sql):
    try:
        c=conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

#tworzenie pliku z bazą danych
if __name__ == '__main__':
    create_connection(r"emails.db")

#tworzenie tabeli accounts
create_accounts_sql = '''
CREATE TABLE IF NOT EXISTS accounts (
    id integer PRIMARY KEY,
    email text NOT NULL,
    password text NOT NULL,
    birthDate text NOT NULL,
    dateCreated text NOT NULL
);
'''

#tworzenie tabeli z imionami i nazwiskami
create_additionalData_sql = '''
CREATE TABLE IF NOT EXISTS additionalData (
    id integer PRIMARY KEY,
    additionalData_id integer NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    FOREIGN KEY (additionalData_id) REFERENCES accounts (id)
);
'''

#nazwa pliku z bazą danych
db_file="emails.db"


conn = create_connection(db_file)
if conn is not None:
    #tworzenie tabeli accounts
    execute_sql(conn, create_accounts_sql)
    print('Utworzono tabelę na dane kont')
    #tworzenie tabeli z imionami i nazwiskami
    execute_sql(conn, create_additionalData_sql)
    print('Utworzono tabelę na dane dodatkowe')
    conn.close

print('-----------------------------')
print("Skrzynka e-mail w serwisie CRUD.pl")
print('-----------------------------')

#wprowadzanie informacji przez użytkownika
while True:
    while True:
        try:
            selection=int(input('1-Zakładanie Konta, 2-Logowanie, 3-Zmiana Hasła, 4-Usuwanie Konta'))
            if 5 > selection > 0:
                break
            else:
                print("Proszę podać cyfrę od 1 do 4")
                continue     
        except:
            print("Proszę podać cyfrę")
            continue

    if selection==1:
        email=str(input('Proszę utworzyć login e-maila np. "jan" = jan@CRUD.pl'))  + str('@CRUD.pl')
        name=str(input('Proszę podać imię'))
        surname=str(input('Proszę podać nazwisko'))
        birthDate=str(input('Proszę podać datę urodzenia'))
        while True:
            password=str(input('Proszę utworzyć hasło'))
            password2=str(input('Proszę potwierdzić hasło'))
            if password==password2:
                break
            else:
                print('hasła się nie zgadzają')
                continue
        dateCreated=date.today()

        #dodawanie wcześniej wprowadzonych danych do tabeli accounts
        def add_accountData(conn,account):
            sql= '''INSERT INTO accounts(email, password, birthDate, dateCreated)
                VALUES (?,?,?,?);'''
            cur = conn.cursor()
            cur.execute(sql,account)
            conn.commit()
            return cur.lastrowid

        #dodawanie wcześniej wprowadzonych danych do tabeli z imionami i nazwiskami
        def add_additionalData(conn,additionalData):
            sql= '''INSERT INTO additionalData(additionalData_id, name, surname)
                VALUES (?,?,?);'''
            cur = conn.cursor()
            cur.execute(sql,additionalData)
            conn.commit()
            return cur.lastrowid

        conn = create_connection("emails.db")
        #krotka z danymi do wprowadzenia do tabeli accounts
        account=(email,password, birthDate, dateCreated)
        pr_id = add_accountData(conn,account)

        conn = create_connection("emails.db")
        #krotka z imionami i nazwiskami
        additionalData=(1,name,surname)
        pr_id = add_additionalData(conn,additionalData)

        conn = create_connection(db_file)
        if conn is not None:
            #inny rodzaj zapisu do wykonywania skryptu *zrobione funkcją execute_sql
            execute_sql(conn, str(account))
            execute_sql(conn, str(additionalData))
            conn.close
        
        print(f'Utworzono nowe konto e-mail: {email}')

    def loginCode():
        while True:
            #wprowadzenie loginu
            login=str(input('Proszę podać login np. "jan" dla adresu jan@CRUD.pl')) + str('@CRUD.pl')
            #szukanie pozycji na której jest login w bazie danych (w tabeli accounts)
            conn = create_connection("emails.db")
            cur= conn.cursor()
            cur.execute(f"SELECT * FROM accounts WHERE email = '{login}'")
            try:
                #wyciąganie wartości liczbowej pozycji na której jest login 
                findLogin=cur.fetchone()[0]
                break
            except:
                #jeśli nie znaleziono podanego loginu w bazie danych
                findLogin='NotFind'
                print('Nie znaleziono takiego loginu!')
                continue

        while True:
            #jeśli znaleziono login program prosi o hasło
            if findLogin is not 'NotFind':
                print(f'Znaleziono login {login} na pozycji {findLogin}')
                print(f'Proszę podać hasło dla adresu {login}:')
                passwordCheck=str(input())
                conn = create_connection("emails.db")
                cur= conn.cursor()
                cur.execute(f"SELECT * FROM accounts WHERE password = '{passwordCheck}'")
                try:
                    passwordMatch=cur.fetchone()[0]
                    break
                except:
                    passwordMatch='NotFind'
                    print('Błędne hasło, proszę spróbować ponownie!')
                    continue
        if findLogin == passwordMatch:
            print(f'Zalogowano poprawnie do adresu {login}!')
        else: 
            print('Błędne hasło, proszę spróbować ponownie!')

        return login,passwordMatch,findLogin


    if selection==2:
        loginCode()

    if selection==3:
        accountData=loginCode()
        passwordMatch=accountData[1]
        login=accountData[0]
        findLogin=accountData[2]

        while True:
            if findLogin == passwordMatch:
                newPassword=str(input(f'Proszę podać nowe hasło dla {login}!'))
                newPassword2=str(input(f'Proszę powtórzyć nowe hasło dla {login}!')) 
                if newPassword==newPassword2:
                    conn = create_connection("emails.db")
                    cur= conn.cursor()
                    cur.execute(f''' UPDATE accounts 
                        SET password = "{newPassword}"
                        WHERE id = "{passwordMatch}"''')
                    conn.commit()
                    print(f'Hasło dla {login} zostało zmienione')
                    break
                else:
                    print('Hasła się nie zgadzają!')
                    continue
            else:
                break

    if selection==4:
        accountData=loginCode()
        passwordMatch=accountData[1]
        login=accountData[0]
        findLogin=accountData[2]

        while True:
            if findLogin == passwordMatch:
                accountDelete=str(input(f'Jeśli na pewno chcesz usunąć konto {login}?, wpisz Tak'))
                if accountDelete=='Tak':
                    conn = create_connection("emails.db")
                    cur= conn.cursor()
                    cur.execute(f"DELETE FROM accounts WHERE id = '{passwordMatch}'")
                    cur.execute(f"DELETE FROM additionalData WHERE id ='{passwordMatch}'")
                    conn.commit()    
                    print(f'Usunięto konto {login}')
                    break
                else:
                    break
            else:
                break




            



                   
           

    




