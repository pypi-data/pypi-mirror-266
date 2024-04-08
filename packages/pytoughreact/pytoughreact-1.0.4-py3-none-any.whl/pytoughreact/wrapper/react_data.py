from t2data import t2data, padstring, fix_blockname
from fixed_format_file import default_read_function
from pytoughreact.wrapper.reactblock import t2block
import numpy as np


class react_data(t2data):
    """Class for parsing REACTION data file."""
    def __init__(self, filename, mode, read_function=default_read_function):
        """ Initialization of parameters

        Parameters
        -----------
        filename : string
            File name of the reaction data file
        mode : str
            Mode in which to read the dat (read, write)
        read_fuction : function
            Function for processing the different spacing forms

        Returns
        --------

        """
        super(t2data, self).__init__(filename='', meshfilename='',
                                     read_function=default_read_function)

    def read_blocks(self, infile):
        """ Reads grid blocks.

        Parameters
        -----------
        infile : str
            Input file processor

        Returns
        --------

        """
        self.grid.block, self.grid.blocklist = {}, []
        line = padstring(infile.readline())
        while line.strip():
            [name, nseq, nadd, rockname,
                volume, ahtx, pmx, x, y, z] = infile.parse_string(line, 'blocks')
            name = fix_blockname(name)
            if rockname in self.grid.rocktype:
                rocktype = self.grid.rocktype[rockname]
            elif rockname.strip() == '' and self.grid.num_rocktypes > 0:
                rocktype = self.grid.rocktypelist[0]  # default
            else:
                try:  # check if rocktype index specified:
                    rockindex = int(rockname) - 1
                    rocktype = self.grid.rocktypelist[rockindex]
                except Exception:
                    raise RuntimeError("Unknown rocktype " + rockname + " in block " + name)
            if (x is not None) and (y is not None) and (z is not None):
                centre = np.array([x, y, z])
            else:
                centre = None
            if nseq == 0:
                nseq = None
            if nadd == 0:
                nadd = None
            self.grid.add_block(t2block(name, volume, rocktype,
                                        centre=centre, ahtx=ahtx,
                                        pmx=pmx, nseq=nseq, nadd=nadd))
            line = padstring(infile.readline())
