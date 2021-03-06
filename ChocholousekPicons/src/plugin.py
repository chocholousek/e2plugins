# -*- coding: utf-8 -*-
###########################################################################
#  Enigma2 plugin, ChocholousekPicons, written by s3n0, 2018-2019
###########################################################################

###########################################################################
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop, inStandby      # TryQuitMainLoop for the enigma2 gui restart # inStandby to detect if enigma2 is in Standby mode
import urllib2
import ssl                                                  # SSL modul vyuzivam pre neverifikovane pripojenia s modulom urllib2, z dovodu problemov so SSL certifikatmi na google.drive
ssl._create_default_https_context = ssl._create_unverified_context        # nastavenie bez verifikacie SSL-klucom ako defaultne, pre vsetky otvorene HTTPS web-stranky
###########################################################################
from enigma import ePicLoad, eActionMap, eTimer, eEnv       # eEnv sluzi pre ziskavanie premennych z Enigmy (systemove dresare v systeme napriklad)
###########################################################################
from enigma import getDesktop
sizemaxY = getDesktop(0).size().height()
sizemaxX = getDesktop(0).size().width()
###########################################################################
import threading
import re                              # reg-ex modul pre Python jazyk
import glob                            # jednoduchy modul pre ziskavanie kompletneho zoznamu suborov z urceneho adresara, vratene kompletnej cesty
###########################################################################
from os import system as os_system, path as os_path, makedirs as os_makedirs, remove as os_remove, listdir as os_listdir
from sys import maxint                 # maximum value of the integer type - used on eActionMap binding the maximum priority (max. integer value is necessary)
from commands import getstatusoutput   # sluzi na spustenie prikazu v command-line shell, ale s preberanim celeho standardneho vystupu do premennej pythonu
from datetime import datetime          # pouzivam predovsetkym ako:  datetime.now().replace(microsecond=0)  -  vracia UnixTime bez mikrosekund, efektivnejsie je vsak namiesto toho pouzit rychlejsi kod:  int(time.time())
#from time import mktime               # pouzivam na konverziu: datetime <object type> TO unixtime <integer type>
#from time import time
from time import sleep
###########################################################################
from Components.Harddisk import harddiskmanager      # vyuzivam vo funkciach umiestnene dolu v kode - pre vyhladanie dostupnych zloziek + nejakych .PNG picon-suborov v set top boxe
#from Components.Sources.CurrentService import CurrentService
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
#from Components.AVSwitch import AVSwitch
from Components.Sources.StaticText import StaticText
###########################################################################
#from Components.MenuList import MenuList
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigSelection, ConfigYesNo, ConfigSet, ConfigText
###########################################################################
#from Tools.Directories import resolveFilename, SCOPE_PLUGINS
#PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/ChocholousekPicons/')
from . import _, PLUGIN_PATH
###########################################################################



session = None

plugin_version_local  = '0.0.000000'        # napriklad:  '1.0.180625'
plugin_version_online = '0.0.000000'



###########################################################################
###########################################################################


