'''
creates a server to run the flow and task
'''

import sqlite3
con = sqlite3.connect("flow_gibbon.db")
cur = con.cursor()

# TODO: create apis to get the flow and task details
