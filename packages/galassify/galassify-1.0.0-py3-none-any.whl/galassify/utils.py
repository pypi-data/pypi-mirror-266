import os
import re
import sys
import glob
import argparse
from pathlib import Path
import pandas as pd
import pkg_resources
from PyConsoleMenu import SelectorMenu


import warnings
from typing import Union

### OPTION PARSER UTILS

args = None
VERSION = ''
importData = pd.DataFrame()
groups = pd.DataFrame()

def getOptions(version):
    global args
    global VERSION

    parser = argparse.ArgumentParser(prog='GALAssify', description="GALAssify: Tool to manually classify galaxies.")
    parser.add_argument('--version', action='version', version='%(prog)s ' + version,
                        help="Prints software version and exit.\n")

    parser.add_argument('--init',action='store_true',help='Generate a basic config file, and the basic folder structure.')

    parser.add_argument('--example', type=example_type, default='', help='Run a galassify (basic or fits) example.')
    
    parser.add_argument('-p', '--path', type=dir_path, default='img/',
                        help="Path to image files.\n")
    
    parser.add_argument('-c', '--config', type=dir_file, default='config',
                        help="Config json file to load.\n")
    
    #parser.add_argument('-f', '--filename', nargs='+',
    #                    required=not('-p' in sys.argv
    #                    or '--path' in sys.argv
    #                    or '--version' in sys.argv), type=dir_file,
    #                    help="Image or list to classify. Not required if path or path + group are given.\n")

    parser.add_argument('-s', '--savefile',
                        #required=not('--version' in sys.argv),
                        default='output.csv',
                        help="CSV file to load and export changes. If does not exists, a new one is created.\n")
    parser.add_argument("-l", "--list", action="store_true",
                        help="List selected files only and exit.\n")
    
    parser.add_argument('-i', '--inputfile', type=dir_file, default='files/galaxies.csv',
                        help="""Galaxy database file in *.csv format.
                        Minimum required columns: ['galaxy'].
                        Recomended columns: ['group', 'galaxy', 'ra', 'dec',  'filename' and/or 'fits']""")
    
    parser.add_argument('group', metavar='GROUP', nargs='*',
                        help="Group number. Selects images with name format: img_<group>_*.png\n")

    args = parser.parse_args()
    VERSION = version
    return args

def exist_basic_files():
    files = ['files/','img/','config']
    test_files = True
    for file in files:
        if not Path(file).exists():
            test_files = False
    if not Path('files/galaxies.csv').exists:
        test_files = False
    return test_files

def load_menu():    
    
    global select_option
    select_option = 3

    options = ["INIT (--init):\t Generate a basic config file, and the basic folder structure.", 
                "EXAMPLE (--example):\t Generate a files whit a galassify example", 
                "EXIT"]
    menu = SelectorMenu(options, title='GALAssify: A tool to manually classify galaxies.')
    ans = menu.input()
    if ans.index==0:
        select_option = 0
        #return(0)
    elif ans.index==1:
        options_2 = ["BASIC (--example basic):\t Load the images example", 
                    "FITS (--example fits):\t Load the images fits example", 
                    "BACK"]
        menu_2 = SelectorMenu(options_2, title='GALAssify Example: Generate a files whit a galassify example')
        ans_2 = menu_2.input()
        if (ans_2.index==0):
            select_option = 10
            #return(10)
        elif (ans_2.index==1):
            select_option = 11
            #return(11)
        else:
            load_menu()
    return select_option

def init_flag():
    print(f"INFO:\t Generating the necessary files...")
    try:
        os.system(f"cp '{getPackageResource('config')}' config")
        os.system("mkdir -p files img/fits")
        os.system('echo "group,galaxy,ra,dec,filename,fits" >> files/galaxies.csv')
        print(f"INFO:\t The necessary files were created. \nINFO:\t Now, complete de input files and open GALAssify with: galassify -i files/galaxies.csv -s files/output.csv -p img/ ")
    except:
        pass

