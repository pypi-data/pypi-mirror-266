'''
MIT License

Copyright (c) [2022] [Temitope Ajayi]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import os
import shutil
import itertools


class t2UtilitiesToughReact(object):
    # takes in file names as a list
    """
    This class prepares the output files from TOUGHREACT for plot visualizations and analysis
    """

    def __init__(self, location, word, mesh_file_name='MESH'):
        """ Initialization of Parameters
        An instance of this class takes in five parameters the last of which is optional;

        Parameters
        -----------
        location : string
            The current file location where the simulations have been carried out
        word : string
            The word where the truncation in the MESH file is to begin. Typically this should be 'CONNE'
        mesh_file_name : string
            The name of the mesh file

        Returns
        --------
        """

        self.location = location
        self.word = word
        self.file2 = mesh_file_name

    def copy_file(self, filename, destination):
        """ This method copies single file from the location to the destination folder. it takes in a a single argument

        Parameters
        -----------
        filename : str
            the name of the file to be transferred
        destination : str
            the name of the file to receive it

        Returns
        --------

        """
        # copy specific file
        src_files = os.listdir(self.location)
        for file_name in src_files:
            if file_name == filename:
                full_file_name = os.path.join(self.location, file_name)
                if (os.path.isfile(full_file_name)):
                    shutil.copy(full_file_name, destination)

    def copy_all_files(self, filenames):
        """This method copies all files given in the instance of the class to the destination folder. It makes use
        of the copyfile() method in achieving this

        Parameters
        -----------
        filenames : list
            list of all filename

        Returns
        --------

        """
        # copy all files
        for i in range(0, len(filenames)):
            a = filenames[i]
            self.copy_file(a)
        print('...copying files...')

    def find_word(self):
        """ This method finds the word where the truncation of the MESH file is to occur.

        Parameters
        -----------

        Returns
        --------
        point : int
            point where MESH word is found

        """
        # find the position of a word
        with open(self.file2) as myFile:
            for num, line in enumerate(myFile, 1):
                if self.word in line:
                    point1 = num
                    return point1
        myFile.close()

    def slice_off_file(self):
        """ This method slices off all parameters below the word stated in the instance of the class

        Parameters
        -----------

        Returns
        --------
        point : int
            point where MESH word is found

        """

        #        os.remove("test2.txt")
        f = open("test2.txt", "w+")
        f.close()
        f = open("test.txt", "w+")
        f.close()
        f = open('test2.txt', 'r+')
        f.truncate(0)
        f.close()
        os.remove("test.txt")
        point1 = self.find_word()
        with open("test2.txt", "w") as f1:
            with open(self.file2, "r") as text_file:
                for line in itertools.islice(text_file, 1, point1 - 2):
                    f1.write(line)
        f1.close()

    def slice_off_line(self):
        """ This method slices off all grid parameter such as the volume, distance betweeen grids as stated in
        the TOUGHREACT flow.inp file

        The aim of the findword(), sliceofffile() and this method is to provide us with a list of all gridblocks
        in the simulation

        Parameters
        -----------

        Returns
        --------
        output : list
            list of grids

        """
        self.slice_off_file()
        with open('test2.txt') as thefile:
            lines = thefile.readlines()
            output = []
            for i in range(0, len(lines)):
                a = lines[i]
                b = a[0:5]
                output.append(b)

        return output

    def write_to_file(self):
        """ This method writes all gridblocks to a separate file called 'test.txt' for easy location and onward
        manipulations

        The aim of the find_word(), slice_off_file() and this method is to provide us with a list of all gridblocks
        in the simulation

        Parameters
        -----------

        Returns
        --------

        """
        mesh = self.slice_off_line()
        with open("test.txt", "w") as f1:
            for item in mesh:
                f1.write("%s\n" % item)
        f1.close()
