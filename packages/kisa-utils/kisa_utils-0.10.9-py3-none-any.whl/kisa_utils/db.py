import os, sys
import sqlite3
from types import SimpleNamespace
import string
from typing import Generator
import inspect

from . import storage
from . import codes

if sqlite3.sqlite_version_info[1]<38:
    sys.exit(f'we need sqlite3 v3.38.0+ to run this program. current version::{sqlite3.sqlite_version}')

MAX_FETCH_ITEMS = 8*1024

__EXT__ = 'sqlite3'

# you want this to throw erros in user-defined functions
sqlite3.enable_callback_tracebacks(True)

TRIGGERS:dict = {
    # eg
    # 'userActiveStateChange':{
    #     'table': 'users',
    #     'when': 'after', # before | after | instead of
    #     'action': 'update', # insert | update | delete
    #     'condition':'''
    #         old.active != new.active
    #     ''',
    #     'code':'''
    #         insert into logs values(
    #             datetime('now', '+03:00'), 
    #             new.addedBy, 
    #             "users.active: change "||old.active||"->"||new.active,
    #             "{}"
    #         )
    #     '''
    # },

}

# *********************************************************************
def _checkContext(method):
    '''
    this decorator will be used to enforce the calling of Api class instances
    from `with` contexts. this will ensure resources are always released as they
    should
    '''
    def _(self, *args, **kwargs):
        if (not self._in_with_statement) and (not self._txnDecorated):
            raise Exception(f'method `db.Api.{method.__name__}` called from outside `with` statement/context')
        if method.__name__ in ['insert','update','delete'] and self._readonly:
            return {
                'status':False,
                'log': f'calling a write method (`db.Api.{method.__name__}`) on a read-only database'
            }
            # raise Exception(f'calling a write method (`db.Api.{method.__name__}`) on a read-only database')
        return method(self,*args, **kwargs)
    return _

def _getNumberOfArgsAndKwargs(function:callable) -> tuple[int]:
    signature = inspect.signature(function)

    nArgs = sum(
        p.default == inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        for p in signature.parameters.values()
    )

    nKwargs = len(signature.parameters) - nArgs

    return nArgs, nKwargs

