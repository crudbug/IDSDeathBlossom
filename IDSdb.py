# -*- coding: utf-8 -*-

#*************************************************************
#  Copyright (c) 2003-2012, Emerging Threats
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the 
#  following conditions are met:
#  
#  * Redistributions of source code must retain the above copyright notice, this list of conditions and the following 
#    disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the 
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#  * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, 
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
#  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
#
#*************************************************************

from IDSLogging import *

class IDSdb:

    def __init__(self, options={}):

        self.options = options
        self.dbtype = self.options["type"]

        if self.dbtype == "MYSQL":
            import MySQLdb
            import _mysql
            p_info("DBType: %s" % self.dbtype)

            db_user = self.options["user"]
            db_pass = self.options["pass"]
            db_server = self.options["server"]
            db_scheme = self.options["scheme"]

            self.db = _mysql.connect(host=db_server,user=db_user, passwd=db_pass,db=db_scheme)

        elif self.dbtype == "sqlite3":
            import sqlite3
            db_file = self.options["file"]

            if not os.path.exists(db_file):
                self.db = sqlite3.Connection(db_file)
                self.initSqliteTables()
            else:
                self.db = sqlite3.Connection(db_file)

    def query(self, cmd):
            self.last_result = None
            p_debug("Trying to query " + cmd)
#        try:
            if self.dbtype == "MYSQL":
                import MySQLdb
                import _mysql
                r = self.db.query(cmd)
                rs = self.db.store_result()

                if rs:
                    row = rs.fetch_row()
                    self.last_result = []

                    while row:
                        for r in row: 
                            break

                        self.last_result.append(r)
                        row = rs.fetch_row()

            elif self.dbtype == "sqlite3":
                import sqlite3
                self.last_result = self.db.execute(cmd)

            try:
                if cmd.find("insert") >= 0 or cmd.find("INSERT") >= 0:
                    self.db.commit()
            except:
                p_debug("No commit needed")
            return self.last_result
 #       except:
            #print "Error!!!"
            #p_error("Error executing query")
            #return None
        #return None

    # An alias for query
    def execute(self, cmd):
        return self.query(cmd)

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def initMysqlTables(self):
        #Todo, check if the db tables are present or not. Try to create them if needed
        pass

    def initSqliteTables(self):
        # Todo, check if the db tables are present or not. Try to create them if needed
        # create the reports table
        try:
            self.query('''create table report (id integer primary key, reportgroup text, timestamp text, status text, engine text, path text, relpath text, errors integer, warnings integer, time integer, commented integer)''')
        except:
            p_error("failed to create the rulestats table")
            sys.exit(1);
        # create the rulestats table
        try:
            self.query('''create table rulestats (id integer primary key, runid, timestamp, file, alertfile, engine, rank integer , sid integer, gid integer, rev integer , checks integer, matches integer, alerts integer, microsecs integer, avgtcheck float, avgtmatch float, avgtnomatch float)''')
        except:
            p_error("failed to create the rulestats table")
            sys.exit(1);



# Usage example:

#db = IDSdb()
#la = db.query("drop table test;")
#db.close()