def example_flag(type_example):
    print(f"INFO:\t Generating the necessary files...")
    try:
        # Copy common files
        os.system(f"cp '{getPackageResource('config')}' config")
        os.system("mkdir -p files img")

        # Copy and create example-specific files
        if type_example == 'basic':
            os.system(f"cp '{getPackageResource('files/galaxies.csv')}' files/galaxies.csv")
            content = glob.glob(f"{getPackageResource('img/')}")
            content = [f for f in os.listdir(f"{getPackageResource('img/')}") if re.match(r'.*\.jpeg', f)]
            for element in content:
                elemet_dir = getPackageResource('img/'+element)
                os.system(f"cp '{elemet_dir}' img/{element}")

        else:
            os.system(f"cp '{getPackageResource('files/galaxies_fits.csv')}' files/galaxies.csv")
            os.system("mkdir -p img/fits")
            content=glob.glob(f"{getPackageResource('img/fits/')}")
            content = [f for f in os.listdir(f"{getPackageResource('img/fits/')}") if re.match(r'.*\.fits', f)]
            for element in content:
                elemet_dir = getPackageResource('img/fits/'+element)
                os.system(f"cp '{elemet_dir}' img/fits/{element}")

        print(f"INFO:\t The necessary files were created. \nINFO:\t Now, open GALAssify with: galassify -i files/galaxies.csv -s files/output.csv -p img/ ")
        print(f"INFO:\t If needed, you can download catalogue images by executing: get_images_sdss -i files/galaxies.csv -p img/ ")
    except Exception as e:
        print(f"ERROR: Error while creating the necessary files: {e}")

def getVersion():
    global VERSION
    return VERSION

def getPackageResource(relative_path):
    """Get the absolute path to a resource file."""

    # Using pkg_resources
    module_path = pkg_resources.resource_filename(__name__, '')

    return os.path.join(module_path, relative_path)

def getFiles():
    global args
    global groups
    # files = []
    selectedGroups = []
    selectedFiles = pd.DataFrame(columns = groups.columns)

    imgpath = args.path
    
    if imgpath:
        fname = args.inputfile
        file = Path(fname)
        if file.is_file():
            groups = readInputFile(fname)
        else:
            groups = createInputFile(imgpath, fname)

        availableGroups = None
        if 'group' in groups.columns:
            availableGroups = groups.group.unique()
            print(f"INFO:\tAvailable groups: {str(availableGroups)}")

            inputGroups = args.group
            if len(inputGroups) > 0:
                for group in inputGroups:
                    if group in availableGroups:
                        selectedFiles = pd_concat(selectedFiles, groups[groups.group == group])
                        selectedGroups.append(group)
                    else:
                        print(f'WARNING:\tGroup {group} not available.')
            else:
                print(f'INFO:\tNo group selected. Using all available by default.')
                selectedFiles = groups.copy()
                selectedGroups = availableGroups
        else:
            print(f'INFO:\tNo group in input file. Using all galaxies by default.')
            selectedFiles = groups.copy()
            selectedGroups = availableGroups

        #else:
        #    formats = ['*.png']

        #for format in formats:
        #    for entry in Path(args.path).glob(format):
        #        files.append(entry)

    #elif args.filename:
    #    for entry in args.filename:
    #        files.append(Path(entry))

    #else:
    #    files = []
    return selectedFiles, selectedGroups

def example_type(type_text):
    if type_text == 'basic':
        return(type_text)
    elif type_text == 'fits':
        return(type_text)
    elif type_text == '':
        return(type_text)
    else:
        raise argparse.ArgumentTypeError(f"readable_example_type: {type_text} is not a valid example type.")

def dir_path(path):
    d = Path(path)
    if path == 'img/':
        return path
    elif not d.is_dir():
        raise argparse.ArgumentTypeError(f"readable_dir: {path} is not a valid path.")
    return path

def dir_file(file):
    d = Path(file)
    if file == 'config' or file == 'files/galaxies.csv':
        return file
    elif not d.is_file():
        raise argparse.ArgumentTypeError(f"readable_file: {file} is not a valid file.")
    return file


INPUTCOLUMNS = ['group','galaxy','ra','dec','filename']

def readInputFile(fname:str) -> pd.DataFrame:
    print(f"INFO:\tReading from '{fname}' file... ", end='', flush=True)
    df = pd.read_csv(fname,
                     converters={
                            'group': str,
                            'galaxy': str,
                            'ra': float,
                            'dec': float,
                         }
                    )
    sortby=[]
    if 'galaxy' in df.columns:
        sortby.insert(0, 'galaxy')
    if 'group' in df.columns:
        sortby.insert(0, 'group')
    df = df.sort_values(by=sortby)
    
    if 'filename' in df.columns:
        not_found = sum(df['filename']=='')
    else:
        not_found = 0
    #     imgpath = Path(args.path)
    #     df['filename'] = ''
    #     for i, row in df.iterrows():
    #         if 'group' in df.columns:
    #             imgfile = f'img_{row.group}_{row.galaxy}.*'
    #         else:
    #             imgfile = f'img_*_{row.galaxy}.*'
    #         image = glob.glob(f"{imgpath.absolute()}/{imgfile}")
    #         if len(image)>0:
    #             df.loc[i, 'filename'] = image[0]
    
    
    if not_found >0:
        print(f'\nWARNING: {not_found} images where not found. Check if the provided path is correct. Or download the images using the provided tool.')
    else:
        print('Done!')
    return df

