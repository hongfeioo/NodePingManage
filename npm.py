#!/usr/bin/python
#filename: npm.py
#---ATTENTION: change NPM.XX
from collections import defaultdict
import telnetlib
import os,sys,commands,multiprocessing
import smtplib  
import time
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  



from  messagemodule  import messageMode
from pingModule import ping

#-------config------------------
devicefile_init = '/home/NodePingManage/npm.ini'
devicetmp = '/home/NodePingManage/npm.tmp'
#--------logfile--------------
pythonlog =  '/root/mylog.txt'

npm_title = "npm.idc1"    #example:NPM.idc3
linecount = 0
MAX_process = 300       #mutiprocessing
sms_off = 0
mail_off = 0


#-------read file into idct-----------
begintime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
devtmp_exi =  os.path.exists(devicetmp)
devinit_exi =  os.path.exists(devicefile_init)

if (devtmp_exi == False)&(devinit_exi == False):
    os.system("echo "+begintime+"  NPM  no init &  no tmp file !  >> "+pythonlog)  # log to mylog.txt 
    print "no init no temp!!!"
    sys.exit()

if (devtmp_exi == False):
    devicefile = devicefile_init
    os.system("echo "+begintime+"  NPM  devicefile init !  >> "+pythonlog)  # log to mylog.txt 
else:
    devicefile = devicetmp

#sys.exit()


device_idct = defaultdict(lambda:defaultdict(dict))
file = open(devicefile)
for line in file.readlines():
    if (line.split()[0].find('#') >= 0)|(len(line) < 7): #jump the comments,jump short than 1.1.1.1
        continue
    else:
        device_idct[linecount]['ip'] = line.split()[0]
        device_idct[linecount]['name']= line.split()[1]  
        #device_idct[linecount]['lastpoll']= line.split()[2].replace('\n','')
        device_idct[linecount]['lastpoll']= line.split()[2]
        device_idct[linecount]['muti_mail']= line.split()[3]
        device_idct[linecount]['muti_phone']= line.split()[4]
        linecount += 1    #line counter
file.close()
#print "linecount:",linecount
#print device_idct




def poll(_ip):
    #print "polling"
    Stats = 'unknow'
    Stats = ping.verbose_ping(_ip)

    return Stats
    

def func(_index):
    new_idct = defaultdict(lambda:defaultdict(dict))
    new_idct = device_idct
    fuc_ip = new_idct[_index]['ip']
    fuc_name = new_idct[_index]['name']
    fuc_last = new_idct[_index]['lastpoll']
    fuc_muti_mail = new_idct[_index]['muti_mail']
    fuc_muti_phone = new_idct[_index]['muti_phone']



    print '---',_index,'/',linecount,'---',fuc_ip,'---',fuc_name,'---[',fuc_last,']---',fuc_muti_mail,fuc_muti_phone,'---'
    newstatus = poll(fuc_ip)
    #write to tmp file---
    iofile = open(devicetmp,'a')
    write_line = fuc_ip + '\t' + fuc_name +'\t'+ newstatus+'\t'+fuc_muti_mail+'\t'+fuc_muti_phone+'\n'
    iofile.write(write_line)
    iofile.close()
    #print 'write to file ok'

    if (fuc_last != newstatus):
        #print fuc_ip+' change [' +fuc_last+'] to ['+newstatus+']'
        warning_str = "Name:"+fuc_name+" IP:"+fuc_ip+" Status:"+fuc_last+"_to_"+newstatus
        os.system("echo "+begintime+" NPM node status change:"+warning_str+" >> "+pythonlog)  # log to mylog.txt 
        sendtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        warning_str_mail = "Name:"+fuc_name+"</p> IP:"+fuc_ip+"</p> Status:"+fuc_last+"_to_"+newstatus


        messageMode.send_muti_sms(fuc_muti_phone,sms_off,'NPM sms send',npm_title+' '+warning_str)
        messageMode.sendtxtmail(fuc_name+' '+npm_title,mail_off,warning_str_mail,fuc_muti_mail,sendtime)


    return 'func ok'

def main(_linecount):
    pool = multiprocessing.Pool(processes=MAX_process)
    result = []
    for index in xrange(_linecount):
        result.append(pool.apply_async(func, (index, )))
        #time.sleep(1)
    pool.close()
    pool.join()

    for res in result:
        if (res.successful() != True):
            print "Mutiprocess fail !"
            #print 'Mutiprocess ret:',res.get(),res.successful()

if __name__ == "__main__":
    os.system("echo "+begintime+"  NPM  scan  begin !  >> "+pythonlog)  # log to mylog.txt 

    os.system("rm -f "+devicetmp)
    main(linecount)


    endtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    os.system("echo "+endtime+"  NPM  Scanned over !  >> "+pythonlog)  # log to mylog.txt 
