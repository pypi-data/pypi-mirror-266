from databarge.functions import write_to_log

# ===================================================================================================
# EXECUTE CODE
# ===================================================================================================

def run_sql_server_code(my_conn, my_db, my_code, log_path):
    
    import sys
    from gen_mods.misc_fns import write_to_log
    
    if log_path != None and len(log_path) > 0:
        write_to_log(log_path, 'code execution started: ' + my_code)

    my_cursor = my_conn.connection.cursor()
    my_cursor.execute("USE " + my_db)
        
    try:
        my_cursor.execute(my_code)
    except Exception as e:        
        err_msg = '*** code execution failed -- error below ***'  + '\r' + str(e)
        if log_path != None and len(log_path) > 0:
            write_to_log(log_path, err_msg)
        sys.exit('code execution failed -- check log file')
        
    my_conn.connection.commit()
    
    if log_path != None and len(log_path) > 0:
        write_to_log(log_path, 'code execution succeeded')

def execute_sql_file(my_conection, my_file, **kwargs):

    import re
    
    log_path = None
    for k, v in kwargs.items():
        if k == 'log_path':
            log_path = v    
    
    with open(my_file) as file:
        sql_statements = re.split(r';\s*$', file.read(), flags=re.MULTILINE)
    
    for ss in sql_statements:
        if ss:
            if log_path != None:
                write_to_log(log_path, 'started executing code: ' + '\n' + ss)
            my_conection.cursor.execute(ss)
            my_conection.connection.commit()
            if log_path != None:
                write_to_log(log_path, 'finished executing code')
                
def alt_execute_sql_file(my_conection, my_file, **kwargs):
    
    log_path = None
    for k, v in kwargs.items():
        if k == 'log_path':
            log_path = v    
    
    with open(my_file) as file:
        raw_file = file.read()

    # cleansed_file = ''
    first_line = True
    for line in raw_file.split('\n'):
        line = line.strip('\r')
        if len(line) > 0:
            if line[:2] != '--':
                if first_line == True:
                    cleansed_file = line
                    first_line = False
                else:
                    cleansed_file = cleansed_file + '\n' + line
    # print(cleansed_file)
    
    sql_statements = cleansed_file.split(';')
    
    for ss in sql_statements:
        if len(ss) > 0:
            if log_path != None:
                write_to_log(log_path, 'started executing code: ' + '\n' + ss)
            my_conection.cursor.execute(ss)
            my_conection.connection.commit()
            if log_path != None:
                write_to_log(log_path, 'finished executing code')
        
def change_sql_svr_db(conn, db):
    
    conn.connection.execute("USE " + db)
    conn.engine.execute("USE " + db)
    conn.cursor.execute("USE " + db)

class SqlServerProc:
    def __init__(self, my_conn, my_db, my_proc):
        self.my_conn = my_conn
        self.my_db = my_db
        self.my_proc = my_proc
        
    def exec_proc(self):    
        my_sql = "EXEC " + self.my_db + ".dbo." + self.my_proc
        self.my_conn.cursor.execute(my_sql)
        self.my_conn.connection.commit()

# ===================================================================================================
# ===================================================================================================
# ===================================================================================================