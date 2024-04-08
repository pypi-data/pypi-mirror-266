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

from pytoughreact.plotting.plot_multiple_files_routine import PlotMultiFiles


class FileReadMultiple(object):
    """
    Class for processing multiple file results
    """

    def __init__(self, simulator_type, file_locations, file_titles, props, **kwargs):
        """Initialization of Parameters

        Parameters
        -----------
        simulator_type :  string
            List of type of simulator being run. Can either be 'tmvoc', 'toughreact' or 'tough3'.
            Should be tough3 for this class
        file_location : list[string]
            List of location of results file on system
        file_title : list[string]
            List of title or name of the file. Example is 'kddconc.tec' or 'OUTPUT.csv'
        prop : list[string]
            Properties to be plotted. Example could be 'portlandite'
        kwargs: dict
            1) x_slice_value (integer) - if the plot should be sliced on the  x axis
            2) per_file  (boolean) - if the plot should be made per file and not per property
            3) title (list of strings) - title of each of the plots


        Returns
        --------

        """
        assert isinstance(file_locations, list)
        assert isinstance(file_titles, list)
        self.file_locations = file_locations
        self.file_titles = file_titles
        self.simulator_type = simulator_type
        self.props = props
        self.x_slice_value = kwargs.get('x_slice_value')
        self.per_file = kwargs.get('per_file')
        self.title = kwargs.get('title')

    def plotTime(self, grid_block_number, legend, plot_kind='property', format_of_date='day'):
        # TODO write code to slice x axis
        # TODO write code to slice through domain

        """ Plot selected parameter on y axis and time on x axis

        Parameters
        -----------
        grid_block_number : int
            The grid block number in mesh for which to retrieve the results
        legend : list[string]
            List of titles for the legend of the plot
        plot_kind : string
            If the plot should be made based on property or based on files
        format_of_date : str
            Provides information to the method on format of the date. For example. year, hour, min or seconds

        Returns
        --------

        """
        plottest = PlotMultiFiles(self.simulator_type, self.file_locations, self.file_titles, self.props,
                                  x_slice_value=self.x_slice_value, per_file=self.per_file, title=self.title)
        if len(self.props) == 1:
            plottest.multiFileSinglePlot(grid_block_number, legend)
        else:
            plottest.plotMultiElementMultiFile(grid_block_number, legend, format_of_date, plot_kind)

    def plotTimePerPanel(self, grid_block_number, panels, format_of_date='day'):
        """ Plot Multiple plots in a panel

        Parameters
        -----------
        grid_block_number : int
            The grid block number in mesh for which to retrieve the results
        panels: list[string]
            Data to be retrieved for each of the panel in the canvas
        format_of_date : str
            Provides information to the method on format of the date. For example. year, hour, min or seconds

        Returns
        --------

        """
        plottest = PlotMultiFiles(self.simulator_type, self.file_locations, self.file_titles, self.props,
                                  x_slice_value=self.x_slice_value, per_file=self.per_file, title=self.title)
        plottest.plotMultiPerPanel(grid_block_number, panels, format_of_date)

    def plotParamWithLayer(self, directionX, directionY, layer_num, time, legend):
        """ Plot of Parameter with Layer

        Parameters
        -----------
        directionX :  string
            Direction to be plotted on the X axis. Can be 'X', 'Y', 'Z'
        directionY :  string
            Direction to be plotted on the Y axis. Can be 'X', 'Y', 'Z'
        layer_num: int
            Layer number in which to retrieve data
        time : float
            Time in which the data should be retrieved.
        legend : list[string]
            List of titles for the legend of the plot

        Returns
        --------

        """
        plottest = PlotMultiFiles(self.simulator_type, self.file_locations, self.file_titles, self.props,
                                  x_slice_value=self.x_slice_value, per_file=self.per_file, title=self.title)
        if len(self.props) == 1:
            pass
        else:
            plottest.plotMultiFileDistance(directionX, directionY, time, layer_num, legend)
