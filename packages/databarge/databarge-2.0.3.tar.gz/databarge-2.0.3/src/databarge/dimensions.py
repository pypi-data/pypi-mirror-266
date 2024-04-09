# from databarge.functions import write_to_log

# ===================================================================================================
# UPDATE DIMENSION TABLE
# ===================================================================================================

class UpdateDimensionTable():

# CREATES NEW DIMENSION RECORDS IN PYTHON THEN APPENDS THEM TO THE SQL SERVER TABLE
    
    def __init__(self, conn, dim_database, dim_table, dim_id, dim_desc, fact_database, fact_table, fact_desc):
        self.conn = conn
        self.dim_database = dim_database
        self.dim_table = dim_table
        self.dim_id = dim_id
        self.dim_desc = dim_desc
        self.fact_database = fact_database
        self.fact_table = fact_table
        self.fact_desc = fact_desc
    
    def update_table(self):
        
        import pandas as pd
    
        self.dim_frame = pd.read_sql('SELECT * FROM ' + self.dim_database + '.dbo.' + self.dim_table, self.conn.engine)
        self.fact_frame = pd.read_sql('SELECT DISTINCT ' + self.fact_desc + ' FROM ' + self.fact_database + '.dbo.' + self.fact_table, self.conn.engine)
        
        # temp_frame = pd.DataFrame({self.fact_desc: ['DUMMY 1', 'DUMMY 2']})
        # self.fact_frame = self.fact_frame.append(temp_frame)
        # self.fact_frame = self.fact_frame.reset_index(drop=True)
        
        mask = self.fact_frame[self.fact_desc].isin(self.dim_frame[self.dim_desc])
        new_frame = self.fact_frame.loc[~mask]
        
        n = self.dim_frame[self.dim_id].max()
        # new[dim_id] = new[fact_desc].astype('category').cat.codes.add(n + 1)
        new_frame[self.dim_id] = new_frame[self.fact_desc].ne(new_frame[self.fact_desc].shift()).cumsum() + n
        new_frame = new_frame[[self.dim_id, self.dim_desc]]
        
        self.conn.engine.execute("USE " + self.dim_database) # use ENGINE.execute and do NOT commit this line otherwise the default database will be used
        new_frame.to_sql(self.dim_table, self.conn.engine, if_exists='append', index=False)

# ===================================================================================================
# ===================================================================================================
# ===================================================================================================