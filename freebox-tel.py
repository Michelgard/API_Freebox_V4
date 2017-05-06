#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import hmac
import hashlib
import MySQLdb
import xml.dom.minidom
import sys

verbose = 0
if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        verbose = 1
    else:
        print "Argument non reconnu !  -v pour verbose"
        sys.exit(0)

def connexion_post(method,data=None,headers={}):
    url = "http:/mafreebox.freebox.fr/api/v4/"+method
    if data: data = json.dumps(data)
    return json.loads(requests.post(url, data=data, headers=headers).text)

def connexion_get(method, headers={}):
    url = "http:mafreebox.freebox.fr/api/v4/"+method
    return json.loads(requests.get(url, headers=headers).text)
	
def mksession():
    token = "64frjkgzbgjrsgbklqnaerj876;,nbvfdsfghjkhj2X0Hyf3e2JU9E"
    challenge=connexion_get("login/")["result"]["challenge"]
    data={
    	  "app_id": "fr.freebox.testapp",
      	"password": hmac.new(token,challenge,hashlib.sha1).hexdigest()
    }
    return connexion_post("login/session/",data)["result"]["session_token"]

def recherche_app(session_token):
    method = "lan/browser/pub/"
    resultat =  connexion_get(method, headers={"X-Fbx-App-Auth": session_token})
    #recherche dans resultat des élements connectés avec le adresse MAC
    for val in resultat["result"]:
	for  val2  in val["l2ident"].values():
	    #if val2 == "5C:CF:7F:D0:0E:33":
		#espwifi = val["active"]
	    if val2 == "28:5A:EB:83:25:8C":
		telephone = val["active"]
    if verbose: print "Telephone : " + str(telephone)
	#print "ESPWIFI : " + str(espwifi)    
    return telephone    #, espwifi

def connexion_SQL():
    """Connexion et insertion de la données dans la base"""
    """import données connexion SGL d'un fichier config en XML"""
    valeurListe = xml.dom.minidom.parse("/home/michelgard/utilitaire/tacheDomotic/Freebox/configSQL.xml").getElementsByTagName("SQL")
    for valeur in valeurListe:
        #connexion  à la base de données
        db = MySQLdb.connect(valeur.attributes['ip'].value, valeur.attributes['login'].value, valeur.attributes['mdp'].value, valeur.attributes['dbase'].value)
    dbSQL = db.cursor(MySQLdb.cursors.DictCursor)
    return db, dbSQL

def verification_tel(sql, telephone):
    db, dbSQL = sql
    sql ="SELECT * FROM Autonome"
    if verbose: print sql
    dbSQL.execute(sql)
    rows = dbSQL.fetchall()
    # On parcourt toutes les lignes
    for row in rows:
        auto = row['Autonome']
    if auto == 'OFF':
        if verbose: print "auto : " + auto
        sql ="SELECT * FROM `Position_prise` WHERE `N_Prise`='LED3'"
        if verbose: print sql
        dbSQL.execute(sql)
        rows = dbSQL.fetchall()
        # On parcourt toutes les lignes
        for row in rows:
            val = row['Valeur_Prise']
            nom = row['N_Prise']
        if verbose: print "valeur ecran : " + val

        if not telephone: 
            if val == 'ON':
                params = "/?" + nom + "=OFF"
                requests.get("http://xx.xx.xxx.xx:xx", params=params)
                sql2="UPDATE Position_prise SET  Valeur_Prise = 'OFF' WHERE  N_Prise ='" + nom +"'"
	        if verbose: print sql2
	        try:
                    # On exécute la requête SQL
                    dbSQL.execute(sql2)
                    # On commit
                    db.commit()
                except MySQLdb.Error, e:
                    # En cas d'erreur on annule les modifications
                    db.rollback()

        if telephone: 
 	    if val == 'OFF':
                params = "/?" + nom + "=ON"
                requests.get("http://xxx.xx.xx.xx:xx", params=params)
                sql2="UPDATE Position_prise SET  Valeur_Prise = 'ON' WHERE  N_Prise ='" + nom +"'"
                if verbose: print sql2
                try:
                    # On exécute la requête SQL
                    dbSQL.execute(sql2)
                    # On commit
                    db.commit()
                except MySQLdb.Error, e:
                    # En cas d'erreur on annule les modifications
                    db.rollback()
    db.close()
    
#session_token = mksession() #création session API Freebox
#telephone = recherche_app(session_token) #Récupère les valeurs du téléphone
#db, dbSQL = connexion_SQL() # connexion mySQL
#verification_tel(db, dbSQL, telephone) #commande écran

verification_tel(connexion_SQL(), recherche_app(mksession())) # tout sur une ligne 