class Api:
    def __init__(
        self,
        path:str=':memory:', 
        tables:dict = {}, 
        readonly:bool=True, 
        bindingFunctions:list=[],
        transactionMode:bool = False,
        indices:dict = {},
    ):
        '''
        attempt to open an sqlite3 database connection

        @param `path`: path to the database file. if;
            + `path` does not exist and it does not end with the `.sqlite3` extension, it will be added`
            
            + `path` is set to `':memory:'`, an in-memory db will be opened and `readonly` will automatically be set to False
        
        @param `tables`: dict[str,str]
                eg
                {
                    'credentials':"""
                        key             varchar(256) not null,
                        value           varchar(256) not null
                    """,
                    'users':"""
                        firstName       varchar(256) not null,
                        lastName        varchar(256) not null,
                        username        varchar(256) not null
                    """,
                }

        @param `readonly`: flag indicating if the database should be opened in read-only mode.
            + if `path` is set to `':memory:'`, `readonly` will automatically be reset to False

        @param `bindingFunctions`:  Custom functions defined in python to be used by sqlite3. 
            + Each entry is in form (name:str, nargs:int, func:py-function)

        @param `indices`: dict representing the indices to be made. format is
            {
                `tableName`: [`singleCol`, (`multiCol1`,`multiCol2`,...),...]
            }
            eg
            {
                'users': ['userId', ('firstName','lastName')]
            }
            i.e for single column-indices, a string is provided in the list. for composite/multi-col indices, a tuple is provided

        '''

        self._in_with_statement = False
        self.isOpen = False
        self.functions:dict = {}
        self._txnDecorated = False
        
        self.__transactionMode = True if transactionMode else False
        self.__withContextCount = 0

        if  path not in [':memory:', ':ram:',':RAM:']:
            while path.endswith('/'): path = path[:-1]
            if not path.endswith(f'.{__EXT__}') and not os.path.isfile(path):
                path += f'.{__EXT__}'

            path_root = os.path.split(path)[0]
            
            if (not os.path.isdir(path_root)) and os.system(f'mkdir -p "{path_root}"'):
                return

            if not os.path.isfile(path):
                initTables = True
        else:
            path = ':memory:'

        readonly = False if (':memory:' == path or self.__transactionMode) else readonly

        self._readonly = True if readonly else False 

        self.db:sqlite3.Connection = sqlite3.connect(path)
        if self.__transactionMode:
            self.db.isolation_level = None
        self.cursor:sqlite3.Cursor = self.db.cursor();

        initTables = True if tables else False
        if initTables:
            self.__startTransaction()
            for table in tables:
                self.cursor.execute(f'create table if not exists {table} ({tables[table]})')
            if self.__transactionMode:
                self.db.commit()
            else:
                self.__commit()
        
        if bindingFunctions:
            functionBindReply = self.bindFunctions(bindingFunctions)
            if not functionBindReply['status']:
                raise Exception(f'binding error:: {functionBindReply["log"]}')                

        self.isOpen = True

        if indices:
            currentindices = self.__getIndicesDict()
            tablesList = self.__getTablesList()
            for table in indices:
                cols = indices[table]

                for col in cols:
                    if (table in currentindices) and (col in currentindices[table]):
                        # columns already indexed
                        continue

                    if table not in tablesList:
                        raise ValueError(f'[DB-index Error] unknown table `{table}`')
                    
                    col = col if isinstance(col,str) else ','.join(col)
                    indexName = codes.new()
                    self.cursor.execute(f'create index if not exists i{indexName} on {table}({col})')

        self.__startTransaction()

        if readonly:
            self.cursor.execute(f'''
            pragma query_only = ON;   -- disable changes
            ''')

    def __bind_functions(self, functions):
        for entry in functions:
            if entry[0] in self.functions: continue
            self.db.create_function(*entry)
            self.functions[entry[0]] = entry[-1]

    def __startTransaction(self):
        if self.__transactionMode:
            self.cursor.execute('begin')
            self.__transactionData = {
                op:{'passed':0, 'failed':0}
                for op in ['insert','delete','update','createTable']
            }

    def __commit(self):
        '''
        attempt to commit to the database IF its not open in `transactionMode=True`
        '''
        if not self.__transactionMode:
            self.db.commit()

    def __formatDBJson(self, jsonPath:str, separator:str='::') -> str:
        '''
        attempt to format JSON from the KISA-way to the sqlite3 way

        @param `jsonPath`: the path to the json object
        @return formated string

        NB: array indices may be -1 indicating `end of array` for some oepration such as updates
        '''
        jsonPath = jsonPath.replace(' AS ',' as ').\
            replace(' As ',' as ').\
            replace(' aS ',' as ').\
            strip('/')

        jsonPath = [_.strip() for _ in jsonPath.split(' as ')]
        if len(jsonPath)==2:
            jsonPath, alias = jsonPath
        else:
            jsonPath, alias = jsonPath[0],None

        jsonPath = jsonPath.replace(separator,'.').strip('.')

        arrayIndex = jsonPath.index('[') if '[' in jsonPath else len(jsonPath)
        keyIndex = jsonPath.index('.') if '.' in jsonPath else len(jsonPath)

        if arrayIndex<keyIndex:
            jsonPath = jsonPath[:arrayIndex]+f'->>"${jsonPath[arrayIndex:]}"'
        elif keyIndex<arrayIndex:
            jsonPath = jsonPath[:keyIndex]+f'->>"${jsonPath[keyIndex:]}"'

        if alias:
            jsonPath += f' as {alias}'

        return jsonPath

    def __encodeIncomingData(self,data:list) -> list:
        '''
        attempt to jsonify data to be written to the database

        @param `data`: 1d/2d list to be written to the database
        '''
        _data = []
        _2d = isinstance(data[0], (list,tuple))
        for entry in data:
            if _2d:
                entry = [_ if not isinstance(_,(tuple,list,dict)) else storage.encodeJSON(_) for _ in entry]
            else:
                entry = entry if not isinstance(entry,(tuple,list,dict)) else storage.encodeJSON(entry) 

            _data.append(entry)

        return _data

    def __decodeOutgoingData(self, data:list) -> tuple:
        '''
        attempt to decode json objects to python list/dict where applicable. 

        @param `data`: list[tuple] returned by `cursor.fetch*`
        '''
        _data = []
        for entry in data:
            _entry = []
            for value in entry:
                if value and isinstance(value,str) and (value[0] in '[{'):
                    try:
                        value = storage.decodeJSON(value)
                    except:
                        pass

                _entry.append(value)
            _data.append(tuple(_entry))

        return _data

    def __formatJSONCondition(self, condition:str, separator:str='::') -> str:
        if separator not in condition: return condition

        jsonXters = string.digits+string.ascii_letters+separator+'[]-_'

        jsonIndexRanges = []
        index = 0
        conditionLength = len(condition)
        while separator in condition[index:]:
            separatorIndex = index + condition[index:].index(separator)

            # find start and end of the json-path
            leftIndex, rightIndex = separatorIndex, separatorIndex
            while leftIndex >= 0:
                if condition[leftIndex] not in jsonXters: break
                leftIndex -= 1
            leftIndex += 1 # by the time we break out, we've already found a bad xter

            while rightIndex < conditionLength:
                if condition[rightIndex] not in jsonXters: break
                rightIndex += 1
            rightIndex -= 1 # by the time we break out, we've already found a bad xter

            jsonIndexRanges.append((leftIndex,rightIndex))
            # print(f'<{condition[leftIndex:rightIndex+1]}><{__formatDBJson(condition[leftIndex:rightIndex+1])}>')

            index = rightIndex + 1

        startIndex = 0
        _condition = ''
        jsonIndexRanges.append((conditionLength, conditionLength))
        for leftIndex,rightIndex in jsonIndexRanges:
            _condition += condition[startIndex:leftIndex]
            _condition += self.__formatDBJson(condition[leftIndex:rightIndex+1])
            startIndex = rightIndex+1

        return _condition

    def __getIndicesDict(self) -> dict[str,list]:
        indices = {}

        if not self.isOpen: return indices

        self.cursor.execute('''
            SELECT name, tbl_name
            FROM sqlite_master
            WHERE type = 'index';
        ''')

        for indexName, table in self.cursor.fetchall():
            if table not in indices: indices[table] = []
            self.cursor.execute(f'pragma index_info("{indexName}")')
            cols = tuple([_[2] for _ in self.cursor.fetchall()])
            cols = cols[0] if 1==len(cols) else cols
            if cols not in indices[table]:
                indices[table].append(cols)

        return indices

    def __getTablesList(self) -> list:
        tables = []

        if not self.isOpen: return tables

        self.cursor.execute('''
            SELECT name, tbl_name
            FROM sqlite_master
            WHERE type = 'table';
        ''')

        tables = [_[0] for _ in self.cursor.fetchall()]
        
        return tables


    #---------------------------------------------------------------------------
    @_checkContext
    def execute(self, cmd:str, cmdData:list=[], commit:bool=False) -> dict[str,bool|str]:
        reply = {'status':False, 'log':''}

        try:
            self.cursor.execute(cmd,cmdData)
            if commit: self.__commit() # ?
        except Exception as e:
            reply['log'] = str(e)
            return reply

        reply['status'] = True
        return reply

    @_checkContext
    def __createFetchResultsGenerator(self, results:sqlite3.Cursor, columnTitles:list, parseJson:bool, mode:str) -> Generator[tuple|dict|SimpleNamespace,None,None]:

        for entry in results:
            if parseJson:
                entry = self.__decodeOutgoingData([entry])[0]

            yield entry if 'plain' == mode else (
                dict(zip(columnTitles,entry)) if 'dicts' == mode else(
                    SimpleNamespace(**dict(zip(columnTitles,entry))) if 'namespaces' == mode else(
                        entry
                    )
                )
            )

    @_checkContext
    def fetch(self, table:str, columns:list, condition:str, conditionData:list, limit:int=MAX_FETCH_ITEMS, returnDicts:bool=False, returnNamespaces:bool=False, parseJson:bool=False, returnGenerator:bool=False) -> list:
        '''
        attempt to fetch from the database

        @param `table`: database table name
        @parm `columns`: list of the columns to fetch. json columns are accessed using the `/` separator eg `other/bio/contacts[0]`
        @param `condition`: a string indicating the SQL condition for the fetch eg `userId=? and dateCreated<?`. all values a represented with the `?` placeholder
        @param `conditionData`: a list containing the values for each `?` placeholder in the condition
        @param `limit`: number indicating the maximum number of results to fetch
        @param `returnDicts`: bool; if `True`, we shall return a list of dictionaries as opposed to a list of tuples
        @param `returnNamespaces`: bool; if `True`, we shall return a list of named-tuples as opposed to a list of tuples
            ** if both `returnDicts` and `returnNamespaces` are set, `returnDicts` is effected
        @param `parseJson`: bool; if `True`, we shall parse json objects to python lists and dictionaries where possible
        @param `returnGenerator`: bool; if True, a generator will be returned instead of the list of tuple|dict|SimpleNamespace. this is especially recommended for large data
        '''
        assert (limit>0 and limit<=MAX_FETCH_ITEMS), f'please set a limit on the returned rows. maximum should be {MAX_FETCH_ITEMS}'

        condition = condition.strip() or '1'
        assert(len(condition.strip()))

        try:
            condition = self.__formatJSONCondition(condition)
        except:
            pass

        if columns in [['*']]:
            self.cursor.execute(f'select * from {table} where {condition} limit {limit}',conditionData)
            columns = [description[0] for description in self.cursor.description]

        columns = [self.__formatDBJson(_) for _ in columns]

        self.cursor.execute(f"select {','.join(columns)} from {table} where {condition} limit {limit}",conditionData)
        
        fetchedData = self.cursor
        if parseJson and not returnGenerator:
            fetchedData = self.__decodeOutgoingData(fetchedData)

        cols = [_[0] for _ in self.cursor.description]

        if not (returnDicts or returnNamespaces):
            return [_ for _ in fetchedData] if not returnGenerator else self.__createFetchResultsGenerator(fetchedData, cols, parseJson, 'plain')

        if returnDicts:
            return [dict(zip(cols,_)) for _ in fetchedData] if not returnGenerator else self.__createFetchResultsGenerator(fetchedData, cols, parseJson, 'dicts')

        # namepsaces...
        if [_ for _ in cols if (
            (' ' in _) or not (
                'a'<=_[0]<='z' or \
                'A'<=_[0]<='Z' or \
                '_'==_[0]
            )
        )]:
            raise TypeError('one or more column names is invalid as a key for namespaces')

        return [SimpleNamespace(**dict(zip(cols,_))) for _ in fetchedData] if not returnGenerator else self.__createFetchResultsGenerator(fetchedData, cols, parseJson, 'namespaces')

    @_checkContext
    def createTables(self, tables:dict[str,str]) -> dict:
        '''
        attempt to create tables to the database

        @param `tables`: dict[str,str]
                eg
                {
                    'credentials':"""
                        key             varchar(256) not null,
                        value           varchar(256) not null
                    """,
                    'users':"""
                        firstName       varchar(256) not null,
                        lastName        varchar(256) not null,
                        username        varchar(256) not null
                    """,
                }
        
        @return standard dict of {status:BOOL, log:STR}
        '''

        reply = {'status':False, 'log':''}

        for table in tables:
            try:
                self.cursor.execute(f'create table if not exists {table} ({tables[table]})')
                self.__commit()
                if self.__transactionMode: self.__transactionData['createTable']['passed'] += 1
            except Exception as e:
                if self.__transactionMode: self.__transactionData['createTable']['failed'] += 1
                reply['log'] = str(e)
                return reply

        reply['status'] = True
        return reply

    @_checkContext
    def insert(self, table:str, data:list) -> dict[str,bool|str]:
        self.cursor.execute(f'select * from {table}')
        column_value_placeholders = ['?' for description in self.cursor.description]
        
        reply = {'status':False, 'log':''}
        try:
            data = self.__encodeIncomingData(data)
            if isinstance(data[0],(list,tuple)):
                self.cursor.executemany(f'insert into {table} values ({",".join(column_value_placeholders)})',data)
            else:
                self.cursor.execute(f'insert into {table} values ({",".join(column_value_placeholders)})',data)
            self.__commit()
            if self.__transactionMode: self.__transactionData['insert']['passed'] += 1
        except Exception as e:
            if self.__transactionMode: self.__transactionData['insert']['failed'] += 1
            reply['log'] = str(e)
            return reply

        reply['status'] = True
        return reply

    @_checkContext
    def update(self, table:str, columns:list, columnData:list, condition:str, conditionData:list) -> dict[str,bool|str]:
        reply = {'status':False, 'log':''}

        if columns in [['*']]:
            self.cursor.execute(f'select * from {table}')
            columns = [description[0] for description in self.cursor.description]

        if len(columns) != len(columnData):
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = 'same number of items in `columns` as in `columnData`'
            return reply

        try:
            columnData = self.__encodeIncomingData(columnData)
        except:
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = 'failed to encode incoming data'
            return reply

        values = []
        columns = [self.__formatDBJson(_) for _ in columns]
        _columns = []
        json_roots = {}
        for index,col in enumerate(columns):
            if '->>' not in col:
                _columns.append(f'{col}=?')
            else:
                accessorIndex = col.index('->>')
                root, path = col[:accessorIndex], col[accessorIndex+3:]

                path = path.replace('[-1]','[#]')

                if '[#]' in path:
                    if path.count('[#]')>1:
                        if self.__transactionMode: self.__transactionData['update']['failed'] += 1
                        reply['log'] = 'we dont allow more than `[-1]` or `[#]` signatures for json'
                        return reply
                    if not path[:-1].endswith('[#]'):
                        if self.__transactionMode: self.__transactionData['update']['failed'] += 1
                        reply['log'] = 'json-array `[-1]` or `[#]` should be the last in the path'
                        return reply

                _columns.append(f'{root}=json_set({root},{path},?)')

                if root not in json_roots:
                    json_roots[root] = 0
                json_roots[root] += 1

            values.append(columnData[index])

        for root in json_roots:
            if json_roots[root] > 1:
                if self.__transactionMode: self.__transactionData['update']['failed'] += 1
                reply['log'] = f'expects only one json update per call. `{root}` has `{json_roots[root]}` updates'
                return reply


        columns = _columns
        values += conditionData

        condition = condition.strip()
        if not condition:
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = 'please provide an update condition. use `1` if you want all data updated'
            return reply

        try:
            condition = self.__formatJSONCondition(condition)
        except:
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = 'failed to format condition json'
            return reply

        try:
            if not self.fetch(table,['rowid'],condition, conditionData, limit=1):
                if self.__transactionMode: self.__transactionData['update']['failed'] += 1
                reply['log'] = 'update condition does NOT affect any rows'
                return reply
        except:
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = 'failed to check if update condition will affect rows'
            return reply

        try:
            self.cursor.execute(f'update {table} set {",".join(columns)} where {condition}',values)
            self.__commit()
            if self.__transactionMode: self.__transactionData['update']['passed'] += 1
        except Exception as e:
            if self.__transactionMode: self.__transactionData['update']['failed'] += 1
            reply['log'] = str(e)
            return reply

        reply['status'] = True
        return reply

    @_checkContext
    def delete(self, table:str, condition:str, conditionData:list) -> dict[str,bool|str]:
        reply = {'status':False, 'log':''}

        condition = condition.strip()
        if not condition:
            if self.__transactionMode: self.__transactionData['delete']['failed'] += 1
            reply['log'] = 'please provide a delete condition. use `1` if you want all data gone'
            return reply
        try:
            condition = self.__formatJSONCondition(condition)
        except:
            if self.__transactionMode: self.__transactionData['delete']['failed'] += 1
            reply['log'] = 'failed to format condition json'
            return reply

        try:
            if not self.fetch(table,['rowid'],condition, conditionData, limit=1):
                if self.__transactionMode: self.__transactionData['delete']['failed'] += 1
                reply['log'] = 'delete condition does NOT affect any rows'
                return reply
        except:
            if self.__transactionMode: self.__transactionData['delete']['failed'] += 1
            reply['log'] = 'failed to check if delete condition will affect rows'
            return reply

        try:
            self.cursor.execute(f'delete from {table} where {condition}',conditionData)
            self.__commit()
            if self.__transactionMode: self.__transactionData['delete']['passed'] += 1
        except Exception as e:
            if self.__transactionMode: self.__transactionData['delete']['failed'] += 1
            reply['log'] = str(e)
            return reply

        reply['status'] = True
        return reply

    @_checkContext
    def commitTransaction(self) -> dict:
        '''
        attempt to commits all operations of a transaction

        @return `dict` in form of `{'status':BOOL, 'log':STR}`
        '''
        reply = {'status':False, 'log':''}

        if not self.__transactionMode:
            reply['log'] = 'database not in transaction mode'
            return reply

        if not self.isOpen:
            reply['log'] = 'database not open'
            return reply

        for op in self.__transactionData:
            if self.__transactionData[op]['failed']:
                reply['log'] = f'{self.__transactionData[op]["failed"]} `{op}` operation(s) returned a `False` status'
                return reply
        
        self.cursor.execute('commit')

        self.__startTransaction()

        reply['status'] = True
        return reply

    def bindFunctions(self, functions:list[callable]) -> dict:
        '''
        attempt to bind python functions to the db-handle

        @param `functions`: a list of functions

        @return: standard kisa-dict of `{'status':BOOL, 'log':STR}`
        '''
        reply = {'status':False, 'log':''}

        if not isinstance(functions, list):
            reply['log'] = 'expected `functions` to be a list'
            return reply

        if not functions:
            reply['log'] = 'no functions provided'
            return reply
        
        signatures = []
        for index, function in enumerate(functions):
            if isinstance(function, tuple):
                if 3 != len(function):
                    reply['log'] = 'invalid tuple-style function signature given'
                    return reply
                signatures.append(function)
                continue

            if not callable(function):
                reply['log'] = f'item at index {index} is not a function'
                return reply

            name = function.__name__
            if name.startswith('<'):
                reply['log'] = f'function at index {index} seems to be a lambda function. these are not allowed'
                return reply

            nArgs, nKwargs = _getNumberOfArgsAndKwargs(function)

            signatures.append((name,nArgs,function))

        try:
            self.__bind_functions(signatures)
        except Exception as e:
            reply['log'] = f'functino binding error: {e}'
            return reply

        reply['status'] = True
        return reply

    # @_checkContext
    def close(self):
        if self.isOpen:
            # self.db.execute('pragma optimize;')
            if self.__transactionMode:
                pass # self.commitTransaction()
            else:
                self.db.commit()

            if self.__withContextCount <= 0:
                self.db.close()
                # self.db, self.cursor = None,None
                self.isOpen = False

    # @_checkContext
    def release(self):
        return self.close()

    # methods to add context to the handle
    def __enter__(self) -> 'Api':
        self._in_with_statement = True
        self.__withContextCount += 1
        return self

    def __exit__(self, *args) -> bool:
        self.__withContextCount -= 1
        if self.__withContextCount > 0:
            return True

        # args = [exc_type, exc_value, traceback]
        self.release()

        self._in_with_statement = False

        # False=propagate exceptions, True=supress them
        # you want to propagate exceptions so that the calling code can know what went wrong
        if args[0] is None:
            return True
        else:
            return False

    # to be called when the GC deletes the instance. this is important for callers that somehow dont use a context manager and forget to call the `release` method leading to dangling resources and database locks
    def __del__(self):
        self.close()

