#!/usr/bin/env python
u"""
aviso_fes_tides.py
Written by Tyler Sutterley (04/2023)
Downloads the FES (Finite Element Solution) global tide model from AVISO
Decompresses the model tar files into the constituent files and auxiliary files
    https://www.aviso.altimetry.fr/data/products/auxiliary-products/
        global-tide-fes.html
    https://www.aviso.altimetry.fr/en/data/data-access.html

CALLING SEQUENCE:
    python aviso_fes_tides.py --user <username> --tide FES2014
    where <username> is your AVISO data dissemination server username

COMMAND LINE OPTIONS:
    --help: list the command line options
    --directory X: working data directory
    -U X, --user: username for AVISO FTP servers (email)
    -P X, --password: password for AVISO FTP servers
    -N X, --netrc X: path to .netrc file for authentication
    --tide X: FES tide model to download
        FES1999
        FES2004
        FES2012
        FES2014
    --load: download load tide model outputs (fes2014)
    --currents: download tide model current outputs (fes2012 and fes2014)
    -G, --gzip: compress output ascii and netCDF4 tide files
    -t X, --timeout X: timeout in seconds for blocking operations
    --log: output log of files downloaded
    -M X, --mode X: Local permissions mode of the files downloaded

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        https://python-future.org/

PROGRAM DEPENDENCIES:
    utilities.py: download and management utilities for syncing files

UPDATE HISTORY:
    Updated 05/2023: added option to change connection timeout
    Updated 04/2023: using pathlib to define and expand paths
        added option to include AVISO FTP password as argument
    Updated 11/2022: added encoding for writing ascii files
        use f-strings for formatting verbose or ascii output
    Updated 04/2022: use argparse descriptions within documentation
    Updated 10/2021: using python logging for handling verbose output
    Updated 07/2021: can use prefix files to define command line arguments
    Updated 05/2021: use try/except for retrieving netrc credentials
    Updated 04/2021: set a default netrc file and check access
    Updated 10/2020: using argparse to set command line parameters
    Updated 07/2020: add gzip option to compress output ascii and netCDF4 files
    Updated 06/2020: added netrc option for alternative authentication
    Updated 05/2019: new authenticated ftp host (changed 2018-05-31)
    Written 09/2017
"""
from __future__ import print_function, annotations

import sys
import os
import io
import gzip
import netrc
import shutil
import logging
import tarfile
import getpass
import pathlib
import argparse
import builtins
import posixpath
import calendar, time
import ftplib
import pyTMD.utilities

