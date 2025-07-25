import sqlite3 as sqlite
import google.generativeai as genai
import os
import pandas as pd
import numpy as np
import time as t
from fpdf import FPDF
import inquirer as inq
import colorama as color
import subprocess
from tkinter import filedialog
import unicodedata
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyfiglet
import requests
import PyPDF2
sql = sqlite.connect('data.db')
cursor = sql.cursor()
color.init()

def procurauser():
    cursor.execute('SELECT COUNT(*) FROM users')
    n = cursor.fetchone()[0]

    if n == 0:
        print(color.Fore.RED + '* Nenhum usuário cadastrado, adicionar?')
        q = [
            inq.List(
                'OP',
                message='Adicionar usuário?',
                choices=['Sim', 'Não'],
            )
        ]
        resposta = inq.prompt(q)
        if resposta['OP'] == 'Sim':
            cadastro()
        else:
            print(color.Fore.RED + '* Fechando programa...')
            t.sleep(3)
            exit()
    else:
        cursor.execute('SELECT user FROM users')
        nomes = cursor.fetchall()

        lista_usuarios = [nome[0] for nome in nomes]
        lista_usuarios.append('Sair')
        lista_usuarios.append('Cadastrar')

        print(color.Fore.GREEN + '* Usuário encontrado, escolha seu usuário:')

        q3 = [
            inq.List(
                'usuario_selecionado',
                message='Escolha seu user:',
                choices=lista_usuarios
            )
        ]

        resposta_usuario = inq.prompt(q3)

        if resposta_usuario['usuario_selecionado'] == 'Cadastrar':
            cadastro()
        elif resposta_usuario['usuario_selecionado'] == 'Sair':
            print(color.Fore.RED + '* Fechando programa...')
            t.sleep(3)
            exit()

        global user
        user = resposta_usuario['usuario_selecionado']
        global APIKEY
        APIKEY = cursor.execute('SELECT apikey FROM users WHERE user = ?', (user,)).fetchone()[0]
        HOME()

def cadastro():
    print(color.Fore.GREEN + '* Insira o nome do usuário:')
    user = input('>_')

    print(color.Fore.GREEN + '* Insira sua senha:')
    senha = input('>_').encode('utf-8')

    print(color.Fore.GREEN + '* Insira sua API key:')
    APIKEY_raw = input('>_')

    print(color.Fore.GREEN + '* Insira o email:')
    email = input('>_')

    print(color.Fore.GREEN + '* Insira sua senha de app:')
    print(color.Fore.YELLOW + '*Caso não tenha, crie uma em: https://myaccount.google.com/apppasswords')
    app_password = input('>_')

    senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt())

    query = '''
    INSERT INTO users (user, senha, apikey, email, app_pass)
    VALUES (?, ?, ?, ?, ?)
    '''

    cursor.execute(query, (user, senha_hash.decode('utf-8'), APIKEY_raw, email, app_password))
    sql.commit()

    print(color.Fore.GREEN + '* Usuário cadastrado com sucesso!')
    t.sleep(3)
    procurauser()

def HOME():
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
    print('''
░██████╗░█████╗░░█████╗░░█████╗░██╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██║
╚█████╗░███████║██║░░╚═╝███████║██║
░╚═══██╗██╔══██║██║░░██╗██╔══██║██║
██████╔╝██║░░██║╚█████╔╝██║░░██║██║
╚═════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝
''' + color.Fore.MAGENTA)
    print('* Bem-vindo ao SacAI. Escolha uma opção:')
    q4 = [
        inq.List(
            'OP',
            message='Bem vindo ao SacAI. Escolha uma opção:',
            choices=['Gerar texto', 'Gerar documento', 'Responder clientes', 'Resumir PDFs', 'enviar E-mail', 'HTTP', 'Sair']
        )
    ]
    rp = inq.prompt(q4)
    if rp['OP'] == 'Gerar texto':
        gerar_texto()
    elif rp['OP'] == 'Gerar documento':
        gerar_documento()
    elif rp['OP'] == 'Responder clientes':
        responder_clientes()
    elif rp['OP'] == 'Resumir PDFs':
        resumir_pdfs()
    elif rp['OP'] == 'enviar E-mail':
        enviar_email()
    elif rp['OP'] == 'HTTP':
        http()
    elif rp['OP'] == 'Sair':
        print(color.Fore.RED + '* Saindo...')
        t.sleep(3)
        subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
        procurauser()

def limpar_unicode(texto):
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

