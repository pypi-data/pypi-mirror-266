import os
from math import pi
import numpy as np
from va.utils.misc import *


class GetStars:



    def __init__(self, star_file):
        self.star_file_name = os.path.basename(star_file)
        self.star_file = star_file
        self.star_blocks = self.read_star_file()


    def read_star_file(self):
        """
        find the data block which defined by 'block'
        """

        star_data = {}
        current_block = None

        with open(self.star_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("data_"):
                    current_block = line
                    star_data[current_block] = []
                elif current_block is not None and line:
                    star_data[current_block].append(line)

        return star_data


    def data_general_block(self):
        """
        Get the data_general block
        """

        data_general_block = {}
        for line in self.star_blocks['data_general']:
            if line.startswith('# version'):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                data_general_block[key] = float(value.strip()) if value.isdigit() else value

        return data_general_block


    def data_fsc_block(self):
        """
        Get the data_fsc block
        """

        data_fsc_block = {}
        useful_data = self.star_blocks['data_fsc'][1:-2]
        header = [line.split(maxsplit=1)[0][4:] for line in useful_data[:8]]
        data = useful_data[8:]
        column_data_list = [row.split() for row in data]
        new_data_list = list(map(list, zip(*column_data_list)))
        # data_list = [[float(value) for value in sublist] for sublist in data_list]
        data_list = []
        for sublist in new_data_list:
            column_data_list = []
            for value in sublist:
                column_data_list.append(keep_three_significant_digits(float(value)))
            data_list.append(column_data_list)

        if len(header) == len(data_list):
            for header, data_list in zip(header, data_list):
                data_fsc_block[header] = data_list

        return data_fsc_block

    def data_extra(self, data_fsc_block):
        """
        Add half bit, one-bit and 3-sigma to data_fsc_block
        """

        indices = data_fsc_block['SpectralIndex']
        asym = 1.0
        half_bit = []
        one_bit = []
        for i in range(0, len(indices)):
            volume_diff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
            novox_ring = volume_diff / (1 ** 3)
            effno_vox = (novox_ring * ((1.5 * 0.66) ** 2)) / (2 * asym)
            if effno_vox < 1.0: effno_vox = 1.0
            sqreffno_vox = np.sqrt(effno_vox)

            bit_value = (0.2071 + 1.9102 / sqreffno_vox) / (1.2071 + 0.9102 / sqreffno_vox)
            half_bit.append(keep_three_significant_digits(bit_value))
            onebit_value = (0.5 + 2.4142 / sqreffno_vox) / (1.5 + 1.4142 / sqreffno_vox)
            one_bit.append(keep_three_significant_digits(onebit_value))

        gold_line = [0.143] * len(indices)
        half_line = [0.5] * len(indices)
        half_bit.insert(0, 1)
        one_bit.insert(0, 1)

        data_fsc_block['halfbit'] = half_bit[:-1]
        data_fsc_block['onebit'] = one_bit[:-1]
        data_fsc_block['0.5'] = half_line
        data_fsc_block['0.143'] = gold_line

        return data_fsc_block

    def _xy_check(self, x, y):
        """
        check the x, y value and return the results
        """

        if x.size == 0 and y.size == 0:
            return None, None
        else:
            x = np.round(x[0][0], 4)
            y = np.round(y[0][0], 4)
            return x, y

    def all_intersection(self, data_fsc_block):
        """
        Get all intersections from data_fsc_block
        """

        x = data_fsc_block['Resolution']
        correlation = data_fsc_block['FourierShellCorrelationUnmaskedMaps']
        half_bit = data_fsc_block['halfbit']
        gold = data_fsc_block['0.143']
        half = data_fsc_block['0.5']

        x_gold, y_gold = interpolated_intercept(x, correlation, gold)
        x_half, y_half = interpolated_intercept(x, correlation, half)
        x_half_bit, y_half_bit = interpolated_intercept(x, correlation, half_bit)

        x_gold, y_gold = self._xy_check(x_gold, y_gold)
        x_half, y_half = self._xy_check(x_half, y_half)
        x_half_bit, y_half_bit = self._xy_check(x_half_bit, y_half_bit)
        if not x_gold or not y_gold:
            print('!!! No intersection between FSC and 0.143 curves.')
        if not x_half or not y_half:
            print('!!! No intersection between FSC and 0.143 curves.')
        if not x_half_bit or not y_half_bit:
            print('!!! No intersection between FSC and 0.143 curves.')

        intersections = {'intersections': {
                          'halfbit': {'x': x_half_bit, 'y': y_half_bit},
                          '0.5': {'x': x_half, 'y': y_half},
                          '0.143': {'x': x_gold, 'y': y_gold}}}

        return intersections


    def all_curves(self, data_fsc_block):
        """
        Get all curves from data_fsc_block
        """

        curve_mapping = {
            'fsc': 'FourierShellCorrelationUnmaskedMaps',
            'onebit': 'onebit',
            'halfbit': 'halfbit',
            '0.5': '0.5',
            '0.143': '0.143',
            'level': 'Resolution',
            'angstrom_resolution': 'AngstromResolution',
            'phaserandmization': 'CorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps',
            'fsc_masked': 'FourierShellCorrelationMaskedMaps',
            'fsc_corrected': 'FourierShellCorrelationCorrected'
        }
        curves = {key: data_fsc_block[value] for key, value in curve_mapping.items() if value in data_fsc_block}
        final_curves = {'curves': curves}

        return final_curves




