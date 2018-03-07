#! /usr/bin/python
# Functions for renaming BIDS files 
# 9.6.17 KLS

import os, shutil, fnmatch, json

def parse_filename (file_name):
  '''
  This function splits the filenames output from dcm2niix into useful
  variables usage: [file_str, file_ext] = parse_filename
  '''
  fields = file_name.split('.')
  if len(fields) == 3:
      file_ext = fields[1] + '.' + fields[2]
  else:
      file_ext = fields[1]
  return fields[0], file_ext

def det_file_type(file_str):
  '''
  This function takes the file string and determines the corresponding
  search_term, data_type label and folder label usage:
  [search_term, dir_name, file_type] = det_file_type(data_type)
  '''
  BIDS_dir = {'T1W': 'anat', 'T2W': 'anat', 'flash': 'anat', 'task':'func', 'rest':'func', 'diff':'dwi', 'FieldMap':'fmap'}
  BIDS_data = {'T1W':'T1w', 'T2W':'T2w', 'flash':'FLASH', 'task':'bold', 'rest':'bold', 'diff':'dwi', 'FieldMap': ['phasediff', 'magnitude1', 'magnitude2']}
  names = ['T1W', 'T2W', 'flash', 'task', 'rest', 'diff', 'FieldMap', 'localizer']
  dt = [s for s in names if s in file_str][0] # should return the search_term
  dt_label = BIDS_data[dt] # should return the data_type label
  f_label = BIDS_dir[dt] # should return the directory label
  return dt, dt_label, f_label

def count_num_data_type(file_list, file_name, file_type, file_ext):
  '''
  This function takes the file_list and the file_type and determines how many
  files there are for each file type usage:
  [n, run_num] = count_num_data_type(file_list,data_type)
  '''
  same_file= [i for i in file_list if file_type in i if file_ext in i]
  run_num = same_file.index(file_name) + 1
  return len(same_file), run_num

def create_dir(base_dir, subject, dir_name):
    '''
    This function takes the dir_name and if the directory does not exist, it
    creates a new directory
    '''
    path = os.path.join(base_dir, subject, dir_name)
    if not os.path.isdir(path):
        os.makedirs(path)

def id_file_type(file_list, id_text):
    '''
    Identify fieldmap files
    '''
    file_subset = [j for j in file_list if id_text in j]
    return file_subset

def read_echo(fmap_json_path):
    '''
    Read echo time from field map .json magnitude files
    '''
    with open(fmap_json_path) as txt:
        d = json.load(txt)
    echo = d['EchoTime']
    return echo

def rename_file(s, b, file, files, task = '', bold=''):
    #print file
    name = parse_filename(file)[0]
    file_ext = parse_filename(file)[1]
    search_for = det_file_type(name)[0]
    BIDS_name = det_file_type(name)[1]
    BIDS_dir = det_file_type(name)[2]
    num = count_num_data_type(files, file, search_for, file_ext)[0]
    run = count_num_data_type(files, file, search_for, file_ext)[1]
    dir_path = os.path.join(base_dir, s)
    i_file = os.path.join(dir_path, name + '.' + file_ext)
    if num == 1:
        o_file = os.path.join(dir_path, BIDS_dir, s + '_' + BIDS_name + '.' + file_ext)
    elif task != '':
        o_file = os.path.join(dir_path, BIDS_dir, s + '_task-' + task +
        '_run-0' + str(run) + '_' + BIDS_name + '.' + file_ext)
    else:
        o_file = os.path.join(dir_path, BIDS_dir, s + '_run-0' + str(run) + '_'
        + BIDS_name + '.' + file_ext)
    shutil.move(i_file, o_file)

def new_f_name(s, file, files, task = '', bold = ''):
    name = parse_filename(file)[0]
    file_ext = parse_filename(file)[1]
    search_for = det_file_type(name)[0]
    BIDS_name = det_file_type(name)[1]
    BIDS_dir = det_file_type(name)[2]
    num = count_num_data_type(files, file, search_for, file_ext)[0]
    run = count_num_data_type(files, file, search_for, file_ext)[1]
    new_file_name = s + '_run-0' + str(run) + '_'+ BIDS_name + '.' + file_ext
    return(new_file_name)

