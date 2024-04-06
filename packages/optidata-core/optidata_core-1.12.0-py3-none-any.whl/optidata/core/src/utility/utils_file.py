import logging
import os
import time

import numpy as np
# from numba import cuda, typed
import pandas as pd
import vaex
from joblib import Parallel, delayed
from pandas.errors import InvalidIndexError

from ..config import constantes
from ..config import settings
from ..enums.enums import DataTypeEnum
from ..utility.utils import get_start_end_day_month

# import cudf
# import torch

# Configura las opciones de Pandas para mejorar el rendimiento
pd.options.mode.chained_assignment = None  # Deshabilita las advertencias de asignaciones
chunk_size: int = 100000  # Tamaño de cada fragmento de lectura

# Item en donde se produce el error en el proceso de Consolidación
item_error = ''

# Establecer el formato de moneda local
# locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')

log = logging.getLogger(__name__)


# Funciones Privadas
def __getfile_from_path(sub_path: str, filename: str, ext: str):
    return os.path.join(settings.FLASK_UPLOAD_FOLDER, sub_path, f'{filename}{ext}')


# @cuda.jit(target="cuda")
def __get_columns_dataframe(file, ext: str):
    cols = None
    if ext == f'.{settings.FILE_EXT_TXT}':
        pass
    elif ext == f'.{settings.FILE_EXT_CSV}':
        cols = pd.read_csv(file, sep=settings.CSV_SEPARATOR).to_dict()
    elif ext == f'.{settings.FILE_EXT_XLS}' or ext == f'.{settings.FILE_EXT_XLSX}':
        cols = pd.read_excel(file.read(), nrows=1).to_dict()
    else:
        pass

    return __remove_spaces_name(cols)


# @cuda.jit(target="cuda")
def __get_dataframe(ext: str, file_name: str, path_file: str):
    df = pd.DataFrame()
    if ext == f'.{settings.FILE_EXT_TXT}':
        pass
    elif ext == f'.{settings.FILE_EXT_CSV}':
        df = pd.read_csv(path_file, sep=settings.CSV_SEPARATOR, dayfirst=True)
    elif ext == f'.{settings.FILE_EXT_XLS}' or ext == f'.{settings.FILE_EXT_XLSX}':
        dfs = __read_excel(path_file)
        df = pd.concat(dfs, ignore_index=True)
    else:
        df = vaex.open(path=f'{path_file}', group=f'{file_name}').to_pandas_df()

    return df


def __read_excel(path_file: str):
    xls = pd.ExcelFile(path_file)
    nombres_hojas = xls.sheet_names
    dfs = Parallel(n_jobs=-1)(delayed(__loop_read_excel)(path_file, hoja) for hoja in nombres_hojas)
    return dfs


# @cuda.jit(target="cuda")
def __loop_read_excel(file, sheet_name):
    return pd.read_excel(file, sheet_name=sheet_name)


# @cuda.jit(target="cuda")
def __normalized_data(df, key: str, type_data: str):
    if type_data == DataTypeEnum.DATE.value:
        df[f'{key}'] = pd.to_datetime(df[f'{key}'], format='mixed')
    elif type_data == DataTypeEnum.STRING.value:
        df[f'{key}'] = df[f'{key}'].fillna('-').astype(str).apply(lambda x: x.strip())
    elif type_data == DataTypeEnum.INTEGER.value:
        df[f'{key}'] = df[f'{key}'].astype(float).astype('Int64').fillna(0)
    elif type_data == DataTypeEnum.FLOAT.value:
        df[f'{key}'] = df[f'{key}'].astype(float).astype('Int64').fillna(0)
    else:
        df[f'{key}'] = df[f'{key}'].fillna('-').astype(str).apply(lambda x: x.strip())

    return df[f'{key}']


def __remove_spaces_name_columns(df):
    trim_name_columns = []
    for col in df.columns:
        trim_name_columns.append(col.strip())
    df.columns = trim_name_columns
    return df


