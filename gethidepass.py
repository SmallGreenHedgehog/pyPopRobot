# -*- coding: utf8 -*-
__author__ = 'Jill'

import jillmodule

passwd=input('Введите отрытый пароль:')
if len(passwd)<1:
    print('Слишком короткий пароль. Перезапустите скрипт и попробуйте снова.')
else:
    passhider=jillmodule.JpassHider()
    encrpasswd=passhider.crypt(passwd)
    print('Закрытый пароль: "'+encrpasswd+'"')
input('Нажмите любую клавишу.')
