import collections
import inspect
import json
import os


def load_config_path(path='config',project_name='algo_trading_app'):
    # pwd = os.getcwd()
    pwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    dirFound = os.path.isdir(os.path.join(pwd,path))
    while not dirFound and os.path.basename(pwd)!=project_name and pwd != os.path.realpath(os.path.join(pwd, '..')):
        pwd = os.path.realpath(os.path.join(pwd,os.pardir))
        dirFound = os.path.isdir(os.path.join(pwd,path))
    # One last check for Directory
    if not os.path.isdir(os.path.join(pwd,path)):
        raise IOError("Could not find {0} directory.".format(path))
    return os.path.join(pwd,path)


def load_config_file(path='config', default_filename='default.cfg', project_name='algo_trading_app'):
    # Traverse upwards to find config path
    default_filename = 'default.cfg'
    custom_filename = 'custom.cfg'
    config_path = load_config_path(path=path,project_name=project_name)
    # Get default.cfg
    with open(os.path.join(config_path, default_filename), 'r') as f:
        default = json.load(f)

    if os.path.isfile(os.path.join(config_path,custom_filename)):
        try:
            with open(os.path.join(config_path, custom_filename), 'r') as f:
                custom = json.load(f)
            default = update_parameters(default,custom,add_new=True)
        except:
            print ("Custom.cfg is empty or Could not resolve format of {0}. Make sure format mimics JSON format.")
    return default

def get_path(name, forcepath=True, cfg=None):
    if cfg is None: cfg = load_config_file()
    try:
        if not isinstance(name,list): path = cfg['paths'].get(name,name)
        else: path = name
        if isinstance(path,(str,unicode)) and os.path.splitext(path)[-1]=='.path': # *.path file
            config_path = load_config_path()
            with open(os.path.join(config_path,path),'r') as f:
                path = f.read()
            return path
        elif isinstance(path,list): #
            path_list = list(path)
            path = ''
            for p in path_list:
                if os.path.isdir(os.path.join(path,p)) or (forcepath and p not in cfg['paths']):
                    path = os.path.join(path,p)
                else:
                    path = os.path.join(path,get_path(p,cfg=cfg))
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(get_path(cfg['paths']['project'],cfg=cfg),path)
    except:
        raise IOError("Could not resolve path.")


def get_params(*args,**kwargs):
    def _finditem(obj, key):
        if key in obj: return obj[key]
        for k, v in obj.items():
            if isinstance(v,dict):
                item = _finditem(v, key)
                if item is not None:
                    return item
    cfg = kwargs.get('cfg',load_config_file())
    if len(args) > 1:
        res = []
        for arg in args:
            res.append(_finditem(cfg,arg))
    elif len(args)==1: res = _finditem(cfg,args[0])
    else: res = None
    return res


def update_parameters(parameters, new_parameters, add_new=False):
    for k, v in new_parameters.iteritems():
        if isinstance(v, collections.Mapping) and (add_new or k in parameters) and v is not None:
            parameter_subset = parameters.get(k, {})
            r = update_parameters(parameter_subset, v)
            parameters[k] = r
        else:
            parameters[k] = new_parameters[k]
    return parameters


#--------------------------------------#
###        Generic File IO           ###
#--------------------------------------#


def load_file(name,asSeries=True,aslist=False,load_param_name=None,cfg=None,**kwargs):
    if cfg is None: cfg = load_config_file()
    if isinstance(name,list) and len(name) == 1: name = name[0]
    if not isinstance(name,list):
        res = cfg['files'].get(name,name)
    else:
        res = name
    full_filename = get_path(res)
    ext = os.path.splitext(full_filename)[-1]
    if ext in cfg['extension_mappings']['.csv']:
        if load_param_name is None :
            if not isinstance(name, list):
                load_param_name = name
            else:
                load_param_name = name[-1]
        csv2df_kwargs = cfg['load_kwargs'].get(load_param_name,{})
        csv2df_kwargs.update(kwargs)
        res = pd.read_csv(full_filename,**csv2df_kwargs)
        if asSeries and res.ndim > 1 and len(res.columns) == 1: res = res[res.columns[0]]
        if aslist: res = res.values.ravel().tolist()
    elif ext in cfg['extension_mappings']['.json']:
        with open(full_filename,'r') as f:
            res = json.load(f)
    else:
        with open(full_filename,'r') as f:
            res = f
    return res


def save_file(name,data,cfg=None,astype=None,**kwargs):
    if cfg is None:cfg = load_config_file()
    if not isinstance(name,list):
        res = cfg['files'].get(name,None)
    else:
        res = name
        name = ''
    if res is None: return False
    if isinstance(res,list):
        dir_name,filename = res[:-1],res[-1]
        dir_name = dir_name[0] if len(dir_name) == 1 else dir_name
    else:
        dir_name,filename = get_path(name='project_path',cfg=cfg),res
    full_filename = os.path.join(get_path(name=dir_name,cfg=cfg),filename)
    ext = os.path.splitext(full_filename)[-1]
    if ext in cfg['extension_mappings']['.csv'] or \
            (astype is not None and astype in cfg['extension_mappings']['.csv']):
        if isinstance(data,(pd.core.frame.DataFrame,pd.core.series.Series)):
            df2csv_kwargs = cfg['save_kwargs'].get(name,{})
            df2csv_kwargs.update(kwargs)
            data.to_csv(full_filename,**df2csv_kwargs)
            return True
    elif ext  in cfg['extension_mappings']['.json'] or \
            (astype is not None and astype in cfg['extension_mappings']['.json']):
        with open(full_filename,'w') as f:
            json.dump(data,f,indent=2)
            return True
    else:
        return False



def load_key(key_name,cfg=None):
    if cfg is None: cfg = load_config_file()
    res = cfg['keys'].get(key_name, None)
    if res is None:
        raise KeyError("{0} not contained in default.cfg \"keys\".".format(key_name))
    if isinstance(res,list):
        dir_name,filename = res[:-1],res[-1]
        full_filename = os.path.join(get_path(name=dir_name,cfg=cfg),filename)
    else:
        full_filename = os.path.join(get_path('keys', cfg=cfg), res)
    ext = os.path.splitext(full_filename)[-1]
    if ext == '.json':
        with open(full_filename,'r') as f:
            res = json.load(f)
    elif ext == '.key': #
        with open(full_filename,'r') as f:
            res = f.read()
    else:
        raise TypeError('{0} value is not in correct format.'.format(key_name))
    return res