def __remove_spaces_name(cols):
    trim_name_columns = []
    for col in cols:
        trim_name_columns.append(col.strip())
    return trim_name_columns


def __change_data_nat_nan_to_str(df):
    for col in df.columns:
        if df[col].dtype == np.dtype('object'):
            df[col] = df[col].where(df[col].notnull(), '')
            df[col] = df[col].where(df[col].notna(), '')
            df[col] = df[col].astype("string")
        elif df[col].dtype == np.dtype('datetime64[ns]'):
            df[col] = df[col].astype(object).where(df[col].notnull(), '')
            df[col] = df[col].astype(object).where(df[col].notna(), '')
            df[col] = df[col].astype("string")
        elif df[col].dtype == np.dtype('float64') or df[col].dtype == np.dtype('int64'):
            df[col] = df[col].where(df[col].notnull(), 0)
            df[col] = df[col].where(df[col].notna(), 0)
            df[col] = df[col].astype("int64")

    return df


def __create_index_in_df(df, index_key: str, cols_list: list):
    init = False
    for col in cols_list:
        if not init:
            df[f'{index_key}'] = df[f'{col}'].fillna(0).astype(str).apply(lambda x: x.strip())
            init = True
        else:
            df[f'{index_key}'] = df[f'{index_key}'] + df[f'{col}'].fillna(0).astype(str).apply(lambda x: x.strip())

    if init:
        df.set_index(f'{index_key}', inplace=True)
    return df


def __sort_datetime_data(df, column_name: str):
    return df.sort_values(by=[f'{column_name}'])