def gerar_texto():
    genai.configure(api_key=APIKEY)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(color.Fore.RED + f'* Erro ao inicializar o modelo: {e}')
        return

    print(color.Fore.CYAN + 'Insira o prompt')
    inp = input('>_')
    try:
        resp = model.generate_content(
            inp + ' Sem formatação de texto (ex: **, ``, #). É para PDF.',
            generation_config={"max_output_tokens": 200}
        ).text
    except Exception as e:
        print(color.Fore.RED + f'* Erro ao gerar conteúdo: {e}')
        return

    print(resp)
    q5 = [
        inq.List(
            'OP',
            message='Deseja salvar o texto como PDF?',
            choices=['Sim', 'Não']
        )
    ]
    rep = inq.prompt(q5)
    if rep['OP'] == 'Sim':
        ideia = input('Nome do arquivo: ')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        texto_limpo = limpar_unicode(resp)
        pdf.multi_cell(0, 10, texto_limpo)
        caminho = filedialog.askdirectory()
        pdf.output(f'{caminho}/{ideia}.pdf')
    input('Pressione enter para voltar...')
    HOME()

def gerar_documento():
    genai.configure(api_key=APIKEY)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(color.Fore.RED + f'* Erro: {e}')
        return
    print("Assunto do documento:")
    inp = input('>_')
    print("Ideia central:")
    IDEIA = input('>_')
    print("Dados (separados por vírgula):")
    DADOS = input('>_')
    print("Seu nome:")
    NOME = input('>_')
    print("Data:")
    DATA = input('>_')

    try:
        resp = model.generate_content(f"""
Escreva um documento formal com base no assunto: "{inp}", ideia central: "{IDEIA}", dados: {DADOS}. Nome do autor: {NOME}. Data: {DATA}.
Sem formatações (ex: **, #). Apenas o texto puro para PDF.
""")
    except:
        print("Erro ao gerar conteúdo com IA.")
        return

    out = limpar_unicode(resp.text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, out)
    caminho = filedialog.askdirectory()
    pdf.output(f'{caminho}/{IDEIA}.pdf')
    input('Pressione enter para voltar...')
    HOME()

def enviar_email():
    genai.configure(api_key=APIKEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    remetente = cursor.execute("SELECT email FROM users WHERE user = ?", (user,)).fetchone()[0]
    app_pass = cursor.execute("SELECT app_pass FROM users WHERE user = ?", (user,)).fetchone()[0]

    print(color.Fore.YELLOW + "\n== Envio de E-mails ==")
    print(color.Fore.CYAN + "→ Assunto do e-mail:")
    assunto = input("> ").strip()

    print(color.Fore.CYAN + "→ Destinatário:")
    destinatario = input("> ").strip()

    print(color.Fore.CYAN + "→ Tema / ideia central do e-mail:")
    ideia = input("> ").strip()

    print(color.Fore.YELLOW + "\nGerando corpo do e-mail com IA...")
    try:
        resposta = model.generate_content(
            f"Crie um e-mail formal com o assunto '{assunto}', com base na ideia: {ideia}. e o nome do autor é {user}"
        )
        corpo = resposta.text
    except Exception as e:
        print(color.Fore.RED + f"Erro ao gerar texto com IA: {e}")
        return

    print(color.Fore.GREEN + "\nE-mail gerado:")
    print("-" * 40)
    print(corpo)
    print("-" * 40)

    confirmar = input(color.Fore.YELLOW + "\nDeseja enviar esse e-mail? (s/n): ").lower()
    if confirmar != 's':
        print(color.Fore.RED + "Envio cancelado.")
        return

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, app_pass)
        server.sendmail(remetente, destinatario, msg.as_string())
        print(color.Fore.GREEN + "✔ E-mail enviado com sucesso!")
    except Exception as e:
        print(color.Fore.RED + f"Erro ao enviar o e-mail: {e}")
    finally:
        server.quit()

    input('Pressione enter para voltar...')
    HOME()

