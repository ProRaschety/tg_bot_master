import logging

import os
import csv


def get_temp_folder(temp_dir_name='temp'):
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
    temp_dir_path = os.path.join(os.getcwd(), temp_dir_name)
    if not os.path.isdir(temp_dir_path):
        os.mkdir(temp_dir_path)
    return temp_dir_path


def send_csv_file(data, file_name):
    file = str(file_name)
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
