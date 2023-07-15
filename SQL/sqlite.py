import sqlite3

from SQL import CommonUtil


class Database():
    def __init__(self,db_name):
        self.db_name=db_name
        self._conn = sqlite3.connect(self.db_name)
        self._cur = self._conn.cursor()
        self.create_table()

    def create_table(self):
        try:
            create_tb_cmd = '''
                            CREATE TABLE IF NOT EXISTS USER
                            (
                            id VARCHAR(128) NOT NULL,
                            email CHAR(50)  NOT NULL,
                            pwd CHAR(50) NOT NULL,
                            bank_id CHAR(50) NOT NULL,
                            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (`id`)
                            );
                            '''
            self._cur.execute(create_tb_cmd)
        except:
            print("Create table failed")
            return False
        self._conn.commit()

    def insert_user(self,data):
        self._cur.execute("INSERT INTO USER (id,email,pwd,bank_id,create_time) VALUES(?,?,?,?,?);",(data[0],data[1],data[2],data[3],data[4],))
        self._conn.commit()

    def query_super(self,table,Email,email):
        self._cur.execute("SELECT * FROM USER where email=? ;",(email,))
        self._conn.commit()
        ret = self._cur.fetchall()
        count=len(ret)
        return count, ret

    def close(self):
        self._conn.close()

    def sql_edit(self,table,*args):
        self._cur.execute("update USER set bank_id= ? where email= ? ;",(args[0],args[1],))  # 執行
        self._conn.commit()

    def sql_search(self, table_name,  *args):
        self._cur.execute("select pwd from USER where  email = ? ;",(args[0],))#執行
        self._conn.commit()
        ret=self._cur.fetchone()
        return ret








