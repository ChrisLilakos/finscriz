#! python3
# finscriz.py - scrapes certain data from finviz and sends an email of it
try:  # imports
    from pathlib import Path as path
    # from pyhelpers.ops import is_downloadable  # results in this warning:
        # C:\Users\chris\AppData\Local\Programs\Python\Python39\lib\site-packages\fuzzywuzzy\fuzz.py:11:
        # UserWarning: Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning
        # warnings.warn('Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning')
            # error arose when i did "pip install python-Levenshtein" in the cmd
    import lxml, itertools, requests, datetime, re, shutil, sys, os, time
# browser start off/up
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from selenium.common import exceptions as selErr
    from selenium.webdriver.common.keys import Keys as keys
    from selenium.webdriver.support.ui import WebDriverWait
    def xpath_soup(element):  # copied from github
        """Generate xpath of soup element
        :param element: bs4 text or node
        :return: xpath as string"""
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            """
            @type parent: bs4.element.Tag
            """
            previous = itertools.islice(parent.children, 0, parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)
    # '# MNE!*' = may have to edit on your end
    browser = webdriver.Edge(executable_path=r"C:\Users\chris\OneDrive\Desktop\edgedriver_win64\msedgedriver.exe")  #MNE
        # "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        # r"C:\Users\chris\OneDrive\Desktop\edgedriver_win64\msedgedriver.exe"
    wait, cnt, todayte, finLink = WebDriverWait(browser, 1), 0, datetime.datetime.today().date(), \
                          "https://finviz.com/screener.ashx?v=152&f=sh_relvol_o3&ft=4&o=-relativevolume&c=0,1,2,64,65"
# logging in
    browser.maximize_window()
    browser.get(finLink)
    # try:
    def finvCjLogin():
    # logging in
        browser.implicitly_wait(4)
        browser.find_element_by_link_text("Login").click()
        browser.implicitly_wait(4)
        browser.find_element_by_css_selector('[name="email"]').send_keys('cjwillis92@yahoo.com')
        browser.minimize_window()
        browser.implicitly_wait(4)
        browser.minimize_window()
        browser.find_element_by_css_selector('[type="password"]').send_keys(input("fv pcode:\n"))  # MNE!!!!!!!!!!!!!!
        browser.maximize_window()
        browser.implicitly_wait(4)
        browser.find_element_by_css_selector('[type="password"]').submit()
        browser.get(finLink)
    finvCjLogin()
# editing columns
    colTitleLis = ["Ticker", "Company", "Relative Volume", "Price", "Volume"]
    def finvColEdit(settingsLis):
        for column in settingsLis:
            column = column.title()
        settingsTdTags = BeautifulSoup(browser.page_source, 'lxml').select('.filters-border tbody tr td')
        for td in settingsTdTags:  # this to get every td tag in settings
            try:
                tdText, tdStatus, tdInput = td.select(".screener-combo-title")[0].getText(), False, td.select("input")
                if len(td.select('[checked="checked"]')) == 1:  # if unfound it'll return an empty list
                    tdStatus = True
                if tdText in settingsLis and tdStatus is False:  # if in the list but not checked, it should be checked
                    browser.find_element_by_xpath(xpath_soup(tdInput[0])).click()
                    settingsLis.remove(tdText)
                    tdStatus = not tdStatus
                elif tdText not in settingsLis and tdStatus:  # if not in list but checked, uncheck it
                    browser.find_element_by_xpath(xpath_soup(tdInput[0])).click()
                    tdStatus = not tdStatus
            except IndexError:
                break
    finvColEdit(colTitleLis)
# exporting and moving the csv
    browser.find_element_by_link_text("export").click()
    time.sleep(2)  # wait for file to download
    destinPath = path(path.cwd() / f'finvizCSV{todayte}.csv')  # MNE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    shutil.move(path(r"C:\Users\chris\OneDrive\Downloads\finviz.csv"), destinPath)  # MNE!!!!!!!!!!!!!!!!!!!!!!!!!!
