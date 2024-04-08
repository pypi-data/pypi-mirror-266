import logging , os , inspect
from datetime import datetime
from logging.handlers import RotatingFileHandler
from .utils import getRandomKey
from .custom_env import custom_env , setupEnvironment
import json

def setGlobalHomePath( path ) :
    env = custom_env()
    env['debugger_homepath'] = path
    if not os.path.exists( path ) :
        print(f'Warning: Provided path does not exist. Path is {path}')

def setGlobalDisableOnScreen(on_screen=False) :
    env = custom_env()
    env['debugger_on_screen'] = on_screen

class DEBUGGER:
    def __init__(self, name, level='info', onscreen=True,log_rotation=3,homePath=None,id=getRandomKey(9) , global_debugger=None,disable_log_write=False):
        env = custom_env()
        env['debugger_on_screen'] = True
        self.env = env
        self.logger = logging.getLogger(name)
        self.set_level(level)
        self.LOG_SIZE_THRESHOLD = 10 * 1024 * 1024
        self.BACKUP_COUNT = log_rotation
        self.homePath = homePath
        self.onScreen= onscreen
        self.id = id
        self.stream_service = None
        self.name = name
        self.global_debugger = global_debugger
        self.type = "CUSTOM_DEBUGGER"
        setupEnvironment( 'debugger' )
        env['debugger'][id] = self
        path = self.homepath(homePath)
        f = f"[%(asctime)s]-[{name}]-[%(levelname)s]: %(message)s"
        formatter = logging.Formatter(f , datefmt='%Y-%m-%d %H:%M:%S' )
        file_handler = RotatingFileHandler(path ,  maxBytes=self.LOG_SIZE_THRESHOLD , backupCount=self.BACKUP_COUNT )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addFilter(self.on_log )
        self._disable_log_write = disable_log_write
        if onscreen : self.enable_print()
        elif not onscreen : self.disable_print()

    def updateGlobalDebugger(self , logger ) :
        '''
        this function pass the log message to other logger to write the same log message to it.
        logger must be debugger class.
        '''
        if logger.type != 'CUSTOM_DEBUGGER' :
            raise Exception(f'Invalid logger type. must pass debugger class.')
        self.global_debugger = logger


    def addStreamService( self , socketio , streampath='/debugger/stream/log' ) :
        """
        This function takes a live socketio server. it emit the log message using default path which is /debugger/stream/log
        """
        self.stream_service = socketio
        self.streampath = streampath
        
    def updateLogName( self , name ) :
        self.name = name

    def disable_log_write(self) :
        '''
        this function is used to disable the log write to file. if onScreen is enabled, logs will be displayed only on screen.
        '''
        self._disable_log_write = True

    def on_log(self , record) :
        d = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        l = f"[{d}] - [{self.name}] - [{record.levelname}]: {record.getMessage()}"
        if not self._disable_log_write :
            with open(self.homePath , 'a+') as f :
                f.write(f"{l}\n")
        if self.stream_service is not None :
            self.stream_service.emit( self.streampath , json.dumps({
                'message' : l ,
                'level' : record.levelname ,
                'msg' : record.getMessage(),
                'date' : d ,
                'id' : self.id
            }))
        if self.onScreen and self.env['debugger_on_screen'] == True :
            print(l)


    def change_log_size(self, size):
        '''
        change the size of each log file rotation.
        default is 10M
        size should be passed as MB
        '''
        self.LOG_SIZE_THRESHOLD = size
    

    def homepath(self , path=None ) :
        env = custom_env()
        getFromEnv = env.get('debugger_homepath' , None )
        if getFromEnv is not None :
            self.homePath = getFromEnv
        else :
            if path is not None :
                self.homePath = path
            else :
                self.homePath = os.getcwd()
        if not os.path.exists( self.homePath ) :
            os.makedirs( self.homePath )
        self.homePath = os.path.join( self.homePath, f'{self.name}.log' ) 
        return self.homePath

    def enable_print(self) :
        self.onScreen = True

    def disable_print(self) : 
        self.onScreen = False

    def changeHomePath( self , path ) :
        self.homePath = path

    def set_level(self, level : str):
        if 'info' in level.lower() : lvl = logging.INFO
        elif 'warn' in level.lower() : lvl = logging.WARNING
        elif 'warning' in level.lower() : lvl = logging.WARNING
        elif 'critical' in level.lower() : lvl = logging.CRITICAL
        elif 'debug' in level.lower() : lvl = logging.DEBUG
        elif 'error' in level.lower() : lvl = logging.ERROR
        else : raise ValueError('Unknown level, not one of [info,warn,warning,critical,debug,error]')
        self.logger.setLevel(lvl)

    def get_logger(self) : 
        return self.logger

    def info(self, message):
        self.logger.info(message)
        if self.global_debugger : 
            self.global_debugger.info(message)

    def debug(self, message):
        self.logger.debug(message)
        if self.global_debugger : 
            self.global_debugger.debug(message)

    def warning(self, message):
        self.logger.warning(message)
        if self.global_debugger : 
            self.global_debugger.warning(message)

    def error(self, message):
        self.logger.error(message)
        if self.global_debugger : 
            self.global_debugger.error(message)

    def critical(self, message):
        self.logger.critical(message)
        if self.global_debugger : 
            self.global_debugger.critical(message)