def createInputFile(imgpath:str, fname:str) -> pd.DataFrame:
    print(f'INFO:\tCreating {fname} file... ', end='', flush=True)
    df = pd.DataFrame(columns=INPUTCOLUMNS)
    if imgpath:
        for file in Path(imgpath).glob('img_*_*.*'):
            entry = {
                        'group': int(file.stem.split('_')[1]),
                        'galaxy': int(file.stem.split('_')[2]),
                        'ra':float(0),
                        'dec':float(0),
                        'filename': str(file.name),
                    }
            df = pd_concat(df, entry)
            #groups = groups.append(entry, ignore_index=True)
    # if groups not defined
    if sum(df["groups"] == '-') == len(df):
        df.drop("groups", axis=1, inplace=True)
        INPUTCOLUMNS.remove("groups")
    # sort
    sortby=[]
    if 'galaxy' in df.columns:
        sortby.insert(0, 'galaxy')
    if 'group' in df.columns:
        sortby.insert(0, 'group')
    df = df.sort_values(by=sortby)
    
    df.to_csv(fname, columns=INPUTCOLUMNS, index=False)
    print('Done!')
    return df


### PANDAS UTILS

COLUMNS = ["filename", "group", "galaxy", "morphology", "large", "tiny", "faceon",
           "edgeon", "star", "calibration", "recentre", "duplicated",
           "member", "hiiregion", "yes", "no", "comment", "processed",
           "fullpath", "ra", "dec"]

IDS = {
    'FILE':[],
    'TB':[],
    'CB':[],
    'RB':[],
    'RBG':[]
}

def getColumns():
    return COLUMNS

def getExportableColumns():
    return COLUMNS[:-4]

def getRadioButtonGroups():
    return IDS['RBG']

def getRadioButtonsNames():
    return IDS['RB']

def getCheckBoxesColumns():
    return IDS['CB']

def getTextBoxes():
    return IDS['TB']


def checkColumnsMismatch(importDataColumns):
    mismatch = False
    setID = set(importDataColumns)
    setEC = set(getExportableColumns())
    if not ( setID == setEC ):
        print('WARNING:\tColumn mismatch:')
        print("\t(-) → Missing columns in CSV:", list(setEC.difference(setID)))
        print("\t(+) → Additional columns in CSV:", list(setID.difference(setEC)), '\n')
        print("\tMaybe you are using an old savefile. Missing columns will be CREATED.")
        print("\tAdditional columns will be ERASED if you make any change.")
        mismatch = True

    return mismatch


def expand_df(selectedFiles):
    global args
    global importData
    global groups
    if Path(args.savefile).is_file():
        importData = pd.read_csv(args.savefile,
                                 converters={
                                                'group': str,
                                                'galaxy': str,
                                            }
                                )
        
        if 'fits_coords' in importData.columns:
            importData['fits_coords'] = importData['fits_coords'].fillna("[]").apply(lambda x: eval(x))
            
        checkColumnsMismatch(importData.columns.values)
        importData['processed'] = True
        if 'filename' in groups.columns:
            importData['fullpath'] = ''
        if 'ra' in groups.columns and 'dec' in groups.columns:
            importData['ra'] = 0.0
            importData['dec'] = 0.0

        # I know there is a best way to implement it, maybe in next release
        try:
            # Saved and selected data:
            for i, row in selectedFiles.iterrows():
                item = importData.loc[importData.galaxy == row.galaxy]
                # If selected row is imported in savefile:
                if (item.size > 0):
                    if 'filename' in importData.columns:
                        file = Path(args.path) / Path(row['filename'])
                        importData.loc[importData.galaxy == row.galaxy, 'fullpath'] = file.absolute()
                    if 'ra' in importData.columns and 'dec' in importData.columns:
                        importData.loc[importData.galaxy == row.galaxy, 'ra'] = row.ra
                        importData.loc[importData.galaxy == row.galaxy, 'dec'] = row.dec
                # If selected row is not in savefile:
                else:
                    importData = pd_concat(importData, newEntry(row))

            # Add the full path to imported but unselected data:
            processedUnselectedData = importData[importData.fullpath == '']
            for i, row in processedUnselectedData.iterrows():
                if 'filename' in importData.columns:
                    file = Path(args.path) / Path(row['filename'])
                    importData.loc[importData.galaxy == row.galaxy, 'fullpath'] = file.absolute()
                if 'ra' in importData.columns and 'dec' in importData.columns:
                    ra = groups.loc[groups.galaxy == row.galaxy].ra.item()
                    dec = groups.loc[groups.galaxy == row.galaxy].dec.item()
                    importData.loc[importData.galaxy == row.galaxy, 'ra'] = ra
                    importData.loc[importData.galaxy == row.galaxy, 'dec'] = dec

        except KeyError as e:
                print(f"ERROR:\tError while parsing CSV. [{e}]")

    else:
        importData = pd.DataFrame(columns=COLUMNS)
        for i, row in selectedFiles.iterrows():
            importData = pd_concat(importData, newEntry(row))

    return importData


