import pandas as pd


def get_excel_sheets(uploaded_file):
    """
    Devuelve la lista de hojas disponibles en un archivo Excel.
    """
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        return excel_file.sheet_names
    except Exception:
        return []


def load_financial_file(uploaded_file, sheet_name=None):
    """
    Carga un archivo financiero en formato CSV o Excel.
    Devuelve:
    - dataframe
    - metadata
    """

    if uploaded_file is None:
        raise ValueError("No se recibió ningún archivo.")

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_type = "CSV"
        selected_sheet = None

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        file_type = "Excel"
        selected_sheet = sheet_name

    else:
        raise ValueError("Formato no soportado. Usá archivos .xlsx o .csv.")

    df = clean_basic_dataframe(df)

    metadata = {
        "file_name": uploaded_file.name,
        "file_type": file_type,
        "sheet_name": selected_sheet,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns)
    }

    return df, metadata


def clean_basic_dataframe(df):
    """
    Limpieza básica inicial:
    - elimina filas y columnas completamente vacías
    - normaliza nombres de columnas
    - elimina columnas duplicadas por nombre
    """

    df = df.copy()

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    df.columns = [
        str(col).strip().replace("\n", " ").replace("\r", " ")
        for col in df.columns
    ]

    df = df.loc[:, ~df.columns.duplicated()]

    return df