# Get subject names and set input/output directories
# -----------------------------------------------------------------------
# Replace the following path with the path to your raw BIDS directory
base_dir = '/Users/kendraseaman/Dropbox (MCAB Lab)/MCAB/data/agerl/BIDS'
#subjects = [i for i in os.listdir(base_dir)]

for s in subjects:
    files = [f for f in os.listdir(os.path.join(base_dir, s))]
    print files

    # Organize and rename anat files
    create_dir(base_dir, s, 'anat')
    t1_files = id_file_type(files, 'T1W')
    [rename_file(s, base_dir, f, files) for f in t1_files]
    t2_files = id_file_type(files, 'T2W')
    [rename_file(s, base_dir, f, files) for f in t2_files]
    flash_files = id_file_type(files, 'flash')
    [rename_file(s, base_dir, f, files) for f in flash_files]

    # # Organize and rename func files
    create_dir(base_dir, s, 'func')
    step2_files = id_file_type(files, 'task')
    [rename_file(s,base_dir, f, files, task = '2step', bold = 'bold') for f in step2_files]
    new_step2_files = [new_f_name(s, f, files, task = '2step', bold = 'bold') for f in step2_files if f.endswith('.nii.gz')]
    rest_files = id_file_type(files, 'rest')
    [rename_file(s,base_dir, f, files, task = 'rest', bold = 'bold') for f in rest_files]
    new_rest_files = [new_f_name(s, f, files, task = 'rest', bold = 'bold') for f in rest_files if f.endswith('.nii.gz')]
    new_file_names = new_step2_files + new_rest_files

    # Organize and rename dwi files
    create_dir(base_dir, s, 'dwi')
    dwi_files = id_file_type(files, 'diff')
    [rename_file(s,base_dir, f, files) for f in dwi_files]

    # Deal with Field Map Files
    create_dir(base_dir, s, 'fmap')
    fmap_files = id_file_type(files, 'FieldMap')
    if len(fmap_files) > 0:

        m1file = [f for f in fmap_files if f.endswith('_FieldMap_2mm.json')][0]
        echo1 = read_echo(os.path.join(base_dir, s, m1file))

        m2file = [f for f in fmap_files if f.endswith('_FieldMap_2mm_e2a.json')][0]
        echo2 = read_echo(os.path.join(base_dir, s, m2file))

        new_dict = {'EchoTime1': echo1, 'EchoTime2': echo2, 'IntendedFor': new_file_names}
        pdfile = os.path.join(base_dir, s, s + '_FieldMap_2mm_e2.json')
        pdname = os.path.join(base_dir, s, 'fmap', s + '_phasediff.json')

        with open(pdfile) as txt:
	            file = json.load(txt)
        file.update(new_dict)

        with open(pdname, 'w') as f:
	           json.dump(file, f)
        os.remove(os.path.join(base_dir, s, m1file))
        os.remove(os.path.join(base_dir, s, m2file))
        os.remove(pdfile)

        [os.rename(os.path.join(base_dir, s, d), os.path.join(base_dir, s, 'fmap', s + '_phasediff.nii.gz'))
        for d in fnmatch.filter(fmap_files, '*FieldMap_2mm_e2.nii.gz')]
        [os.rename(os.path.join(base_dir, s, d), os.path.join(base_dir, s, 'fmap', s + '_magnitude1.nii.gz'))
        for d in fnmatch.filter(fmap_files, '*FieldMap_2mm.nii.gz')]
        [os.rename(os.path.join(base_dir, s, d), os.path.join(base_dir, s, 'fmap', s + '_magnitude2.nii.gz'))
        for d in fnmatch.filter(fmap_files, '*FieldMap_2mm_e2a.nii.gz')]

    local_files = id_file_type(files, 'localizer')
    print local_files
    [os.remove(os.path.join(base_dir, s, f)) for f in local_files]
