# -*- coding: utf-8 -*-
"""Respostas que a coleta digita quando o ssh pergunta algo (regex esperada, texto digitado)."""
SIM = ["\\(yes/no", "yes\n"]                 # a pergunta da primeira conexão
NAO = ["\\(yes/no", "no\n"]
SENHA = ["password: ", "lab123\n"]            # a senha do usuário lab no servidor de teste
def ERRADA(n):                                # uma senha errada
    return ["password: ", "errada%d\n" % n]
def FRASE(texto, pergunta="passphrase"):      # frase secreta da chave
    return [pergunta + "[^:]*: ", texto + "\n"]
def NO(host, cmd, user="lab"):                # um comando digitado no prompt de outro computador
    return ["%s@%s:[^$#\\n]*[$#] " % (user, host), cmd + "\n"]
def SFTP(cmd):
    return ["sftp> ", cmd + "\n"]
