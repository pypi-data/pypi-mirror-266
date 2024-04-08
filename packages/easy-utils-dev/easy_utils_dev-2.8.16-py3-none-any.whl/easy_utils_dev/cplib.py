
from easy_utils_dev.debugger import DEBUGGER
import requests, time
import urllib3
from threading import Thread
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version = '1.0 build 22032024'

class CommonPlatformLib :
    def __init__(self, address,  username , password,port=8443 ,debug_name='cplib', token_refresh_period=1700, client_id='',client_secret='') -> None:
        '''
        address: string
        token_refresh_period number , string
        password : string
        port : int
        debug_name : string
        '''
        self.logger = DEBUGGER(debug_name)
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.users = []
        self.autoRefreshTokenPeriod = token_refresh_period
        self.client_id=client_id
        self.client_secret=client_secret
        self.baseUrl = self.updateBaseUrl(address , port )
        self.sessions = {}

    def set_debug_level(self , level ) :
        self.logger.set_level(level)    

    def updateBaseUrl( self, address, port ) :
            self.baseUrl = f"https://{address}:{port}/wavesuite/cp/admin"
            self.logger.debug(f'baseUrl={self.baseUrl}')
            self.address = address
            self.port = port
            return self.baseUrl

    def disableOnScreenDebugPrint( self ) :
        self.logger.disable_print()
    
    def enableOnScreenDebugPrint( self ) :
        self.logger.enable_print()

    def autoRefreshToken(self) :
        self.logger.info(f'Auto refresh token started. waiting for {self.autoRefreshTokenPeriod} refresh ...')
        time.sleep(self.autoRefreshTokenPeriod )
        self.logout()
        self.authentication()
        self.logger.info(f'Auto Token refresh completed.')


    def authentication(self,autoRefresh=True) :
        self.logger.info('Starting to authenticate with CP platform ..')
        url = f'{self.baseUrl}/api/v1/authenticate'
        self.logger.info(f"Authentication Params: username={self.username} password=********")
        self.logger.debug(f"Authentication Params: username={self.username} password={self.password} url={url}")
        payload = {
            'grant_type': 'client_credentials',
            'username': self.username ,
            'password': self.password,
            'client_id': self.client_id ,
            'client_secret': self.client_secret
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded' }
        self.logger.debug(f'Authentication Payload: {payload}')
        response = requests.post(url , data=payload , headers=headers , verify=False)
        self.logger.info(f'Authentication response code={response.status_code}')
        self.logger.debug(f'raw response in authentication {response.text}')
        if response.status_code != 200 :
            self.logger.error(f'Authentication failed. status_code={response.status_code} {response.text}')
            raise Exception(f'Authentication Failure {response.status_code}')
        response = response.json()
        self.accessToken = response['access_token']
        self.refreshToken = response['refresh_token']
        self.bearertoken = f"Bearer {self.accessToken}"
        if autoRefresh :
            self.logger.debug(f'auto refresh is enabled. starting auto refresh thread ..')
            t = Thread( target=self.autoRefreshToken )
            t.start()
        self.logger.debug(f'returning access token {self.accessToken}')
        return self.accessToken
        
    def getAccessToken(self) :
        return self.accessToken
    
    def getRefreshToken(self) :
        return self.refreshToken
    
    def getBearerToken(self) :
        return self.bearertoken

    def getAuthorizationToken(self) :
        return self.getBearerToken()

    def getHeaders( self , headers={}, json=True , inject_auth=True ) :
        if inject_auth :
            _h = {'Authorization' : self.getBearerToken() }
        else : 
            _h = {}
        self.logger.debug(f'request headers is {_h}')
        if json :
            self.logger.debug(f"json content type is Enabled. adding Content-type as application/json ")
            _h.update({'Content-type': 'application/json'})
        _h.update(headers)
        return _h

    def logout(self) :
        self.logger.info('Starting to logout form CP platform ..')
        url = f'{self.baseUrl}/api/v1/logout'
        self.logger.info(f"Authentication Params: username={self.username}.")
        payload = {'refreshToken' : self.refreshToken }
        headers = self.getHeaders()
        self.logger.debug(f'Logout out headers {headers}')
        self.logger.debug(f'Logout out payload {payload}')
        response = requests.post(url , data=payload , headers=headers , verify=False)
        self.logger.debug(f'raw response in logout {response.text}')
        self.logger.info(f'Logout status code={response.status_code}')
        return response

    def getRegisteredClients(self) :
        jobName = 'registered clients'
        self.logger.info(f"Get {jobName} from CP ...")
        url= f"{self.baseUrl}/api/v1/clients/public-clients"
        headers = self.getHeaders()
        self.logger.debug(f'Get {jobName} headers = {headers}')
        response = requests.get(url , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json()
        else :
            self.logger.error(f'Error getting {jobName}  {response.text}')
            return []

    def getCommonPlatformInfo(self) :
        jobName = 'CP Information'
        self.logger.info(f"Get {jobName} from CP ...")
        url= f"{self.baseUrl}/api/v1/server/info"
        headers = self.getHeaders(inject_auth=False)
        self.logger.debug(f'Get {jobName} headers = {headers}')
        response = requests.get(url , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json()
        else :
            self.logger.error(f'Error getting {jobName}  {response.text}')
            return {}

    def getCommonPlatformRelease(self) :
        return self.getCommonPlatformInfo().get('version')

    def getCommonPlatformBuild(self) :
        return self.getCommonPlatformInfo().get('build')

    def getCommonPlatformName(self) :
        return self.getCommonPlatformInfo().get('name')


    def getCreateNewUserTemplate(self) :
        '''
        {
            "name": "email@email.com",
            "address": None,
            "phoneNumber": None,
            "contact": None,
            "loginAttemptLocked": None,
            "enabled": True,
            "localUser": False,
            "email": "email@email.com",
            "lastLoginTime": None,
            "numberOfFailedLoginAttempts": None,
            "roles": [
                "ROLE_ADMIN"
            ],
            "username": "email@email.com",
            "password": None,
            "newPassword": None,
            "userPreferences": None,
            "status": "Active"
        }'''
        return {
            "name": "email@email.com",
            "address": None,
            "phoneNumber": None,
            "contact": None,
            "loginAttemptLocked": None,
            "enabled": True,
            "localUser": False,
            "email": "email@email.com",
            "lastLoginTime": None,
            "numberOfFailedLoginAttempts": None,
            "roles": [
                "ROLE_ADMIN"
            ],
            "username": "email@email.com",
            "password": None,
            "newPassword": None,
            "userPreferences": None,
            "status": "Active"
        }

    def getUserTemplateKeysAsArray(self) :
        return list(self.getCreateNewUserTemplate().keys())

    def getRoles(self) :
        jobName = 'user roles'
        self.logger.info(f"Get {jobName} from CP ...")
        url= f"{self.baseUrl}/api/v1/roles?start=0length=300&direction=asc"
        headers = self.getHeaders()
        self.logger.debug(f'Get {jobName} headers = {headers}')
        response = requests.get(url , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json()
        else :
            self.logger.error(f'Error getting {jobName}  {response.text}')
            return []
        
    def getUsers(self) :
        jobName = 'get users'
        self.logger.info(f"Get {jobName} from CP ...")
        url= f"{self.baseUrl}/api/v1/users"
        headers = self.getHeaders()
        self.logger.debug(f'Get {jobName} headers = {headers}')
        response = requests.get(url , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json().get('items')
        else :
            self.logger.error(f'Error getting {jobName}  {response.text}')
            return []
        
    def deleteUser(self , userId ) :
        jobName = f'delete user userId={userId}'
        self.logger.info(f"Delete {jobName} from CP ...")
        url= f"{self.baseUrl}/api/v1/users/{userId}"
        headers = self.getHeaders()
        self.logger.debug(f'{jobName} headers= {headers} userid= {userId}')
        response = requests.delete(url , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 204 :
            self.logger.debug(f'response is 204 , return the response')
            return True
        else :
            self.logger.error(f'Error getting {jobName}  {response.text}')
            return False


    def getUserId(self, searchKey='username' , searchValue=None ) :
        self.logger.info(f'Getting user id by searchKey={searchKey} searchValue={searchValue}')
        template = self.getUserTemplateKeysAsArray()
        if not searchKey in template :
            self.logger.error(f'{searchKey} not a valid searchKey. possible keys are: {self.getUserTemplateKeysAsArray()}')
            return False
        users = self.getUsers()
        userId = None
        userEntry={}
        for user in users :
            if user.get(searchKey) == searchValue :
                userId = user.get('id')
                userEntry=user
                break
        if not userId :
            self.logger.error(f'User not found by searchKey={searchKey} searchValue={searchValue}')
            userId= False
        else :
            self.logger.debug(f'user id is {userId} found in {userEntry}')
        return userId

    def createUser(self, payload : dict , internal=None) :
        '''
        self.getCreateNewUserTemplate() can return => 
        {
            "name": "email@email.com",
            "address": None,
            "phoneNumber": None,
            "contact": None,
            "loginAttemptLocked": None,
            "enabled": True,
            "localUser": False,
            "email": "email@email.com",
            "lastLoginTime": None,
            "numberOfFailedLoginAttempts": None,
            "roles": [
                "ROLE_ADMIN"
            ],
            "username": "email@email.com",
            "password": None,
            "newPassword": None,
            "userPreferences": None,
            "status": "Active"
        }'''
        jobName = 'create user'
        self.logger.info(f"{jobName} from CP ...")
        if internal != None and ( internal == True or internal == False) :
            payload['localUser'] = internal
        url= f"{self.baseUrl}/api/v1/users"
        headers = self.getHeaders()
        self.logger.debug(f' {jobName} headers= {headers} payload= {payload}')
        response = requests.post(url , data=payload , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json().get('id')  , response.json()
        else :
            self.logger.error(f'Error {jobName}  {response.text}')
            return False , {}
        
    def updateUser(self, userId ,payload : dict , internal=None) :
        '''
        self.getCreateNewUserTemplate() can return => 
        {
            "name": "email@email.com",
            "address": None,
            "phoneNumber": None,
            "contact": None,
            "loginAttemptLocked": None,
            "enabled": True,
            "localUser": False,
            "email": "email@email.com",
            "lastLoginTime": None,
            "numberOfFailedLoginAttempts": None,
            "roles": [
                "ROLE_ADMIN"
            ],
            "username": "email@email.com",
            "password": None,
            "newPassword": None,
            "userPreferences": None,
            "status": "Active"
        }'''
        jobName = f'udpating user {userId}'
        self.logger.info(f"{jobName} from CP ...")
        if internal != None and ( internal == True or internal == False) :
            payload['localUser'] = internal
        url= f"{self.baseUrl}/api/v1/users/{userId}"
        headers = self.getHeaders()
        self.logger.debug(f' {jobName} headers= {headers} payload= {payload}')
        response = requests.put(url , data=payload , headers=headers , verify=False)
        self.logger.info(f'{jobName} response code={response.status_code}')
        self.logger.debug(f'raw response in {jobName} {response.text}')
        if response.status_code == 200 :
            self.logger.debug(f'response is 200 , return the response')
            return response.json().get('id')  , response.json()
        else :
            self.logger.error(f'Error {jobName}  {response.text}')
            return False , {}
        

        
if __name__ == '__main__':
    pass