class mainConfigScreen(Screen, ConfigListScreen):

    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="1100,800" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="version_txt" position="0,0" size="1100,60"  font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"  position="0,60" size="1100,40" font="Regular;28" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="config"      position="center,100" size="1000,600" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" backgroundColor="#22000000" />

            <widget name="previewImage" position="center,350" size="500,300" zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="25,755"  size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="200,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="470,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="775,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"    position="65,755"  size="250,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_green"  position="240,755" size="250,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_yellow" position="510,755" size="250,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_blue"   position="815,755" size="260,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="800,600" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="version_txt" position="0,0"  size="800,40" font="Regular;26" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"  position="0,40" size="800,30" font="Regular;16" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="config"      position="center,70" size="750,400" font="Regular;22" itemHeight="20" scrollbarMode="showOnDemand" backgroundColor="#22000000" />

            <widget name="previewImage" position="80,230" size="500,300" zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="5,560"   size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="125,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="295,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="475,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"    position="45,560"  size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_green"  position="165,560" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_yellow" position="335,560" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_blue"   position="515,560" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
        </screen>'''

    def __init__(self, session):

        Screen.__init__(self, session)
        #self.session = session          # toto netreba, toto sa vykona uz aj v Screen.__init__

        self.onChangedEntry = []        # list pomenenych poloziek pre zobrazovane konfiguracne MENU nastavim pri inicializacii tiez naprazdno
        self.list = []                  # list pre konfiguracne MENU zatial ponecham prazdny a naplnim ho az neskor resp. aj pri zmenach hodnoty konfiguracie (po sttlaceni tlacidiel do lava / do prava)

        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)       # ???? asi tu ma byt:  session = self.session
        #ConfigListScreen.__init__(self, self.list, session, on_change = self.changedEntry)

        self.lineHeight = 1             # for text height auto-correction on dmm-enigma2 (0 = enable auto-correction ; 1 = disable auto-correction)

        self['previewImage'] = Pixmap()

        self['txt_red']      = StaticText(_('Exit'))
        self['txt_green']    = StaticText(_('Save & Exit'))
        self['txt_yellow']   = StaticText(_('Update plugin'))
        self['txt_blue']     = StaticText(_('Update picons'))

        global plugin_version_local
        self['version_txt']  = Label('Chocholousek picons - plugin ver.%s' % plugin_version_local)
        self['author_txt']   = Label('(https://github.com/s3n0)')

        self['actions'] = ActionMap( ['SetupActions', 'ColorActions'], {
            'left'  : self.keyToLeft,
            'right' : self.keyToRight,
            'yellow': self.keyToUpdatePlugin,
            'blue'  : self.keyToUpdatePicons,
            'green' : self.exitWithSave,
            'red'   : self.exitWithoutSave,
            'cancel': self.keyToExit,
            'ok'    : self.keyToOk
            } , -2)

        global piconResults
        piconResults = {'added': 0, 'changed': 0, 'removed': 0}

        self.bin7zip = None             # path to '7z' or '7za' executable (binary) file
        self.chochoContent = None       # content of the file "id_for_permalinks*.log" from google.drive

        #self.onShown.append(self.showListMenu)
        #self.onLayoutFinish.append(self.layoutFinished)

        #self.prepareSetup()

        self.layoutFinishTimer = eTimer()
        self.layoutFinishTimer.callback.append(self.prepareSetup)
        self.layoutFinishTimer.start(200, True)

        #self.onLayoutFinish.append(self.check7zip)    # tento riadok je tiez bez ucelu - Screen totiz stale nieje pripraveny, aby bolo mozne pouzivat MessageBox vo funkcii check7zip

    def prepareSetup(self):

        self.loadChochoContent()

        config.plugins.chocholousekpicons = ConfigSubsection()
        config.plugins.chocholousekpicons.piconFolder = ConfigSelection(default = '/usr/share/enigma2/picon',
                choices = [ ('/usr/share/enigma2/picon','/usr/share/enigma2/picon'),
                            ('/media/hdd/picon','/media/hdd/picon'),
                            ('/media/usb/picon','/media/usb/picon'),
                            ('/picon','/picon'),
                            ('/usr/share/enigma2/XPicons/picon','/usr/share/enigma2/XPicons/picon'),
                            ('/usr/share/enigma2/ZZPicons/picon','/usr/share/enigma2/ZZPicons/picon'),
                            ('(user defined)' , _('(user defined)')  )
                          ]
                        )   # https://github.com/openatv/MetrixHD/blob/aa9a302bd06a844fc5d53e017fec0d420bccd762/usr/lib/enigma2/python/Components/Renderer/MetrixHDXPicon.py
        config.plugins.chocholousekpicons.piconFolderUser = ConfigText(default = '/')
        # change the default picon directory + set this found entry, if some .png files will found in some folder
        if config.plugins.chocholousekpicons.piconFolder.value != '(user defined)':
            for picdir in config.plugins.chocholousekpicons.piconFolder.choices:
                if glob.glob(picdir[0] + '/*.png'):
                    config.plugins.chocholousekpicons.piconFolder.default = picdir[0]
                    config.plugins.chocholousekpicons.piconFolder.setValue(picdir[0])
                    break
        config.plugins.chocholousekpicons.radio = ConfigYesNo(default = False)
        #config.plugins.chocholousekpicons.satauto  = ConfigYesNo(default = False)
        config.plugins.chocholousekpicons.usersats = ConfigSet(default = ['23.5E','19.2E'] , choices = self.getAllSat() )
        config.plugins.chocholousekpicons.resolution = ConfigSelection(default = '220x132',
                choices = [('50x30','50x30'), ('96x64','96x64'), ('100x60','100x60'), ('132x46','132x46'), ('150x90','150x90'), ('220x132','220x132'), ('400x170','(ZZPicons) 400x170'), ('400x240','400x240'), ('500x300','500x300')]  )
        config.plugins.chocholousekpicons.background = ConfigSelection(default = 'black',
                choices = [ (s, s) for s in self.getAllBckByUserCfg( config.plugins.chocholousekpicons.usersats.value, config.plugins.chocholousekpicons.resolution.value ) ]    )  # default='white' , choices=[('white', _('White')), ('black', _('Black')), ('transparent', _('Transparent')), ('transparentwhite', _('Transparent-White')), ('mirrorglass', _('Mirror-Glass')) ])      # !!!! ( _(s),s ) biela/white nenajde subor s pikonami v slovencine:)

        self.downloadPreviewPicons()
        self.showListMenu()

    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        self.showListMenu()

    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        self.showListMenu()

    def keyToOk(self):
        k = self['config'].getCurrent()[0]            # [0] = config text/label (from cursor position) , [1] user selected config value (from cursor position)
        if k == _('Satellite positions'):
            self.session.openWithCallback(self.satellitesConfigScreenReturn, satellitesConfigScreen, self.getAllSat() )
        elif k == _('User defined folder'):
            self.keyOK()

    def satellitesConfigScreenReturn(self, retval):
        if retval:
            self.loadChochoContent()       # ak doslo k zmene v nastaveni potrebnych satelitov, tak musim vykonat nove preskenovanie dostupnych dizajnov pikon podla predvoleneho rozlisenia pikon
            self.reloadAvailableBackgrounds()
            self.changedEntry()
            self.showListMenu()

    def keyToUpdatePicons(self):
        if self.bin7zip:
            self.session.open(piconsUpdateJobScreen, self.chochoContent, self.bin7zip)
        else:
            self.check7zip()

    def keyToUpdatePlugin(self):
        global pluginUpdateDo, plugin_version_local
        if pluginUpdateDo():
            message = _("The plugin has been updated to the new version.\nA quick reboot is required.\nDo a quick reboot now ?")
            self.session.openWithCallback(self.restartEnigmaBeforeClosing, MessageBox, message, type = MessageBox.TYPE_YESNO, default = False) # ukazem tzv. MessageBox s upozornenim a moznostou rebootovania, ze uz bol updatnuty plugin a ze je potrebny restart Enigmy (GUI)
        else:
            message = _("Plugin version is up to date.\n\n"
                        "Installed version: %s") % (plugin_version_local)
            self.session.open(MessageBox, message, type = MessageBox.TYPE_INFO, timeout = 10)

    def exitWithSave(self):
        self.exitWithConditionalSave(True)

    def exitWithoutSave(self):
        self.exitWithConditionalSave(False)

    def keyToExit(self):
        self.s = self['txt_green'].getText()
        if self.s[-1:] == '*':                  # doslo k zmene konfiguracie pluginu... ? ak ano, tak vyvolam MessageBox s moznostou ulozenia ci naopak obnovenia povodnych nastaveni v konfiguracii pluginu
            message = _("You have changed the plugin configuration.\nDo you want to save all changes now ?")
            self.session.openWithCallback(self.exitWithConditionalSave, MessageBox, message, type = MessageBox.TYPE_YESNO, timeout = 0, default = True)
        else:
            self.exitWithConditionalSave(False)

    def exitWithConditionalSave(self, condition=True):       # ulozim alebo stornujem vykonane zmeny v uzivatelskej konfiguracii pluginu, default = True => ulozenie konfiguracie
        if condition:
            for x in self['config'].list:
                x[1].save()
            configfile.save()                               # '/etc/enigma2/settings' - the configuration file will be saved only when the Enigma is stopped or restarted
        else:
            for x in self['config'].list:
                x[1].cancel()
        self.close()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self['txt_green'].setText(_('Save & Exit') + '*')

        k = self['config'].getCurrent()[0]
        #print('MYDEBUGLOGLINE - self["config"].getCurrent()[0] = %s ; [1] = %s ; k = %s' % (self["config"].getCurrent()[0], self["config"].getCurrent()[1], k)  )
        if k == _('Picon resolution'):
            self.reloadAvailableBackgrounds()
        #elif k == _('Picon background'):
        #    self.showPreviewImage()

    def showListMenu(self):
        self.list = []
        self.list.append(getConfigListEntry( _('Picon folder')    ,  config.plugins.chocholousekpicons.piconFolder  ))
        if config.plugins.chocholousekpicons.piconFolder.value == '(user defined)':
            self.list.append(getConfigListEntry( _('User defined folder'), config.plugins.chocholousekpicons.piconFolderUser ))
        self.list.append(getConfigListEntry( _('Include radio picons'), config.plugins.chocholousekpicons.radio     ))
        #self.list.append(getConfigListEntry( _('Satellite auto-detection') , config.plugins.chocholousekpicons.satauto , _('The plug-in will attempt to automatically detect\nthe used satellite positions\nfrom the tuner configuration.')   ))
        #if not config.plugins.chocholousekpicons.satauto.value:      # ..........
        self.list.append(getConfigListEntry( _('Satellite positions'), config.plugins.chocholousekpicons.usersats   ))
        self.list.append(getConfigListEntry( _('Picon resolution') , config.plugins.chocholousekpicons.resolution  ))
        self.list.append(getConfigListEntry( _('Picon background') , config.plugins.chocholousekpicons.background ,  _('Choose picon design')  ))
        self['config'].list = self.list
        self['config'].l.setList(self.list)
        self.showPreviewImage()

    def restartEnigmaBeforeClosing(self, answer = None):
        if answer:
            self.session.open(TryQuitMainloop, 3)   # 0=Toggle Standby ; 1=Deep Standby ; 2=Reboot System ; 3=Restart Enigma ; 4=Wake Up ; 5=Enter Standby   ### FUNGUJE po vyvolani a uspesnom dokonceni aktualizacie PLUGINu   ### NEFUNGUJE pri zavolani z funkcie leaveSetupScreen(self) po aktualizacii picon lebo vyhodi chybu: RuntimeError: modal open are allowed only from a screen which is modal!
        else:
            self.close()

    def showPreviewImage(self):
        self['previewImage'].instance.setPixmapFromFile(self.getPreviewImagePath())
        self['previewImage'].instance.setScale(0)

    def getPreviewImagePath(self):
        imgpath = PLUGIN_PATH + 'images/nova-cz-' + config.plugins.chocholousekpicons.background.value + '-' + config.plugins.chocholousekpicons.resolution.value + '.png'
        if os_path.isfile(imgpath):
            return imgpath
        else:
            return PLUGIN_PATH + 'images/image_not_found.png'

    def downloadPreviewPicons(self):
        """
        download preview picons if neccessary, i.e. download archive file into the plugin folder and extract all preview picons
        the online version will be detected from the http request header
        the  local version will be detected from the existing local file
        archive filename example:         nova-cz-(all)_by_chocholousek_(191020).7z      (the parentheses will replace by underline characters)
        files inside the archive file:    nova-cz-transparent-220x132.png ; nova-cz-gray-400x240.png
        """
        self.check7zip()
        if not self.bin7zip:
            return

        localfilenamefull = glob.glob(PLUGIN_PATH + 'nova-cz-*.7z')
        if localfilenamefull:
            localfilenamefull = localfilenamefull[0]                                                # simple converting the list type to string type
        else:
            localfilenamefull = '___(000000).7z'                                                    # version 000000 as very low version means to download a preview images from internet in next step
        url = 'https://drive.google.com/uc?export=download&id=1wX6wwhTf2dJ30Pe2GWb20UuJ6d-HjERA'    # archiv .7z v ktorom sa nachadzaju nahladove obrazky (pikony kanalu NOVA pre vsetky styly avsak nie pre vsetky rozlisenia !)
        try:
            rq = urllib2.urlopen(url)
        except urllib2.URLError as e:
            print('Error %s when reading from URL: %s' % (e.reason, url))
        except Exception as e:
            print('Error: %e, URL: %s' % (e, url))
        else:
            onlinefilename = rq.headers['Content-Disposition'].split('"')[1].replace('(','_').replace(')','_')      # get file name from html header and replace the parentheses by underline characters
            if onlinefilename[-10:-4] > localfilenamefull[-10:-4]:                                  # comparsion, for example as the following:   '191125' > '191013'
                self.deleteFile(localfilenamefull)
                localfilenamefull = PLUGIN_PATH + onlinefilename
                data = rq.read()
                with open(localfilenamefull, 'w') as f:
                    f.write(data)

                # extracting .7z archive (picon preview images):
                self.deleteFile(PLUGIN_PATH + 'images/nova-cz-*.png')
                status, out = getstatusoutput('%s e -y -o%s %s nova-cz-*.png' % (self.bin7zip, PLUGIN_PATH + 'images', localfilenamefull) )
                
                # check the status error and clean the archive file (will be filled with a short note)
                if status == 0:
                    print('MYDEBUGLOGLINE - Picon preview files v.%s were successfully updated. The archive file was extracted into the plugin directory.' % localfilenamefull[-10:-4] )
                    with open(localfilenamefull, 'w') as f:
                        f.write('This file was cleaned by the plugin algorithm. It will be used to preserve the local version of the picon preview images.')
                elif status == 32512:
                    print('...error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status )
                    self.deleteFile(localfilenamefull)
                elif status == 512:
                    print('...error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, localfilenamefull) )
                    self.deleteFile(localfilenamefull)
                else:
                    print('...error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
                    self.deleteFile(localfilenamefull)

    def deleteFile(self, directorymask):
        lst = glob.glob(directorymask)
        if lst:
            for file in lst:
                os_remove(file)

    def check7zip(self):
        if not self.find7zip():
            message = _('The 7-zip archiver was not found on your system.\nThere is possible to update the 7-zip archiver now in two steps:\n\n(1) try to install via package manager "opkg install p7zip"\n...or...\n(2) try to download the binary file "7za" (standalone archiver) from the internet\n\nDo you want to try it now?')
            self.session.openWithCallback(self.download7zip, MessageBox, message, type = MessageBox.TYPE_YESNO, default = True)

    def find7zip(self):
        if os_path.isfile('/usr/bin/7za'):
            self.bin7zip = '/usr/bin/7za'
            return True
        elif os_path.isfile('/usr/bin/7z'):
            self.bin7zip = '/usr/bin/7z'
            return True
        else:
            self.bin7zip = ''
            return False

    def download7zip(self, result):
        if result:
            os_system('opkg update > /dev/null 2>&1')
            if not os_system('opkg list | grep p7zip > /dev/null 2>&1'):   # if no error received from opkg manager, then...
                os_system('opkg install p7zip')
                self.message = _('The installation of the 7-zip archiver from the Enigma2\nfeed server was successful.')
            else:
                arch = self.getChipsetArch()
                if 'mips' in arch:
                    filename = '7za_mips32el'
                elif 'arm' in arch:
                    filename = '7za_cortexa15hf-neon-vfpv4'
                elif 'aarch64' in arch:
                    filename = '7za_aarch64'
                elif 'sh4' in arch or 'sh_4' in arch:
                    filename = '7za_sh4'
                else:
                    filename = 'ERROR_-_UNKNOWN_CHIPSET_ARCHITECTURE'
                #if not os_system('wget -q --no-check-certificate -O /usr/bin/7za "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s" > /dev/null 2>&1' % filename):  # if no error received from os_system, then...
                if downloadFile('https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s' % filename , '/usr/bin/7za'):
                    os_system('chmod 755 /usr/bin/7za')
                    if os_system('/usr/bin/7za'):                   # let's try to execute the binary file cleanly    # if some error number was received from the 7za executed binary file, then...
                        os_remove('/usr/bin/7za')                   # remove the binary file on error - because of a incorect binary file for the chipset architecture !!!
                    else:
                        self.message = _('Installation of standalone "7za" (7-zip) archiver was successful.')
            if self.find7zip():
                self.session.open(MessageBox, self.message, type = MessageBox.TYPE_INFO)        # MessageBox with message about successful installation - either a standalone binary file or an ipk package
            else:
                self.session.open(MessageBox, _('Installation of 7-zip archiver failed!'), type = MessageBox.TYPE_ERROR)

    def getChipsetArch(self):
        '''
        detecting chipset architecture
        mips32el, armv7l, armv7a-neon, armv7ahf, armv7ahf-neon, cortexa9hf-neon, cortexa15hf-neon-vfpv4, aarch64, sh4, sh_4
        '''
        status, out = getstatusoutput('opkg print-architecture | grep -E "arm|mips|cortex|aarch64|sh4|sh_4"')
        if status == 0:
            return out.replace('arch ','').replace('\n',' ')        # return architectures by OPKG manager, such as:  'mips32el 16 mipsel 46'

        t = re.findall('isa\s*:\s*(.*)\n+', open('/proc/cpuinfo','r').read() )
        if t:
            return t[0]                                             # return list type converted to a string value, like as:  'mips1 mips2 mips32r1'

        status, out = getstatusoutput('uname -m')
        if status == 0:
            return out                                              # return architectures from system, like as:  'mips'

        print('MYDEBUGLOGLINE - Error ! Unknown or unidentified chipset architecture.')
        return ''

    #def createDefaultPiconDir(self):
    #   if not os_path.exists('/usr/share/enigma2/picon'):
    #       os_makedirs('/usr/share/enigma2/picon')

    ###########################################################################

    def loadChochoContent(self):
        self.downloadChochoFile()
        path = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        if path:
            with open(path[0],'r') as f:            # full path-name as the string from list index 0
                txt = f.read()
        else:
            txt = ''
            print('MYDEBUGLOGLINE - Warning! The file %s was not found on the internet but also on the internal disk.' % (PLUGIN_PATH + 'id_for_permalinks*.log'))
        self.chochoContent = txt

    def downloadChochoFile(self):
        '''
        checking new online version, download if neccessary and load the content from file with the list of all IDs for google.drive download
        the online version will be detected from the http request header
        the  local version will be detected from the existing local file
        file name example:   id_for_permalinks191017.log
        example entry from inside the file:   1xmITO0SouVDTrATgh0JauEpIS7IfIQuB              piconblack-220x132-13.0E_by_chocholousek_(191016).7z                              bin   16.3 MB    2018-09-07 19:40:54
        '''
        url = 'https://drive.google.com/uc?export=download&id=1oi6F1WRABHYy8utcgaMXEeTGNeznqwdT'   # id_for_permalinks191017.log

        pathlist = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        if pathlist:
            localfilenamefull = pathlist[0]                                             # string converted as from list[0]
        else:
            localfilenamefull = PLUGIN_PATH + 'id_for_permalinks000000.log'             # low version, to force update the file (as the first download)

        try:
            rq = urllib2.urlopen(url)
            #mycontext = ssl._create_unverified_context()
            #rq = urllib2.urlopen(url, context = mycontext)
        except urllib2.URLError as err:
            print('Error %s when reading from URL: %s' % (err.reason, url)  )
        except Exception:
            print('Error when reading URL: %s' % url)
        else:
            onlinefilename = rq.headers['Content-Disposition'].split('"')[1]            # get filename from html header
            if onlinefilename[-10:-4] > localfilenamefull[-10:-4]:                      # comparsion, for example as the following:   '191125' > '191013'
                txt = rq.read()
                with open(PLUGIN_PATH + onlinefilename, 'w') as f:
                    f.write(txt)
                if os_path.exists(localfilenamefull):
                    os_remove(localfilenamefull)
                print('MYDEBUGLOGLINE - file id_for_permalinks*.log was updated to new version: %s' % onlinefilename)

    def reloadAvailableBackgrounds(self):
        '''
        reload all available picon-backgrounds (picon-styles)
        by user selected configuration
        (by user configuration in the plugin MENU)
        '''
        config.plugins.chocholousekpicons.background = ConfigSelection( default = None ,   # default = config.plugins.chocholousekpicons.background.value  ,
          choices = [ (s, s) for s in self.getAllBckByUserCfg( config.plugins.chocholousekpicons.usersats.value, config.plugins.chocholousekpicons.resolution.value ) ]    )     # !!!! ( _(s),s ) biela/white nenajde subor s pikonami v slovencine:)

    def contentByUserCfgSatRes(self, satellites, resolution):
        result = []
        for line in self.chochoContent.splitlines():
            if resolution in line:
                for sat in satellites:
                    if sat in line:
                        result.append(line)
                        continue
        return '\n'.join(result)            # return = a very long string with "\n" newlines

    def getAllBckByUserCfg(self, sats, res):
        self.userdata = self.contentByUserCfgSatRes(sats, res)
        return sorted(list(set(  re.findall('.*picon(.*)-%s-[0-9]+\.[0-9]+.*\n+' % res, self.userdata)  )))    # using the set() to remove duplicites and the sorted() to sort the list by ASCII

    def getAllSat(self): # Satellites
        lst = re.findall('.*piconblack-220x132-(.*)_by_chocholousek_.*\n+', self.chochoContent)
        lst.sort(key = self.fnSort)
        #print('MYDEBUGLOGLINE - getAllSat = %s' % lst)
        return lst

    def fnSort(self, s):
        if s[0].isdigit():
            if s.endswith('E'):
                return float(s[:-1]) + 500
            if s.endswith('W'):
                return float(s[:-1]) + 1000
        else:
            return 0

    #def getAllRes(self): # Resolutions
    #    tmp = list(set(re.findall('.*picon.*-([0-9]+x[0-9]+)-23\.5.*\n+', self.chochoContent)))
    #    tmp = [int(x) for x in tmp]     # simple sort method for numeric strings (better as the .sort() method)
    #    return tmp

    #def getAllBck(self): # Backgrounds
    #    return re.findall('.*picon(.*)-220x132-23\.5.*\n+', self.chochoContent)


###########################################################################
###########################################################################


class satellitesConfigScreen(Screen, ConfigListScreen):

    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="450,900" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="title_txt" position="center,50" size="350,60" font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="top" />

            <widget name="config" position="center,120" size="350,700" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" />

            <ePixmap pixmap="skin_default/buttons/green.png" position="25,854" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <widget render="Label" source="txt_green" position="65,854" size="250,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="350,600" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="title_txt" position="center,50" size="300,40" font="Regular;26" foregroundColor="yellow" transparent="1" halign="center" valign="top" />

            <widget name="config" position="center,70" size="300,500" font="Regular;22" itemHeight="22" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" />

            <ePixmap pixmap="skin_default/buttons/green.png" position="5,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <widget render="Label" source="txt_green" position="45,560" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''

    def __init__(self, session, satList):

        self.allSatellites = satList

        Screen.__init__(self, session)

        self.onChangedEntry = []        # list pomenenych poloziek pre zobrazovane konfiguracne MENU nastavim pri inicializacii tiez naprazdno
        self.list = []                  # list pre konfiguracne MENU zatial ponecham prazdny a naplnim ho az neskor resp. aj pri zmenach hodnoty konfiguracie (po sttlaceni tlacidiel do lava / do prava)

        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self.lineHeight = 1             # for text height auto-correction on dmm-enigma2 (0 = enable auto-correction ; 1 = disable auto-correction)

        self['title_txt'] = Label(_('Select satellites:'))
        self['txt_green'] = StaticText(_('OK'))

        self["actions"] = ActionMap( ["SetupActions", "ColorActions"], {
            'left'  : self.keyToLeft,
            'right' : self.keyToRight,
            'green' : self.keyToExit,
            'ok'    : self.keyToExit,
            'cancel': self.keyToExit
            } , -2)

        self.onShown.append(self.showListMenu)

    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        self.switchSelectedSat()
        self.showListMenu()

    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        self.switchSelectedSat()
        self.showListMenu()

    def switchSelectedSat(self):
        selected = self['config'].getCurrent()[0]                               # value example:  '23.5E'
        if selected in config.plugins.chocholousekpicons.usersats.value:        # list example:   ['19.2E', '23.5E']
            config.plugins.chocholousekpicons.usersats.value.remove(selected)
        else:
            config.plugins.chocholousekpicons.usersats.value.append(selected)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self['txt_green'].setText(_('OK') + '*')

    def showListMenu(self):
        self.list = []
        for sat in self.allSatellites:
            if sat in config.plugins.chocholousekpicons.usersats.value:
                self.list.append(  getConfigListEntry( sat, ConfigYesNo(default=True)  ) )
            else:
                self.list.append(  getConfigListEntry( sat, ConfigYesNo(default=False) ) )
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyToExit(self):
        self.s = self['txt_green'].getText()
        if self.s[-1:] == '*':                  # doslo k zmene konfiguracie... ?
            self.close(True)
        else:
            self.close(False)


###########################################################################
###########################################################################


class piconsUpdateJobScreen(Screen):

    if sizemaxX > 1900:   # skin Full-HD or higher
        logfontsize = "23"
    else:                 # skin HD ready or lower
        logfontsize = "17"

    skin = '''
        <screen name="piconsUpdateJobScreen" position="center,center" size="''' + str(sizemaxX - 80) + ',' + str(sizemaxY - 80) + '''" title="picons update in progress" flags="wfNoBorder" backgroundColor="#22000000">
            <widget name="logWindow" position="center,center" size="''' + str(sizemaxX - 180) + ',' + str(sizemaxY - 180) + '''" font="Regular;''' + logfontsize + '''" transparent="0" foregroundColor="white" backgroundColor="#11330000" zPosition="3" />
        </screen>'''

    def __init__(self, session, chochoContent, bin7zip):

        self.chochoContent = chochoContent
        self.bin7zip = bin7zip

        Screen.__init__(self, session)
        #self.session = session            # toto netreba, nakolko presne toto vykonava uz aj Screen.__init__

        self['logWindow'] = ScrollLabel('LOG:\n\n')
        self['logWindow'].scrollbarmode = "showOnDemand"
        
        self['actions'] = ActionMap( ['SetupActions','DirectionActions'], {
            "up"    :   self["logWindow"].pageUp,
            "left"  :   self["logWindow"].pageUp,
            "down"  :   self["logWindow"].pageDown,
            "right" :   self["logWindow"].pageDown
            }, -1)

        self.timeoutPrevention = eTimer()
        self.timeoutPrevention.callback.append(self.abortPiconsUpdating)
        self.timeoutPrevention.start(15000, True)                       # (milisekundy , True = spustit len 1x / False = spustat opakovane)

        self.startTime = datetime.now()

        threading.Thread(target = self.mainFunc).start()

        #self.onLayoutFinish.append(self.mainFunc)
        #self.onShown.append(self.mainFunc)
        #self.onClose.append(self.nazov_funkcie)

    def mainFunc(self):
        global piconResults
        piconResults = {'added': 0, 'changed': 0, 'removed': 0}
        
        # 1) Ocheckuje sa internetové pripojenie
        if os_system('ping -c 1 -w 1 www.google.com > /dev/null 2>&1'): # test konektivity do internetu
            self.abortPiconsUpdating(True, _("Internet connection is not available !") )
        else:
            self.writeLog(_('Internet connection is OK.'))

        # 2) Vytvorí sa zoznam všetkých dostupných súborov "userbouquet.*.tv" aj ".radio" ktoré sa nachádzajú v "/etc/enigma2" zložke
        self.bouqet_list = glob.glob('/etc/enigma2/userbouquet.*.tv')
        if config.plugins.chocholousekpicons.radio.value:
            self.bouqet_list.extend(glob.glob('/etc/enigma2/userbouquet.*.radio'))
        if not self.bouqet_list:
            self.abortPiconsUpdating(True, _('No userbouquet files found !\nPlease check the folder /etc/enigma2 for the userbouquet files.')  )

        # 3a) Skontroluje sa zložka s pikonami a ak neexistuje, vytvorí sa nová zložka
        if config.plugins.chocholousekpicons.piconFolder.value == '(user defined)':
            self.piconDIR = config.plugins.chocholousekpicons.piconFolderUser.value
        else:
            self.piconDIR = config.plugins.chocholousekpicons.piconFolder.value
        if not os_path.exists(self.piconDIR):
            os_makedirs(self.piconDIR)
        #if not os_path.exists(self.piconDIR):
        #    self.abortPiconsUpdating(True, _('The configured picon folder does not exist!\nPlease check the picon folder in plugin configuration.\nCurrent picon folder: %s') % (self.piconDIR)  )
        
        # 3b) Vytvorí sa zoznam z picon uložených na disku (v internej flash pamäti set top boxu alebo na externom USB ci HDD) - včetne atributu veľkosti u týchto súborov
        self.writeLog(_('Preparing a list of picons from the picon directory on the local disk...'))
        self.piconCodesInHDD = {}
        dir_list = glob.glob(self.piconDIR + '/*.png') # osetrim tymto prvym krokom neexistujuce PNG subory v adresary, aby sa predislo vyvolaniu vynimky pri pouziti metody listdir, a tiez tymto docielim to, aby sa ignorovali aj pripadne *.txt alebo dalsie formaty suborov, ktore je nutne ignorovat v tomto adresari
        if dir_list:
            for path_N_file in dir_list:
                self.piconCodesInHDD.update( { path_N_file.split("/")[-1].split(".")[0]  :   int(os_path.getsize(path_N_file))  } )     # os.stat.st_time('/etc/enigma2/'+filename)

        # 4) Vytvorí sa zoznam picon, zo serv.ref.kódov nájdených vo všetkych userbouquet súboroch na disku (vytiahnem z nich len servisné referenčné kódy)
        self.writeLog(_('Preparing a list of picons from userbouquet files...'))
        self.piconCodesInBouquets = ''
        for bq_file in self.bouqet_list:
            self.piconCodesInBouquets += open(bq_file,'r').read()
            #with open(bq_file) as f:
            #    self.piconCodesInBouquets += f.read()
        self.piconCodesInBouquets = re.findall('.*#SERVICE\s([0-9a-fA-F]+_0_[0-9a-fA-F_]+0_0_0).*\n*', self.piconCodesInBouquets.replace(":","_") )
        #--- povodne som pouzival pomalsi a komplikovanejsi regex - cely proces spomaloval "match" s otaznikom ".*?" alebo aj niektore flags (re.S + re.M) a tiez som pouzival vtedy 2x po sebe spomaleny "re.sub" ---
        #self.piconCodesInBouquets = re.sub(ur'#DESCR.*|#NAME.*|#SERVICE 1:64.*', '', self.piconCodesInBouquets, flags=re.M)     # remove a unneccesary lines
        #self.piconCodesInBouquets = re.sub(r'.*?#SERVICE ([0-9a-fA-F]+:)(0:)([:0-9a-fA-F]+)(:0:0:0).*?\n+', r'1_\2\3\4;', self.piconCodesInBouquets, flags = re.S).replace(':','_').split(';')   # get the service reference codes only
        #self.piconCodesInBouquets = [s for s in self.piconCodesInBouquets if s != '']
        self.piconCodesInBouquets = list(set(self.piconCodesInBouquets))      # a small trick to remove duplicated entries ---- converting to <set> and then again back to the <list>
        self.writeLog(_('...done.'))

        # 5) Vymažú sa neexistujúce picon-súbory na disku v set-top-box-e, ktoré sú zbytočné nakoľko neexistujú v žiadnom userbouquet súbore a teda na disku budú iba zavadziať
        self.writeLog(_('Deleting unneccessary picons from local disk...'))
        self.piconsToDelete = list(  set(self.piconCodesInHDD.keys()) - set(self.piconCodesInBouquets)  )
        #self.piconsToDelete = list(  set( [self.kluc for self.kluc in self.piconCodesInHDD] )  -  set(self.piconCodesInBouquets)   )
        for self.piconcode in self.piconsToDelete:
            os_remove(self.piconDIR + '/' + self.piconcode + '.png') # v OpenATV nedostavam v adresaroch aj lomitko naviac, takze ho tu musim pridavat
            #os_remove(self.piconDIR + self.piconcode + '.png') # v OpenPLi dostavam v adresaroch aj lomitko naviac, takze ho tu netreba pridavat
            piconResults['removed'] += 1
        self.writeLog(_('...%s picons deleted.') % piconResults['removed'] )

        # 6) Pripraví sa zoznam názvov archívov .7z pre sťahovanie z internetu - podľa konfigurácie pluginu
        self.piconArchivesToDownload = []
        for sat in config.plugins.chocholousekpicons.usersats.value:            # example:  ['19.2E','23.5E']
            self.piconArchivesToDownload.append('picon%s-%s-%s_by_chocholousek' % (config.plugins.chocholousekpicons.background.value , config.plugins.chocholousekpicons.resolution.value , sat)   )

        # 7) Následovne v cykle sa budú sťahovať z internetu všetky používateľom zafajknuté archívy s piconami a spracovávať po jednom (t.j. pre viacero družíc, postupne jeden archív a potom stiahnem ďalší a znova spracujem)
        self.writeLog(_('The process started...') + _('(downloading and extracting all necessary picons)')  )
        self.writeLog('#' * 40)
        for count, fname in enumerate(self.piconArchivesToDownload, 1):
            s = ' %s / %s ' % (count, len(self.piconArchivesToDownload))
            self.writeLog('-' * 16 + s.ljust(20,'-'))
            self.proceedArchiveFile(fname)
            #self.writeLog('-' * 40)
        self.writeLog('#' * 40)
        self.writeLog(_('...the process is complete.') + _('(downloading and extracting all necessary picons)')  )
        
        # 8) Nakoniec sa zobrazí výsledok celého procesu do konzoly a zavolá sa "ukončovacia procedúra" (metóda) pod aktuálnou triedou, určenou na updatovanie pikon
        if piconResults['added'] or piconResults['changed']:
            message = _('After updating the picons you may need to restart the Enigma (GUI).') + '\n' + _('(%s added / %s changed / %s removed)') % (piconResults['added'] , piconResults['changed'] , piconResults['removed'])
            self.abortPiconsUpdating(False, message)
        else:
            message = _('No picons added or changed.') + '\n' + _('(%s added / %s changed / %s removed)') % (piconResults['added'] , piconResults['changed'] , piconResults['removed'])
            self.abortPiconsUpdating(False, message)

    def proceedArchiveFile(self, search_filename):

        # 0. Vyhľadanie google.drive ID kódu v obsahu "chochoContent" pre download konkrétneho súboru
        found = []
        for line in self.chochoContent.splitlines():
            if search_filename in line:
                found = line.split()
                break
        
        if not found:
            self.writeLog(_('Download ID for file %s was not found!') % search_filename)
            self.abortPiconsUpdating(True, _('Download ID for file %s was not found!') % search_filename )
        
        url_link = 'https://drive.google.com/uc?export=download&id=' + found[0]
        dwn_filename = found[1].replace('(','_').replace(')','_')               # replace the filename mask by new original archive filename and replace the parentheses by underline characters

        # 1. Stiahnutie archívu z internetu (súboru s piconami) do zložky "/tmp"
        self.writeLog(_('Trying download the file archive... %s') % dwn_filename)
        if not downloadFile(url_link, '/tmp/' + dwn_filename):
            self.writeLog(_('...file download failed !'))
            self.abortPiconsUpdating(True, _('Download failed!\nFile: %s\nURL: %s') % ('/tmp/' + dwn_filename , url_link)   )
        else:
            self.writeLog(_('...file download successful.'))

        # 2. Načítanie zoznamu všetkých súborov z archívu, včetne ich atribútov (veľkosti súborov)
        self.writeLog(_('Browse the contents of the downloaded archive file.'))
        self.piconCodesInArchive = self.getPiconListFromArchive('/tmp/' + dwn_filename)
        if not self.piconCodesInArchive:
            self.writeLog(_('Error! No picons found in the downloaded archive file!'))
            return          # navratenie vykonavania kodu z tohto podprogramu pre spracovanie archivu/suboru s piconami

        # 3. Rozbalenie a prepísanie potrebných picon (podľa listu potrebných piconiek), priamo do zložky s piconami v internej flash pamäti alebo do USB kľúča
        # 3A. ak meno súboru na disku existuje, tak potom ak veľkosť súborov sa nezhoduje, tak súbor nakopírujem/prepíšem z archívu na disk
        # 3B. ak meno súboru na disku vôbec neexistuje, tak súbor nakopírujem z archívu na disk
        self.writeLog(_('Preparing picon list for extracting (missing files and files of different sizes)...'))
        self.piconsToExtract = []
        global piconResults
        # zaujimam sa len o tie picony z archivu, ktore sa nachadzaju zaroven v zozname piconCodesInBouquets a zaroven v zozname piconCodesInArchive - tzn. vyberiem len zhodne prvky z dvoch mnozin: set(a) & set(b)
        #print('MYDEBUGLOGLINE\npikony v archive: %s \n pikony v buketoch: %s \npikony z hdd: %s \nprienik: %s' % (self.piconCodesInArchive, self.piconCodesInBouquets, self.piconCodesInHDD, set(self.piconCodesInArchive) & set(self.piconCodesInBouquets)  ))
        for piconcode in set(self.piconCodesInArchive) & set(self.piconCodesInBouquets):
            if piconcode in self.piconCodesInHDD:                                          # ak sa uz nachadza cez cyklus prechadzana picona z archivu aj na HDD (v klucoch slovnikoveho typu), tak...
                if self.piconCodesInHDD[piconcode] != self.piconCodesInArchive[piconcode]: # porovnam este velkosti tychto dvoch piconiek (archiv VS. HDD) a ak su velkosti picon odlisne...
                    self.piconsToExtract.append(piconcode)                                 # tak pridam tuto piconu do zoznamu potrebnych pre pozdejsie nakopirovanie pikon z archivu
                    piconResults['changed'] += 1
                else:
                    pass
            else:                                                                          # no ak sa vobec este nenachadza cyklom prechadzana picona z archivu aj na HDD, tak...
                self.piconsToExtract.append(piconcode)                                     # ju musim nakopirovat na HDD (pridam ju na zoznam kopirovanych)
                piconResults['added'] += 1

        # Overovanie, či sa našli vôbec nejaké picony k nakopírovaniu do boxu, ak áno potom sa začne extrakcia + kopírovanie súborov,
        # a v prípade že sa nenašli, tak funkcia bude prerušená (k žiadnému nakopírovaniu súborov nedôjde)
        if self.piconsToExtract:
            self.extractPiconsFromArchive('/tmp/' + dwn_filename , self.piconsToExtract)        
        self.writeLog(_('...%s picons was extracted from the archive.') % len(self.piconsToExtract))

        os_remove('/tmp/' + dwn_filename)

    def getPiconListFromArchive(self, archiveFile = ''):
        #out, status = subprocess.Popen([self.bin7zip, 'l', archiveFile], stdout=subprocess.PIPE ).communicate()
        #out = subprocess.check_output([self.bin7zip, 'l', archiveFile])
        status, out = getstatusoutput('%s l %s' % (self.bin7zip, archiveFile))      # vracia dvojicu, prva prestavuje chybovy kod (0 ak nedoslo k ziadnym problemom) a druha predstavuje std.output (kompletny textovy vystup z command-line / Shell)
        if status == 0:
            out = out.splitlines()
            tempDict = {}
            i = -3
            while not '-----' in out[i]:
                # vycucnem udaje z vystupu / z kazdeho riadka:
                # 0               :19 20:25    26  :  38             53:
                # 2018-07-14 14:48:53 ....A          797               CONTROL/postinst
                fdatetime, fattr, fsize, fpath = out[i][0:19] , out[i][20:25] , out[i][26:38] , out[i][53:]
                if fattr[0] != 'D':    # retreive all files with a full path, but no individual directories from the list
                    tempDict.update({  fpath.split('/')[-1].split('.')[0]  :  int(fsize)  })      #  { servisny_referencny_kod_<key> : velkost_suboru_<int> }
                i -= 1
            return tempDict
        elif status == 32512:
            self.writeLog('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:\nopkg update && opkg install p7zip\n...or download and install the package from internet.\n' % status )
        elif status == 512:
            self.writeLog('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out) )
        return ''         # return the empty string on any errors !

    def extractPiconsFromArchive(self, archiveFile, piconsForProcessing):
        self.writeLog(_('Extracting files from the archive...'))
        with open('/tmp/picons-to-extraction.txt','w') as f:
            for s in piconsForProcessing:
                f.write(s + '.png\n')
        status, out = getstatusoutput('%s e -y -o%s %s @/tmp/picons-to-extraction.txt' % (self.bin7zip, self.piconDIR, archiveFile) )
        if status == 0:
            self.writeLog(_('...done.'))
            return True
        elif status == 32512:
            self.writeLog('...error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status )
        elif status == 512:
            self.writeLog('...error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('...error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
        if os_path.exists('/tmp/picons-to-extraction.txt'):
            os_remove('/tmp/picons-to-extraction.txt')
        return False

    def abortPiconsUpdating(self, boo=True, msssg=''):   # boo=True -- exit with some errors ;  boo=False -- exit without errors
        self.message = msssg
        if boo:
            self.type = MessageBox.TYPE_ERROR
            if not self.message:
                self.message = _('Some errors has occurred !')
        else:
            self.type = MessageBox.TYPE_INFO
            if not self.message:
                self.message = _('Done !') + '\n' + _('(%s added / %s changed / %s removed)') % (piconResults['added'] , piconResults['changed'] , piconResults['removed'])
        self.writeLog(self.message)
        sleep(3)
        if self.timeoutPrevention is not None:
            self.timeoutPrevention.stop()
        self.timeoutPrevention = None
        self['logWindow'].hide()
        self.session.open(MessageBox, self.message, type = self.type)
        self.close()

    def writeLog(self, msgg = ''):
        if self.timeoutPrevention is not None:
            self.timeoutPrevention.stop()
            print(msgg)
            self['logWindow'].appendText('\n[' + str( ( datetime.now() - self.startTime ).total_seconds() ).ljust(10,"0")[:6] + '] ' + msgg)
            self['logWindow'].lastPage()
            self.timeoutPrevention.start(20000, True)                  # (milisekundy , True = spustit len 1x / False = spustat opakovane)


###########################################################################
###########################################################################


def findHostnameAndNewPlugin():
    '''
    return "" ----- if a new online version was not found
    return URL ---- if a new online version was found
    '''
    global plugin_version_local, plugin_version_online
    url_lnk = ''
    url_list = ['https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/', 'http://aion.webz.cz/ChocholousekPicons/']        # pozor ! je dolezite zachovat na konci retazca vo web.adresach vzdy aj lomitko, pre dalsie korektne pouzivanie tohoto retazca v algoritme
    for hostname in url_list:
        try:
            mycontext = ssl._create_unverified_context()
            url_handle = urllib2.urlopen(hostname + 'version.txt', context = mycontext)
        except urllib2.URLError as err:
            print('Error %s when reading from URL %s' % (err.reason, hostname + 'version.txt')  )
        except Exception:
            print('Error when reading URL %s' % hostname + 'version.txt')
        else:
            plugin_version_online = url_handle.read()
            if plugin_version_online > plugin_version_local:    # Python 2.7 dokaze porovnat aj dva retazce... poradie porovnavania dvoch <str> je postupnostou hodnot znakov ASCII kodov v poradi z lava do prava a paradoxom v porovnani je, ze male znaky ASCII maju vyssiu hodnotu a preto su v porovnani <str> na vyssiej urovni ! v mojom pripade sa vsak jedna o cislice a tie su v ASCII kode rovnake (kod 0x30 az 0x39)
                url_lnk = hostname
                break
    return url_lnk

def pluginUpdateDo():
    '''
    return True ----- if a new version was successfull downloaded and installed
    return False ---- if a new version was not found
    '''
    global plugin_version_local, plugin_version_online
    url_host = findHostnameAndNewPlugin()
    if url_host:
        url_host = url_host + 'enigma2-plugin-extensions-chocholousek-picons_' + plugin_version_online + '_all.ipk'
        dwn_file = '/tmp/' + url_host.split('/')[-1]
        if downloadFile(url_host, dwn_file):
            os_system("opkg install --force-reinstall %s > /dev/null 2>&1" % dwn_file)
            print('New plugin version was installed ! old ver.:%s , new ver.:%s' % (plugin_version_local, plugin_version_online)  )
            plugin_version_local = plugin_version_online
            return True
        else:
            return False
    else:
        print('New plugin version is not available - local ver.:%s , online ver.:%s' % (plugin_version_local, plugin_version_online)  )
        return False


###########################################################################
###########################################################################


def downloadFile____old(self, url, targetfile):
    if os_system('wget -q -O "%s" --no-check-certificate "%s" > /dev/null 2>&1' % (targetfile, url)  ):
        return False
    else:
        return True

def downloadFile______old(self, url, targetfile):
    status, out = getstatusoutput('wget -q -O "%s" --no-check-certificate "%s"' % (targetfile, url) )
    if status == 0:
        return True
    else:
        self.writeLog('CMD-Line: %s\nDownload error number: %s\nError console output: %s\n' % ('wget -q -O "%s" --no-check-certificate "%s"' % (targetfile,url) , status , out)   )
        return False

def downloadFile(url, targetfile):
    header = {'User-Agent':'Mozilla/5.0'}
    my_context = ssl._create_unverified_context()
    try:
        req = urllib2.Request(url, None, header)
        data = urllib2.urlopen(req, context = my_context).read()
        with open(targetfile, 'wb') as f:
            f.write(data)
    except urllib2.HTTPError as e:
        print("HTTP Error: %s, URL: %s" % (e.code, url))
        return False
    except urllib2.URLError as e:
        print("URL Error: %s, URL: %s" % (e.reason, url))
        return False
    except IOError as e:
        print("I/O Error: %s, File: %s" % (e.reason, targetfile))
        return False
    except Exception as e:
        print("File download error: %s, URL: %s" % (e, url))
        return False
    return True

def downloadFile________old(url, targetfile):
    header = {'User-Agent':'Mozilla/5.0'}
    mycontext = ssl._create_unverified_context()
    try:
        req = urllib2.Request(url, None, header)
        handle = urllib2.urlopen(req, context = mycontext)
        with open(file, 'wb') as f:
            while True:
                cache = handle.read(16 * 1024)
                if not cache:
                    break
                f.write(cache)
    except urllib2.HTTPError as e:
        print("HTTP Error: %s, URL: %s" % (e.code, url))
        return False
    except urllib2.URLError as e:
        print("URL Error: %s, URL: %s" % (e.reason, url))
        return False
    except IOError as e:
        print("I/O Error: %s, File: %s" % (e.reason, targetfile))
        return False
    except Exception as e:
        print("File download error: %s, URL: %s" % (e, url))
        return False
    return True


###########################################################################
###########################################################################


def autoStart(reason, **kwargs):                           # starts DURING the Enigma2 booting
    if reason == 0:    # and kwargs.has_key('session'):
        print('PLUGINSTARTDEBUGLOG - autoStart executed , reason == 0 , kwargs.has_key("session") = %s' % kwargs.has_key("session")  )
    if reason == 1:
        print('PLUGINSTARTDEBUGLOG - autoStart executed , reason == 1 , kwargs.has_key("session") = %s' % kwargs.has_key("session")  )

def pluginMenu(session, **kwargs):                          # starts when the plugin is opened via Plugin-MENU
    print('PLUGINSTARTDEBUGLOG - pluginMenu executed')
    global plugin_version_local
    plugin_version_local = open(PLUGIN_PATH + 'version.txt','r').read()
    session.open(mainConfigScreen)

def sessionStart(reason, session):                         # starts AFTER the Enigma2 booting
    if reason == 0:
        print('PLUGINSTARTDEBUGLOG - sessionStart executed, reason == 0')
        #session = kwargs['session']
    if reason == 1:
        print('PLUGINSTARTDEBUGLOG - sessionStart executed, reason == 1')
        session = None

def Plugins(**kwargs):
    """ Register plugin in the plugin menu and prepare the plugin with autostart """
    return [
        PluginDescriptor(
            where = PluginDescriptor.WHERE_AUTOSTART,      # starts DURING the Enigma2 booting
            #where = [PluginDescriptor.WHERE_AUTOSTART , PluginDescriptor.WHERE_SESSIONSTART],
            fnc = autoStart),
        PluginDescriptor(
            where = PluginDescriptor.WHERE_SESSIONSTART,   # starts AFTER the Enigma2 booting
            fnc = sessionStart),
        PluginDescriptor(
            where = PluginDescriptor.WHERE_PLUGINMENU,     # starts when the plugin is opened via Plugin-MENU
            name = "Chocholousek picons",
            description = "Download and update Chocholousek picons",
            icon = "images/plugin.png",
            fnc = pluginMenu)
        ]
