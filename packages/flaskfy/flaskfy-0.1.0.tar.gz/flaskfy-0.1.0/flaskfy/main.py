import os
import pymysql
import shutil

VERSION = "0.0.1"
DESCRIPTION = "A lib to manage your flask projects"

def criar_projeto_flask(nome_projeto):
    os.makedirs(nome_projeto)
    
    # Cria os arquivos dentro da pasta do projeto
    with open(os.path.join(nome_projeto, 'README.md'), 'w') as f:
        f.write("# Meu Projeto Flask\n\nEste é um projeto Flask básico.")
    
    with open(os.path.join(nome_projeto, '.gitignore'), 'w') as f:
        f.write("# Arquivos e pastas a serem ignorados pelo Git")
    
    with open(os.path.join(nome_projeto, 'main.py'), 'w') as f:
        f.write('''
from flask import Flask, render_template
from models import model

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
''')
        

        
    os.makedirs(os.path.join(nome_projeto, 'static'))
    with open(os.path.join(nome_projeto, 'static', 'styles.css'), 'w') as f:
        f.write('''





/* styles.css */

*{
    padding: 0;
    margin: 0;
    box-sizing: border-box;
}


nav{
    width: 100%;
    height: 50px;
    background-color: #001721;
    justify-content: space-around;
    display: flex;
    align-items: center;
    position: fixed;
    top: 0;
}


h1 {
    color: skyblue;
    font-weight: 600;
}

nav ul{
    display: flex;
}

nav ul li{
    padding: 10px 10px;
    list-style: none;
}
nav ul li a{
    padding: 10px 20px;
    list-style: none;
    text-decoration: none;
    color: #fff;
}

body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    align-items: center;
    display: flex;
    justify-content: center;
    width: 100%;
    height: 100vh;
}

main{
    align-items: center;
    display: flex;
    justify-content: center;
    flex-direction: column;
}

main span{
    padding-top: 10px;
    color: #ccc;
}


main span .release{
    color: orange;
}


button{
    width: 150px;
    height: 40px;
    background-color: skyblue;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
}


''')
   
    

    os.makedirs(os.path.join(nome_projeto, 'templates'))
    with open(os.path.join(nome_projeto, 'templates', 'index.html'), 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Index</title>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles.css') }}">
    <nav>
        <h1>Flask</h1>
        <ul>
            <li><a href="/#">Home</a></li>
            <li><a href="/#">Flaskfy</a></li>
            <li><a href="/#">About</a></li>
        </ul>
    </nav>
</head>

<body>
        <main>
            <h2>The installation worked succesfully! Congratilations</h2>
            <span>This page was genereted using flaskfy | <span class="release">release 0.0.1</span></span>
            <span>Flaskfy simplifies your project</span>
            <br>
            <br>
            <button>WELCOME</button>
        </main>
</body>

</html>
''')
    # Cria a pasta dos models
    models_path = os.path.join(nome_projeto, 'models')
    os.makedirs(models_path)
    
    # Cria o arquivo '__init__.py' dentro da pasta 'models'
    with open(os.path.join(models_path, '__init__.py'), 'w') as f:
        f.write('')
    
    # Cria o arquivo 'model.py' dentro da pasta 'models' com o código para conexão ao MySQL e criação da tabela
    with open(os.path.join(models_path, 'model.py'), 'w') as f:
        f.write('''
import pymysql

def database_conection():
    try:
        conn = pymysql.connect(
        host='localhost',
        user='user',
        password='password',
        database='database'
        )
        conn.close()
        return True
    except pymysql.Error:
        return False

def table_user():
    if database_conection():
        conn = pymysql.connect(
        host='localhost',
        user='user',
        password='password',
        database='database'
        )

        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            number VARCHAR(20)
        )
        """

        cursor.execute(create_table_query)

        cursor.close()
        conn.close()
    else:
        print("App not connected to database")

table_user()
''')
    
    print(f"Projeto '{nome_projeto}' criado com sucesso!")