# emailing the csv
    browser.minimize_window()
    sender, senderAccss, recvr = 'chrigs1ist@gmail.com', input("gm access\n"), 'chrigs1ist@gmail.com'  # MNE!!!!!!!!!
    finvMailSubj, outgFile, addtnlTxt = f'finviz csv {todayte}', destinPath, 'sup\n'
    def emailSend(senderIM, senderPC, sendee, subject, bodyAsTxt='', attchmnt=''):
        # there's a way to format/send the body as/in html. its not shown/needed (rn/here) tho.
            # find out how @ https://docs.python.org/3.9/library/email.examples.html
        # from email.mime.multipart import MIMEMultipart
        # from email.mime.text import MIMEText
        # from email.mime.base import MIMEBase
        # from email import encoders
        # from email.mime import application
        from email.message import EmailMessage
        from pathlib import Path as path
        import mimetypes, smtplib
        if attchmnt:
            attchmnt = path(attchmnt)
            openAtt = open(attchmnt, 'rb')

        msg = EmailMessage()  # MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = senderIM, sendee, subject
        # msg.preamble = 'yeo'  # what dis even do doe?
        msg.set_content(bodyAsTxt)
        if attchmnt:
            ctype, encoding = mimetypes.guess_type(str(attchmnt))
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            msg.add_attachment(openAtt.read(), maintype=maintype, subtype=subtype, filename=attchmnt.name)
    # csvMsg.attach(MIMEText("relative volumes over 3 from greatest to least", 'plain'))
    # csvAtt = application.MIMEApplication(openDP.read(), _subtype="csv")
    # csvAtt.add_header('Content-Decomposition', 'attachment', filename=destinPath)
    # csvMsg.attach(csvAtt)
    # payload = MIMEBase('application', 'octate-stream')
    # payload.set_payload(openDP.read())  # Open the future attached file as binary mode
    # encoders.encode_base64(payload)  # encode the attachment
    # payload.add_header('Content-Decomposition', 'attachment', filename=destinPath)
    # csvMsg.attach(payload)     # adding the payload header with the filename^<
        smtpObj, smtpErrCheck, smtpErrNone = smtplib.SMTP('smtp.gmail.com', 587), [], [250, 220, 235, {}, 221]  # MNE!!
        smtpErrCheck.append(smtpObj.ehlo()[0])
        smtpErrCheck.append(smtpObj.starttls()[0])
        smtpErrCheck.append(smtpObj.login(senderIM, senderPC)[0])
# msgTxt = csvMsg.as_string()
# print(smtpObj.sendmail(senderIM, sendee, msgTxt))
        smtpErrCheck.append(smtpObj.send_message(msg))
        time.sleep(2)
        smtpErrCheck.append(smtpObj.quit()[0])
        if smtpErrCheck != smtpErrNone:
            raise Exception("something may be wrong with the sending of the email")
        if attchmnt:
            time.sleep(2)
            openAtt.close()
    emailSend(sender, senderAccss, recvr, finvMailSubj, bodyAsTxt=addtnlTxt, attchmnt=str(outgFile))
# final touches
    os.remove(destinPath)
    # except selErr.NoSuchElementException:
    #     print("problem okurred")
    if input("type something in then press enter to close browser\n"):  # MNE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        browser.close()
except Exception as err:  # text somebody if an exception be up
    twilioGoDir = path(r'C:\Users\chris\OneDrive\profile links\PycharmProjectsLink\pythonProject')
    # sys.path.append(str(twilioGoDir))
    # import twilio_go
    # from twilio.rest import Client  # correct way to access twilio mod
    # accountSID, authToken, myCellNum, myTwilioNum = \
    #     'AC26eedxxxxxxxx....', '530abcxxxxxxxx....', '3475673868', '+14632223597'  # MNE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # twilioMyGetIn = Client(accountSID, authToken)
    # message = twilioMyGetIn.messages.create(body=f"error with the code:\n\n{err}", from_=myTwilioNum, to=myCellNum)
    # sid = message.sid
    # time.sleep(15)  # wait a few seconds to see if the msg sent
    # print(twilioMyGetIn.messages(sid).fetch().status)  # if dis don't werk eider, den I.D.K. What.