# PURPOSE: download local AVISO FES files with ftp server
def aviso_fes_tides(MODEL: str,
    DIRECTORY: str | pathlib.Path | None = None,
    USER: str = '',
    PASSWORD: str = '',
    LOAD: bool = False,
    CURRENTS: bool = False,
    GZIP: bool = False,
    TIMEOUT: int | None = None,
    LOG: bool = False,
    MODE: oct = 0o775):

    # connect and login to AVISO ftp server
    f = ftplib.FTP('ftp-access.aviso.altimetry.fr', timeout=TIMEOUT)
    f.login(USER, PASSWORD)
    # check if local directory exists and recursively create if not
    localpath = pathlib.Path(DIRECTORY).joinpath(MODEL.lower()).expanduser()
    localpath.mkdir(MODE, parents=True, exist_ok=True)

    # create log file with list of downloaded files (or print to terminal)
    if LOG:
        # format: AVISO_FES_tides_2002-04-01.log
        today = time.strftime('%Y-%m-%d',time.localtime())
        LOGFILE = localpath.joinpath(f'AVISO_FES_tides_{today}.log')
        fid = LOGFILE.open(mode='w', encoding='utf8')
        logger = pyTMD.utilities.build_logger(__name__,stream=fid,
            level=logging.INFO)
        logger.info(f'AVISO FES Sync Log ({today})')
        logger.info(f'\tMODEL: {MODEL}')
    else:
        # standard output (terminal output)
        logger = pyTMD.utilities.build_logger(__name__,level=logging.INFO)

    # path to remote directory for FES
    FES = {}
    # mode for reading tar files
    TAR = {}
    # flatten file structure
    FLATTEN = {}

    # 1999 model
    FES['FES1999']=[]
    FES['FES1999'].append(['fes1999_fes2004','readme_fes1999.html'])
    FES['FES1999'].append(['fes1999_fes2004','fes1999.tar.gz'])
    TAR['FES1999'] = [None,'r:gz']
    FLATTEN['FES1999'] = [None,True]
    # 2004 model
    FES['FES2004']=[]
    FES['FES2004'].append(['fes1999_fes2004','readme_fes2004.html'])
    FES['FES2004'].append(['fes1999_fes2004','fes2004.tar.gz'])
    TAR['FES2004'] = [None,'r:gz']
    FLATTEN['FES2004'] = [None,True]
    # 2012 model
    FES['FES2012']=[]
    FES['FES2012'].append(['fes2012_heights','readme_fes2012_heights_v1.1'])
    FES['FES2012'].append(['fes2012_heights','fes2012_heights_v1.1.tar.lzma'])
    TAR['FES2012'] = []
    TAR['FES2012'].extend([None,'r:xz'])
    FLATTEN['FES2012'] = []
    FLATTEN['FES2012'].extend([None,True])
    if CURRENTS:
        subdir = 'fes2012_currents'
        FES['FES2012'].append([subdir,'readme_fes2012_currents_v1.1'])
        FES['FES2012'].append([subdir,'fes2012_currents_v1.1_block1.tar.lzma'])
        FES['FES2012'].append([subdir,'fes2012_currents_v1.1_block2.tar.lzma'])
        FES['FES2012'].append([subdir,'fes2012_currents_v1.1_block3.tar.lzma'])
        FES['FES2012'].append([subdir,'fes2012_currents_v1.1_block4.tar.lzma'])
        TAR['FES2012'].extend([None,'r:xz','r:xz','r:xz','r:xz'])
        FLATTEN['FES2012'].extend([None,False,False,False,False])
    # 2014 model
    FES['FES2014']=[]
    FES['FES2014'].append(['fes2014_elevations_and_load',
        'readme_fes2014_elevation_and_load_v1.2.txt'])
    FES['FES2014'].append(['fes2014_elevations_and_load',
        'fes2014b_elevations','ocean_tide.tar.xz'])
    TAR['FES2014'] = []
    TAR['FES2014'].extend([None,'r'])
    FLATTEN['FES2014'] = []
    FLATTEN['FES2014'].extend([None,False])
    if LOAD:
        FES['FES2014'].append(['fes2014_elevations_and_load',
            'fes2014a_loadtide','load_tide.tar.xz'])
        TAR['FES2014'].extend(['r'])
        FLATTEN['FES2014'].extend([False])
    if CURRENTS:
        subdir = 'fes2014a_currents'
        FES['FES2014'].append([subdir,'readme_fes2014_currents_v1.2.txt'])
        FES['FES2014'].append([subdir,'eastward_velocity.tar.xz'])
        FES['FES2014'].append([subdir,'northward_velocity.tar.xz'])
        TAR['FES2014'].extend(['r'])
        FLATTEN['FES2014'].extend([False])

    # for each file for a model
    for remotepath,tarmode,flatten in zip(FES[MODEL],TAR[MODEL],FLATTEN[MODEL]):
        # download file from ftp and decompress tar files
        ftp_download_file(logger,f,remotepath,localpath,tarmode,flatten,GZIP,MODE)
    # close the ftp connection
    f.quit()
    # close log file and set permissions level to MODE
    if LOG:
        LOGFILE.chmod(mode=MODE)

# PURPOSE: pull file from a remote ftp server and decompress if tar file
def ftp_download_file(logger,ftp,remote_path,local_dir,tarmode,flatten,GZIP,MODE):
    # remote and local directory for data product
    remote_file = posixpath.join('auxiliary','tide_model',*remote_path)

    # Printing files transferred
    remote_ftp_url = posixpath.join('ftp://', ftp.host, remote_file)
    logger.info(f'{remote_ftp_url} -->')
    if tarmode:
        # copy remote file contents to bytesIO object
        fileobj = io.BytesIO()
        ftp.retrbinary(f'RETR {remote_file}', fileobj.write)
        fileobj.seek(0)
        # open the AOD1B monthly tar file
        tar = tarfile.open(name=remote_path[-1], fileobj=fileobj, mode=tarmode)
        # read tar file and extract all files
        member_files = [m for m in tar.getmembers() if tarfile.TarInfo.isfile(m)]
        for m in member_files:
            member = posixpath.basename(m.name) if flatten else m.name
            fileBasename, fileExtension = posixpath.splitext(m.name)
            # extract file contents to new file
            if fileExtension in ('.asc','.nc') and GZIP:
                local_file = local_dir.joinpath(*posixpath.split(f'{member}.gz'))
                logger.info(f'\t{str(local_file)}')
                # recursively create output directory if non-existent
                local_file.parent.mkdir(mode=MODE, parents=True, exist_ok=True)
                # extract file to compressed gzip format in local directory
                with tar.extractfile(m) as fi,gzip.open(local_file, 'wb') as fo:
                    shutil.copyfileobj(fi, fo)
            else:
                local_file = local_dir.joinpath(*posixpath.split(member))
                logger.info(f'\t{str(local_file)}')
                # recursively create output directory if non-existent
                local_file.parent.mkdir(mode=MODE, parents=True, exist_ok=True)
                # extract file to local directory
                with tar.extractfile(m) as fi,open(local_file, 'wb') as fo:
                    shutil.copyfileobj(fi, fo)
            # get last modified date of remote file within tar file
            # keep remote modification time of file and local access time
            pathlib.os.utime(local_file, (local_file.stat().st_atime, m.mtime))
            local_file.chmod(mode=MODE)
    else:
        # copy readme and uncompressed files directly
        local_file = local_dir.joinpath(local_dir,remote_path[-1])
        logger.info(f'\t{str(local_file)}\n')
        # copy remote file contents to local file
        with local_file.open('wb') as f:
            ftp.retrbinary(f'RETR {remote_file}', f.write)
        # get last modified date of remote file and convert into unix time
        mdtm = ftp.sendcmd(f'MDTM {remote_file}')
        remote_mtime = calendar.timegm(time.strptime(mdtm[4:],"%Y%m%d%H%M%S"))
        # keep remote modification time of file and local access time
        pathlib.os.utime(local_file, (local_file.stat().st_atime, remote_mtime))
        local_file.chmod(mode=MODE)

# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Downloads the FES (Finite Element Solution) global tide
            model from AVISO.  Decompresses the model tar files into the
            constituent files and auxiliary files.
            """,
        fromfile_prefix_chars="@"
    )
    parser.convert_arg_line_to_args = pyTMD.utilities.convert_arg_line_to_args
    # command line parameters
    # AVISO FTP credentials
    parser.add_argument('--user','-U',
        type=str, default=os.environ.get('AVISO_USERNAME'),
        help='Username for AVISO Login')
    parser.add_argument('--password','-W',
        type=str, default=os.environ.get('AVISO_PASSWORD'),
        help='Password for AVISO Login')
    parser.add_argument('--netrc','-N',
        type=pathlib.Path, default=pathlib.Path().home().joinpath('.netrc'),
        help='Path to .netrc file for authentication')
    # working data directory
    parser.add_argument('--directory','-D',
        type=pathlib.Path, default=pathlib.Path.cwd(),
        help='Working data directory')
    # FES tide models
    parser.add_argument('--tide','-T',
        metavar='TIDE', type=str, nargs='+',
        default=['FES2014'], choices=['FES1999','FES2004','FES2012','FES2014'],
        help='FES tide model to download')
    # download FES load tides
    parser.add_argument('--load',
        default=False, action='store_true',
        help='Download load tide model outputs')
    # download FES tidal currents
    parser.add_argument('--currents',
        default=False, action='store_true',
        help='Download tide model current outputs')
    # download FES tidal currents
    parser.add_argument('--gzip','-G',
        default=False, action='store_true',
        help='Compress output ascii and netCDF4 tide files')
    # connection timeout
    parser.add_argument('--timeout','-t',
        type=int, default=360,
        help='Timeout in seconds for blocking operations')
    # Output log file in form
    # AVISO_FES_tides_2002-04-01.log
    parser.add_argument('--log','-l',
        default=False, action='store_true',
        help='Output log file')
    # permissions mode of the local directories and files (number in octal)
    parser.add_argument('--mode','-M',
        type=lambda x: int(x,base=8), default=0o775,
        help='Permission mode of directories and files downloaded')
    # return the parser
    return parser

# This is the main part of the program that calls the individual functions
def main():
    # Read the system arguments listed after the program
    parser = arguments()
    args,_ = parser.parse_known_args()

    # AVISO FTP Server hostname
    HOST = 'ftp-access.aviso.altimetry.fr'
    # get authentication
    if not args.user and not args.netrc.exists():
        # check that AVISO credentials were entered
        args.user = builtins.input(f'Username for {HOST}: ')
        # enter password securely from command-line
        args.password = getpass.getpass(f'Password for {args.user}@{HOST}: ')
    elif args.netrc.exists():
        args.user,_,args.password = netrc.netrc(args.netrc).authenticators(HOST)
    elif args.user and not args.password:
        # enter password securely from command-line
        args.password = getpass.getpass(f'Password for {args.user}@{HOST}: ')

    # check internet connection before attempting to run program
    if pyTMD.utilities.check_ftp_connection(HOST,args.user,args.password):
        for m in args.tide:
            aviso_fes_tides(m,
                DIRECTORY=args.directory,
                USER=args.user,
                PASSWORD=args.password,
                LOAD=args.load,
                CURRENTS=args.currents,
                GZIP=args.gzip,
                TIMEOUT=args.timeout,
                LOG=args.log,
                MODE=args.mode)

# run main program
if __name__ == '__main__':
    main()
