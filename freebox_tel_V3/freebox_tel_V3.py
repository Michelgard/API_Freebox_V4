#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import hmac
import hashlib
import MySQLdb
import sys

#PushOver
import httplib, urllib

#Module de config
from config import *

#module pour mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#mode verbose : python freebox.py -v
verbose = 0
if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        verbose = 1
    else:
        print "Argument non reconnu !  -v pour verbose"
        sys.exit(0)

#Reqête API Freebox en POST 
def connexion_post(url, data=None, headers={}):
    if data: data = json.dumps(data)
    return json.loads(requests.post(url, data=data, headers=headers).text)

#Reqête API Freebox en GET
def connexion_get(url, headers={}):
    return json.loads(requests.get(url, headers=headers).text)

#Ouverture session API FreeBOX
def mksession(url, token):
    challenge=connexion_get(url + "login/")["result"]["challenge"]
    data={
    	"app_id": "fr.freebox.testapp",
      	"password": hmac.new(token,challenge,hashlib.sha1).hexdigest()
        }
    return connexion_post(url + "login/session/", data)["result"]["session_token"]

#Recherche du téléphone retour de True : Présent ou False : Absent
def recherche_app(url ,session_token):
    method = url + "lan/browser/pub/"
    resultat =  connexion_get(method, headers={"X-Fbx-App-Auth": session_token})
    #recherche dans resultat des élements connectés avec le adresse MAC
    for val in resultat["result"]:
	for  val2  in val["l2ident"].values():
	    if val2 == "xx:xx:xx:xx:xx:xx": #Adresse Imac
		telephone = val["active"]
    if verbose: print "Telephone : " + str(telephone)    
    return telephone    

#connexion SQL
def connexion_SQL():
    try:
        #connexion  à la base de données
        db = MySQLdb.connect(**paramMysql)
        dbSQL = db.cursor(MySQLdb.cursors.DictCursor)
        return db, dbSQL
    except MySQLdb.Error, e:
        # En cas d'anomalie
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

# Envoie mail 
def sendEmail(email_from, email_to, subject, text, smtp, portSmtp, mailLogin, passLogin):
    if verbose : print "Mail : " + text
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = email_from
    msg['To']      = email_to
    codage = 'utf-8'
    msg['Charset'] = codage
    typetexte = 'html'
    msg.attach(MIMEText(text.encode(codage), typetexte, _charset=codage))
    msg['Content-Type'] = 'text/html' + text + '; charset=' + codage
    s = smtplib.SMTP(smtp, portSmtp)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(mailLogin, passLogin)
    try:
        s.sendmail(email_from,[email_to],msg.as_string())
    except smtplib.SMTPException as e:
        if verbose: print e
    s.quit()

def pushOver(message):
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.urlencode({
    "token": "yyssshhdkldlmkdhdjkdkldlpckdi",
    "user": "jglfdjfkfghdgfuiisfjsfsfmf",
    "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

#La fonction vérifie si la maison est en autonome et si non regarde la position du téléphone et de l'écran
def verification_tel(telephone):
    db, dbSQL = connexion_SQL()
    if verbose: print sql1
    dbSQL.execute(sql1)
    rows = dbSQL.fetchall()
    # On parcourt toutes les lignes
    for row in rows:
        auto = row['Autonome']
        if verbose: print "auto : " + auto
    if auto == 'OFF': #Si la maison n'est pas en autonnome on cherche la position de l'écran et le nom de la prise 
        if verbose: print sql2
        dbSQL.execute(sql2)
        rows = dbSQL.fetchall()
        # On parcourt toutes les lignes 
        for row in rows:
            val = row['Valeur_Prise']
            nom = row['N_Prise']
        if verbose: print "valeur ecran : " + val 
        if not telephone: 
            if val == 'ON':
                params = "/?" + nom + "=OFF"
                try:
                    requests.get("http://xx.xxx.xx.xx:yy", params=params)
                    if verbose: print sql3 + nom +"'"
                    try:
                        # On exécute la requête SQL
                        dbSQL.execute(sql3 + nom + "'")
                        # On commit
                        db.commit()
                        if mail: sendEmail(email_from, email_to, sujetMailOFF, texteMailOFF, smtp, portSmtp, mailLogin, passLogin)
                        if pushover: pushOver(messageOFF)
                    except MySQLdb.Error, e:
                        # En cas d'erreur on annule les modifications
                        db.rollback()
                        if verbose : print "Erreur sur la requête : " + str(e)
                except:
                    if verbose : print "Erreur sur la requête : "
        if telephone: 
 	    if val == 'OFF':
                params = "/?" + nom + "=ON"
                try:
                    requests.get("http://xx.xxx.xx.xx:yy", params=params)
                    if verbose: print sql4 + nom + "'"
                    try:
                        # On exécute la requête SQL
                        dbSQL.execute(sql4+ nom +"'")
                        # On commit
                        db.commit()
                        if mail: sendEmail(email_from, email_to, sujetMailON, texteMailON, smtp, portSmtp, mailLogin, passLogin)
                        if pushover: pushOver(messageON)
                    except MySQLdb.Error, e:
                        # En cas d'erreur on annule les modifications
                        db.rollback()
                        if verbose : print "Erreur sur la requête : " + str(e)
                except e:
                    if verbose : print "Erreur sur la requête : "
    db.close()
    
#session_token = mksession() #création session API Freebox
#telephone = recherche_app(session_token) #Récupère les valeurs du téléphone
#db, dbSQL = connexion_SQL() # connexion mySQL
#verification_tel(db, dbSQL, telephone) #commande écran

verification_tel(recherche_app(url, mksession(url, token))) # tout sur une ligne 