def newEntry(row:pd.Series) -> dict:
    entry = {}
        
    if 'group' in row:
        entry.update({'group': row.group})
        
    if 'galaxy' in row:
        entry.update({'galaxy': row.galaxy})
        
    if 'filename' in row:
        file = Path(args.path) / Path(row['filename'])
        entry.update({'filename': file.name}) # default value
    
    if 'fits' in row:
        entry.update({'fits': row.fits})
        entry.update({'fits_coords': []})
        
    # ID needed? to separate widget groups?
    for i, rbgCol in enumerate(getRadioButtonGroups()):
        entry.update({rbgCol: getRadioButtonsNames()[-1]}) # default value 

    for i, cbCol in enumerate(getCheckBoxesColumns()):
        entry.update({cbCol: False})

    for i, tbCol in enumerate(getTextBoxes()):
        entry.update({tbCol: ''})

    entry.update({'processed': False})
    
    if 'filename' in row:
        entry.update({'fullpath': file.absolute()})
        
    if 'ra' in row and 'dec' in row:
        entry.update({
            'ra': row.ra,
            'dec':  row.dec
        })
        
    return entry


def save_df(df:pd.DataFrame) -> None:
    global args
    global importData

    # Concatenate items in CSV with our processed items:
    processedItems = pd_concat(importData.loc[df['processed'] == True],
                               df.loc[df['processed'] == True])
    # processedItems = pd.concat([importData.loc[df['processed'] == True],
    #                            df.loc[df['processed'] == True]])

    # Remove old values, keep last ones:
    
    s_cols = ['galaxy']
    if 'group' in processedItems.columns:
        s_cols.insert(0,'group')
    exportData = processedItems.drop_duplicates(s_cols, keep='last').sort_values(by=s_cols)

    # Export final dataframe:
    exportData.to_csv(args.savefile, columns=getExportableColumns(),
                          index=False)
    
def pd_concat(df: pd.DataFrame, data: Union[pd.DataFrame, list, dict]) -> pd.DataFrame:
        """ Concats data to the given dataframe

        Parameters
        ----------
        df: pandas.Dataframe
            Pandas dataframe to use

        data: list, dict or pandas.Dataframe
            Data to be concatenated to the input pandas Dataframe.
            - List of the values to be concatenated (order of input values and Dataframe columns must match).
            - Dict of the 'key:values', where keys match the Dataframe columns (if not, values are put to NaN).
            - pandas.Dataframe where columns (should) match the input Dataframe 
              (if not, new columns are created or values are put to NaN).

        Returns
        -------
        pandas.DataFrame
        """
        # check if data is list
        df_data = pd.DataFrame()
        if type(data) == list:
            if len(data) != len(df.columns):
                raise Exception('ERROR: Input data [list] length is not equal to input dataframe')
            df_data = pd.DataFrame([data], columns=df.columns)
        elif type(data) == dict:
            if len(data) != len(df.columns):
                warnings.warn('Input data [dict] missing input dataframe keys. Missing values inserted as NaN')
                print(list(data.keys()))
                print(list(df.columns))
            df_data = pd.DataFrame([data])
        elif type(data) == pd.DataFrame:
            if not df.empty:
                cmp_df_data = list(df.keys()[~df.keys().isin(data.keys())])
                cmp_data_df = list(data.keys()[~data.keys().isin(df.keys())])
                if len(cmp_df_data) > 0:
                    warnings.warn(f'Input data missing input dataframe column. {cmp_df_data}')
                if len(cmp_data_df) > 0:
                    warnings.warn(f'Input data column(s) not in input dataframe. {cmp_data_df}')
            df_data = data
        df = pd.concat([df, df_data], ignore_index=True) if len(df) > 0 else df_data
        return df

