import logging

import os
import csv


def get_temp_folder(dir_name='temp_files', fold_name='temp'):
    """
    Возвращает местоположение временной папки
    и создает ее при необходимости

    Parameters
    ----------
    temp_dir_name : str, optional
        Name of temporary folder (default is 'temp')

    Returns
    -------
    temp_dir_path : str
        absolute path to temporary folder
    """
    temp_dir_path = os.path.join(os.getcwd(), dir_name, fold_name)
    if not os.path.isdir(temp_dir_path):
        os.mkdir(temp_dir_path)
    return temp_dir_path


def get_csv_file(data, name_file):
    file = str(name_file)
    try:
        with open(file, 'w', newline='') as file_w:
            csv_writer = csv.writer(
                file_w, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data)

    except csv.Error:
        print(f"Ошибка в CSV-файле на строке {reader.line_num}: {csv.Error}")
    except UnicodeDecodeError:
        print("Ошибка декодирования. Возможно, файл имеет другую кодировку.")
    except FileNotFoundError:
        print("Файл не найден.")
    except IOError:
        print(f"Ошибка ввода-вывода при работе с файлом. {IOError}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")


def get_txt_file(data, name_file):

    pass
