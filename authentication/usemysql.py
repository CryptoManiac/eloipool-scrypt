# Copyright (C) 2013 Westly Ward <sonicrules1234@gmail.com>
# Written by Westly Ward <sonicrules1234@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import config, pymysql, traceback
class usemysql:
    def __init__(self, **k) :
        print("Got to __init__\n")
        self.settings = config.ShareLogging[1]['dbopts']
        self.connect()
 
    def connect(self) :
        self.conn = pymysql.connect(host=self.settings['host'], port=3306, user=self.settings['user'], passwd=self.settings['passwd'], db=self.settings['db'])
        self.dbc = self.conn.cursor()
        print("Connected to mysql\n")
    def checkAuthentication(self, user, password) :
        print("Checking Authentication\n")
        try :
            self.dbc.execute(
                """SELECT password
FROM pool_worker
WHERE username = '%s';""" % (user,))
            response = self.dbc.fetchone()
            print(repr(response))
            if response == None :
                print("Not connected!  Reconnecting now!\n")                
                self.connect()
                self.dbc.execute(
                    """SELECT password
FROM pool_worker
WHERE username = '%s';""" % (user,))
                response = self.dbc.fetchone()
            db_password = response[0]
        except :
            traceback.print_exc()
            return False
        if password == db_password : return True
        else : return False