def __convert_datetime_to_str(df, key: str, type_data: str):
    if type_data == DataTypeEnum.DATE.value:
        df[f'{key}'] = df[f'{key}'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df[f'{key}']


def __get_duplicate(df):
    return df.loc[df.duplicated(keep=False)]


def __delete_duplicate(df, columns):
    return df.drop_duplicates(columns)


def __concat_data(df_origin, df_compared, union_columns=False):
    df_origin = df_origin.loc[~df_origin.index.duplicated(keep='first')]
    df_compared = df_compared.loc[~df_compared.index.duplicated(keep='first')]
    return pd.concat([df_origin, df_compared], axis=union_columns)


# @cuda.jit(target="cuda")
def __merge_data(df_origin, df_compared, name_index, is_common=True):
    _suffixes = ('_primary', '_external')
    if is_common:
        df = pd.merge(
            df_origin,
            df_compared,
            on=name_index,
            suffixes=_suffixes,
            how='inner'
        )
    else:
        df = pd.merge(
            df_origin,
            df_compared,
            on=name_index,
            suffixes=_suffixes,
            how='outer',
            indicator=True
        ).query("_merge != 'both'")

    return df


def __get_totals_dataframe_by_column(df, key: str):
    return df[f'{key}'].sum()


def __get_data_filter_dates(
        df,
        column,
        start_day,
        end_day,
        month: int,
        year: int):
    if len(f'{month}') < 2:
        m = f'0{month}'
    else:
        m = month

    init_date = pd.to_datetime(f'{year}-{m}-0{start_day}').date()
    finish_date = pd.to_datetime(f'{year}-{m}-{end_day}').date()

    return df[
        (pd.to_datetime(df[f'{column}']).dt.date >= init_date) &
        (pd.to_datetime(df[f'{column}']).dt.date <= finish_date)
        ]


def __add_column_description(df_c, df_nc, idx_columns):
    msg_diff = ""
    msg_part = "en la columna"
    is_more = False
    for col in idx_columns:
        if not np.where(df_c[f'{col}_primary'] == df_nc[f'{col}']):
            if len(msg_diff) == 0:
                msg_diff = f"{col}"
            else:
                msg_diff += f", {col}"
                is_more = True

    if is_more:
        msg_part = "en las columnas"
    return f"Existe una diferencia {msg_part} {msg_diff}." if len(msg_diff) > 0 else ""


##########################################
# Functions Public's
##########################################
def extract_headers_file(file, ext: str):
    columns_list = []
    try:
        df_columns = __get_columns_dataframe(file, ext)

        if df_columns:
            for column in df_columns:
                columns_list.append({
                    "col_name": f"{column}",
                    "col_used": False,
                    "col_type": "",
                    "col_norm": False
                })

            return columns_list
    except Exception as e:
        logging.exception(e)

    return columns_list


def create_file_from_dataframe(df, name_file: str):
    df.to_csv(f"{settings.FLASK_EXPORT_FOLDER}/{name_file}.csv", index=True, sep=';', encoding='utf-8-sig')


# @cuda.jit(target="cuda")
def execute_process_conciliation(data: list, doc_id: str):
    global item_error
    result_process = {}
    try:
        data_item = data[0]
        # Definición de variables base
        columns_df = __remove_spaces_name(data_item['columns_df'])
        sub_path = os.path.join(
            f'{data_item["internal"]["partner"]}',
            f'{data_item["internal"]["year"]}',
            f'{data_item["internal"]["month"]}'
        )

        # Carga de datos
        # Proceso Primary v/s External
        file_name = f"{data_item['internal']['filename']}{data_item['internal']['extension']}"
        item_error = f"Error lectura archivo: {file_name}"
        df_original = __get_dataframe(
            constantes.H5_FILE,  # data_item['internal']['extension'],
            data_item['internal']['filename'],
            __getfile_from_path(sub_path, data_item['internal']['filename'], constantes.H5_FILE)
        )

        file_name = f"{data_item['external'][0]['filename']}{data_item['external'][0]['extension']}"
        item_error = f"Error lectura archivo: {file_name}"
        df_compared = __get_dataframe(
            constantes.H5_FILE,  # data_item['external'][0]['extension'],
            data_item['external'][0]['filename'],
            __getfile_from_path(sub_path, data_item['external'][0]['filename'], constantes.H5_FILE)
        )

        # Obtiene fechas para proceso de filtrado de data para ejecución de consolidación de datos
        start_day, end_day = get_start_end_day_month(
            int(data_item["internal"]["month"]),
            int(data_item["internal"]["year"])
        )

        # Filtra datos por campo fecha
        date_column_filter = data_item['columns_date'][0]
        df_original = __get_data_filter_dates(
            df_original,
            date_column_filter,
            start_day,
            end_day,
            int(data_item["internal"]["month"]),
            int(data_item["internal"]["year"])
        )

        # df_compared = __get_data_filter_dates( df_compared, date_column_filter, start_day, end_day, int(data_item[
        # "internal"]["month"]), int(data_item["internal"]["year"]) )

        # TODO: Acá debiese filtrarse la información con
        #  respecto a la fecha definida dentro del ciclo generado -->
        #  df.loc[df['column_name'] == some_value]

        # Normaliza nombres de columnas / Eliminación de espacios en nombres
        item_error = f"Error al eliminar los espacios en las cabeceras fuente primaria"
        df_original = __remove_spaces_name_columns(df_original)
        item_error = f"Error al eliminar los espacios en las cabeceras fuente externa: {df_compared}"
        df_compared = __remove_spaces_name_columns(df_compared)

        # Normalización de los datos
        item_error = f"Error al normalizar los datos"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_original[f'{key}'] = __normalized_data(df_original, key, value)
            df_compared[f'{key}'] = __normalized_data(df_compared, key, value)

        # Definición de Índices
        item_error = f"Error al definir los indices"
        df_original = __create_index_in_df(df_original, 'idx', data_item['columns_index_df'])
        df_compared = __create_index_in_df(df_compared, 'idx', data_item['columns_index_df'])

        # Definición de campos a considerar dentro del DataFrame
        item_error = f"Error al definir los campos a usar en la consolidación"
        df_original = df_original[columns_df]
        df_compared = df_compared[columns_df]

        # Se ordenan los datos por fecha
        item_error = f"Error al ordenar la data por campo fecha"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            if value == 'datetime':
                df_original = __sort_datetime_data(df_original, key)
                df_compared = __sort_datetime_data(df_compared, key)

        # Se extraen los registros duplicados de cada origen
        item_error = f"Error al extraen los registros duplicados"
        df_duplicated_original = __get_duplicate(df_original)
        df_duplicated_compared = __get_duplicate(df_compared)

        # Elimina los registros duplicados
        item_error = f"Error al eliminar los registros duplicados"
        df_original = __delete_duplicate(df_original, data_item['columns_index_df'])
        df_compared = __delete_duplicate(df_compared, data_item['columns_index_df'])

        # Identificación de las transacciones conciliadas
        item_error = f"Error al identificar las transacciones conciliadas"
        df_reconciled = __merge_data(df_original, df_compared, 'idx')

        # Identificación de las transacciones no conciliadas
        item_error = f"Error al identificar las transacciones no conciliadas"
        df_unreconciled = __merge_data(df_reconciled, df_original, 'idx', False)

        # Identificación de las transacciones duplicadas
        item_error = f"Error al identificar las transacciones duplicadas"
        df_duplicated = __concat_data(df_duplicated_original, df_duplicated_compared, False)

        # Convierte campos datetime a str para conversion a JSON
        item_error = f"Error al tratar de convertir datos a texto"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_reconciled[f'{key}_primary'] = __convert_datetime_to_str(df_reconciled, f'{key}_primary', value)
            df_reconciled[f'{key}_external'] = __convert_datetime_to_str(df_reconciled, f'{key}_external', value)
            df_unreconciled[f'{key}_primary'] = __convert_datetime_to_str(df_unreconciled, f'{key}_primary', value)
            df_unreconciled[f'{key}_external'] = __convert_datetime_to_str(df_unreconciled, f'{key}_external', value)

            if key in df_reconciled:
                df_reconciled[f'{key}'] = __convert_datetime_to_str(df_reconciled, f'{key}', value)

            if key in df_unreconciled:
                df_unreconciled[f'{key}'] = __convert_datetime_to_str(df_unreconciled, f'{key}', value)

            if key in df_duplicated:
                df_duplicated[f'{key}'] = __convert_datetime_to_str(df_duplicated, f'{key}', value)

        # Normalización de campos vacíos (nulos)
        item_error = f"Error al tratar de normalizar campos vacíos (nulos)"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_reconciled[f'{key}_primary'] = __normalized_data(df_reconciled, f'{key}_primary', value)
            df_reconciled[f'{key}_external'] = __normalized_data(df_reconciled, f'{key}_external', value)
            df_unreconciled[f'{key}_primary'] = __normalized_data(df_unreconciled, f'{key}_primary', value)
            df_unreconciled[f'{key}_external'] = __normalized_data(df_unreconciled, f'{key}_external', value)
            df_duplicated[f'{key}'] = __normalized_data(df_duplicated, f'{key}', value)

        df_reconciled = __change_data_nat_nan_to_str(df_reconciled)
        df_unreconciled = __change_data_nat_nan_to_str(df_unreconciled)
        df_duplicated = __change_data_nat_nan_to_str(df_duplicated)

        # Agrega columna con descripción para identificación de problema en no conciliados.
        # __add_column_description(df_reconciled, df_unreconciled, data_item['columns_index_df'])

        # Generación de totales
        total_reconciled = 0
        total_unreconciled = 0
        total_duplicated = 0
        if len(data_item['columns_amount']) > 0:
            amount_column = data_item['columns_amount'][0]

            df_reconciled[f"{amount_column}_external"] = pd.to_numeric(df_reconciled[f"{amount_column}_external"])
            df_unreconciled[f"{amount_column}"] = pd.to_numeric(df_unreconciled[f"{amount_column}"])
            df_duplicated[f"{amount_column}"] = pd.to_numeric(df_duplicated[f"{amount_column}"])

            total_reconciled = df_reconciled[f"{amount_column}_external"].sum()
            total_unreconciled = df_unreconciled[f"{amount_column}"].sum()
            total_duplicated = df_duplicated[f"{amount_column}"].sum()

        # Se genera diccionario y se agrega campo de referencia para búsqueda
        item_error = f"Error al tratar de generar salida datos (Conciliados)"
        df_reconciled = df_reconciled.to_dict('records')
        idx = 1
        for df_rec in df_reconciled:
            df_rec[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_rec['item'] = idx
            df_rec['type_process'] = 'primary'
            idx += 1

        item_error = f"Error al tratar de generar salida datos (No Conciliados)"
        df_unreconciled = df_unreconciled.to_dict('records')
        idx = 1
        for df_unrec in df_unreconciled:
            df_unrec[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_unrec['item'] = idx
            df_unrec['type_process'] = 'primary'
            idx += 1

        df_duplicated = df_duplicated.to_dict('records')
        item_error = f"Error al tratar de generar salida datos (Duplicados)"
        idx = 1
        for df_dup in df_duplicated:
            df_dup[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_dup['item'] = idx
            df_dup['type_process'] = 'primary'
            idx += 1

        df_duplicated_compared = df_duplicated_compared.to_dict('records')
        item_error = f"Error al tratar de generar salida datos (Duplicados.)"
        idx = 1
        for df_dup_com in df_duplicated_compared:
            df_dup_com[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_dup_com['item'] = idx
            df_dup_com['type_process'] = 'primary'
            idx += 1

        result_process["primary-process"] = {
            "total_reconciled": total_reconciled,
            "data_reconciled": df_reconciled,
            "total_unreconciled": total_unreconciled,
            "data_unreconciled": df_unreconciled,
            "data_duplicated": df_duplicated,
            "total_duplicated": total_duplicated
        }

        # Proceso External v/s Primary
        file_name = f"{data_item['external'][0]['filename']}{data_item['external'][0]['extension']}"
        item_error = f"Error lectura archivo: {file_name}"
        df_original = __get_dataframe(
            constantes.H5_FILE,  # data_item['external'][0]['extension'],
            data_item['external'][0]['filename'],
            __getfile_from_path(sub_path, data_item['external'][0]['filename'], constantes.H5_FILE)
        )

        file_name = f"{data_item['internal']['filename']}{data_item['internal']['extension']}"
        item_error = f"Error lectura archivo: {file_name}"
        df_compared = __get_dataframe(
            constantes.H5_FILE,  # data_item['internal']['extension'],
            data_item['internal']['filename'],
            __getfile_from_path(sub_path, data_item['internal']['filename'], constantes.H5_FILE)
        )

        # Normaliza nombres de columnas / Eliminación de espacios en nombres
        item_error = f"Error al eliminar los espacios en las cabeceras fuente primaria"
        df_original = __remove_spaces_name_columns(df_original)
        item_error = f"Error al eliminar los espacios en las cabeceras fuente externa"
        df_compared = __remove_spaces_name_columns(df_compared)

        # Normalización de los datos
        item_error = f"Error al normalizar los datos"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_original[f'{key}'] = __normalized_data(df_original, key, value)
            df_compared[f'{key}'] = __normalized_data(df_compared, key, value)

        # Definición de Índices
        item_error = f"Error al definir los indices"
        df_original = __create_index_in_df(df_original, 'idx', data_item['columns_index_df'])
        df_compared = __create_index_in_df(df_compared, 'idx', data_item['columns_index_df'])

        # Definición de campos a considerar dentro del DataFrame
        item_error = f"Error al definir los campos a usar en la consolidación"
        df_original = df_original[columns_df]
        df_compared = df_compared[columns_df]

        # Se ordenan los datos por fecha
        item_error = f"Error al ordenar la data por campo fecha"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            if value == 'datetime':
                df_original = __sort_datetime_data(df_original, key)
                df_compared = __sort_datetime_data(df_compared, key)

        # Se extraen los registros duplicados de cada origen
        item_error = f"Error al extraen los registros duplicados"
        df_duplicated_original = __get_duplicate(df_original)
        df_duplicated_compared = __get_duplicate(df_compared)

        # Elimina los registros duplicados
        item_error = f"Error al eliminar los registros duplicados"
        df_original = __delete_duplicate(df_original, data_item['columns_index_df'])
        df_compared = __delete_duplicate(df_compared, data_item['columns_index_df'])

        # Identificación de las transacciones conciliadas
        item_error = f"Error al identificar las transacciones conciliadas"
        df_reconciled = __merge_data(df_original, df_compared, 'idx')

        # Identificación de las transacciones no conciliadas
        item_error = f"Error al identificar las transacciones no conciliadas"
        df_unreconciled = __merge_data(df_reconciled, df_original, 'idx', False)

        # Identificación de las transacciones duplicadas
        item_error = f"Error al identificar las transacciones duplicadas"
        df_duplicated = __concat_data(df_duplicated_original, df_duplicated_compared, False)

        # Convierte campos datetime a str para conversion a JSON
        item_error = f"Error al tratar de convertir datos a texto"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_reconciled[f'{key}_primary'] = __convert_datetime_to_str(df_reconciled, f'{key}_primary', value)
            df_reconciled[f'{key}_external'] = __convert_datetime_to_str(df_reconciled, f'{key}_external', value)
            df_unreconciled[f'{key}_primary'] = __convert_datetime_to_str(df_unreconciled, f'{key}_primary', value)
            df_unreconciled[f'{key}_external'] = __convert_datetime_to_str(df_unreconciled, f'{key}_external', value)

            if key in df_reconciled:
                df_reconciled[f'{key}'] = __convert_datetime_to_str(df_reconciled, f'{key}', value)

            if key in df_unreconciled:
                df_unreconciled[f'{key}'] = __convert_datetime_to_str(df_unreconciled, f'{key}', value)

            if key in df_duplicated:
                df_duplicated[f'{key}'] = __convert_datetime_to_str(df_duplicated, f'{key}', value)

        # Normalización de campos vacíos (nulos)
        item_error = f"Error al tratar de normalizar campos vacíos (nulos)"
        for key, value in data_item['columns_normalized'].items():
            key = key.strip()
            df_reconciled[f'{key}_primary'] = __normalized_data(df_reconciled, f'{key}_primary', value)
            df_reconciled[f'{key}_external'] = __normalized_data(df_reconciled, f'{key}_external', value)
            df_unreconciled[f'{key}_primary'] = __normalized_data(df_unreconciled, f'{key}_primary', value)
            df_unreconciled[f'{key}_external'] = __normalized_data(df_unreconciled, f'{key}_external', value)
            df_duplicated[f'{key}'] = __normalized_data(df_duplicated, f'{key}', value)

        df_reconciled = __change_data_nat_nan_to_str(df_reconciled)
        df_unreconciled = __change_data_nat_nan_to_str(df_unreconciled)
        df_duplicated = __change_data_nat_nan_to_str(df_duplicated)

        # Generación de totales
        total_reconciled = 0
        total_unreconciled = 0
        total_duplicated = 0
        if len(data_item['columns_amount']) > 0:
            amount_column = data_item['columns_amount'][0]

            df_reconciled[f"{amount_column}_external"] = pd.to_numeric(df_reconciled[f"{amount_column}_external"])
            df_unreconciled[f"{amount_column}"] = pd.to_numeric(df_unreconciled[f"{amount_column}"])
            df_duplicated[f"{amount_column}"] = pd.to_numeric(df_duplicated[f"{amount_column}"])

            total_reconciled = df_reconciled[f"{amount_column}_external"].sum()
            total_unreconciled = df_unreconciled[f"{amount_column}"].sum()
            total_duplicated = df_duplicated[f"{amount_column}"].sum()

        # Se genera diccionario y se agrega campo de referencia para búsqueda
        item_error = f"Error al tratar de generar salida datos (Conciliados)"
        df_reconciled = df_reconciled.to_dict('records')
        idx = 1
        for df_rec in df_reconciled:
            df_rec[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_rec['item'] = idx
            df_rec['type_process'] = 'secondary'
            idx += 1

        item_error = f"Error al tratar de generar salida datos (No Conciliados)"
        df_unreconciled = df_unreconciled.to_dict('records')
        idx = 1
        for df_unrec in df_unreconciled:
            df_unrec[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_unrec['item'] = idx
            df_unrec['type_process'] = 'secondary'
            idx += 1

        df_duplicated = df_duplicated.to_dict('records')
        item_error = f"Error al tratar de generar salida datos (Duplicados)"
        idx = 1
        for df_dup in df_duplicated:
            df_dup[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_dup['item'] = idx
            df_dup['type_process'] = 'secondary'
            idx += 1

        df_duplicated_compared = df_duplicated_compared.to_dict('records')
        item_error = f"Error al tratar de generar salida datos (Duplicados.)"
        idx = 1
        for df_dup_com in df_duplicated_compared:
            df_dup_com[f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id'] = doc_id
            df_dup_com['item'] = idx
            df_dup_com['type_process'] = 'secondary'
            idx += 1

        result_process["secondary-process"] = {
            "total_reconciled": total_reconciled,
            "data_reconciled": df_reconciled,
            "total_unreconciled": total_unreconciled,
            "data_unreconciled": df_unreconciled,
            "data_duplicated": df_duplicated,
            "total_duplicated": total_duplicated
        }

        return result_process

    except TypeError as te:
        log.error(te)
        return {
            "msg": f"{item_error}.\nError en el tipo de datos: {te}"
        }
    except KeyError as te:
        log.error(te)
        return {
            "msg": f"{item_error}.\nClave no existe: {te}."
        }
    except AttributeError as te:
        log.error(te)
        return {
            "msg": f"{item_error}.\nError en el atributo: {te}"
        }
    except InvalidIndexError as te:
        log.error(te)
        return {
            "msg": f"{item_error}.\nError en la definición del indice: {te}"
        }
    except ValueError as te:
        log.error(te)
        return {
            "msg": f"{item_error}.\nValor erróneo: {te}"
        }
    except Exception as e:
        log.exception(e)
        return {
            "msg": f"{item_error}.\nError: {e}"
        }


def convert_file_to_hfs5(path_file, file_name, extension_file):
    start = time.time()
    path_file_hfs5 = __getfile_from_path(path_file, file_name, constantes.H5_FILE)
    path_file_origin = __getfile_from_path(path_file, file_name, extension_file)

    # Carga de datos
    if extension_file == f'.{settings.FILE_EXT_CSV}':
        df = __get_dataframe(extension_file, file_name, path_file_origin)
    else:
        dfs = __read_excel(path_file_origin)
        df = pd.concat(dfs, ignore_index=True)

    df = df.astype(str)
    df = __remove_spaces_name_columns(df)

    # Convertir el DataFrame de Pandas a un DataFrame de Vaex
    df_vaex = vaex.from_pandas(df, copy_index=False)

    # Convertir todos los datos en cadenas de texto
    for columna in df_vaex.get_column_names():
        df_vaex[columna] = df_vaex[columna].astype('str')

    # Guardar el DataFrame de Vaex en formato HDF5
    df_vaex.export_hdf5(path_file_hfs5, mode='w', group=f'{file_name}')

    end = time.time()
    print(round((end - start) / 60, 2))
    try:
        os.remove(path_file_origin)
    except OSError:
        pass
