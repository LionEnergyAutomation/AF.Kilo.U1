import re
import urllib.request
import hashlib
import time


class netgear_switch:

    def __init__(self):
        # set up the variables that change
        self.port_number = 0
        self.port_matrix = [[False]*3 for i in range(5)]

        # set up information dictionary
        #
        self.config = {
            'switch_ip': '172.16.0.200',
            'passwd': 'Testing1234',
            'port': '',
            # If True, will also print out the status of the switch ports.
            'port_status': '',
            # The pseudo-random 'rand' field from the switch, used to 'encode' plaintext passwd.
            'type'
            # An input var produced from the Switch's web server, needed to identify the switch
            'rand': '',
            # An input var produced from the Switch's web server, needed to change status.
            'hash_val': '',
            # The passwd, interleaved with the supplied passwd.
            'passwd_merged': '',
            # The md5 hash of passwd_enc, what we'll actually post to the switches web interface.
            'passwd_md5': '',
            # The cookie we get back on a successful login.
            'auth_cookie': '',
            'sleep_between_calls': 1,  # Time in seconds to sleep between HTTP calls
        }

        # set the type and rand
        _contents: object = urllib.request.urlopen(
            "http://%s/login.cgi" % self.config['switch_ip']).read().decode("utf-8").replace('\n', '')
        time.sleep(self.config['sleep_between_calls'])
        _tmp_type = re.findall("^.*title>NETGEAR.(.*)</title>.*$", _contents)
        _tmp_rand = re.findall("^.*value=.(\d+). disabled.*$", _contents)
        try:
            _type = (_tmp_type[0])
        except Exception as ex:
            print("Error reading 'type' from switch:", ex)
            exit()
        try:
            _rand = (_tmp_rand[0])
        except Exception as ex:
            print("Error reading 'rand' from switch:", ex)
            exit()
        self.config['type'] = _type
        self.config['rand'] = _rand

        # set password
        i = 0
        for c in self.config['rand']:
            if i < len(self.config['passwd']):
                self.config['passwd_merged'] += self.config['passwd'][i]
            i += 1
            self.config['passwd_merged'] += c
        if i < len(self.config['passwd']):
            self.config['passwd_merged'] += self.config['passwd'][-(len(self.config['passwd']) - i):]
        self.config['passwd_md5'] = hashlib.md5(self.config['passwd_merged'].encode()).hexdigest()
        data = {
            'password': self.config['passwd_md5'],
        }

        # check attempt to login
        data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request("http://%s/login.cgi" % self.config['switch_ip'], data=data)
        resp = urllib.request.urlopen(req)
        time.sleep(self.config['sleep_between_calls'])
        _success_check = resp
        _success_check = _success_check.read().decode("utf-8").replace('\n', '')

        # check for errors
        if 'The password is invalid' in _success_check:
            print("Netgear: ERROR: Invalid Password")
            exit()
        if 'The maximum number of attempts has been reached' in _success_check:
            print("Netgear: The maximum number of attempts has been reached. Wait a few minutes and then try again")
            exit()
        if 'The maximum number of sessions has been reached' in _success_check:
            print("Netgear: The maximum number of sessions has been reached. Wait a few minutes and then try again")
            exit()

        # Example cookie:
        _cookie = re.findall("^(.*SID=.*);.*;HttpOnly$", str(resp.info()['Set-Cookie']))
        try:
            _cookie = (_cookie[0])  # De-tuplify, and convert to list
            self.config['auth_cookie'] = _cookie
        except Exception as ex:
            print("Netgear: Error reading Cookie:", ex)
            exit()
        if not self.config['auth_cookie']:
            print("Netgear: Unable to get cookie!")
            exit()

    def retrieve_data(self, port):
        # define the request
        print("retriveing data")
        self.config['port'] = str(port)
        req = urllib.request.Request("http://%s/status.cgi" % self.config['switch_ip'])
        req.add_header("Cookie", self.config['auth_cookie'])

        # make the request
        _contents = urllib.request.urlopen(req)
        _success_check = _contents
        _success_check = _success_check.read().decode("utf-8")
        _status_check_list = _success_check.splitlines()

        # sift through data and organize it how I want
        port_numb = 1
        print("doing for loop")
        for element in _status_check_list:
            if 'name="port' in element:
                port_numb = int(element[element.index('name="port') + 10])
                self.port_matrix[port_numb - 1][0] = port_numb
            if self.port_matrix[port_numb - 1][0]:
                if '<input type="hidden" value="Down"' in element and not self.port_matrix[port_numb - 1][1]:
                    self.port_matrix[port_numb - 1][1] = "Down"
                if '<input type="hidden" value="Up"' in element and not self.port_matrix[port_numb - 1][1]:
                    self.port_matrix[port_numb - 1][1] = "Up"
                if '<td class="def" sel="select">Disable' in element and not self.port_matrix[port_numb - 1][2]:
                    self.port_matrix[port_numb - 1][2] = "disabled"
                if '<td class="def" sel="select">Auto' in element and not self.port_matrix[port_numb - 1][2]:
                    self.port_matrix[port_numb - 1][2] = "Auto"
        return_downup = self.port_matrix[port - 1][1]
        return_status = self.port_matrix[port - 1][2]
        self.port_matrix = [[False] * 3 for i in range(5)]

        # other checks
        _success_check = _success_check.replace('\n', '')
        _tmp = re.findall("^.*id=.hash. value=.(\d+).>.*$", _success_check)
        try:
            _tmp = (_tmp[0])  # De-tuplify, and convert to list
            self.config['hash_val'] = _tmp
        except Exception as ex:
            print("Netgear GS305E script: Error reading 'hash' from switch:", ex)
            exit()

        return return_downup, return_status

    def set_port(self, port, status):
        self.retrieve_data(port)
        self.config['port'] = str(port)
        print(self.config['port'])
        _port = 'port' + self.config['port']
        _speed = '1' if status == 'enable' else '2'
        print("speed is " + str(_speed))
        data = {
            _port: 'checked',
            'SPEED': _speed,
            'FLOW_CONTROL': '2',
            'hash': self.config['hash_val'],
        }
        print(data)
        data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request("http://%s/status.cgi" % self.config['switch_ip'], data=data)
        req.add_header("Cookie", self.config['auth_cookie'])
        resp = urllib.request.urlopen(req)
        time.sleep(self.config['sleep_between_calls'])

