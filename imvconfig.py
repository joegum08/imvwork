'''
SIEMENS IOT2020 config script
created by sm4llk!d 20201124 

reference library
argparse 
pyserial
time
'''

import serial, time, argparse, json


USERS = [
    ('ftpuser','ftpuser'),
    ('smallkid', 't0mcat')
]


def read_serial(ser):
    line_data = ''
    while ser.in_waiting > 0:
        line_data  += ser.read().decode('UTF-8')
    return line_data

def send_command(ser, cmd, timeout = 1):
    line_data = ''
    ser.write(cmd.encode())
    time.sleep(timeout)
    line_data  = read_serial(ser) 
    return line_data


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip',help='Please Specify IP Address eg 192.168.0.1')
    parser.add_argument('--gateway',help='Please Specify Gateway Address eg 192.168.0.1')
    parser.add_argument('--hostname',help='Please specify Hostname ')
    parser.add_argument('-u',help='Username')
    parser.add_argument('-p',help='Password')
    parser.add_argument('--port', required=False, help='Port')
    parser.add_argument('--get', required=False, help='Get Info')
    parser.add_argument('--gethostname', action='store_true', help='Get hostname')
    parser.add_argument('--getip', action='store_true', help='Get IP')
    parser.add_argument('--getstatus', action='store_true', help='Get status')
    parser.add_argument('--configfile',  help='Config file')
    
    args = parser.parse_args()

    # print(args)

    COM_PORT = 'COM11' #change this based on device manager


    if(args.port):
        COM_PORT = args.port

    ser = serial.Serial(port=COM_PORT, baudrate=115200, timeout=0)
    line_data = ''

    ser.write("\r\n".encode())
    time.sleep(1)
    line_data = read_serial(ser)

    if('login' in line_data):
        # print(line_data)
        print (send_command(ser,'root\r\n'))
    time.sleep(1)

    # print(send_command(ser, 'ls -lah\r\n',2))
    # print(send_command(ser, 'ifconfig eth0 | grep "inet " \r\n'))
    if(args.ip):
        print('Updating IP Address.....')
        print(send_command(ser,'sed -i "s/address .*/address {}/g" /etc/network/interfaces\r\n'.format(args.ip)))
        print(send_command(ser,'sed -i "s/gateway .*/gateway {}/g" /etc/network/interfaces\r\n'.format(args.gateway)))
        print(send_command(ser,'/etc/init.d/networking restart\r\n'.format(args.ip),timeout=5))
    
    if(args.hostname):
        print('Updating Hostname.....')
        print(send_command(ser,'sed -i "s/.*/{}/g" /etc/hostname\r\n'.format(args.hostname)))
        print(send_command(ser,'cat /etc/hostname\r\n'))
        print(send_command(ser,'reboot\r\n'))

    
    if(args.u and args.p):
        print('Add User {}'.format(args.u))
        print(send_command(ser,'useradd -m {0}\r\n'.format(args.u),timeout=2))
        print(send_command(ser,'passwd -q {0}\r\n'.format(args.u),timeout=2))
        print(send_command(ser,'{0}\r\n'.format(args.p),timeout=2))
        print(send_command(ser,'{0}\r\n'.format(args.p),timeout=2))

    if(args.get == 'status' or args.getstatus):
        print('Getting Status....')
        tmpstr = send_command(ser,'\r\n',timeout=2)
        print(tmpstr)

    if(args.get == 'ip' or args.getip):
        print('Getting IP Address....')
        tmpstr =send_command(ser, 'ifconfig eth0 | grep "inet " \r\n') 
        print('IP : {}'.format(tmpstr.split('\r\n')[1]))
    
    if(args.get == 'hostname' or  args.gethostname):
        print('Getting Hostname....')
        tmpstr = send_command(ser, 'cat /etc/hostname\r\n')
        print('Hostname : {}'.format(tmpstr.split('\r\n')[1]))

    if(args.get == 'configfile' or args.configfile):
        with open(args.configfile,"rb") as f:
            imv_config = json.load(f)
            print(imv_config)
            print('Updating IP Address.....')
            print(send_command(ser,'sed -i "s/address .*/address {}/g" /etc/network/interfaces\r\n'.format(imv_config['ipaddress'])))
            print(send_command(ser,'sed -i "s/gateway .*/gateway {}/g" /etc/network/interfaces\r\n'.format(imv_config['gateway'])))
            print(send_command(ser,'/etc/init.d/networking restart\r\n',timeout=5))
            print('Done.....')
            time.sleep(1)

            for u in imv_config['users']:
                print('Add User {}'.format(u['username']))
                usr = send_command(ser,'useradd -m {0}\r\n'.format(u['username']),timeout=2)
                print(usr)
                if not 'exists' in usr:
                    print(send_command(ser,'passwd -q {0}\r\n'.format(u['username']),timeout=2))
                    print(send_command(ser,'{0}\r\n'.format(u['password']),timeout=2))
                    time.sleep(1)   
                    print(send_command(ser,'{0}\r\n'.format(u['password']),timeout=2))
                    time.sleep(1)   
                # print(u['username'])

            print('Updating Hostname.....')
            print(send_command(ser,'sed -i "s/.*/{}/g" /etc/hostname\r\n'.format(imv_config['hostname'])))
            print(send_command(ser,'cat /etc/hostname\r\n'))
            print(send_command(ser,'reboot\r\n'))


        

    #cleanup
    print(send_command(ser, 'exit\r\n'))
    ser.close()

if  __name__ == '__main__':
    main()
