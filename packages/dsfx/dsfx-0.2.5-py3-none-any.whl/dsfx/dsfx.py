#!/usr/bin/env python3

from __future__ import print_function
from __future__ import absolute_import

__version__ = '0.2.4'

from os import system as mkdir, getcwd as pwd, chdir, unlink, chmod, makedirs
from os.path import isdir, isfile, abspath, dirname, basename, join, exists as there, relpath
from shutil import rmtree, ignore_patterns as shutil_ignp, copytree, copyfile, copymode
from tarfile import open as topen
from platform import system as getos
from sys import stderr, argv
from optioner import options
from base64 import encode as bencode
from colorama import init as color, Fore as _
import subprocess
import stat
import curses
try:
    import lzma
except ImportError:
    pass

class _makesfx:
    def __init__(self):
        self._os = getos()
        self._exe_format_ = \
            b"""
from __future__ import print_function
from os import unlink, getcwd as pwd, chdir, chmod
from os.path import join, basename, dirname, abspath
from base64 import decodebytes as db
from sys import argv, stderr
import sys
from shutil import rmtree
from tarfile import open as topen
import argparse
import datetime
import subprocess
import stat
from colorama import init as color, Fore as _

def main():
    color()
    arguments = argparse.ArgumentParser(description='dsfx sfx')
    arguments.add_argument('--check', action='store_true', help='check sfx integrity')
    arguments.add_argument('--list', action='store_true', help='List the files inside the sfx')
    arguments.add_argument('--extract', action='store_true', help='Extract and exit')
    arguments.add_argument('args', nargs=argparse.REMAINDER, help='setup arguments')
    args = arguments.parse_args()
    
    _tempd = pwd()
    _originald = None
    
    try:
    
        # put the tar file in temp dir
        _tar = join(_tempd, _tarname)
        with open(_tar, 'wb') as f:
            f.write(db(DATA))
        
        def check_integrity(default = False):
            if default:
                if sha256_sum:
                    import hashlib
                    BLOCKSIZE = 65536
                    sha256 = hashlib.sha256()
                    with open(_tar, 'rb') as tarf:
                        buf = tarf.read(BLOCKSIZE)
                        while buf:
                            sha256.update(buf)
                            buf = tarf.read(BLOCKSIZE)
                    if sha256_sum != sha256.hexdigest():
                        raise RuntimeError('SHA256 checksum mismatch: FILE maybe corrupted or incomplete.')
                    print(' -> SHA256 checksum [_/] <-')
                else:
                    print(' -> SHA256 checksum [X] <-')
            else:
                print(' -> SHA256 checksum [X] <-')
        
        if args.check:
            check_integrity(True)
            return 0
        
        if label:
            print(label)
        
        # list tarfile:
        if args.list:
            with topen(_tar) as t:
                maxsize = 0
                n = 0
                for ti in t.getmembers():
                    if n<2:
                        n += 1
                        continue
                    size = "%d" % ti.size
                    if len(size) > maxsize:
                        maxsize = len(size)
                
                bits = ['-'] * 10
                j = len(bits) - 1
                fmt = '%%s %%%dd %%s %%s' % maxsize
                n = 0
                
                for ti in t.getmembers():
                    if n<2:
                        n+=1
                        continue
                    mt = datetime.datetime.fromtimestamp(ti.mtime)
                    mts = mt.strftime("%b %d %H:%M")
                    name = ti.name.split('infs/', 1)[-1]
                    i = 0
                    while i < len(bits) - 1:
                        bits[j-i] = 'x' if (ti.mode >> i) & 0x01 else '-'
                        i += 1
                        bits[j-i] = 'w' if (ti.mode >> i) & 0x01 else '-'
                        i += 1
                        bits[j-i] = 'r' if (ti.mode >> i) & 0x01 else '-'
                        i += 1
                    
                    if ti.isfile(): bits[0]= '-'
                    elif ti.isdir(): bits[0] = 'd'
                    elif ti.issym(): bits[0] = 'l'
                    elif ti.islnk(): bits[0] = 'h'
                    elif ti.ischr(): bits[0] = 'c'
                    elif ti.isblk(): bits[0] = 'b'
                    elif ti.isfifo(): bits[0] = 'p'
                    else: bits[0] = '-'
                    print(fmt % (''.join(bits), ti.size, mts, name))
            return 0
        
        # unpack the tarfile
        with topen(_tar) as t:
            t.extractall(_tempd)
        unlink(_tar)
        
        # pkg path
        _pkg = join(_tempd, _pkgname)
        
        if args.extract:
            print(f'Extracted package: {_pkg}')
            _tempd = None
            return 0
        
        if _setup:
            _originald = pwd()
            chdir(_pkg)
            _arch = join(_pkg, 'infs')
            if in_content:
                chdir(_arch)
            
            argv = [join(_pkg, 'infs', basename(_setup))]
            argv.extend(_setupargs)
            
            if not in_content:
                # run setup script inside the content dir,
                # even if setup is not in content dir
                chdir(_arch)
            
            if args.args:
                argv.extend(args.args)
            
            ## give permissions
            
            chmod(join(_pkg, 'infs', basename(_setup)),
             stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |  # rwx user
             stat.S_IRGRP | stat.S_IXGRP |                 # rx group
             stat.S_IROTH | stat.S_IXOTH)                  # rx other
            
            try:
                subprocess.Popen(argv).wait()
            except OSError:
                print(f'{_.RED}dsfx>{_.RESET} Cannot run {argv[0]}.')
            ### NO EXEC BEYOND THIS POINT ###
    except RuntimeError as e:
        print(e, file=stderr)
        return 1
    
    return 0
"""
        
    def _make(self, content: str, outfile: str, _setup: str, _setupargs=(), executable=True, sha256=False, compress='gz', quiet=False, label=None, extension='.dsfx'):
        """Create SFX

        Args:
            content (str): input directory
            outfile (str): output executable name
            _setup (str): setup file which will be executed from the extracted content dir
            _setupargs (tuple, optional): setup file arguments if any. Defaults to ().
            sha256 (bool, optional): Enable (True), Disable (False) SHA256. Defaults to False.
            compress (str, optional): Type of compression. Defaults to 'gz'. Possible -> ['gz', 'bz2', 'xz']
            quiet (bool, optional): Do not print any messages other than errors if True. Defaults to False.
            label (_type_, optional): Text describing the package. Defaults to None.
        
        Return:
            Path to SFX executable
        """
        self._quiet = quiet
        color()
        ## check all parameters
        # check content
        if not content:
            raise RuntimeError('content is not given')
        # check if content is a dir
        if not isdir(content):
            raise RuntimeError(f'content not found: {content}')
        # check outfile
        if not outfile:
            raise RuntimeError('outfile is not given')
        # check setup
        if not _setup:
            raise RuntimeError('setup is not given')
        
        # set _setup is not in content dir
        in_content = False
        # get content path
        content = abspath(content)
        
        # if _setup has no dir in path, then it is in content dir
        if not dirname(_setup):
            _setup = join(content, _setup)
            in_content = True
        else:
            _setup = abspath(_setup)
            # if the directory where _setup is present is the content dir, then _setup is in content directory
            if dirname(_setup) == content:
                in_content = True
        
        # check if _setup is a file or not
        if not isfile(_setup):
            raise RuntimeError(f'setup is not valid: {_setup}')
        
        # remove .py extension from outfile name if it is there, any other can be allowed
        if outfile.endswith('.py'):
            outfile = outfile.rsplit('.py', 1)[0]
        
        # create a temp dir to work on
        _tempd =  pwd() # mkt('_makesfx')
        # set _pkg dir
        _pkg = join(_tempd, basename(outfile))
        
        # copy files

        _copy_package_files(_pkg, content, _setup, in_content, quiet)
        _tar, sha256_sum = _archive_package(_pkg, compress, sha256, quiet)
        self._midfile = self._pkg_to_exe(_tar, outfile, _setup, _setupargs, in_content, sha256_sum, label, quiet)
        
        # set exe name
        _exe_name = basename(self._midfile).split('.')[0] ## remove py extension
        
        # directory at this point is the directory where the script has started
        
        # change to current directory ==> dont
        # chdir(dirname(abspath(__file__)))
        
        _current = pwd()
        
        if not quiet:
            print(f'\n{_.RED}Running Pyinstaller{_.RESET}\n')
        
        # use pyinstaller to make executable of the final file
        if executable:
            if not quiet:
                subprocess.Popen(['pyinstaller', '--onefile', f'{self._midfile}']).wait()
            else:
                subprocess.Popen(['pyinstaller', '--onefile', f'{self._midfile}'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
            
            if not quiet:
                print(f'\n{_.BLUE}Deleting{_.RESET} build')
            # delete build
            rmtree(join(_current, 'build'))
            if not quiet:
                print(f'{_.BLUE}Copying{_.RESET} dist/{_exe_name}')
            # copy from the dist folder
            copyfile(join(_current, 'dist', _exe_name), join(_current, _exe_name+extension))
            if not quiet:
                print(f'{_.BLUE}Deleting{_.RESET} dist')
            # delete dist
            rmtree(join(_current, 'dist'))
            if not quiet:
                print(f'{_.BLUE}Deleting{_.RESET} {_exe_name}.spec')
            # remove .spec file
            unlink(join(_current, _exe_name + '.spec'))
            if not quiet:
                print(f'{_.BLUE}Deleting{_.RESET} {self._midfile}')
            
            unlink(self._midfile)
            
            _exe = join(_current, _exe_name+extension)
            
            # give permissions
            chmod(_exe,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |  # rwx user
                stat.S_IRGRP | stat.S_IXGRP |                 # rx group
                stat.S_IROTH | stat.S_IXOTH)                  # rx other
            
            # rename the file to the extension provided
            # rename(_exe, _exe+extension)
            
            # delete the mid dir
            rmtree(join(_current, _exe_name))
            
            if not quiet:
                print(f'{_.GREEN}Build Complete{_.RESET} {_exe}')
            return _exe
        else:
            # remove mid dir
            rmtree(join(_current, _exe_name))
            # give permissions
            chmod(self._midfile,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |  # rwx user
                stat.S_IRGRP | stat.S_IXGRP |                 # rx group
                stat.S_IROTH | stat.S_IXOTH)                  # rx other
            
            return self._midfile
    
    def _pkg_to_exe(self, _tar: str, outfile: str, _setup: str, _setupargs: tuple, in_content: bool, sha256_sum: str, label: str, quiet:bool = False):
        _tarname = basename(_tar)
        _exe_mid = abspath(outfile) + '.py'
        
        if there(_exe_mid):
            if not quiet:
                print(f'{_.BLUE}Removing existing midfile{_.RESET} {relpath(_exe_mid)}', file=stderr)
            unlink(_exe_mid)
        
        if not quiet:
            print(f'{_.BLUE}Writing{_.RESET} {relpath(_exe_mid)}')
        with open(_exe_mid, 'wb') as exemid:
            # write interpreter invocation line.
            exemid.write(b'#!/usr/bin/env python3\n')
            # write comment
            exemid.write(b'#\n# dsfx sfx. \n#\n')
            
            # write logic
            exemid.write(self._exe_format_)
            
            # write data about install module, tar file and package into script
            exemid.write(f"\n_tarname = \'{_tarname}\'\n".encode())
            if sha256_sum:
                exemid.write(f"sha256_sum = \'{sha256_sum}\'\n".encode())
            else:
                exemid.write(b"sha256_sum = None\n")
            
            if label:
                exemid.write(f"label = \'{label}\'\n".encode())
            else:
                exemid.write(b"label = None\n")
            
            exemid.write(f"_pkgname = \'{_tarname.rsplit('.tar', 1)[0]}\'\n".encode())
            
            if _setup:
                _setupname = basename(_setup)
                exemid.write(f"_setup = \'{_setup}\'\n".encode())
                if in_content:
                    exemid.write(b"in_content = True\n")
                else:
                    exemid.write(b"in_content = False\n")
                
                exemid.write(f"_setupargs = {repr(tuple(_setupargs))}\n".encode())
            else:
                exemid.write(b"_setup = None\n")
            
            ## write base64 encoded tar file into executable script.
            exemid.write(b'\nDATA = b"""\n')
            with open(_tar, 'rb') as pkgf:
                bencode(pkgf, exemid)
            exemid.write(b'"""\n\n')
            
            exemid.write(b'if __name__ == "__main__":\n')
            exemid.write(b'    sys.exit(main())\n')
    
        # remove the tar file that was written into the executable script.
        unlink(_tar)
        
        # set the permissions on the executable installer script that was created ====> no need
        return _exe_mid
        
        
def _copy_package_files(_pkg: str, _install_src: str, _setup: str, in_content: bool, quiet:bool = False):
    makedirs(_pkg,)
    # set install destination
    install_dst = join(_pkg, 'infs')
    
    if not quiet:
        print(f'{_.BLUE}Packaging{_.RESET} from {_install_src}')
    # copy the files
    ignores = shutil_ignp('*~', '.#*', '.ssh')
    copytree(_install_src, install_dst, ignore=ignores)
    
    # copy .ssh/authorized_keys if one exists in source.
    src_dot_ssh = join(_install_src, '.ssh')
    src_auth_keys = join(src_dot_ssh, 'authorized_keys')
    if isfile(src_auth_keys):
        if not quiet:
            print(f'{_.BLUE}Packaging only authorized_keys file{_.RESET} from {src_dot_ssh}')
        dst_dot_ssh = join(install_dst, '.ssh')
        mkdir(dst_dot_ssh, 0o700)
        dst_dot_ssh = join(dst_dot_ssh, 'authorized_keys')
        copyfile(src_auth_keys, dst_dot_ssh)
        copymode(src_auth_keys, dst_dot_ssh)
    
    # check setup
    if _setup:
        if in_content:
            if not quiet:
                print(f'{_.GREEN}_setup already included.{_.RESET}')
        else:
            if not quiet:
                print(f'{_.BLUE}Packaging{_.RESET} {_setup}')
            # copy the script
            _setupname = basename(_setup)
            copyfile(_setup, join(_pkg, 'infs', _setupname))
                
def _archive_package(_pkg: str, compress: str, sha256: bool, quiet:bool = False):
    _tar = _pkg + '.tar' + compress
    
    def reset(tarinfo):
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        return tarinfo
    
    _pkg_parent = dirname(_pkg)
    _originald = pwd()
    chdir(_pkg_parent)
    
    if not quiet:
        print(f'{_.BLUE}Creating tar file{_.RESET} {basename(_tar)}')
    with topen(_tar, 'w:'+compress) as tar:
        # package path must only contain the directory to tar.
        tar.add(basename(_pkg), filter=reset)
    
    chdir(_originald)
    
    sha256_sum = None
    if sha256:
        # import hashlib here and not on the top of the code
        # incase user cannot use checksum and needs to omit
        import hashlib
        BLOCKSIZE = 65536
        sha256_ = hashlib.sha256()
        with open(_tar, 'rb') as tarf:
            buf = tarf.read(BLOCKSIZE)
            while buf:
                sha256_.update(buf)
                buf = tarf.read(BLOCKSIZE)
        sha256_sum = sha256_.hexdigest()
        if not quiet:
            print(f'{_.BLUE}SHA256{_.RESET} {basename(_tar)} = {sha256_sum}')
    else:
        if not quiet:
            print(f'{_.RED}Skipped SHA256{_.RESET}')
    
    return _tar, sha256_sum

def version():
    print(f'{_.BLUE}dsfx{_.RESET} - {_.BLACK}create install packages{_.RESET}')
    print(f'{_.BLACK}version{_.RESET} {_.RED}v{__version__}{_.RESET}')
    print(f'author: {_.GREEN}d33pster{_.RESET}, github: {_.LIGHTBLUE_EX}https://github.com/d33pster{_.RESET}')
    print(f'{_.LIGHTMAGENTA_EX}based on pymakeself{_.RESET}')
    exit(0)

def helper():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    
    try:
        stdscr.addstr(f'dsfx v{__version__}\n\n')
        stdscr.scrollok(1)
        stdscr.addstr(f'HELP TEXT\n\n')
        stdscr.scrollok(1)
        stdscr.addstr('format: $ dsfx [args] -s <setup> [setup-args]\n\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -h or --help             -      show this help text. press q to exit.\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -v or --version          -      show version info and exit.\n    |\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    COMPULSORY ARGUMENTS\n    |\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -i or --infile           -      input file path or relative path.\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -o or --outfile          -      output file name.\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -s or --setup            -      setup script (executable). NOTE: can be a python script with a shebang\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    NORMAL ARGUMENTS\n    |\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -c or --compress-method  -      set compression method. Possible values: [\'gz\', \'bz2\', \'xz\']\n')
        # stdscr.scrollok(1)
        stdscr.addstr('    |    -l or --label            -      set label text. Default: None\n')
        stdscr.scrollok(1)
        stdscr.addstr('    |    -e or --extension        -      specify output file extension. Default: \'*.dsfx\'\n')
        # stdscr.scrollok(1)
        stdscr.addstr('    |    -cs or --checksum        -      set checksum true or false. if not specified, it is off. (switch)\n')
        # stdscr.scrollok(1)
        stdscr.addstr('    |    -q or --quiet            -      set quiet mode on. Default: off. (switch)\n')
        # stdscr.scrollok(1)
        stdscr.addstr('    |    -ne or --no-executable   -      Output .py file. Default: make executable file. (switch)')
        stdscr.addstr('\n\nEND')
        # stdscr.scrollok(1)
        while True:
            key = stdscr.getch()
            if key == ord('q'):
                break
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
    exit(0)

def cli():
    color()
    # define shortargs
    shortargs = ['i', 'o', 's', 'c', 'l', 'e', 'cs', 'q', 'v', 'h', 'ne']
    # define longargs
    longargs = ['infile', 'outfile', 'setup', 'compress-method', 'label', 'extension', 'checksum', 'quiet', 'version', 'help', 'no-executable']
    # get option control
    optionCTRL = options(shortargs, longargs, argv[1:], ['i','o','s'], ['infile', 'outfile', 'setup'], ['-h', '--help', '-v', '--version'])
    # get argument values
    actualargs, argcheck, argerror, falseargs = optionCTRL._argparse()
    
    # define checks and defaults
    extension = '.dsfx'
    label = ''
    compress_method = 'gz'
    checksum = False
    quiet = False
    executable = True
    
    # if errors:
    if not argcheck:
        print(f'{_.RED}dsfx>{_.RESET} {argerror}')
        exit(1)
    else:
        # if version:
        if '-v' in actualargs or '--version' in actualargs:
            version()
        # help text
        if '-h' in actualargs or '--help' in actualargs:
            helper()
        # get all switches
        if '-ne' in actualargs or '--no-executable' in actualargs:
            executable = False
        else:
            pass
        
        if '-e' in actualargs:
            extension = optionCTRL._what_is_('e')
        elif '--extension' in actualargs:
            extension = optionCTRL._what_is_('extension')
        else:
            pass
        
        if '-l' in actualargs:
            label = optionCTRL._what_is_('l')
        elif '--label' in actualargs:
            label = optionCTRL._what_is_('label')
        else:
            pass
        
        if '-c' in actualargs:
            compress_method = optionCTRL._what_is_('c')
        elif '--compress-method' in actualargs:
            compress_method = optionCTRL._what_is_('compress-method')
        else:
            pass
        
        if '-cs' in actualargs:
            checksum = True
        elif '--checksum' in actualargs:
            checksum = True
        else:
            pass
        
        if '-q' in actualargs:
            quiet = True
        elif '--quiet' in actualargs:
            quiet = True
        else:
            pass
        
        ## get infile, outfile, setup and setupargs
        try:
            if '-i' in actualargs:
                infile = optionCTRL._what_is_('i')
            elif '--infile' in actualargs:
                infile = optionCTRL._what_is_('infile')
            else:
                # this will never run as this is a compulsory argument
                pass
            
            if '-o' in actualargs:
                outfile = optionCTRL._what_is_('o')
            elif '--outfile' in actualargs:
                outfile = optionCTRL._what_is_('outfile')
            else:
                # this will never run as this is a compulsory argument
                pass
            
            if '-s' in actualargs:
                setup = optionCTRL._what_is_('s')
            elif '--setup' in actualargs:
                setup = optionCTRL._what_is_('setup')
            else:
                # this will never run as this is a compulsory argument
                pass
        except RuntimeError as e:
            print(f'{_.RED}dsfx>{_.RESET} {e}')
            exit(1)
        
        if abspath(infile) == abspath(outfile):
            print(f'{_.RED}dsfx>{_.RESET} infile and outfile must have different names.')
            exit(1)
        
        # find index of setup in optionCTRL._args
        index = optionCTRL._args.index(setup)
        # increment it 
        index += 1
        # check if setup args are provided
        setupargs = ()
        if len(optionCTRL._args[index:])>0:
            setupargs = tuple(optionCTRL._args[index:])
        
    # get class object
    sfxCTRL = _makesfx()
    # call class method
    sfxCTRL._make(infile, outfile, setup, setupargs, executable, checksum, compress_method, quiet, label, extension)

if __name__=="__main__":
    cli()