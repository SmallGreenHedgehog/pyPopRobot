import os
import socks
import poplib
from email import message_from_bytes
from email import header
from email.utils import parseaddr, unquote
from jillmodule import Jlog, JpassHider


class HeadersHandler(object):
    """ Парсер заголовков сообщения """

    def __init__(self, msg):
        self._msg = msg

    def _decode(self, raw):
        """ Декодирование 'сырого' заголовка """
        parts = []
        for txt, charset in header.decode_header(raw):
            if charset:
                txt = txt.decode(charset, "ignore")
            else:
                txt = txt.decode("utf-8") if isinstance(txt, bytes) else txt
            parts.append(txt)
        return "".join(parts)

    def _get(self, key):
        raw = self._msg.get(key)
        if raw is None:
            return None
        if isinstance(raw, header.Header):
            raw = raw.encode()
        raw = raw.replace("?==?", "?= =?")
        return self._decode(raw)

    @property
    def mesid(self):
        return self._get("Message-Id")

    @property
    def subject(self):
        return self._get("subject")

    @property
    def sender(self):
        s = self._get("from")
        name, addr = parseaddr(s)
        s = unquote(name)
        if s.startswith("=?"):
            name = self._decode(s)
        return name, addr


def getparamsfromstring(line):
    params = []
    lenline = len(line)
    i = 0
    par = ''
    while (i < lenline) and not (line[i] == '\n'):
        sym = line[i]
        if sym == ';':
            params.append(par)
            par = ''
        else:
            par += sym
        i += 1
    return params


def getlinesfromconfig():
    conffile = open(conffilepath)
    conflines = conffile.readlines()
    conffile.close()
    return conflines


def getfiles(POPServer, POPPort, POPLogin, POPPass, NeedToRemoveMail, localDirForAttach, localDirForLetters,
             FromInclude, ThemeIclude):
    log.message('*********************************************')
    log.message('Получение файлов:')
    success = 1

    connection = poplib.POP3(POPServer, POPPort)
    connection.user(POPLogin)
    connection.pass_(POPPass)

    emails, total_bytes = connection.stat()
    print("{0} emails in the inbox, {1} bytes total".format(emails, total_bytes))

    msg_list = connection.list()
    print(msg_list)

    for i in range(emails):
        response = connection.retr(i + 1)
        raw_message = response[1]

        str_message = message_from_bytes(b'\n'.join(raw_message))

        headerS = HeadersHandler(str_message)
        messageid = headerS.mesid
        from_mail_name, from_mail_addr = headerS.sender
        subject_mail = headerS.subject

        print(i)
        print(messageid)
        print(from_mail_name + ' | ' + from_mail_addr)
        print(subject_mail)

        # TODO не обрабатывать повторно
        # TODO реализовать сохранение тела письма и вложений

    connection.quit()
    return success


def processline(params):
    POPServer = params[0]
    POPPort = params[1]
    POPLoginH = params[2]
    POPPassH = params[3]

    if usehideloginpass == 1:
        POPLogin = passhider.decrypt(POPLoginH)
        POPPass = passhider.decrypt(POPPassH)
    else:
        POPLogin = POPLoginH  # Логин и пароль храним в открытом виде
        POPPass = POPPassH

    NeedToRemoveMail = params[4]
    localDirForAttach = params[5]
    localDirForLetters = params[6]
    FromInclude = params[7]
    ThemeIclude = params[8]
    SigFilePath = params[9]
    SigText = params[10]

    # Получим файлы
    succes = getfiles(POPServer, POPPort, POPLogin, POPPass, NeedToRemoveMail, localDirForAttach, localDirForLetters,
                      FromInclude, ThemeIclude)

    if succes == 1:  # Если задание выполнено успешно - генерируем сигнальный файл по необходимости
        if not (SigText == ''):
            log.message('+++++++++++++++++++++++++')
            log.message('Генерация сигнального файла.')
            if SigFilePath == '':
                SigFilePath = pathtoscript + '\mes.sig'
            succes = 1
            try:
                sigfile = open(SigFilePath, 'a')
                sigfile.write(SigText + '\n')
                sigfile.close()
                sigfile = ''
            except:
                succes = 0
            if succes == 1:
                log.message('Сигнальный файл (' + SigFilePath + ';' + SigText + ') успешно сгенерирован.')
            else:
                log.message('Ошибка генерации сигнального файла.', 0)
            log.message('+++++++++++++++++++++++++')


def initial():
    global usehideloginpass
    global passhider
    global pathtoscript
    global conffilepath
    global confproxyfilepath
    global log

    usehideloginpass = 1

    passhider = JpassHider()
    log = Jlog()
    log.setmaxfilesizeMB(5)
    log.setneedprinttext(True)
    log.setlogfilename('poprobot.log')

    log.message('')
    log.message('====================================')
    log.message('START SCRIPT')
    succes = 1
    pathtoscript = os.getcwd()
    conffilepath = pathtoscript + '\config.cfg'
    confproxyfilepath = pathtoscript + '\proxy.cfg'

    if not (os.path.exists(conffilepath)):  # Проверяем наличие основного конфига
        succes = 0
        log.message('Ошибка! Отсутсвует файл "' + conffilepath + '" конфига.')

    if os.path.exists(confproxyfilepath):  # Конфиг прокси существует
        log.message('Найден конфиг прокси. Подгружаем параметры.')
        correct = 1

        confproxyfile = open(confproxyfilepath)
        confproxylines = confproxyfile.readlines()
        countlines = len(confproxylines)
        confproxyfile.close()
        if countlines < 1:
            correct = 0

        if correct == 1:
            proxyline = confproxylines[0]
            proxyparams = getparamsfromstring(proxyline)
            if len(proxyparams) < 4:
                correct = 0

        if correct == 1:
            proxyType = proxyparams[0]
            proxyHost = proxyparams[1]
            proxyPort = proxyparams[2]
            proxyLoginH = proxyparams[3]
            proxyPassH = proxyparams[4]
            if usehideloginpass == 1:
                proxyLogin = passhider.decrypt(proxyLoginH)
                proxyPass = passhider.decrypt(proxyPassH)
            else:
                proxyLogin = proxyLoginH  # Логин и пароль храним в открытом виде
                proxyPass = proxyPassH

            if proxyType.lower() == 'http':
                sockproxyType = socks.PROXY_TYPE_HTTP
            elif proxyType.lower() == 'sock5':
                sockproxyType = socks.PROXY_TYPE_SOCKS5
            try:
                socks.setdefaultproxy(sockproxyType, proxyHost, int(proxyPort), True, proxyLogin, proxyPass)
            except:
                succes = 0
            if succes == 1:
                log.message('Работаем через ' + proxyType + ' прокси (' + proxyHost + ':' + proxyPort + ').')
        else:
            succes = 0
            log.message('Ошибка! Конфиг прокси не корректен!')
    else:
        log.message('Конфиг прокси не найден. Работаем с прямым соединением.')
    return succes


if initial():  # Инициализация
    conflines = getlinesfromconfig()  # Получаем строки из конфига
    countlines = len(conflines)

    if countlines > 0:  # Построчно получаем параметры
        for i in range(0, countlines):
            line = conflines[i]
            params = getparamsfromstring(line)

            # Теперь перезапишем параметры строки в переменные
            if len(params) > 9:
                processline(params)
            else:
                log.message('Недопустимое количество параметров в строке №' + str(i + 1) + '!', 0)
else:
    log.message('Инициализая параметров скрипта не удачна! Проверьте логи и конфигурационные файлы!', 0)