Handle = Api

def transaction(*dbArgs, **dbKwargs) -> dict:
    '''
    attempt to decorate a function in a single transaction
    @params `dbArgs`: args to be passed to Api/Handle when creating the db-handle
    @params `dbKwargs`: keyword-args to be passed to Api when creating the db-handle

    `dbArgs` and `dbKwargs` [in their order] are; 
    + `path:str`=':memory:', 
    + `tables:dict` = {}, 
    + `readonly:bool`=True, 
    + `bindingFunctions:list`=[],
    + `transactionMode:bool` = False
    NB: the exact ordering and naming of `dbArgs` and `dbKwargs` should ALWAYS be got from Api/Handle
    
    '''

    def handler(func) -> dict:
        def wrapper(*args, **kwargs) -> dict:
            reply = {'status':False, 'log':''}

            dbKwargs['transactionMode'] = True
            try:
                handle = Handle(*dbArgs, **dbKwargs)
            except:
                reply['log'] = '[TXN-E01] failed to open database'
                return reply

            if not handle.isOpen:
                reply['log'] = '[TXN-E02] failed to open database'
                return reply

            with handle:
                handle._txnDecorated = True
                kwargs['handle'] = handle
                funcReply = func(*args, **kwargs)
                if (not isinstance(funcReply,dict)) or ('status' not in funcReply):
                    reply['log'] = '[TXN-E03] decorated function does not conform to the expected return structure'
                    return reply

                if not funcReply['status']:
                    return funcReply

                txnCommitReply = handle.commitTransaction()
                if not txnCommitReply['status']:
                    return txnCommitReply

                return funcReply

        return wrapper
    return handler

if __name__=='__main__':
    with Api('/tmp/bukman/database.db2') as handle:
        print(handle.fetch('keys',['*'],'',[]))