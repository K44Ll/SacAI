import sqlite3 as sql
import google.generativeai as genai
import os
import pandas as pd
import numpy as nd
import time as t
from fpdf import FPDF
import inquirer as inq
import colorama as color
import subprocess
from tkinter import filedialog
import unicodedata

sql = sql.connect('data.db')
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
                choices=['Sim', 'Não',],
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
        else:
            pass
        
        selecionado = resposta_usuario['usuario_selecionado']
        global APIKEY
        APIKEY = cursor.execute(f'SELECT apikey FROM users WHERE user = ?', (selecionado,)).fetchone()[0]
        
        HOME()

def cadastro():
    print('* Cadastro de usuário')
    print(' ')
    print('Insira seu nome:')
    u = input(">_")
    print('Insira sua API key:')
    A = input(">_")
    try:
        cursor.execute('INSERT INTO users (user, apikey) VALUES (?, ?)', (u, A))
        sql.commit()
        print(f'* Usuário {u} cadastrado com sucesso!' + color.Fore.GREEN)
        procurauser()
    except Exception as e:
        print(e)
        print(f'* Erro ao cadastrar, tente novamente. Erro: {e}' + color.Fore.RED)
        cadastro()

def HOME():
    subprocess.run('cls', shell=True)
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
            choices=['Gerar texto', 'Gerar documento', 'Responder clientes', 'Resumir PDFs', 'enviar E-mail', 'HTTP', 'Sair' ]
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
        subprocess.run('cls', shell=True)
        procurauser()


def limpar_unicode(texto):
    """
    Remove caracteres que não são compatíveis com 'latin-1', 
    usado pelo FPDF 1.x.
    """
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

def gerar_texto():
    genai.configure(api_key=APIKEY)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(color.Fore.RED + f'* Erro ao inicializar o modelo: {e}')
        print(color.Fore.YELLOW + '* Parece que sua API key virou pó. Tente outro usuário ou verifique sua chave.')
        return

    print(color.Fore.CYAN + 'Insira o prompt')
    inp = input('>_')

    try:
        resp = model.generate_content(
            inp + ' Sem formatação de texto, exemplo **, ``, # e qualquer outra coisa que remeta a títulos. Isso é um PDF e ele não aceita essas formatações. Além de tudo quero apenas o texto, nada mais além disso. Obrigado.',
            generation_config={
                "max_output_tokens": 200
            }
        ).text
    except Exception as e:
        print(color.Fore.RED + f'* Erro ao gerar conteúdo: {e}')
        print(color.Fore.CYAN + """
   ┌───────────────────────────────────────────┐
   │   A IA bugou... Deve estar filosofando.   │
   │   Tente de novo ou reinicie o sistema!    │
   └───────────────────────────────────────────┘
""")
        return

    print(resp)
    print('-------------------------')

    q5 = [
        inq.List(
            'OP',
            message='Deseja salvar o texto como PDF?',
            choices=['Sim', 'Não']
        )
    ]
    rep = inq.prompt(q5)
    if rep['OP'] == 'Sim':
        ideia = input('Insira o nome do arquivo: ')
        pdf_doc = FPDF()  # Criando documento pdf com FPDF
        pdf_doc.add_page()
        pdf_doc.set_font('Arial', '', 12)

        # Limpeza dos caracteres problemáticos
        texto_limpo = limpar_unicode(resp)
        pdf_doc.multi_cell(0, 10, texto_limpo)

        caminho = filedialog.askdirectory()
        pdf_doc.output(f'{caminho}/{ideia}.pdf')
        input('Pressione enter para voltar...')
        HOME()


def gerar_documento():
    pass

def responder_clientes():
    pass

def resumir_pdfs():
    pass

def enviar_email():
    pass

def http():
    pass

procurauser()
