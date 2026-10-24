"Analyse places.sqlite from firefox profile database location"
from typing import Any, Dict


# taken from MuiCache, needed in every parcer for compatibility with Solver.
# TODO: rewrite it for firefox's profile database parsing
class Parser:
    """
    Класс представляет собой интерфейс для подготовки данных и инициализации классов логики обработки данных, а также записи их в базу данных SQLite. 
    В конструкторе класса принимается словарь параметров, который используется для настройки работы парсеров. 
    Также определяются поля записей таблицы Data БД SQLite.
    """    
    def __init__(self,parameters:dict):  
        self.__parameters:dict = parameters 

        self.__recordFields:dict = {
            'UserName':'TEXT',
            'Name':'TEXT',
            'Company':'TEXT',
            'Parameter':'TEXT',
            'Value':'TEXT',
            'DataSource':'TEXT'
         }
            
    async def Start(self) -> Dict:
        """
        Метод начинает процесс обработки данных, вызывая инициализированный парсер. 

        Returns:
            Dict: результат обработки данных
        """        
        storage:str = self.__parameters.get('STORAGE')
        outputWriter:Any = self.__parameters.get('OUTPUTWRITER')
        
        if not self.__parameters.get('DBCONNECTION').IsConnected():
            return # Модуль не может обрабатывать информацию - нет соединения с БД вывода
        
        fields:dict = {
            'UserName':('Имя пользователя',140,'string','Имя пользователя'),
            'Name':('Полный путь / Название',430,'string','Полный путь / Название'),
            'Company':('Производитель ПО', 150,'string', 'Производитель ПО'),
            'Parameter':('Параметр',-1,'string', 'Параметр'),
            'Value':('Описание',430,'string', 'Описание'),
            'DataSource':('Источник данных',230,'string','Источник данных')
        }
        
        HELP_TEXT:str = self.__parameters.get('MODULENAME') + """:
        Списки задания имени программы/библиотеки/иного ресурса 
        в соответствии с языком системы
                        
        Извлекается из веток:
        Windows XP:  
        HKU\\<SID>\\Software\\Microsoft\\Windows\\ShellNoRoam\\MUICache

        Windows 7, 8, 8.1, 10:  
        HKU\\<SID>\\Software\\Classes\\Local Settings\\MuiCache\\<BYTE>\\B1A07F78
        HKU\\<SID>_Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache

        Переменные среды извлекаются из:
        HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SecEdit\\EnvironmentVariables
        """
    
        # Таблица Info
        infoTableData:dict = {
            'Name':self.__parameters.get('MODULENAME'),
            'Help':HELP_TEXT,
            'Timestamp':self.__parameters.get('CASENAME'), # Время начала обработки массива - имя case
            'Vendor':'LabFramework'
        }
        
        # Задать параметры вывода и создать таблицы
        outputWriter.SetFields(fields,self.__recordFields)
        outputWriter.CreateDatabaseTables()

        # Обработать профили
        if self.__muiCacheParser is not None:
            self.__muiCacheParser.SetUserProfilesList(self.__parameters.get('USERPROFILES',{}))
            await self.__muiCacheParser.Start()

            # Удалить временные таблицы
            outputWriter.RemoveTempTables()
        
            # Создать индексы
            await outputWriter.CreateDatabaseIndexes(self.__parameters.get('MODULENAME'))
        
            # Завершить формирование БД
            outputWriter.SetInfo(infoTableData)
            outputWriter.WriteMeta()
            # Закрыть соединение БД
            await outputWriter.CloseOutput()
            
        return {self.__parameters.get('MODULENAME'):outputWriter.GetDBName()}
