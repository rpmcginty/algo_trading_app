import os
import inspect
import json


def find_data_path(pwd,target_dir="algo_trading_app",lvl=0):
    res = ''
    if os.path.split(pwd)[1] == target_dir:
        return os.path.split(pwd)[1]
    elif lvl > 10:
        return res
    elif os.path.isdir(pwd):
        for subdir in os.listdir(pwd):
            if subdir == target_dir:
                return os.path.join(pwd,subdir)
        for subdir in os.listdir(pwd):
            tmp = find_data_path(os.path.join(pwd,subdir),lvl=lvl+1)
            if tmp != '':
                return tmp
    return res

#TODO: Add function that generates empty custom.cfg and custom.parameters file.

def create_custom_files(cfg, config_path):
    def copy_dict_skeleton(d_old):
        d_new = {}
        for k in d_old:
            if isinstance(d_old[k], dict):
                d_new[k] = copy_dict_skeleton(d_old[k])
            # else:
            #     d_new[k] = {}
        return d_new

    if os.path.isfile(os.path.join(config_path, "custom.cfg")):
        print("custom.cfg already exists.")
    else:
        # Creating configuration file
        custom_cfg = copy_dict_skeleton(cfg)
        with open(os.path.join(config_path, "custom.cfg"), 'w') as new_cfg_file:
            json.dump(custom_cfg,new_cfg_file,indent=2)
            print ("custom.cfg created.")


def get_home_path(home_env_vars=("HOME","HOMEPATH")):
    home = None
    for home_env_var in home_env_vars:
        if home is not None:
            continue
        home = os.environ.get(home_env_var,None)
    return home


def main():
    home = get_home_path(('HOME','HOMEPATH'))
    config_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    cfg_file = os.path.join(config_path,'default.cfg')
    if not os.path.isfile(cfg_file):
        raise IOError('Could not find configuration file: {filename}'.format(filename=cfg_file))
    with open(cfg_file,'r') as f:
        cfg =  json.load(f)
    proj_path_filename = os.path.join(config_path,cfg['paths']['project'])
    with open(proj_path_filename,'w') as proj_path_file:
        pardir = os.path.abspath(os.path.join(config_path, os.pardir))
        proj_path_file.write(pardir)
        print ( "Project path updated." )

    # Do not update data path file if it already exists.
    data_path_filename = os.path.join(config_path,cfg['paths']['data'])
    if not os.path.exists(data_path_filename):
        with open(os.path.join(config_path,data_path_filename),'w') as data_path_file:
            if home is not None and os.path.isdir(os.path.join(home, 'Dropbox')):
                data_dir = find_data_path(os.path.join(home, 'Dropbox'))
            else:
                data_dir = os.path.join(os.path.abspath(os.path.join(config_path, os.pardir)),'data')
            data_path_file.write(data_dir)
            print ( "Data path updated." )
    else:
        print ( "Data path not updated" )

    # Creating custom files
    create_custom_files(cfg, config_path)


if __name__=="__main__":
    main()