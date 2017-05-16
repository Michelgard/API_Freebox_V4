# -*- coding: utf-8 -*

mail = 1
pushover = 1

# On créé un dictionnaire contenant les paramètres de connexion MySQL
paramMysql = {
    'host'   : 'localhost',
    'user'   : 'util',
    'passwd' : 'Mot de passe',
    'db'     : 'Nom base'
# Bien respecter les noms des paramètres (host, user, passwd, db)

#Ticket API Freebox
token = "API FREEBOX"

#Url API Freebox
url = "https://nomdomaine free:port/api/v4/"

#Requete SQL pour vérifier la dernière donnée d'une table
sql1 = """\
SELECT * FROM Autonome
"""

sql2 = """\
SELECT * FROM `Position_prise` WHERE `N_Prise`='LED3'
"""

sql3="UPDATE Position_prise SET  Valeur_Prise = 'OFF' WHERE  N_Prise ='"

sql4="UPDATE Position_prise SET  Valeur_Prise = 'ON' WHERE  N_Prise ='"

#Données pour le mail
smtp = 'smtp.....'
portSmtp = 587
mailLogin = 'contact@blog-de-michel.fr'
passLogin = 'Mot de passe'
email_from = 'contact@blog-de-michel.fr'
email_to = 'contact@blog-de-michel.fr'

sujetMailOFF = 'DashScreen OFF'
texteMailOFF = u"""\
<html>
  <head></head>
  <body>
    <p>En ton absence le DashScreen a été éteind !!!
    </p>
  </body>
</html>
"""
messageOFF = 'DashScreen OFF'

sujetMailON = 'DashScreen ON'
texteMailON = u"""\
<html>
  <head></head>
  <body>
    <p>A ton retour DashScreen allumé !!!</p>
  </body>
</html>
"""
messageON = 'DashScreen ON'


    