def responder_clientes():
    print(color.Fore.BLUE +'Responder Clientes')

    genai.configure(api_key=APIKEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    print(color.fore.YELLOW + "Nome do cliente")
    n = input(">_")
    print (color.fore.YELLOW + "Assunto da resposta: ")
    a = input(">_")
    print(color.fore.YELLOW + "Tipo do problema:" )
    t = input(">_")
    print(color.fore.YELLOW + "Resposta")
    r = input('>_')
    try:
        res = model.generate_content(
    f"Você é um especialista em Atendimento ao Cliente. Sua tarefa é redigir uma resposta formal, clara e cordial para o cliente {n}. "
    f"O assunto tratado é {a}. O tipo de pergunta do cliente é {t} e a forma esperada de resposta é {r}. "
    "Utilize a norma‑padrão da língua portuguesa. Entregue apenas a resposta ao cliente, em texto corrido, "
    "sem qualquer tipo de formatação (negrito, itálico, listas, cabeçalhos, código ou quebras de linha extras)."
)
        print(res.text)
        print('______________________________________')
        print(' ')
        q10 = [
    {
        'type': 'list',
        'name': 'OP',
        'message': 'Como deseja salvar a resposta?',
        'choices': ['PDF', 'HTTP', 'TXT']
    }
]

        rep = inq.prompt(q10)
        if rep['OP'] == 'PDF':
            ideia = input('Nome do arquivo: ')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, res.text)
            caminho = filedialog.askdirectory()
            pdf.output(f'{caminho}/resposta.pdf')
        elif rep['OP'] == 'HTTP':
            print(color.Fore.YELLOW + "Insira o servidor: ")
            s = input(">_")
            try:
                requests.post(s, res.text)
                print(color.Fore.GREEN + "✔ Resposta enviada com sucesso!")
            except Exception as e:
                print(color.Fore.RED + f"Erro ao enviar a resposta: {e}")
        elif rep['OP'] == 'TXT':
            dir = filedialog.askdirectory()
            with open(f'{dir}/rep.txt', 'w') as f:
                f.write(res.text)
    except Exception as e:
        print(color.Fore.RED + f""""
               ___________________________________
              |                                   |
              |  Parece que a IA bugou. E ela     |
              |  Retornou o erro: {e}             |
              |                                   |
              |___________________________________|""")

    input('Pressione enter para voltar...')
    HOME()
    
def resumir_pdfs():
    genai.configure(api_key=APIKEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    print(color.Fore.YELLOW + 'Selecione o arquivo PDF:')
    PATH = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not PATH:
        print(color.Fore.RED + "Nenhum arquivo selecionado.")
        return
    
    try:
        with open(PATH, 'rb') as f:
            leitor = PyPDF2.PdfReader(f)
            txt = ""
            for pagina in leitor.pages:
                txt += pagina.extract_text() or ""
        
        prompt_text = (f"Por favor, resuma o conteúdo a seguir, extraído de um arquivo PDF, "
                       f"de forma clara e concisa, mantendo os pontos principais:\n{txt}")
        
        res = model.generate_content(prompt_text)
        resumo = res.text
        
        print(color.Fore.GREEN + "Resumo gerado com sucesso!")
        print(resumo)
        
        q11 = [
            inq.List(
                'OP',
                message='Como deseja salvar o resumo?',
                choices=['PDF', 'TXT']
            )
        ]
        rep = inq.prompt(q11)
        
        ideia = input('Nome do arquivo (sem extensão): ')
        caminho = filedialog.askdirectory()
        if not caminho:
            print(color.Fore.RED + "Nenhum diretório selecionado.")
            return
        
        if rep['OP'] == 'PDF':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, resumo)
            pdf.output(f'{caminho}/{ideia}.pdf')
        elif rep['OP'] == 'TXT':
            with open(f'{caminho}/{ideia}.txt', 'w', encoding='utf-8') as f:
                f.write(resumo)
        
        print(color.Fore.GREEN + f"Arquivo salvo em: {caminho}/{ideia}.{rep['OP'].lower()}")
    
    except Exception as e:
        print(color.Fore.RED + f"Erro: {e}")

    except Exception as e:
        print(color.Fore.RED + f"Erro ao resumir o PDF: {e}")
    input('Pressione enter para voltar...')
    HOME()
        

def http():
    print(color.Fore.YELLOW + "HTTP")
    print('--------------------------------------')
    print(color.Fore.YELLOW + "Insira o servidor: ")
    s = input(">_")
    print(color.Fore.YELLOW + "Insira o texto: ")
    F = filedialog.askopenfilename()
    with open (F, 'r') as f:
        F = f.read()
    try:
        requests.post(s, F)
        print(color.Fore.GREEN + "✔ JSON enviado com sucesso!")
    except Exception as e:
        print(color.Fore.RED + f"Erro ao enviar JSON: {e}")
    input('Pressione enter para voltar...')
    HOME()

procurauser()
