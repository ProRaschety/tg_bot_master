import logging

import os
import csv
import io
import pandas as pd

log = logging.getLogger(__name__)


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


def get_csv_bt_file(data):
    output = io.StringIO()
    with output as file_w:
        writer = csv.writer(file_w, dialect='excel', delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        bite_file = output.getvalue().encode("ANSI")
    return bite_file


def get_xlsx_bt_file(data):
    writer = pd.ExcelWriter('simple-report.xlsx', engine='xlsxwriter')
    df.to_excel(writer, index=False)
    df_footer.to_excel(writer, startrow=6, index=False)
    writer.save()
    output = io.StringIO()
    with output as file_w:
        writer = csv.writer(file_w, dialect='excel', delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        bite_file = output.getvalue().encode("ANSI")
    return bite_file


def get_picture_filling(file_path):
    buffer = io.BytesIO()
    file = file_path
    with open(file, 'rb') as f:
        file_r = f.read()
        buffer.write(file_r)
    buffer.seek(0)
    bite_pic = buffer.getvalue()
    buffer.close()
    return bite_pic


def get_dict(list_: list):
    first, *rest = list_
    return {first: get_dict(rest)} if rest else first
