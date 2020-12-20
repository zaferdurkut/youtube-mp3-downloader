import os, time


def find_paths(directory, stipe):
    """ ""

    Arguments:
        directory {str} -- taranmak istenen ust dizin
        stipe {str} -- taranan uzanti

    Returns:
       path_list {list} -- path list for stipe
    """
    if stipe.islower():
        stipe_u = stipe.upper()
    else:
        stipe_u = stipe.lower()

    if directory:
        path_list = []
        for root, subdirectory, files in os.walk(directory):
            for f in files:
                if f.endswith(stipe) or f.endswith(stipe_u):
                    path_list.append(os.path.join(root, f))

        return path_list
    else:
        return None


def timerfunc(func):
    """
    A timer decorator
    """

    def function_timer(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        msg = "\tThe runtime for {func} took {time} seconds to complete"
        print(msg.format(func=func.__name__, time=runtime))
        return value

    return function_timer


def get_basename_dirname(path):
    base = os.path.basename(path)
    basename, ext = os.path.splitext(base)
    dirname = os.path.dirname(path)
    return basename, dirname


def create_path(directory, file):
    path = os.path.join(directory, file)
    return path


def create_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        raise e


def create_method_path(out_dir, algorithm):
    algorithm_path = create_path(out_dir, algorithm)
    create_directory(algorithm_path)
    values_path = create_path(algorithm_path, "values")
    create_directory(values_path)
    graphs_path = create_path(algorithm_path, "graphs")
    create_directory(graphs_path)
    return algorithm_path, values_path, graphs_path

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d["status"] == "finished":
        print(d["filename"], "Done downloading, converting ...")
