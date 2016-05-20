# -*- coding: utf8 -*-
__author__ = 'Jill'

import os
import logging
import shutil

class Jlog:
    __pathtoscript=os.getcwd()
    __maxfilesizeMB=10
    __logfilename='debug.log'
    __fullfilepath=__pathtoscript+'\\'+__logfilename
    __needprinttext=False

    def setlogfilename(self, logfilename='debug.log'):
        self.__logfilename=logfilename
        self.__fullfilepath=self.__pathtoscript+'\\'+self.__logfilename

    def setmaxfilesizeMB(self, maxfilesizeMB=10):
        self.__maxfilesizeMB=maxfilesizeMB

    def setneedprinttext(self, needprinttext=False):
        self.__needprinttext=needprinttext

    def message(self, text, typemes=1):
        if self.__needprinttext:
            print(text)

        if os.path.exists(self.__fullfilepath): #Если файл существует - проверим его размер
            #Если файл больше максимального значения - переименовываем
            if os.path.getsize(self.__fullfilepath)>self.__maxfilesizeMB*1024**2:
                shutil.move(self.__fullfilepath,self.__fullfilepath+'.bak')

        logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u''+self.__logfilename)
        if typemes==1:
            logging.info(text)
        else:
            logging.error(text)

class JpassHider:
    def crypt(self, passwd):
        encrpasswd=''

        lenthpasswd=len(passwd)
        if lenthpasswd>0:
            i=lenthpasswd-1
            codepasswd=''
            while not(i<0): #Читаем фразу в обратную сторону и преобразовываем
                code=ord(passwd[i])
                newcode=4*code**2-20*code+25
                delimcode=34
                codepasswd+=str(newcode)+str(delimcode)
                i-=1

            i=0
            lenthcodepasswd=len(codepasswd)
            while i<lenthcodepasswd:
                codeforencr=40+int(codepasswd[i])
                encrpasswd+=chr(codeforencr)
                i+=1
        return encrpasswd

    def decrypt(self, encrpasswd):
        passwd=''
        lenthencrpasswd=len(encrpasswd)
        i=0
        codepasswd=''
        while i<lenthencrpasswd:
            code=ord(encrpasswd[i])-40
            codepasswd+=str(code)
            i+=1

        #Распарсим строку и разобьем на числа
        arraypasswd=[]
        lenthcodepasswd=len(codepasswd)
        strsym=''
        i=0
        while i<lenthcodepasswd:
            if codepasswd[i:i+2]=='34':
                arraypasswd.append(int(strsym))
                strsym=''
                i+=1
            else:
                strsym+=codepasswd[i]
            i+=1

        i=len(arraypasswd)-1
        while not(i<0):
            code=arraypasswd[i]
            oldcode=int((code**0.5+5)/2)
            passwd+=chr(oldcode)
            i-=1
        return passwd