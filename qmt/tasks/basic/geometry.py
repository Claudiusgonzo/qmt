# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from shapely.geometry import Polygon, LineString

from qmt.data.geo_data import Geo1DData, Geo2DData, Geo3DData
from qmt.tasks.task import Task


class Geometry1D(Task):
    def __init__(self, options=None, name='geometry_1d_task'):
        """
        Builds a geometry in 1D.
        :param dict options: The dictionary specifying parts, of the form
        {"part_name":(start_coord,stop_coord)}
        :param str name: The name of this task.
        """
        super(Geometry1D, self).__init__([], options, name)

    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_1d: A Geo1DData object.
        """
        geo_1d = Geo1DData()
        for part_name in current_options:
            geo_1d.add_part(part_name, current_options[part_name][0], current_options[part_name][1])
        return geo_1d


class Geometry2D(Task):
    def __init__(self, options=None, name='geometry_2d_task'):
        """
        Builds a geometry in 2D.
        :param dict options: The dictionary holding parts and edges. It should be of the form:
        {'parts':{'part_name':list of 2d points}, 'edges':{'edge_name':list of 2d points}, where these lists are turned into Polygon and
        LineString objects, which are instances of shapely.geometry.
        "part_name":Part3D}
        :param str name: The name of this task.
        """
        super(Geometry2D, self).__init__([], options, name)

    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specification from above.
        :return: geo_2d: A Geo2DData object.
        """
        geo_2d = Geo2DData()
        for part_name in current_options['parts']:
            geo_2d.add_part(part_name, Polygon(current_options['parts'][part_name]))
        for edge_name in current_options['edges']:
            geo_2d.add_edge(edge_name, LineString(current_options['edges'][edge_name]))
        return geo_2d


class Geometry3D(Task):
    def __init__(self, options=None, name='geometry_3d_task'):
        """
        Builds a geometry in 3D.
        :param dict options: The dictionary specifying parts and and FreeCAD infromation. It should
        be of the form {"fcfile":binary_stream_of_fc_file,
                        "parts_dict":parts_dict,
                        "pyenv":path_to_py_2},
        where

        serial_fcdoc is the binary string of the FreeCAD input file (accessed via serialize_fc_file),
        parts_dict is a dictionary of the form {part_name:Part3D},
        pyenv is the path to the python 2 executable (on whatever system will execute the work).

        :param str name: The name of this task.
        """
        super(Geometry3D, self).__init__([], options, name)

    @staticmethod
    def serialize_fc_file(file_path):
        """
        Serialize a freecad file from disk in preparation for passing in through the task
        dictionary.
        :param file_path: path to the FreeCAD file
        :return file_content: binary stream of the FreeCAD file.
        """
        import codecs
        with open(file_path,'rb') as file:
            serial_data = codecs.encode(file.read(), 'base64').decode()
        return serial_data

    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_3d: A Geo3DData object.
        """
        from qmt.geometry.freecad_wrapper import fcwrapper

        # Convert NumPy3 floats to something that Python2 can unpickle
        if 'params' in current_options:
            current_options['params'] = {
                k: float(v) for k, v in current_options['params'].items()
            }

        pyenv = current_options['pyenv'] # the python 2 environment

        assert 'serial_fcdoc' in current_options # make sure the fc doc is in options

        # Send off the instructions
        geo = fcwrapper(pyenv, 'build3d',
                        {'input_result_list': input_result_list,
                         'current_options': current_options},
                         debug=False)

        return geo
