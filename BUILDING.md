# Building guide

> This guide is **outdated**. A updated version should soon be added to replace this one.

Kitten CDDA Launcher is developed using Python. In order to run or build the launcher, you will need to download a recent version of Python and install all the requirements.

## Requirements

The full list of requirements is available in [requirements.txt](requirements.txt). Most of these requirements are Python packages that can be installed using [pip](https://en.wikipedia.org/wiki/Pip_%28package_manager%29). Unfortunately, some of these requirements need build tools which are not easy to use nor easy to install on Windows. Here are those special requirements:

* lxml
* pylzma

Compiled binaries for lxml and pylzma can be found on [Christoph Gohlke's Unofficial Windows Binaries](http://www.lfd.uci.edu/~gohlke/pythonlibs/). If you are using Python >= 3.5, scandir should already be included. If you are using Python <= 3.4, you can also find compiled binaries for scandir on that website.

## Running the launcher

Once you have Python installed and all the requirements, you can run the launcher by going into the project directory and by running `python -m cddagl`.

## Building the launcher installer for distribution

Once you have Python installed and all the requirements, you can build the launcher installer for distribution by going into the project directory and running `python setup.py create_installer`. This will use the PyInstaller package to create a frozen stand-alone executable with all the dependencies alongside. Afterwards, it will build the installer using Inno Setup. If you want the executable to support RAR archives, you will also need to have the [UnRAR command line tool](http://www.rarlab.com/rar_add.htm) in your PATH.

The resulting launcher installer should be in the `dist\innosetup` directory.

## Step by step guide to run and build the launcher executable

1. Download and install Python 3.7 from [python.org](https://www.python.org/downloads/release/python-377/). The rest of this guide will assume that you are using the 32-bit (x86) version of Python. It could also work with the 64-bit version (x86-64) but it would require some tweaks and it is out of scope for this guide.
2. Add Python directory and Scripts subdirectory in your PATH.
    * During installation, there is an optional *Add Python 3.7 to PATH*. If you selected this option, nothing else needs to be done here.
    * If you did not select that option, you will need to set your PATH variable globally or each time you want to use it. Here are the steps to set your PATH variable in a single command line window.
        * Press `⊞ Win`+`R`, type `cmd` and press `↵ Enter` to open a command line window.
        * By default, Python 3.7 is installed in `%LOCALAPPDATA%\Programs\Python\Python37-32`. To setup your PATH if you used the default path during installation, type `set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python37-32;%LOCALAPPDATA%\Programs\Python\Python37-32\Scripts` in your command line window and press `↵ Enter`.
3. Install most requirements by typing the following `pip` command in your command line window: `pip install SQLAlchemy alembic PyQt5 PyInstaller html5lib cssselect arrow rarfile Babel pypiwin32 pywinutils Markdown Werkzeug` and press `↵ Enter`.
4. Download and install the lxml and the pylzma packages from [Christoph Gohlke's Unofficial Windows Binaries](http://www.lfd.uci.edu/~gohlke/pythonlibs/). `cp37` means CPython 3.7 and `win32` means 32-bit and in Christoph Gohlke's packages naming convention. The package names you are looking for should be similar to `lxml-4.5.0-cp37-cp37m-win32.whl` and `pylzma-0.5.0-cp37-cp37m-win32.whl`. To install `.whl` packages from Christoph Gohlke's Unofficial Windows Binaries page, you can use pip. In your command line window, type: `pip install [path to .whl]` and press `↵ Enter`.
5. Download the Kitten CDDA Launcher source code. If you have git installed, you can type the following command in your command line window: `git clone https://github.com/Fris0uman/CDDA-Game-Launcher.git`. You can also download the source code from [https://github.com/Fris0uman/CDDA-Game-Launcher/archive/master.zip](https://github.com/Fris0uman/CDDA-Game-Launcher/archive/master.zip). Make sure to extract the zip file somewhere before trying to run the code.
6. In your command line window, change directory to the source code directory. Type `cd [path to source code]` and press `↵ Enter`.
7. See if you can run the launcher by typing the following command in your command line window: `python -m cddagl` and press `↵ Enter`. If you have everything installed correctly, you should see the launcher running.
8. Download and install [Inno Setup](http://www.jrsoftware.org/isinfo.php). You should use the default installation path to have `Compil32.exe` in `C:\Program Files (x86)\Inno Setup 6\`. If you do not use the default installation path, you will have to use the `--compiler=[path to Compil32.exe]` option with the `create_installer` command.
9. Download the [UnRAR command line tool](http://www.rarlab.com/rar/unrarw32.exe) and extract it to `%LOCALAPPDATA%\Programs\Python\Python37-32\Scripts`.
10. Install [the Windows 10 SDK](https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk). Make sure the Windows 10 SDK option is selected during installation if you choose the Visual Studio Installer optional components.
11. To build the launcher installer, type the following command in your command line window: `python setup.py create_installer` and press `↵ Enter`. The resulting launcher installer should be in the `dist\innosetup` subdirectory.
