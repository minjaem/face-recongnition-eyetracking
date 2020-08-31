import pickle, os, shutil
from os import PathLike


class PickledDict(dict):
    """
    This Dictionary gets stored as a file and is able to handle complex objects, like a Numpyarray.
    Use it the following way. read the data:

    data = pickled_dict(path, 'r')

    To write data inside use the with statement:

    with pickled_dict(path, 'c') as d:
        d[key] = data

    :param filename: this is the name of the pickled_dict (and the path)
    :param mode: this is c = create, r = read, n = new. It indicates whether the Dict is created if it doesn't exist,
    it is only being read or if it is guaranteed to be new.
    """

    def __init__(self, filename: PathLike, mode: str = 'c', *args, **kwargs):
        self.filename = filename
        self.mode = mode  # can be c, r, n
        self.reload()
        dict.__init__(self, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def __len__(self):
        return len(self.keys())

    def sync(self):
        """
        handles writing the data to the disk
       :return:
        """
        if self.mode == 'r':
            return -1
        tempname = self.filename + '.tmp'
        with open(tempname, 'wb') as tempobj:
            try:
                self.dump(tempobj)
            except Exception:
                os.remove(tempname)
                raise Exception("An Error occurred")
        shutil.move(tempname, self.filename)

    def close(self):
        """
        it gets called if the connection ends
        :return:
        """
        self.sync()

    def load(self, fileobj: PathLike):
        """

        loads the data from the disk
        :param fileobj:
        :return:
        """
        try:
            return self.update(pickle.load(fileobj))
        except ValueError:
            raise ValueError('File format not supported')

    def dump(self, fileobj: PathLike) -> None:
        """
        writes data to the disk. It only supports pickled data.
        :return:
        """
        pickle.dump(dict(self), fileobj, protocol=pickle.HIGHEST_PROTOCOL)

    def reload(self) -> None:
        """
        Update your variable, that saved the Data and needs to be updated to have the new Values saved
        :return: 
        """
        if self.mode != 'n' and os.access(self.filename, os.R_OK):
            with open(self.filename, 'rb') as fileobj:
                self.load(fileobj)