# fin.


# pyAnyW online version:
# #! python3
# # finscriz.py - scrapes certain data from finviz and sends an email of it
# import datetime, sys
# if datetime.datetime.now().date().strftime("%A") in ["Saturday", "Sunday"]:
#     sys.exit()
# try:
# # imports
#     from pathlib import Path as path
#     import lxml, itertools, requests, re, shutil, os, time, pwords, traceback
# # browser start off/up
#     import undetected_chromedriver as uc
#     from selenium import webdriver
#     from bs4 import BeautifulSoup
#     from selenium.common import exceptions as selErr
#     from selenium.webdriver.common.keys import Keys as keys
#     from selenium.webdriver.support.ui import WebDriverWait
#     from selenium.webdriver.support import expected_conditions as ec
#     from selenium.webdriver.chrome.options import Options
#     from selenium.webdriver.common.by import By as byy  # results in a locator being produced
#     from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#     # print("started")
#     def xpath_soup(element):  # copied from github
#         """Generate xpath of soup element
#         :param element: bs4 text or node
#         :return: xpath as string"""
#         components = []
#         child = element if element.name else element.parent
#         for parent in child.parents:
#             """
#             @type parent: bs4.element.Tag
#             """
#             previous = itertools.islice(parent.children, 0, parent.contents.index(child))
#             xpath_tag = child.name
#             xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
#             components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
#             child = parent
#         components.reverse()
#         return '/%s' % '/'.join(components)
#     # '# MNE!*' = may have to edit on the pythonAnywhere end. X-MNE-X = pythonAnywhere editing done
#
#     chrome_options, cwdP = Options(), "/home/JimboDF/finscriz//"  # webdriver.ChromeOptions(), path.cwd()
#     chromeOptArgLis = ["--headless", "--disable-gpu", "window-size=1536,934", # '--log-path=chromedriver.log', '--kiosk-printing',
#     "--no-sandbox", "--disable-extensions", '--disable-setuid-sandbox',  '--verbose', '--disable-popup-blocking',
#     '--disable-dev-shm-usage', '--disable-software-rasterizer', "--disable-notifications"]
#     #, """user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (
#     # KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"""]
#     for optArg in chromeOptArgLis:
#         chrome_options.add_argument(optArg)
#
#     # set download directory path and adding preferences to ChromeOptions
#     pref, waitSecs = {"download.default_directory":f"{cwdP}", "download.prompt_for_download": False,
#     'savefile.default_directory': f"{cwdP}", 'profile.default_content_settings.popups': 0, "download.directory_upgrade": True,
#     "download.download_restrictions": 0, "safebrowsing_for_trusted_sources_enabled": False, "safebrowsing.enabled": False,
#     'safebrowsing.disable_download_protection': True}, 5
#
#     chrome_options.add_experimental_option("prefs", pref)
#     chrome_options.experimental_options["prefs"] = pref  # same thing?
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option('useAutomationExtension', False)  # bulk comments line line 60 or 61
#     browser = uc.Chrome(options=chrome_options)  # "home/JimboDF/finscriz/chromedriver", # bulk comments line 58, 60, or 61
#
#     browser.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': f"{cwdP}"})
#         # formerly it was , params and params=what the 2nd parram is
#     def enable_download_in_headless_chrome(browser, download_dir):
#         #add missing support for chrome "send_command"  to selenium webdriver
#         browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
#         params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
#         browser.execute("send_command", params)
#     enable_download_in_headless_chrome(browser, cwdP)
#     wait, cnt, todayte, finLink = WebDriverWait(browser, waitSecs), 0, datetime.datetime.today().date(), \
#                           "https://finviz.com/screener.ashx?v=152&f=sh_relvol_o3&ft=4&o=-relativevolume&c=0,1,2,64,65"
#     # def megaWait(findBy, findStr, waitSecs):
#     def megaWait(secs):
#         ogSecs = secs
#         time.sleep(secs)
#         while browser.execute_script('return document.readyState;') != "complete":
#             if secs == 0:
#                 secs = ogSecs
#                 break
#             time.sleep(1)
#             secs -= 1
#         # wait.until(ec.presence_of_element_located((byy.findBy, findStr)))
#         browser.implicitly_wait(secs)
# # logging in
#     browser.maximize_window()
#     browser.get(finLink)
#     # try:
#     def finvCjLogin():
#         # logging in
#         megaWait(waitSecs)
#         wait.until(ec.presence_of_element_located((byy.LINK_TEXT, "Login")))
#         wait.until(ec.element_to_be_clickable((byy.LINK_TEXT, "Login")))
#         browser.find_element(byy.LINK_TEXT, "Login").click()  # find_element makes the locator a webElement
#         browser.implicitly_wait(4)
#         browser.find_element(byy.CSS_SELECTOR, '[name="email"]').send_keys('cjwillis92@yahoo.com')
#         browser.minimize_window()
#         browser.implicitly_wait(4)
#         browser.minimize_window()
#         browser.find_element(byy.CSS_SELECTOR, '[type="password"]').send_keys(pwords.finviz_password)  # X-MNE-X
#         browser.maximize_window()
#         browser.implicitly_wait(4)
#         browser.find_element(byy.CSS_SELECTOR, '[type="password"]').submit()
#         megaWait(waitSecs)
#         browser.get(finLink)
#         megaWait(waitSecs)
#     finvCjLogin()
#
# # exporting and moving the csv.   # bulk comments for under this section
#     browser.execute_script('document.getElementsByClassName("tab-link")[5].target = "_self";')
#     exportLink = browser.find_element(byy.LINK_TEXT, 'export').get_attribute("href")
#     browser.get(exportLink)
#
#     browser.execute_script('document.getElementsByClassName("tab-link")[5].target = "_self";')
#     browser.find_element(byy.LINK_TEXT, 'export').click()  # bulk comments line 131
#     browser.execute_script('window.open = function(url) {window.location=url}')  #add 'self.' to the beginning?
#
#     megaWait(waitSecs)  # wait for file to download.
#     destinPath = path(path.cwd() / f'finvizCSV{todayte}.csv')  # destinPath needs to be the path of what the csv WILL be
#     # browser.get_screenshot_as_file("screen_snap.png")
#
#     shutil.move(path(cwdP + "finviz.csv"), destinPath)  # bulk comments line 143
# # emailing the csv
#     browser.minimize_window()
#     sender, senderAccss, recvr = 'chrigs1ist@gmail.com', pwords.chrigslist_password, 'cjwillis92@yahoo.com'
#     finvMailSubj, outgFile, addtnlTxt = f'finviz csv {todayte}', destinPath, 'sup\n'  # change the body here if need be
#     def emailSend(senderIM, senderPC, sendee, subject, bodyAsTxt='', attchmnt=''):
#         # there's a way to format/send the body(bodyAsTxt/addtnlTxt) as/in html. its not shown/needed (rn/here) tho.
#             # find out how @ https://docs.python.org/3.9/library/email.examples.html
#         from email.message import EmailMessage
#         from pathlib import Path as path
#         import mimetypes, smtplib
#         if attchmnt:
#             attchmnt = path(attchmnt)
#             openAtt = open(attchmnt, 'rb')
#         msg = EmailMessage()
#         msg['From'], msg['To'], msg['Subject'] = senderIM, sendee, subject
#         msg.set_content(bodyAsTxt)
#         if attchmnt:
#             ctype, encoding = mimetypes.guess_type(str(attchmnt))
#             if ctype is None or encoding is not None:
#                 # No guess could be made, or the file is encoded (compressed), so use a generic bag-of-bits type.
#                 ctype = 'application/octet-stream'
#             maintype, subtype = ctype.split('/', 1)
#             msg.add_attachment(openAtt.read(), maintype=maintype, subtype=subtype, filename=attchmnt.name)
#         smtpObj, smtpErrCheck, smtpErrNone = smtplib.SMTP('smtp.gmail.com', 587), [], [250, 220, 235, {}, 221]
#             # formerly MNE but the email will be sent from my gmail account so nvm
#         smtpErrCheck.append(smtpObj.ehlo()[0])
#         smtpErrCheck.append(smtpObj.starttls()[0])
#         smtpErrCheck.append(smtpObj.login(senderIM, senderPC)[0])
#         smtpErrCheck.append(smtpObj.send_message(msg))
#         time.sleep(2)
#         smtpErrCheck.append(smtpObj.quit()[0])
#         if smtpErrCheck != smtpErrNone:
#             raise Exception("something may be wrong with the sending of the email")
#         if attchmnt:
#             time.sleep(2)
#             openAtt.close()
#     emailSend(sender, senderAccss, recvr, finvMailSubj, bodyAsTxt=addtnlTxt, attchmnt=str(outgFile))
# # final touches  # bulk comments for under this section
#     os.remove(destinPath)  # maybe move to the finally clause
# except Exception as err:  # text somebody if an exception be up  # bulk comments within line 183's exception
#     from twilio.rest import Client  # correct way to access twilio mod
#     chrisLCell, CMLsTwilioNum = '3475673868', '+14632223597'  # X-MNE-X
#     twilioMyGetIn = Client(pwords.CMLtwilio_sid, pwords.CMLtwilio_token)  # X-MNE-X
#     fullErr = f"""at {datetime.datetime.now()} an error occurred:\n\n \tError Traceback: \n\t\t{traceback.format_exc()}
#     \n\n Error: {err}"""
#     message = twilioMyGetIn.messages.create(body=f"error with the code:\n\n{fullErr}", from_=CMLsTwilioNum, to=chrisLCell)
#     sid = message.sid
#     time.sleep(15)  # wait a few seconds to see if the msg sent
#     print(twilioMyGetIn.messages(sid).fetch().status)  # if dis don't werk eider, den I.D.K. What.
#     #     # could nest another try/except statement and have it send me an email but im feeling like going
#     #     # down dat path opens up a rabbit hole. does pythonAnywhere send alerts when there's errors?
# finally:
#     time.sleep(10)
#     browser.quit()  # is this different then .close? yes cuz this will close all browser windows and
#         # terminates the server processes connection or blah blah something like that, goog it
#     # print("fin", datetime.datetime.now())
#     # sys.exit() # ------------------------------------------------------
#     # fin.
#
#
# # bulk ununcommentabls: *line numbers and code on that line are subject to change.*
#     # line 58 - browser = uc.Chrome(options=chrome_options):
#             # , service_args=["--log-path=./Logs/DubiousDan.log"]
#         # , executable_path=
#                 # r"/home/JimboDF/.local/bin:/home/JimboDF/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:."
#           # downloaded chromedriver file for old chromeDriver version 78.0.3904.70 since this is the current browser version for pyAnyW
#             # alt to ^ would be to find out how to update browser version on pythonanywhere
#     # line 131 - browser.find_element(byy.LINK_TEXT, 'export').click():
#         # got a "DeprecationWarning: find_element_by_* commands deprecated. use find_element() instead" b4 being edited
#             # import re  # used this code to transfm the deprec way to the new way. wrap 2nd param in single quotes tho
#             # r = re.compile(r"""(find_element)_by_(css_selector|link_text|xpath)\(('[0-9a-zA-Z=\[\]"_()]+')\)""")
#             # oldWayexamplesLis = ["""find_element_by_css_selector('[name="email"]')""",
#             # """find_element_by_xpath('xpath_soup(tdInput[0])')""", """find_element_by_link_text('export')"""]
#             # for old in oldWayexamplesLis:
#             #     print(f"""{r.findall(old)[0][0]}(byy.{r.findall(old)[0][1].upper()}, {r.findall(old)[0][2]})""")
#         # see where the download ended up after this click (if anywhere. is there a
#         # default directory setting for downloads? yes, and code has been edited accordingly)
#     # line 143 - shutil.move(path(cwdP / "finviz.csv"), destinPath):
#         # shutil.move(path(r"C:\Users\chris\OneDrive\Downloads\finviz.csv"), destinPath)
#             # made dis dir da default dir for downloads earlier in the code. shutil kept to change the name of the file tho
#             # make the source path for shutil where the csv will be when export is clicked
#     # section final touches:
#             # except selErr.NoSuchElementException:
#         #       print("problem okurred")
#         # if input("type something in then press enter to close browser\n"):  # X-MNE-X
#             # browser.close()  # maybe move to the finally clause? no cuz this is just to close the current browser window
#         # raise Exception("Mock Error")
#     # under line 183 exception:
#         # twilioGoDir = path(r'C:\Users\chris\OneDrive\profile links\PycharmProjectsLink\pythonProject')
#         # sys.path.append(str(twilioGoDir))
#         # import twilio_go
#         # print("yeoooo\n\n", traceback.format_exc(), err, datetime.datetime.now(), sep="\n")  # testing print
#             # edited with traceback...() to print a full(er) or more informative err msg
#         # browser.get_screenshot_as_file("screen_snap.png")
#     # section exporting and moving the csv.:
#         # i have no idea whether this would've also worked or not:
#             # browser.execute_script('document.getElementsByClassName("tab-link")[5].target = "_self";')
#             # browser.find_element(byy.LINK_TEXT, 'export').click()
#             # instances = browser.window_handles
#             # browser.switch_to.window(instances[1])
#             # WebDriverWait(browser, 60).until(lambda browser: browser.execute_script('return document.readyState') == 'complete')
#             # enable_download_in_headless_chrome(browser, cwdP)
#     # the entirety of the editing columns section formerly at line 107:
#         # # editing columns  # this section is no longer needed because it's reflected in the link address
#         #     colTitleLis = ["Ticker", "Company", "Relative Volume", "Price", "Volume"]
#         #     def finvColEdit(settingsLis):
#         #         for column in settingsLis:
#         #             column = column.title()
#         #         settingsTdTags = BeautifulSoup(browser.page_source, 'lxml').select('.filters-border tbody tr td')
#         #         for td in settingsTdTags:  # this to get every td tag in settings
#         #             try:
#         #                 tdText, tdStatus, tdInput = td.select(".screener-combo-title")[0].getText(), False, td.select("input")
#         #                 if len(td.select('[checked="checked"]')) == 1:  # if unfound it'll return an empty list
#         #                     tdStatus = True
#         #                 if tdText in settingsLis and tdStatus is False:  # if in the list but not checked, it should be checked
#         #                     browser.find_element(byy.XPATH, xpath_soup(tdInput[0])).click()
#         #                     settingsLis.remove(tdText)
#         #                     tdStatus = not tdStatus
#         #                 elif tdText not in settingsLis and tdStatus:  # if not in list but checked, uncheck it
#         #                     browser.find_element(byy.XPATH, xpath_soup(tdInput[0])).click()
#         #                     tdStatus = not tdStatus
#         #             except IndexError:
#         #                 break
#         #     finvColEdit(colTitleLis)
#     # line 60 or 61 - chrome_options.add_experimental_option('useAutomationExtension', False) &
#         # browser = uc.Chrome(options=chrome_options)  # "home/JimboDF/finscriz/chromedriver", # bulk comments line 58
#      # :
#         # browser = webdriver.Edge(executable_path=r"C:\Users\chris\OneDrive\Desktop\edgedriver_win64\msedgedriver.exe")
#         # # print ("Headless Chrome Initialized")
#         # potential other answers for python selenium headless download:
#             # https://bugs.chromium.org/p/chromedriver/issues/detail?id= 2454, 3120, 3548
#         # browser = webdriver.Chrome(options=chrome_options
#
# # -------------------------------------------------------------------------------------------------------------------------------