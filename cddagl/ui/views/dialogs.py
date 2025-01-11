import html
import logging
import os
import platform
import traceback
from io import StringIO
from urllib.parse import urlencode

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QToolButton,
    QDialog, QTextBrowser, QMessageBox, QHBoxLayout, QTextEdit
)

import cddagl.constants as cons
from cddagl import __version__ as version
from cddagl.constants import get_resource_path
from cddagl.functions import clean_qt_path, bitness
from cddagl.i18n import proxy_gettext as _
from cddagl.win32 import get_downloads_directory

import markdown2

logger = logging.getLogger('cddagl')


class BrowserDownloadDialog(QDialog):
    def __init__(self, name, url, expected_filename):
        super(BrowserDownloadDialog, self).__init__()

        self.name = name
        self.url = url
        self.expected_filename = expected_filename
        self.downloaded_path = None

        layout = QGridLayout()

        info_label = QLabel()
        info_label.setText(_('This {name} cannot be directly downloaded by the '
            'launcher. You have to use your browser to download it.').format(
            name=name))
        layout.addWidget(info_label, 0, 0, 1, 2)
        self.info_label = info_label

        step1_label = QLabel()
        step1_label.setText(_('1. Open the URL in your browser.'))
        layout.addWidget(step1_label, 1, 0, 1, 2)
        self.step1_label = step1_label

        url_tb = QTextBrowser()
        url_tb.setText('<a href="{url}">{url}</a>'.format(url=html.escape(url)))
        url_tb.setReadOnly(True)
        url_tb.setOpenExternalLinks(True)
        url_tb.setMaximumHeight(23)
        url_tb.setLineWrapMode(QTextEdit.NoWrap)
        url_tb.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(url_tb, 2, 0, 1, 2)
        self.url_tb = url_tb

        step2_label = QLabel()
        step2_label.setText(_('2. Download the {name} on that page and wait '
            'for the download to complete.').format(name=name))
        layout.addWidget(step2_label, 3, 0, 1, 2)
        self.step2_label = step2_label

        step3_label = QLabel()
        step3_label.setText(_('3. Select the downloaded archive.'))
        layout.addWidget(step3_label, 4, 0, 1, 2)
        self.step3_label = step3_label

        path = get_downloads_directory()
        if expected_filename is not None:
            path = os.path.join(path, expected_filename)

        download_path_le = QLineEdit()
        download_path_le.setText(path)
        layout.addWidget(download_path_le, 5, 0)
        self.download_path_le = download_path_le

        download_path_button = QToolButton()
        download_path_button.setText('...')
        download_path_button.clicked.connect(self.set_download_path)
        layout.addWidget(download_path_button, 5, 1)
        self.download_path_button = download_path_button

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_container.setLayout(buttons_layout)

        install_button = QPushButton()
        install_button.setText(_('Install this {name}').format(name=name))
        install_button.clicked.connect(self.install_clicked)
        buttons_layout.addWidget(install_button)
        self.install_button = install_button

        do_not_install_button = QPushButton()
        do_not_install_button.setText(_('Do not install'))
        do_not_install_button.clicked.connect(self.do_not_install_clicked)
        buttons_layout.addWidget(do_not_install_button)
        self.do_not_install_button = do_not_install_button

        layout.addWidget(buttons_container, 6, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
        self.buttons_container = buttons_container
        self.buttons_layout = buttons_layout

        self.setLayout(layout)

        self.setWindowTitle(_('Browser download'))

    def set_download_path(self):
        options = QFileDialog.DontResolveSymlinks
        selected_file, selected_filter = QFileDialog.getOpenFileName(self,
            _('Downloaded archive'), self.download_path_le.text(),
            _('Archive files {formats}').format(formats='(*.zip *.rar *.7z)'),
            options=options)
        if selected_file:
            self.download_path_le.setText(clean_qt_path(selected_file))

    def install_clicked(self):
        choosen_file = self.download_path_le.text()
        if not os.path.isfile(choosen_file):
            filenotfound_msgbox = QMessageBox()
            filenotfound_msgbox.setWindowTitle(_('File not found'))

            text = (_('{filepath} is not an existing file on your system. '
                'Make sure to download the archive with your browser. Make '
                'sure to select the downloaded archive afterwards.')).format(
                    filepath=choosen_file
                )

            filenotfound_msgbox.setText(text)
            filenotfound_msgbox.addButton(_('I will try again'),
                QMessageBox.AcceptRole)
            filenotfound_msgbox.setIcon(QMessageBox.Warning)
            filenotfound_msgbox.exec()

            return

        self.downloaded_path = choosen_file
        self.done(1)

    def do_not_install_clicked(self):
        self.done(0)


class FaqDialog(QDialog):
    def __init__(self, parent=0, f=0):
        super(FaqDialog, self).__init__(parent, f)

        layout = QGridLayout()

        text_content = QTextBrowser()
        text_content.setReadOnly(True)
        text_content.setOpenExternalLinks(True)

        layout.addWidget(text_content, 0, 0)
        self.text_content = text_content

        ok_button = QPushButton()
        ok_button.clicked.connect(self.done)
        layout.addWidget(ok_button, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.ok_button = ok_button

        layout.setRowStretch(0, 100)

        self.setMinimumSize(640, 450)

        self.setLayout(layout)
        self.set_text()

    def set_text(self):
        self.setWindowTitle(_('Frequently asked questions (FAQ)'))
        self.ok_button.setText(_('OK'))

        m = _('<h2>Kitten CDDA Launcher Frequently asked questions (FAQ)</h2>')

        html_faq = markdown2.markdown(_('''
### Where is my previous version?

Is it stored in the `previous_version` directory inside your game directory.

### How does the launcher update my game?

* The launcher downloads the archive for the new version.
* If the `previous_version` subdirectory exists, the launcher moves it in the recycle bin.
* The launcher moves everything from the game directory in the `previous_version` subdirectory.
* The launcher extracts the downloaded archive in the game directory.
* The launcher inspect what is in the `previous_version` directory and it copies the saves, the mods, the tilesets, the soundpacks and a bunch of others useful files from the `previous_version` directory that are missing from the downloaded archive to the real game directory. It will assume that mods that are included in the downloaded archive are the newest and latest version and it will keep those by comparing their unique ident value.

### I think the launcher just deleted my files. What can I do?

The launcher goes to great lengths not to delete any file that could be important to you. With the default and recommended settings, the launcher will always move files instead of deleting them. If you think you lost files during an update, check out the `previous_version` subdirectory. That is where you should be able to find your previous game version. You can also check for files in your recycle bin. Those are the main 2 places where files are moved and where you should be able to find them.

### My antivirus product detected the launcher as a threat. What can I do?

Poor antivirus products are known to detect the launcher as a threat and block its execution or delete the launcher. A simple workaround is to add the launcher binary in your antivirus whitelist or select the action to trust this binary when detected.

If you are paranoid, you can always inspect the source code yourself and build the launcher from the source code. You are still likely to get false positives. There is little productive efforts we can do as software developers with these. We have [a nice building guide](https://github.com/Fris0uman/CDDA-Game-Launcher/blob/master/BUILDING.md) for those who want to build the launcher from the source code.

Many people are dying to know why antivirus products are identifying the launcher as a threat. There has been many wild speculations to try to pinpoint the root cause for this. The best way to find out would be to ask those antivirus product developers. Unfortunatly, they are unlikely to respond for many good reasons. We could also speculate on this for days on end. Our current best speculation is because we use a component called PyInstaller [that is commonly flagged as a threat](https://github.com/pyinstaller/pyinstaller/issues/4633). Now, if you want see how deep the rabbit hole goes, you can keep on searching or speculating on why PyInstaller itself is commonly flagged as a threat. This research is left as an exercise to the reader.

Many people are also asking why not simply report the launcher as a false positive to those antivirus products. We welcome anyone who wants to take the time to do it, but we believe it is mostly unproductive. Those processes are often time-consuming and ignored. Someone would also have to do them all over again each time we make a new release or when one of the component we use is updated or changed. The current state of threat detection on PC is quite messy and sad especially for everyone using *free* antivirus products.

### I found an issue with the game itself or I would like to make a suggestion for the game itself. What should I do?

You should [contact the game developpers](https://cataclysmdda.org/#ive-found-a-bug--i-would-like-to-make-a-suggestion-what-should-i-do) about this. We are mainly providing a tool to help with the game. We cannot provide support for the game itself.

### How do I update to a new version of the game launcher?

[TBD]
### The launcher keeps crashing when I start it. What can I do?

You might need to delete your configs file to work around this issue. That filename is `configs.db` and it is located in `%LOCALAPPDATA%\CDDA Game Launcher\`. Some users have reported and encountered unrelated starting issues. In some cases, running a debug version of the launcher to get more logs might help to locate the issue. [Creating an issue about this](https://github.com/Fris0uman/CDDA-Game-Launcher/issues) is probably the way to go.

### I just installed the game and it already has a big list of mods. Is there something wrong?

The base game is bundled with a good number of mods. You can view them more like modules that you can activate or ignore when creating a new world in game. These mods or modules can provide a different game experience by adding new items, buildings, mobs, by disabling some game mechanics or by changing how you play the game. They are a simple way of having a distinctive playthrough using the same game engine. The game is quite enjoyable without any of these additional mods or by using the default mods when creating a new world. You should probably avoid using additional mods if you are new to the game for your first playthrough to get familiar with the game mechanics. Once you are comfortable, after one or a few playthroughs, I suggest you check back the base game mods or even some external mods for your next world.

### Will you make a Linux or macOS version?

[TBD]

### It does not work? Can you help me?

Submit your issues [on Github](https://github.com/Fris0uman/CDDA-Game-Launcher/issues). Try to [report bugs effectively](http://www.chiark.greenend.org.uk/~sgtatham/bugs.html).
'''))

        m += html_faq

        self.text_content.setHtml(m)

class AboutDialog(QDialog):
    def __init__(self, parent=0, f=0):
        super(AboutDialog, self).__init__(parent, f)

        layout = QGridLayout()

        text_content = QTextBrowser()
        text_content.setReadOnly(True)
        text_content.setOpenExternalLinks(True)

        text_content.setSearchPaths([get_resource_path()])
        layout.addWidget(text_content, 0, 0)
        self.text_content = text_content

        ok_button = QPushButton()
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.ok_button = ok_button

        layout.setRowStretch(0, 100)

        self.setMinimumSize(640, 450)

        self.setLayout(layout)
        self.set_text()

    def set_text(self):
        self.setWindowTitle(_('About Kitten CDDA Launcher'))
        self.ok_button.setText(_('OK'))
        m = _('<p>Kitten CDDA Launcher version {version}</p>').format(version=version)
        m += _('<p>Get the latest release'
               ' <a href="https://github.com/Fris0uman/CDDA-Game-Launcher/releases">on GitHub</a>.'
               '</p>')
        m += _('<p>Please report any issue'
               ' <a href="https://github.com/Fris0uman/CDDA-Game-Launcher/issues/new">on GitHub</a>.'
               '</p>')
        m += _('<p>Thanks to Rémy Roy for the <a href="https://github.com/remyroy/CDDA-Game-Launcher/">original implementation</a>' )
        m += _('<p>Thanks to the following people for their efforts in'
               ' translating the Kitten CDDA Launcher</p>'
               '<ul>'
               '<li>Russian: Daniel from <a href="http://cataclysmdda.ru/">cataclysmdda.ru</a>'
               ' and Night_Pryanik'
               '</li>'
               '<li>Italian: Rettiliano Verace from'
               ' <a href="http://emigrantebestemmiante.blogspot.com">Emigrante Bestemmiante</a>'
               '</li>'
               '<li>French: Rémy Roy</li>'
               '<li>Spanish: KurzedMetal</li>'
               '</ul>')
        m += _('<p>This software is distributed under the MIT License. That means this is'
               ' 100&#37; free software, completely free to use, modify and/or distribute.'
               ' If you like more details check the following boring legal stuff...</p>')
        m += '<p>Copyright (c) 2015-2021 Rémy Roy</p>'
        m += ('<p>Permission is hereby granted, free of charge, to any person obtaining a copy'
              ' of this software and associated documentation files (the "Software"), to deal'
              ' in the Software without restriction, including without limitation the rights'
              ' to use, copy, modify, merge, publish, distribute, sublicense, and/or sell'
              ' copies of the Software, and to permit persons to whom the Software is'
              ' furnished to do so, subject to the following conditions:</p>'
              '<p>The above copyright notice and this permission notice shall be included in'
              ' all copies or substantial portions of the Software.</p>'
              '<p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
              ' IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,'
              ' FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE'
              ' AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER'
              ' LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,'
              ' OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE'
              ' SOFTWARE.</p>')
        self.text_content.setHtml(m)


class ExceptionWindow(QWidget):
    def __init__(self, app, extype, value, tb):
        super(ExceptionWindow, self).__init__()

        self.app = app

        layout = QGridLayout()

        information_label = QLabel()
        information_label.setText(_('The Kitten CDDA Launcher just crashed. An '
            'unhandled exception was raised. Here are the details.'))
        layout.addWidget(information_label, 0, 0)
        self.information_label = information_label

        tb_io = StringIO()
        traceback.print_tb(tb, file=tb_io)
        traceback_content = html.escape(tb_io.getvalue()).replace('\n', '<br>')

        text_content = QTextBrowser()
        text_content.setReadOnly(True)
        text_content.setOpenExternalLinks(True)
        text_content.setHtml(_('''
<p>Kitten CDDA Launcher version: {version}</p>
<p>OS: {os} ({bitness})</p>
<p>Type: {extype}</p>
<p>Value: {value}</p>
<p>Traceback:</p>
<code>{traceback}</code>
''').format(version=html.escape(version), extype=html.escape(str(extype)),
    value=html.escape(str(value)), os=html.escape(platform.platform()),
    traceback=traceback_content, bitness=html.escape(bitness())))

        layout.addWidget(text_content, 1, 0)
        self.text_content = text_content

        report_url = cons.NEW_ISSUE_URL + '?' + urlencode({
            'title': _('Unhandled exception: [Enter a title]'),
            'body': _('''* Description: [Enter what you did and what happened]
* Version: {version}
* OS: {os} ({bitness})
* Type: `{extype}`
* Value: {value}
* Traceback:
```
{traceback}
```
''').format(version=version, extype=str(extype), value=str(value),
    traceback=tb_io.getvalue(), os=platform.platform(), bitness=bitness())
        })

        report_label = QLabel()
        report_label.setOpenExternalLinks(True)
        report_label.setText(_('Please help us make a better launcher '
            '<a href="{url}">by reporting this issue on GitHub</a>.').format(
                url=html.escape(report_url)))
        layout.addWidget(report_label, 2, 0)
        self.report_label = report_label

        exit_button = QPushButton()
        exit_button.setText(_('Exit'))
        exit_button.clicked.connect(lambda: self.app.exit(-100))
        layout.addWidget(exit_button, 3, 0, Qt.AlignmentFlag.AlignRight)
        self.exit_button = exit_button

        self.setLayout(layout)
        self.setWindowTitle(_('Something went wrong'))
        self.setMinimumSize(350, 0)


class LicenceDialog(QDialog):
    def __init__(self, parent=0, f=0):
        super(LicenceDialog, self).__init__(parent, f)

        layout = QGridLayout()

        text_content = QTextBrowser()
        text_content.setReadOnly(True)
        text_content.setOpenExternalLinks(True)

        text_content.setSearchPaths([get_resource_path()])
        layout.addWidget(text_content, 0, 0)
        self.text_content = text_content

        ok_button = QPushButton()
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.ok_button = ok_button

        layout.setRowStretch(0, 100)

        self.setMinimumSize(640, 450)

        self.setLayout(layout)
        self.set_text()

    def set_text(self):
        self.setWindowTitle(_('Licenses'))
        self.ok_button.setText(_('OK'))
        m = _('<p>Kitten CDDA Launcher uses a number of packages under different licenses:</p>')

        m += _('<h3>Pyside6 and Qt are licensed under the LGPL license: </h3>')
        m += " <h3 style='text-align: center;'>GNU LESSER GENERAL PUBLIC LICENSE</h3>"\
            "<p style='text-align: center;'>Version 3, 29 June 2007</p> <p>Copyright © 2007 Free Software Foundation, "\
            "Inc.  &lt;<a href='https://fsf.org/'>https://fsf.org/</a>&gt;</p><p>  Everyone is permitted to copy and "\
            "distribute verbatim copies  of this license document, but changing it is not allowed.</p> <p>This "\
            "version of the GNU Lesser General Public License incorporates the terms and conditions of version 3 of "\
            "the GNU General Public License, supplemented by the additional permissions listed below.</p> <h4 "\
            "id='section0'>0. Additional Definitions.</h4> <p>As used herein, “this License” refers to version 3 of "\
            "the GNU Lesser General Public License, and the “GNU GPL” refers to version 3 of the GNU General Public "\
            "License.</p> <p>“The Library” refers to a covered work governed by this License, other than an "\
            "Application or a Combined Work as defined below.</p> <p>An “Application” is any work that makes use of "\
            "an interface provided by the Library, but which is not otherwise based on the Library. Defining a "\
            "subclass of a class defined by the Library is deemed a mode of using an interface provided by the "\
            "Library.</p> <p>A “Combined Work” is a work produced by combining or linking an Application with the "\
            "Library.  The particular version of the Library with which the Combined Work was made is also called the "\
            "“Linked Version”.</p> <p>The “Minimal Corresponding Source” for a Combined Work means the Corresponding "\
            "Source for the Combined Work, excluding any source code for portions of the Combined Work that, "\
            "considered in isolation, are based on the Application, and not on the Linked Version.</p> <p>The "\
            "“Corresponding Application Code” for a Combined Work means the object code and/or source code for the "\
            "Application, including any data and utility programs needed for reproducing the Combined Work from the "\
            "Application, but excluding the System Libraries of the Combined Work.</p> <h4 id='section1'>1. Exception "\
            "to Section 3 of the GNU GPL.</h4> <p>You may convey a covered work under sections 3 and 4 of this "\
            "License without being bound by section 3 of the GNU GPL.</p> <h4 id='section2'>2. Conveying Modified "\
            "Versions.</h4> <p>If you modify a copy of the Library, and, in your modifications, a facility refers to "\
            "a function or data to be supplied by an Application that uses the facility (other than as an argument "\
            "passed when the facility is invoked), then you may convey a copy of the modified version:</p> <ul> "\
            "<li>a) under this License, provided that you make a good faith effort to    ensure that, in the event an "\
            "Application does not supply the    function or data, the facility still operates, and performs    "\
            "whatever part of its purpose remains meaningful, or</li> <li>b) under the GNU GPL, with none of the "\
            "additional permissions of    this License applicable to that copy.</li> </ul> <h4 id='section3'>3. "\
            "Object Code Incorporating Material from Library Header Files.</h4> <p>The object code form of an "\
            "Application may incorporate material from a header file that is part of the Library.  You may convey "\
            "such object code under terms of your choice, provided that, if the incorporated material is not limited "\
            "to numerical parameters, data structure layouts and accessors, or small macros, inline functions and "\
            "templates (ten or fewer lines in length), you do both of the following:</p> <ul> <li>a) Give prominent "\
            "notice with each copy of the object code that the    Library is used in it and that the Library and its "\
            "use are    covered by this License.</li> <li>b) Accompany the object code with a copy of the GNU GPL and "\
            "this license    document.</li> </ul> <h4 id='section4'>4. Combined Works.</h4> <p>You may convey a "\
            "Combined Work under terms of your choice that, taken together, effectively do not restrict modification "\
            "of the portions of the Library contained in the Combined Work and reverse engineering for debugging such "\
            "modifications, if you also do each of the following:</p> <ul> <li>a) Give prominent notice with each "\
            "copy of the Combined Work that    the Library is used in it and that the Library and its use are    "\
            "covered by this License.</li> <li>b) Accompany the Combined Work with a copy of the GNU GPL and this "\
            "license    document.</li> <li>c) For a Combined Work that displays copyright notices during    "\
            "execution, include the copyright notice for the Library among    these notices, as well as a reference "\
            "directing the user to the    copies of the GNU GPL and this license document.</li> <li>d) Do one of the "\
            "following: <ul> <li>0) Convey the Minimal Corresponding Source under the terms of this        License, "\
            "and the Corresponding Application Code in a form        suitable for, and under terms that permit, "\
            "the user to        recombine or relink the Application with a modified version of        the Linked "\
            "Version to produce a modified Combined Work, in the        manner specified by section 6 of the GNU GPL "\
            "for conveying        Corresponding Source.</li> <li>1) Use a suitable shared library mechanism for "\
            "linking with the        Library.  A suitable mechanism is one that (a) uses at run time        a copy of "\
            "the Library already present on the user's computer        system, and (b) will operate properly with a "\
            "modified version        of the Library that is interface-compatible with the Linked        Version.</li> "\
            "</ul></li> <li>e) Provide Installation Information, but only if you would otherwise    be required to "\
            "provide such information under section 6 of the    GNU GPL, and only to the extent that such information "\
            "is    necessary to install and execute a modified version of the    Combined Work produced by "\
            "recombining or relinking the    Application with a modified version of the Linked Version. (If    you "\
            "use option 4d0, the Installation Information must accompany    the Minimal Corresponding Source and "\
            "Corresponding Application    Code. If you use option 4d1, you must provide the Installation    "\
            "Information in the manner specified by section 6 of the GNU GPL    for conveying Corresponding "\
            "Source.)</li> </ul> <h4 id='section5'>5. Combined Libraries.</h4> <p>You may place library facilities "\
            "that are a work based on the Library side by side in a single library together with other library "\
            "facilities that are not Applications and are not covered by this License, and convey such a combined "\
            "library under terms of your choice, if you do both of the following:</p> <ul> <li>a) Accompany the "\
            "combined library with a copy of the same work based    on the Library, uncombined with any other library "\
            "facilities,    conveyed under the terms of this License.</li> <li>b) Give prominent notice with the "\
            "combined library that part of it    is a work based on the Library, and explaining where to find the    "\
            "accompanying uncombined form of the same work.</li> </ul> <h4 id='section6'>6. Revised Versions of the "\
            "GNU Lesser General Public License.</h4> <p>The Free Software Foundation may publish revised and/or new "\
            "versions of the GNU Lesser General Public License from time to time. Such new versions will be similar "\
            "in spirit to the present version, but may differ in detail to address new problems or concerns.</p> "\
            "<p>Each version is given a distinguishing version number. If the Library as you received it specifies "\
            "that a certain numbered version of the GNU Lesser General Public License “or any later version” applies "\
            "to it, you have the option of following the terms and conditions either of that published version or of "\
            "any later version published by the Free Software Foundation. If the Library as you received it does not "\
            "specify a version number of the GNU Lesser General Public License, you may choose any version of the GNU "\
            "Lesser General Public License ever published by the Free Software Foundation.</p> <p>If the Library as "\
            "you received it specifies that a proxy can decide whether future versions of the GNU Lesser General "\
            "Public License shall apply, that proxy's public statement of acceptance of any version is permanent "\
            "authorization for you to choose that version for the Library.</p> "

        m += _('<h3>SQLAlchemy, alembic, pywinutils, and markdown2 are licensed under the MIT license</h3>')
        m += "<h3 style='text-align: center;'>The MIT License (MIT)</h3> <p>Permission is hereby granted, " \
             "free of charge, to any person obtaining a copy of this software and associated documentation files (the " \
             "“Software”), to deal in the Software without restriction, including without limitation the rights to " \
             "use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, " \
             "and to permit persons to whom the Software is furnished to do so, subject to the following " \
             "conditions:</p> <p>The above copyright notice and this permission notice shall be included in all " \
             "copies or substantial portions of the Software.</p> <p>THE SOFTWARE IS PROVIDED “AS IS”, " \
             "WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF " \
             "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR " \
             "COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF " \
             "CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR " \
             "OTHER DEALINGS IN THE SOFTWARE.</p> "

        m += _('<h3>Requests and arrow are licensed under the Apache 2.0 license: </h3>')
        m += "<h3 style='text-align: center;'>Apache License</h3>   <p style='text-align: center;'> Version 2.0, "\
               "January 2004</p>   <p style='text-align: center;'>http://www.apache.org/licenses/</p> <p>TERMS AND "\
               "CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION</p> <p>1. Definitions.</p> <p>'License' shall mean "\
               "the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 "\
               "of this document.</p> <p>'Licensor' shall mean the copyright owner or entity authorized by the "\
               "copyright owner that is granting the License.</p> <p>'Legal Entity' shall mean the union of the "\
               "acting entity and all other entities that control, are controlled by, or are under common control "\
               "with that entity. For the purposes of this definition, 'control' means (i) the power, "\
               "direct or indirect, to cause the direction or management of such entity, whether by contract or "\
               "otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, "\
               "or (iii) beneficial ownership of such entity.</p> <p>'You' (or 'Your') shall mean an individual or "\
               "Legal Entity exercising permissions granted by this License.</p> <p>'Source' form shall mean the "\
               "preferred form for making modifications, including but not limited to software source code, "\
               "documentation source, and configuration files.</p> <p>'Object' form shall mean any form resulting "\
               "from mechanical transformation or translation of a Source form, including but not limited to compiled "\
               "object code, generated documentation, and conversions to other media types.</p> <p>'Work' shall mean "\
               "the work of authorship, whether in Source or Object form, made available under the License, "\
               "as indicated by a copyright notice that is included in or attached to the work (an example is "\
               "provided in the Appendix below).</p> <p>'Derivative Works' shall mean any work, whether in Source or "\
               "Object form, that is based on (or derived from) the Work and for which the editorial revisions, "\
               "annotations, elaborations, or other modifications represent, as a whole, an original work of "\
               "authorship. For the purposes of this License, Derivative Works shall not include works that remain "\
               "separable from, or merely link (or bind by name) to the interfaces of, the Work and Derivative Works "\
               "thereof.</p> <p>'Contribution' shall mean any work of authorship, including the original version of "\
               "the Work and any modifications or additions to that Work or Derivative Works thereof, "\
               "that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an "\
               "individual or Legal Entity authorized to submit on behalf of the copyright owner. For the purposes of "\
               "this definition, 'submitted' means any form of electronic, verbal, or written communication sent to "\
               "the Licensor or its representatives, including but not limited to communication on electronic mailing "\
               "lists, source code control systems, and issue tracking systems that are managed by, or on behalf of, "\
               "the Licensor for the purpose of discussing and improving the Work, but excluding communication that "\
               "is conspicuously marked or otherwise designated in writing by the copyright owner as 'Not a "\
               "Contribution.'</p> <p>'Contributor' shall mean Licensor and any individual or Legal Entity on behalf "\
               "of whom a Contribution has been received by Licensor and subsequently incorporated within the "\
               "Work.</p> <p>2. Grant of Copyright License. Subject to the terms and conditions of this License, "\
               "each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, "\
               "irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, "\
               "publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object "\
               "form.</p> <p>3. Grant of Patent License. Subject to the terms and conditions of this License, "\
               "each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, "\
               "irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, "\
               "sell, import, and otherwise transfer the Work, where such license applies only to those patent claims "\
               "licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by "\
               "combination of their Contribution(s) with the Work to which such Contribution(s) was submitted. If "\
               "You institute patent litigation against any entity (including a cross-claim or counterclaim in a "\
               "lawsuit) alleging that the Work or a Contribution incorporated within the Work constitutes direct or "\
               "contributory patent infringement, then any patent licenses granted to You under this License for that "\
               "Work shall terminate as of the date such litigation is filed.</p> <p>4. Redistribution. You may "\
               "reproduce and distribute copies of the Work or Derivative Works thereof in any medium, "\
               "with or without modifications, and in Source or Object form, provided that You meet the following "\
               "conditions:</p> <p>(a) You must give any other recipients of the Work or  Derivative Works a copy of "\
               "this License; and</p> <p>(b) You must cause any modified files to carry prominent notices  stating "\
               "that You changed the files; and</p> <p>(c) You must retain, in the Source form of any Derivative "\
               "Works  that You distribute, all copyright, patent, trademark, and  attribution notices from the "\
               "Source form of the Work,  excluding those notices that do not pertain to any part of  the Derivative "\
               "Works; and</p> <p>(d) If the Work includes a 'NOTICE' text file as part of its  distribution, "\
               "then any Derivative Works that You distribute must  include a readable copy of the attribution "\
               "notices contained  within such NOTICE file, excluding those notices that do not  pertain to any part "\
               "of the Derivative Works, in at least one  of the following places: within a NOTICE text file "\
               "distributed  as part of the Derivative Works; within the Source form or  documentation, if provided "\
               "along with the Derivative Works; or,  within a display generated by the Derivative Works, "\
               "if and  wherever such third-party notices normally appear. The contents  of the NOTICE file are for "\
               "informational purposes only and  do not modify the License. You may add Your own attribution  notices "\
               "within Derivative Works that You distribute, alongside  or as an addendum to the NOTICE text from the "\
               "Work, provided  that such additional attribution notices cannot be construed  as modifying the "\
               "License.</p> <p>You may add Your own copyright statement to Your modifications and may provide "\
               "additional or different license terms and conditions for use, reproduction, or distribution of Your "\
               "modifications, or for any such Derivative Works as a whole, provided Your use, reproduction, "\
               "and distribution of the Work otherwise complies with the conditions stated in this License.</p> <p>5. "\
               "Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally "\
               "submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of "\
               "this License, without any additional terms or conditions. Notwithstanding the above, nothing herein "\
               "shall supersede or modify the terms of any separate license agreement you may have executed with "\
               "Licensor regarding such Contributions.</p> <p>6. Trademarks. This License does not grant permission "\
               "to use the trade names, trademarks, service marks, or product names of the Licensor, "\
               "except as required for reasonable and customary use in describing the origin of the Work and "\
               "reproducing the content of the NOTICE file.</p> <p>7. Disclaimer of Warranty. Unless required by "\
               "applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its "\
               "Contributions) on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or "\
               "implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, "\
               "MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the "\
               "appropriateness of using or redistributing the Work and assume any risks associated with Your "\
               "exercise of permissions under this License.</p> <p>8. Limitation of Liability. In no event and under "\
               "no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by "\
               "applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, "\
               "shall any Contributor be liable to You for damages, including any direct, indirect, special, "\
               "incidental, or consequential damages of any character arising as a result of this License or out of "\
               "the use or inability to use the Work (including but not limited to damages for loss of goodwill, "\
               "work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), "\
               "even if such Contributor has been advised of the possibility of such damages.</p> <p>9. Accepting "\
               "Warranty or Additional Liability. While redistributing the Work or Derivative Works thereof, "\
               "You may choose to offer, and charge a fee for, acceptance of support, warranty, indemnity, "\
               "or other liability obligations and/or rights consistent with this License. However, in accepting such "\
               "obligations, You may act only on Your own behalf and on Your sole responsibility, not on behalf of "\
               "any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless "\
               "for any liability incurred by, or claims asserted against, such Contributor by reason of your "\
               "accepting any such warranty or additional liability.</p> <p>END OF TERMS AND CONDITIONS</p> "\
               "<p>APPENDIX: How to apply the Apache License to your work.</p> <p>To apply the Apache License to your "\
               "work, attach the following boilerplate notice, with the fields enclosed by brackets '[]' replaced "\
               "with your own identifying information. (Don't include the brackets!)  The text should be enclosed in "\
               "the appropriate comment syntax for the file format. We also recommend that a file or class name and "\
               "description of purpose be included on the same 'printed page' as the copyright notice for easier "\
               "identification within third-party archives.</p> <p>Copyright [yyyy] [name of copyright owner]</p> "\
               "<p>Licensed under the Apache License, Version 2.0 (the 'License'); you may not use this file except "\
               "in compliance with the License. You may obtain a copy of the License at</p>  "\
               "<p>http://www.apache.org/licenses/LICENSE-2.0</p> <p>Unless required by applicable law or agreed to "\
               "in writing, software distributed under the License is distributed on an 'AS IS' BASIS, "\
               "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the "\
               "specific language governing permissions and limitations under the License.</p> "\

        m += _('<h3>Werkzeug and babel are licensed under the 3-Clause BSD license: </h3>')
        m += "<p>Babel</p> <p>Copyright (c) 2013-2024 by the Babel Team, "\
               "see https://github.com/python-babel/babel/blob/master/AUTHORS for more information.</p> "\
               "<p>Werkzeug:</p> <p>Copyright 2007 Pallets</p> <h3 style='text-align: center;'>The 3-Clause BSD "\
               "License</h3> <p>Redistribution and use in source and binary forms, with or without modification, "\
               "are permitted provided that the following conditions are met:</p> <p> 1. Redistributions of source "\
               "code must retain the above copyright     notice, this list of conditions and the following "\
               "disclaimer.</p> <p> 2. Redistributions in binary form must reproduce the above copyright     notice, "\
               "this list of conditions and the following disclaimer in     the documentation and/or other materials "\
               "provided with the     distribution.</p> <p> 3. Neither the name of the copyright holder nor the names "\
               "of its     contributors may be used to endorse or promote products derived     from this software "\
               "without specific prior written permission.</p> <p>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "\
               "AND CONTRIBUTORS 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, "\
               "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO "\
               "EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, "\
               "SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF "\
               "SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED "\
               "AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE "\
               "OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY "\
               "OF SUCH DAMAGE.</p>"

        m += _('<h3>Pylzma is licensed under the LGPL v2.1 license: </h3>')
        m += "<h3 style='text-align: center;'>GNU LESSER GENERAL PUBLIC LICENSE</h3> <p style='text-align: " \
             "center;'>Version 2.1, February 1999</p> <p>Copyright (C) 1991, 1999 Free Software Foundation, " \
             "Inc.  59 Temple Place, Suite 330, Boston, MA02111-1307USA  Everyone is permitted to copy and distribute " \
             "verbatim copies  of this license document, but changing it is not allowed.</p> <p>[This is the first " \
             "released version of the Lesser GPL.It also counts  as the successor of the GNU Library Public License, " \
             "version 2, hence  the version number 2.1.]</p> <p style='text-align:Preamble</p> <p>The licenses for " \
             "most software are designed to take away your freedom to share and change it.By contrast, " \
             "the GNU General Public Licenses are intended to guarantee your freedom to share and change free " \
             "software--to make sure the software is free for all its users.</p> <p>This license, the Lesser General " \
             "Public License, applies to some specially designated software packages--typically libraries--of the " \
             "Free Software Foundation and other authors who decide to use it.You can use it too, but we suggest you " \
             "first think carefully about whether this license or the ordinary General Public License is the better " \
             "strategy to use in any particular case, based on the explanations below.</p> <p>When we speak of free " \
             "software, we are referring to freedom of use, not price.Our General Public Licenses are designed to " \
             "make sure that you have the freedom to distribute copies of free software (and charge for this service " \
             "if you wish); that you receive source code or can get it if you want it; that you can change the " \
             "software and use pieces of it in new free programs; and that you are informed that you can do these " \
             "things.</p> <p>To protect your rights, we need to make restrictions that forbid distributors to deny " \
             "you these rights or to ask you to surrender these rights.These restrictions translate to certain " \
             "responsibilities for you if you distribute copies of the library or if you modify it.</p> <p>For " \
             "example, if you distribute copies of the library, whether gratis or for a fee, you must give the " \
             "recipients all the rights that we gave you.You must make sure that they, too, receive or can get the " \
             "source code.If you link other code with the library, you must provide complete object files to the " \
             "recipients, so that they can relink them with the library after making changes to the library and " \
             "recompiling it.And you must show them these terms so they know their rights.</p> <p>We protect your " \
             "rights with a two-step method: (1) we copyright the library, and (2) we offer you this license, " \
             "which gives you legal permission to copy, distribute and/or modify the library.</p> <p>To protect each " \
             "distributor, we want to make it very clear that there is no warranty for the free library.Also, " \
             "if the library is modified by someone else and passed on, the recipients should know that what they " \
             "have is not the original version, so that the original author's reputation will not be affected by " \
             "problems that might be introduced by others.</p> <p>Finally, software patents pose a constant threat to " \
             "the existence of any free program.We wish to make sure that a company cannot effectively restrict the " \
             "users of a free program by obtaining a restrictive license from a patent holder.Therefore, " \
             "we insist that any patent license obtained for a version of the library must be consistent with the " \
             "full freedom of use specified in this license.</p> <p>Most GNU software, including some libraries, " \
             "is covered by the ordinary GNU General Public License.This license, the GNU Lesser General Public " \
             "License, applies to certain designated libraries, and is quite different from the ordinary General " \
             "Public License.We use this license for certain libraries in order to permit linking those libraries " \
             "into non-free programs.</p> <p>When a program is linked with a library, whether statically or using a " \
             "shared library, the combination of the two is legally speaking a combined work, a derivative of the " \
             "original library.The ordinary General Public License therefore permits such linking only if the entire " \
             "combination fits its criteria of freedom.The Lesser General Public License permits more lax criteria " \
             "for linking other code with the library.</p> <p>We call this license the 'Lesser' General Public " \
             "License because it does Less to protect the user's freedom than the ordinary General Public License.It " \
             "also provides other free software developers Less of an advantage over competing non-free " \
             "programs.These disadvantages are the reason we use the ordinary General Public License for many " \
             "libraries.However, the Lesser license provides advantages in certain special circumstances.</p> <p>For " \
             "example, on rare occasions, there may be a special need to encourage the widest possible use of a " \
             "certain library, so that it becomes a de-facto standard.To achieve this, non-free programs must be " \
             "allowed to use the library.A more frequent case is that a free library does the same job as widely used " \
             "non-free libraries.In this case, there is little to gain by limiting the free library to free software " \
             "only, so we use the Lesser General Public License.</p> <p>In other cases, permission to use a " \
             "particular library in non-free programs enables a greater number of people to use a large body of free " \
             "software.For example, permission to use the GNU C Library in non-free programs enables many more people " \
             "to use the whole GNU operating system, as well as its variant, the GNU/Linux operating system.</p> " \
             "<p>Although the Lesser General Public License is Less protective of the users' freedom, it does ensure " \
             "that the user of a program that is linked with the Library has the freedom and the wherewithal to run " \
             "that program using a modified version of the Library.</p> <p>The precise terms and conditions for " \
             "copying, distribution and modification follow.Pay close attention to the difference between a 'work " \
             "based on the library' and a 'work that uses the library'.The former contains code derived from the " \
             "library, whereas the latter must be combined with the library in order to run.</p> <p " \
             "style='text-align: center;'>GNU LESSER GENERAL PUBLIC LICENSE <p> TERMS AND CONDITIONS FOR COPYING, " \
             "DISTRIBUTION AND MODIFICATION</p> <p>0. This License Agreement applies to any software library or other " \
             "program which contains a notice placed by the copyright holder or other authorized party saying it may " \
             "be distributed under the terms of this Lesser General Public License (also called 'this License'). Each " \
             "licensee is addressed as 'you'.</p> <p>A 'library' means a collection of software functions and/or data " \
             "prepared so as to be conveniently linked with application programs (which use some of those functions " \
             "and data) to form executables.</p> <p>The 'Library', below, refers to any such software library or work " \
             "which has been distributed under these terms.A 'work based on the Library' means either the Library or " \
             "any derivative work under copyright law: that is to say, a work containing the Library or a portion of " \
             "it, either verbatim or with modifications and/or translated straightforwardly into another language.(" \
             "Hereinafter, translation is included without limitation in the term 'modification'.)</p> <p>'Source " \
             "code' for a work means the preferred form of the work for making modifications to it.For a library, " \
             "complete source code means all the source code for all modules it contains, plus any associated " \
             "interface definition files, plus the scripts used to control compilation and installation of the " \
             "library.</p> <p>Activities other than copying, distribution and modification are not covered by this " \
             "License; they are outside its scope.The act of running a program using the Library is not restricted, " \
             "and output from such a program is covered only if its contents constitute a work based on the Library (" \
             "independent of the use of the Library in a tool for writing it).Whether that is true depends on what " \
             "the Library does and what the program that uses the Library does.</p> <p>1. You may copy and distribute " \
             "verbatim copies of the Library's complete source code as you receive it, in any medium, provided that " \
             "you conspicuously and appropriately publish on each copy an appropriate copyright notice and disclaimer " \
             "of warranty; keep intact all the notices that refer to this License and to the absence of any warranty; " \
             "and distribute a copy of this License along with the Library.</p> <p>You may charge a fee for the " \
             "physical act of transferring a copy, and you may at your option offer warranty protection in exchange " \
             "for a fee.</p> <p>2. You may modify your copy or copies of the Library or any portion of it, " \
             "thus forming a work based on the Library, and copy and distribute such modifications or work under the " \
             "terms of Section 1 above, provided that you also meet all of these conditions:</p> <p " \
             "style='text-align: center;'>a) The modified work must itself be a software library.</p> <p " \
             "style='text-align: center;'>b) You must cause the files modified to carry prominent notices stating " \
             "that you changed the files and the date of any change.</p> <p style='text-align: center;'>c) You must " \
             "cause the whole of the work to be licensed at no charge to all third parties under the terms of this " \
             "License.</p> <p style='text-align: center;'>d) If a facility in the modified Library refers to a " \
             "function or a table of data to be supplied by an application program that uses the facility, " \
             "other than as an argument passed when the facility is invoked, then you must make a good faith effort " \
             "to ensure that, in the event an application does not supply such function or table, the facility still " \
             "operates, and performs whatever part of its purpose remains meaningful.</p> <p style='text-align: " \
             "center;'>(For example, a function in a library to compute square roots has a purpose that is entirely " \
             "well-defined independent of the application.Therefore, Subsection 2d requires that any " \
             "application-supplied function or table used by this function must be optional: if the application does " \
             "not supply it, the square root function must still compute square roots.)</p> <p>These requirements " \
             "apply to the modified work as a whole.If identifiable sections of that work are not derived from the " \
             "Library, and can be reasonably considered independent and separate works in themselves, " \
             "then this License, and its terms, do not apply to those sections when you distribute them as separate " \
             "works.But when you distribute the same sections as part of a whole which is a work based on the " \
             "Library, the distribution of the whole must be on the terms of this License, whose permissions for " \
             "other licensees extend to the entire whole, and thus to each and every part regardless of who wrote " \
             "it.</p> <p>Thus, it is not the intent of this section to claim rights or contest your rights to work " \
             "written entirely by you; rather, the intent is to exercise the right to control the distribution of " \
             "derivative or collective works based on the Library.</p> <p>In addition, mere aggregation of another " \
             "work not based on the Library with the Library (or with a work based on the Library) on a volume of a " \
             "storage or distribution medium does not bring the other work under the scope of this License.</p> <p>3. " \
             "You may opt to apply the terms of the ordinary GNU General Public License instead of this License to a " \
             "given copy of the Library.To do this, you must alter all the notices that refer to this License, " \
             "so that they refer to the ordinary GNU General Public License, version 2, instead of to this License.(" \
             "If a newer version than version 2 of the ordinary GNU General Public License has appeared, then you can " \
             "specify that version instead if you wish.)Do not make any other change in these notices.</p> <p>Once " \
             "this change is made in a given copy, it is irreversible for that copy, so the ordinary GNU General " \
             "Public License applies to all subsequent copies and derivative works made from that copy.</p> <p>This " \
             "option is useful when you wish to copy part of the code of the Library into a program that is not a " \
             "library.</p> <p>4. You may copy and distribute the Library (or a portion or derivative of it, " \
             "under Section 2) in object code or executable form under the terms of Sections 1 and 2 above provided " \
             "that you accompany it with the complete corresponding machine-readable source code, which must be " \
             "distributed under the terms of Sections 1 and 2 above on a medium customarily used for software " \
             "interchange.</p> <p>If distribution of object code is made by offering access to copy from a designated " \
             "place, then offering equivalent access to copy the source code from the same place satisfies the " \
             "requirement to distribute the source code, even though third parties are not compelled to copy the " \
             "source along with the object code.</p> <p>5. A program that contains no derivative of any portion of " \
             "the Library, but is designed to work with the Library by being compiled or linked with it, is called a " \
             "'work that uses the Library'.Such a work, in isolation, is not a derivative work of the Library, " \
             "and therefore falls outside the scope of this License.</p> <p>However, linking a 'work that uses the " \
             "Library' with the Library creates an executable that is a derivative of the Library (because it " \
             "contains portions of the Library), rather than a 'work that uses the library'.The executable is " \
             "therefore covered by this License. Section 6 states terms for distribution of such executables.</p> " \
             "<p>When a 'work that uses the Library' uses material from a header file that is part of the Library, " \
             "the object code for the work may be a derivative work of the Library even though the source code is " \
             "not. Whether this is true is especially significant if the work can be linked without the Library, " \
             "or if the work is itself a library.The threshold for this to be true is not precisely defined by " \
             "law.</p> <p>If such an object file uses only numerical parameters, data structure layouts and " \
             "accessors, and small macros and small inline functions (ten lines or less in length), then the use of " \
             "the object file is unrestricted, regardless of whether it is legally a derivative work.(Executables " \
             "containing this object code plus portions of the Library will still fall under Section 6.)</p> " \
             "<p>Otherwise, if the work is a derivative of the Library, you may distribute the object code for the " \
             "work under the terms of Section 6. Any executables containing that work also fall under Section 6, " \
             "whether or not they are linked directly with the Library itself.</p> <p>6. As an exception to the " \
             "Sections above, you may also combine or link a 'work that uses the Library' with the Library to produce " \
             "a work containing portions of the Library, and distribute that work under terms of your choice, " \
             "provided that the terms permit modification of the work for the customer's own use and reverse " \
             "engineering for debugging such modifications.</p> <p>You must give prominent notice with each copy of " \
             "the work that the Library is used in it and that the Library and its use are covered by this " \
             "License.You must supply a copy of this License.If the work during execution displays copyright notices, " \
             "you must include the copyright notice for the Library among them, as well as a reference directing the " \
             "user to the copy of this License.Also, you must do one of these things:</p> <p style='text-align: " \
             "center;'>a) Accompany the work with the complete corresponding machine-readable source code for the " \
             "Library including whatever changes were used in the work (which must be distributed under Sections 1 " \
             "and 2 above); and, if the work is an executable linked with the Library, with the complete " \
             "machine-readable 'work that uses the Library', as object code and/or source code, so that the user can " \
             "modify the Library and then relink to produce a modified executable containing the modified Library.(It " \
             "is understood that the user who changes the contents of definitions files in the Library will not " \
             "necessarily be able to recompile the application to use the modified definitions.)</p> <p " \
             "style='text-align: center;'>b) Use a suitable shared library mechanism for linking with the Library.A " \
             "suitable mechanism is one that (1) uses at run time a copy of the library already present on the user's " \
             "computer system, rather than copying library functions into the executable, and (2) will operate " \
             "properly with a modified version of the library, if the user installs one, as long as the modified " \
             "version is interface-compatible with the version that the work was made with.</p> <p style='text-align: " \
             "center;'>c) Accompany the work with a written offer, valid for at least three years, to give the same " \
             "user the materials specified in Subsection 6a, above, for a charge no more than the cost of performing " \
             "this distribution.</p> <p style='text-align: center;'>d) If distribution of the work is made by " \
             "offering access to copy from a designated place, offer equivalent access to copy the above specified " \
             "materials from the same place.</p> <p style='text-align: center;'>e) Verify that the user has already " \
             "received a copy of these materials or that you have already sent this user a copy.</p> <p>For an " \
             "executable, the required form of the 'work that uses the Library' must include any data and utility " \
             "programs needed for reproducing the executable from it.However, as a special exception, the materials " \
             "to be distributed need not include anything that is normally distributed (in either source or binary " \
             "form) with the major components (compiler, kernel, and so on) of the operating system on which the " \
             "executable runs, unless that component itself accompanies the executable.</p> <p>It may happen that " \
             "this requirement contradicts the license restrictions of other proprietary libraries that do not " \
             "normally accompany the operating system.Such a contradiction means you cannot use both them and the " \
             "Library together in an executable that you distribute.</p> <p>7. You may place library facilities that " \
             "are a work based on the Library side-by-side in a single library together with other library facilities " \
             "not covered by this License, and distribute such a combined library, provided that the separate " \
             "distribution of the work based on the Library and of the other library facilities is otherwise " \
             "permitted, and provided that you do these two things:</p> <p style='text-align: center;'>a) Accompany " \
             "the combined library with a copy of the same work based on the Library, uncombined with any other " \
             "library facilities.This must be distributed under the terms of the Sections above.</p> <p " \
             "style='text-align: center;'>b) Give prominent notice with the combined library of the fact that part of " \
             "it is a work based on the Library, and explaining where to find the accompanying uncombined form of the " \
             "same work.</p> <p>8. You may not copy, modify, sublicense, link with, or distribute the Library except " \
             "as expressly provided under this License.Any attempt otherwise to copy, modify, sublicense, link with, " \
             "or distribute the Library is void, and will automatically terminate your rights under this " \
             "License.However, parties who have received copies, or rights, from you under this License will not have " \
             "their licenses terminated so long as such parties remain in full compliance.</p> <p>9. You are not " \
             "required to accept this License, since you have not signed it.However, nothing else grants you " \
             "permission to modify or distribute the Library or its derivative works.These actions are prohibited by " \
             "law if you do not accept this License.Therefore, by modifying or distributing the Library (or any work " \
             "based on the Library), you indicate your acceptance of this License to do so, and all its terms and " \
             "conditions for copying, distributing or modifying the Library or works based on it.</p> <p>10. Each " \
             "time you redistribute the Library (or any work based on the Library), the recipient automatically " \
             "receives a license from the original licensor to copy, distribute, link with or modify the Library " \
             "subject to these terms and conditions.You may not impose any further restrictions on the recipients' " \
             "exercise of the rights granted herein. You are not responsible for enforcing compliance by third " \
             "parties with this License.</p> <p>11. If, as a consequence of a court judgment or allegation of patent " \
             "infringement or for any other reason (not limited to patent issues), conditions are imposed on you (" \
             "whether by court order, agreement or otherwise) that contradict the conditions of this License, " \
             "they do not excuse you from the conditions of this License.If you cannot distribute so as to satisfy " \
             "simultaneously your obligations under this License and any other pertinent obligations, " \
             "then as a consequence you may not distribute the Library at all.For example, if a patent license would " \
             "not permit royalty-free redistribution of the Library by all those who receive copies directly or " \
             "indirectly through you, then the only way you could satisfy both it and this License would be to " \
             "refrain entirely from distribution of the Library.</p> <p>If any portion of this section is held " \
             "invalid or unenforceable under any particular circumstance, the balance of the section is intended to " \
             "apply, and the section as a whole is intended to apply in other circumstances.</p> <p>It is not the " \
             "purpose of this section to induce you to infringe any patents or other property right claims or to " \
             "contest validity of any such claims; this section has the sole purpose of protecting the integrity of " \
             "the free software distribution system which is implemented by public license practices.Many people have " \
             "made generous contributions to the wide range of software distributed through that system in reliance " \
             "on consistent application of that system; it is up to the author/donor to decide if he or she is " \
             "willing to distribute software through any other system and a licensee cannot impose that choice.</p> " \
             "<p>This section is intended to make thoroughly clear what is believed to be a consequence of the rest " \
             "of this License.</p> <p>12. If the distribution and/or use of the Library is restricted in certain " \
             "countries either by patents or by copyrighted interfaces, the original copyright holder who places the " \
             "Library under this License may add an explicit geographical distribution limitation excluding those " \
             "countries, so that distribution is permitted only in or among countries not thus excluded.In such case, " \
             "this License incorporates the limitation as if written in the body of this License.</p> <p>13. The Free " \
             "Software Foundation may publish revised and/or new versions of the Lesser General Public License from " \
             "time to time. Such new versions will be similar in spirit to the present version, but may differ in " \
             "detail to address new problems or concerns.</p> <p>Each version is given a distinguishing version " \
             "number.If the Library specifies a version number of this License which applies to it and 'any later " \
             "version', you have the option of following the terms and conditions either of that version or of any " \
             "later version published by the Free Software Foundation.If the Library does not specify a license " \
             "version number, you may choose any version ever published by the Free Software Foundation.</p> <p>14. " \
             "If you wish to incorporate parts of the Library into other free programs whose distribution conditions " \
             "are incompatible with these, write to the author to ask for permission.For software which is " \
             "copyrighted by the Free Software Foundation, write to the Free Software Foundation; we sometimes make " \
             "exceptions for this.Our decision will be guided by the two goals of preserving the free status of all " \
             "derivatives of our free software and of promoting the sharing and reuse of software generally.</p> <p " \
             "style='text-align: center;'>NO WARRANTY</p> <p>15. BECAUSE THE LIBRARY IS LICENSED FREE OF CHARGE, " \
             "THERE IS NO WARRANTY FOR THE LIBRARY, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE " \
             "STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE LIBRARY 'AS IS' WITHOUT " \
             "WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED " \
             "WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.THE ENTIRE RISK AS TO THE QUALITY " \
             "AND PERFORMANCE OF THE LIBRARY IS WITH YOU.SHOULD THE LIBRARY PROVE DEFECTIVE, YOU ASSUME THE COST OF " \
             "ALL NECESSARY SERVICING, REPAIR OR CORRECTION.</p> <p>16. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW " \
             "OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR " \
             "REDISTRIBUTE THE LIBRARY AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, " \
             "SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE LIBRARY (" \
             "INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU " \
             "OR THIRD PARTIES OR A FAILURE OF THE LIBRARY TO OPERATE WITH ANY OTHER SOFTWARE), EVEN IF SUCH HOLDER " \
             "OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.</p> <p style='text-align: " \
             "center;'>END OF TERMS AND CONDITIONS</p> <p style='text-align: center;'>How to Apply These Terms to " \
             "Your New Libraries</p> <p>If you develop a new library, and you want it to be of the greatest possible " \
             "use to the public, we recommend making it free software that everyone can redistribute and change.You " \
             "can do so by permitting redistribution under these terms (or, alternatively, under the terms of the " \
             "ordinary General Public License).</p> <p>To apply these terms, attach the following notices to the " \
             "library.It is safest to attach them to the start of each source file to most effectively convey the " \
             "exclusion of warranty; and each file should have at least the 'copyright' line and a pointer to where " \
             "the full notice is found.</p> <p style='text-align: center;'><one line to give the library's name and a " \
             "brief idea of what it does.> Copyright (C) <year><name of author></p> <p style='text-align: " \
             "center;'>This library is free software; you can redistribute it and/or modify it under the terms of the " \
             "GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of " \
             "the License, or (at your option) any later version.</p> <p style='text-align: center;'>This library is " \
             "distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied " \
             "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the GNU Lesser General Public " \
             "License for more details.</p> <p style='text-align: center;'>You should have received a copy of the GNU " \
             "Lesser General Public License along with this library; if not, write to the Free Software Foundation, " \
             "Inc., 59 Temple Place, Suite 330, Boston, MA02111-1307USA</p> <p>Also add information on how to contact " \
             "you by electronic and paper mail.</p> <p>You should also get your employer (if you work as a " \
             "programmer) or your school, if any, to sign a 'copyright disclaimer' for the library, if necessary.Here " \
             "is a sample; alter the names:</p> <p>Yoyodyne, Inc., hereby disclaims all copyright interest in the " \
             "library `Frob' (a library for tweaking knobs) written by James Random Hacker.</p> <p><signature of Ty " \
             "Coon>, 1 April 1990 Ty Coon, President of Vice</p> <p>That's all there is to it!</p> "

        m += _('<h3>Rarfile is licensed under the ISC license: </h3>')
        m += "<h3 style='text-align: center;'>ISC License <p>Copyright (c) 2005-2024 Marko Kreen</h3>" \
             "<markokr@gmail.com></p> <p>Permission to use, copy, modify, and/or distribute this software for any " \
             "purpose with or without fee is hereby granted, provided that the above copyright notice and this " \
             "permission notice appear in all copies.</p> <p>THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR " \
             "DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF " \
             "MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, " \
             "OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, " \
             "WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION " \
             "WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.</p> "


        self.text_content.setHtml(m)
