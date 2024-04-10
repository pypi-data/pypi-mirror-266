import os
import codecs
import json
import numpy as np


def change_filename(input_filename, output_filename):
    try:
        os.rename(input_filename, output_filename)
        print(f"File name changed from '{input_filename}' to '{output_filename}'")
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
    except FileExistsError:
        print(f"Error: File '{output_filename}' already exists.")

def create_directory(dir):
    """
    Create a directory if it doesn't exist and return the dir otherwise None

    :return: str or None
    """

    try:
        os.makedirs(dir, exist_ok=True)

        return dir
    except Exception as e:
        print(f'Create folder error: {e}')

        return None


def create_symbolic_link(file_path, link_name):
    """
    Create symbolic link to a file

    :return: str or None
    """

    file_dir = os.path.dirname(file_path)
    link_path = os.path.join(file_dir, link_name)

    if os.path.isfile(link_path):
        print(f"Symbolic link '{link_name}' already exists")
        return link_path
    else:
        try:
            os.symlink(file_path, link_path)
            print(f"Symbolic link '{link_name}' created successfully")
            return link_path
        except Exception as e:
            print(f"Error creating symbolic link: {e}")

            return None


def interpolated_intercept(x, y1, y2):
    """

        Find the intercept of two curves, given by the same x data

    """

    def intercept(point1, point2, point3, point4):
        """

            Find the intersection between two lines
            the first line is defined by the line between point1 and point2
            the second line is defined by the line between point3 and point4
            each point is an (x,y) tuple.

            So, for example, you can find the intersection between
            intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

            :return: Intercept, in (x,y) format

        """

        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0] * p2[1] - p2[0] * p1[1])

            return A, B, -C

        def intersection(L1, L2):
            D = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]

            x = Dx / D
            y = Dy / D

            return x, y

        L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
        L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

        R = intersection(L1, L2)

        return R

    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    if not isinstance(y1, np.ndarray):
        y1 = np.asarray(y1)
    if not isinstance(y2, np.ndarray):
        y2 = np.asarray(y2)
    idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
    # Remove the first point usually (0, 1) to avoid all curves starting from (0, 1) which pick as one intersection
    if idx.size != 0:
        if idx[0][0] == 0:
            idx = np.delete(idx, 0, 0)
        xc, yc = intercept((x[idx], y1[idx]), ((x[idx + 1], y1[idx + 1])), ((x[idx], y2[idx])),
                           ((x[idx + 1], y2[idx + 1])))
        return xc, yc
    else:
        nullarr = np.empty(shape=(0, 0))
        return nullarr, nullarr


def out_json(data_dict, out_file_path):
    """
    Given the data_dict and out_file_path, write the data to a json file
    """

    try:
        with codecs.open(out_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(data_dict, outfile)
        print("Data successfully written to", out_file_path)
    except Exception as e:
        print("Error:", e)


def first_non_zero_index(number_str):
    """
    Find the index of the first non-zero digit in a string representation of a number.
    """

    for i, digit in enumerate(number_str):
        if digit != '0':
            return i
    return -1


def keep_three_significant_digits(number, significant_digits=3):
    """
    Keep three significant digits without using scientific notation.
    """

    number_float = float(number)

    # Check if the number is an integer
    if number_float.is_integer():
        return int(number_float)  # Return the integer part as a string

    if number_float > 1:
        return round(number_float, significant_digits)
    else:
        # Convert the float to a string with the desired precision
        number_str = '{:.10f}'.format(number_float).rstrip('0')  # Avoid trailing zeros

        # Split the number into integer and fractional parts
        integer_part, decimal_part = number_str.split('.')
        non_zero_index = first_non_zero_index(decimal_part)
        if non_zero_index == -1:
            return round(number_float, significant_digits)
        else:
            final_decimal_part = decimal_part[:non_zero_index + significant_digits]
            final = f'{integer_part}.{final_decimal_part}'

            # Return the number with the desired number of significant digits
            return float(final)

def floatohex(numlist):
    """
        Produce hex color between red and green
    :param numlist: A list of RGB values
    :return: A list of hex value between R and G with B = 0
    """

    numlist = [-1 if i < 0 else i for i in numlist]
    rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
    resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

    return resultlist


def check_same_keys(dict1, dict2):
    """
    check if two dictionaries have the same keys at all levels
    dict1: A dictionary
    dict2: A dictionary
    return True if all keys are same, else False
    """

    # Base case: if one of the inputs is not a dictionary, return False
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False

    # Get the keys of both dictionaries
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    # Check if the keys are different
    if keys1 != keys2:
        return False

    # Recursively compare keys in nested dictionaries
    for key in keys1:
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            # If both values are dictionaries, recursively compare their keys
            if not check_same_keys(dict1[key], dict2[key]):
                return False
        else:
            # If one of the values is not a dictionary, don't compare the values
            if not isinstance(dict1[key], dict) and not isinstance(dict2[key], dict):
                continue
            else:
                return False  # If one value is a dictionary and the other is not, return False

    # If all comparisons pass, return True
    return True
