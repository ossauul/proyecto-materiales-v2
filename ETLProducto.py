import os
import glob
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import pandas as pd
from tqdm import tqdm  # For progress bars

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Dictionary for column mapping
COLUMN_MAPPINGS = {
    'hs_code': ['Código HS', 'Codigo HS', 'PARTIDA ARANCELARIA', 'HS CODE', 'PARTIDA'],
    'cantidad': ['Cantidad KG', 'KILOS NETOS', 'CANTIDAD', 'PESO BRUTO TOTAL', 
                'PESO NETO KG', 'PESO NETO', 'PESO NETO POR ITEM', 'PESO BRUTO KG', 'Gross Weight (kg)', 'KILO NETO'], 
    #'Cantidad' (KILO NETO, )
    'valor_cif': ['Valor CIF', 'VALOR CIF USD', 'US$ CIF', 'CIF USD ITEM', 'CIF U$S', 
                 'US$ CIF ITEM', 'Value of Goods, Item CIF (USD)'],
    'anio': ['AÑO', 'ANO', 'YEAR'],
    'mes': ['MES', 'MONTH'],
    'dia': ['DIA', 'DAY', 'DÍA'],
    'fecha': ['Fecha', 'FECHA', 'Fecha Embarque', 'Shipment Date', 'DATE'],
    'importador': ['PROBABLE IMPORTADOR', 'IMPORTADOR', 'Consignatario', 'CONSIGNEE'],
    'exportador': ['EMISOR', 'PROVEEDOR', 'PROBABLE PROVEEDOR', 'Expedidor', 'SHIPPER'],
    'marca': ['MARCA'],
    'origen_pais': ['PAIS DE ORIGEN', 'Item Origin', 'ORIGIN COUNTRY', 'PAÍS DE ORIGEN', 'PAÍS ORÍGEN', 'PAIS ORIGEN'],
    'adquisicion_pais': ['PAIS DE ADQUISICION', 'ACQUISITION COUNTRY', 'PAÍS DE SALIDA', 'PAIS ADQUISICION'],
    'transporte': ['VIA DE TRANSPORTE', 'Metodo de transporte', 'Método de transporte', 'WAY OF TRANSPORT', 'VIA TRANSPORTE', 'VÍA DE TRANSPORTE'],
    'port_unlanding': ['Port of Unlading (Original Format)'],
    'codigo_importador': ['Consignee Profile', 'RUT', 'TRADER ID', 'RUT PROBABLE IMPORTADOR', 'NIT IMPORTADOR', 'ID DEL IMPORTADOR', 'RUC IMPORTADOR'],
    'codigo_exportador': ['Shipper Profile'],
    'mercancia': ['Mercancías enviadas'],
    'unidad': ['UNIDAD', 'unidad', 'Unidad', 'UNIDAD COMERCIAL', 'UNIDAD DE MEDIDA', 'BULTO']
}

# HS code to Product mapping
hs_codes = {
    "LDPE": [
        "3901010", "3901100301", "39011010", "3901100000", "390110000000",
        "39011092000W", "39011030000X", "39011020900L", "39011010000C", "3901191000N",
        "39011020100T", "39011092", "390110", "390110000"
    ],
    "HDPE": [
        "3901200100", "39012000", "3901200000", "390120000000", "3901200000",
        "39012029000V", "39012019000K", "3901202100"
    ],
    "LLDPE": [
        "39014000", "3901400000", "390140000000", "39014000000K", "3901400000", "3901400100"
    ],
    "LLDPE MET": [
        "3901100302", "39011020"
    ],
    "EVA": [
        "3901300100", "39013000", "3901300000", "390130000000", "3901300000", "39013010000F", "3901300000", "3901309000"
    ],
    "OTROS PE": [
        "390190", "39019000", "3901901000", "390190000000", "3901901000", "39019090000U", "3901901000",
        "3901909000", "3901909000", "39019040000V", "3901909000", "3901900100", "3901909901",
        "3901909902", "3901909999"
    ],
    "PP HOMO": [
        "39021000", "390210000000", "3902100000", "39021010000W", "3902100000",
        "3902100100", "39021020000F", "39021001", "39021099", "3902109900"
    ],
    "PP COPO": [
        "3902300100", "3902309900", "39023000", "3902300000", "390230000000", "3902300000", "39023000000P", "3902300000", "39023001", "9802001200"
    ],
    "OTROS PP": [
        "3902909900", "39029000", "3902900000", "390290000000", "3902900000", "39029000000Z", "3902900000", "39029099", "3902900100"
    ],
    "SAN": [
        "3903200100", "39032000", "3903200000", "390320000000", "3903200000", "39032000000U", "3903200000", "7318220299"
    ],
    "ABS": [
        "3903300100", "39033000", "3903300000", "390330000000", "3903300000", "39033020000C",
        "3903300000", "3933010000T", "39033001", "3903301000"
    ],
    "PC": [
        "3907400402", "3907400499", "39074000", "3907400000", "390740000000", "3907400000", "39074090000J", "3907400000", "39074004", "3907400401",
        "3907400403"
    ],
    "POM": [
        "3907100501", "39071000", "3907100000", "390710000000", "3907100000", "39071039000B", "3907100000",
        "39071020000Y", "39071099000K", "39071091000Z", "39071049000L", "3907100502", "3907100599",
        "3907291100", "3907293900", "3907294900", "3907299000", "3907991100", "3907301900", "3907302200",
        "3907302900", "3907501000", "3907509000"
    ],  
    "PBT": [
        "3907990100", "39079100", "390790000000", "39079100000D", "3907910000",
        "3907990200", "39079900", "39079911999R", "3907990000", "3907990400",
        "39079919000C", "3907990900", "39079991000V", "3907990400"
    ],
    "OTRAS PBT": [
        "3907990300", "39079999000F", "3907990500", "3907990600", "3907990700", "3907991000", "3907999900"
    ],
    "PET": [
        "3907600100", "39076100", "3907611000", "390761000000", "3907611000", "39076100000L", "3907619000",
        "3907610100", "3907619000", "3907691000", "3907690100", "39076900", "3907691000", "390769000000",
        "39076900000G", "3907699000", "3907699900", "3907699000", "3907699000", "3907619090", "3907699090",
        "3907301100"
    ],
    "PA 6.12": [
        "3908100100", "39081000", "3908101000", "390810000000", "3908101000", "39081023000P",
        "39081101000", "3908100200", "39081029000K", "39081109000"
    ],
    "PA 6": [
        "3908100400", "39081014000M"
    ],
    "PA 12": [
        "3908100600", "39081019000A"
    ],
    "PA 6.6": [
        "3908100800", "39081025000E"
    ],
    "PA": [
        "3908900100", "3908900200", "3908900300", "39081090", "3908109000"
    ],
    "OTRAS PA": [
        "3908909900", "39089000", "390890000000", "39089020000E",
        "3908900000", "3908100300", "39089090000Y", "3908100500", "3908100700"
    ],
    "PU": [
        "3909500400", "39095000", "390950000010", "39095019000A",
        "3909500000", "3909500500", "390950000090", "3909611000P"
    ],
    "OTROS PU": [
        "3909500000", "39095010", "3909512000X", "3909509901", "39095090", "39095029000K", "3909509902",
        "39095021000Z", "3909509903", "3909509999", "3909501100", "3909501200"
    ]
}


class ETLProcessor:
    """Class for ETL processing from XLSX to CSV with specific transformations."""
    
    def __init__(self, 
                 input_path: str, 
                 output_base_path: str = "ArchivosCSV", 
                 column_mappings: Dict = COLUMN_MAPPINGS,
                 hs_product_mappings: Dict = hs_codes):
        """
        Initialize the ETL processor.
        
        Args:
            input_path: Path to the directory containing XLSX files.
            output_base_path: Base path for output CSV files.
            column_mappings: Dictionary mapping standardized column names to possible source column names.
            hs_product_mappings: Dictionary mapping HS codes to product names.
        """
        self.input_path = input_path
        self.output_base_path = output_base_path
        self.column_mappings = column_mappings
        self.hs_product_mappings = hs_product_mappings
        
        # Create output directory if it doesn't exist
        os.makedirs(output_base_path, exist_ok=True)
    
    def create_folder(self, path: str) -> None:
        """Create a folder if it doesn't exist."""
        os.makedirs(path, exist_ok=True)
    
    def read_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        Read an Excel file into a dictionary of DataFrames.
        
        Args:
            file_path: Path to the Excel file.
            
        Returns:
            Dictionary of DataFrames where keys are sheet names.
        """
        try:
            return pd.read_excel(file_path, sheet_name=None)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {}
    
    def get_country_from_path(self, file_path: str) -> str:
        """
        Extract country name from file path.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Country name extracted from the path.
        """
        try:
            return file_path.split(os.sep)[-2]  # Country folder
        except IndexError:
            logger.warning(f"Could not extract country from path {file_path}, using 'unknown'")
            return "unknown"
    
    def find_matching_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[pd.Series]:
        """
        Find a column in the DataFrame based on a list of possible column names.
        
        Args:
            df: Input DataFrame.
            possible_names: List of possible column names to search for.
            
        Returns:
            Column from DataFrame if found, None otherwise.
        """
        for name in possible_names:
            if name in df.columns:
                return df[name]
        return None
    
    def map_hs_code_to_product(self, hs_code: Union[str, int, float]) -> str:
        """
        Map HS code to product name based on a dictionary of HS code lists.
        Uses flexible matching to handle variations in HS code formats.

        Args:
            hs_code: HS code to map.

        Returns:
            Corresponding product name or 'Desconocido' if not found.
        """
        if pd.isna(hs_code):
            return "Desconocido"

        # Convert to string and clean
        hs_str = str(hs_code).strip().replace(".", "").replace("-", "").replace(" ", "")
        
        # Remove trailing zeros and handle float conversion issues
        if hs_str.endswith('.0'):
            hs_str = hs_str[:-2]
        
        # Try exact match first
        for product, codes in self.hs_product_mappings.items():
            if hs_str in codes:
                return product
        
        # Try partial matches - check if HS code starts with any of the mapped codes
        for product, codes in self.hs_product_mappings.items():
            for code in codes:
                # Clean the code from dictionary
                clean_code = str(code).strip().replace(".", "").replace("-", "").replace(" ", "")
                
                # Try different matching strategies
                if (hs_str == clean_code or 
                    hs_str.startswith(clean_code) or 
                    clean_code.startswith(hs_str)):
                    return product
        
        # If still no match, try with first 6, 8, or 10 digits
        for length in [10, 8, 6]:
            if len(hs_str) >= length:
                truncated_hs = hs_str[:length]
                for product, codes in self.hs_product_mappings.items():
                    for code in codes:
                        clean_code = str(code).strip().replace(".", "").replace("-", "").replace(" ", "")
                        if len(clean_code) >= length and truncated_hs == clean_code[:length]:
                            return product

        return "Desconocido"
    
    
    def convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to a single datetime column.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            DataFrame with standardized date column.
        """
        # Find year, month, day columns
        year_col = self.find_matching_column(df, self.column_mappings.get('anio', []))
        month_col = self.find_matching_column(df, self.column_mappings.get('mes', []))
        day_col = self.find_matching_column(df, self.column_mappings.get('dia', []))
        
        # If we have all three components, create a date column
        if year_col is not None and month_col is not None and day_col is not None:
            # Create temporary columns with standardized names
            df['_year'] = year_col
            df['_month'] = month_col
            df['_day'] = day_col
            
            # Convert to date format, handling errors
            try:
                df['fecha'] = pd.to_datetime(
                    df[['_year', '_month', '_day']].astype(str).agg('-'.join, axis=1), 
                    errors='coerce'
                )
                # Drop temporary columns
                df.drop(['_year', '_month', '_day'], axis=1, inplace=True)
            except Exception as e:
                logger.warning(f"Error converting date components: {e}")
        
        # If there's already a date column, try to standardize it
        else:
            date_col = self.find_matching_column(df, self.column_mappings.get('fecha', []))
            if date_col is not None:
                try:
                    df['fecha'] = pd.to_datetime(date_col, errors='coerce')
                except Exception as e:
                    logger.warning(f"Error converting date column: {e}")
        
        return df
    
    def map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract only the columns specified in the column mappings dictionary.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            DataFrame with only the specified mapped columns.
        """
        result_df = pd.DataFrame()
        
        # For each target column, try to find a matching source column
        for target_col, source_cols in self.column_mappings.items():
            matched_col = self.find_matching_column(df, source_cols)
            if matched_col is not None:
                result_df[target_col] = matched_col
        
        return result_df
    
    def process_excel_file(self, file_path: str) -> None:
        """
        Process an Excel file and save each sheet as a CSV.
        
        Args:
            file_path: Path to the Excel file.
        """
        country = self.get_country_from_path(file_path)
        logger.info(f"Processing file: {file_path} for country: {country}")
        
        # Create country folder for output
        country_output_path = os.path.join(self.output_base_path, country)
        self.create_folder(country_output_path)
        
        # Read Excel file
        sheets_dict = self.read_excel_file(file_path)
        if not sheets_dict:
            logger.error(f"No data found in {file_path}")
            return
        
        # Get filename without extension
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        
        # Process each sheet
        for idx, (sheet_name, df) in enumerate(sheets_dict.items()):
            try:
                if df.empty:
                    logger.warning(f"Empty sheet: {sheet_name} in {file_path}")
                    continue
                
                # Extract only the mapped columns
                processed_df = self.map_columns(df)
                
                if processed_df.empty:
                    logger.warning(f"No matching columns found in sheet: {sheet_name} in {file_path}")
                    continue
                
                # Convert date columns
                processed_df = self.convert_date_columns(processed_df)
                
                # Add country column
                processed_df['pais'] = country
                
                # Map HS code to product if hs_code column exists
                if 'hs_code' in processed_df.columns:
                    processed_df['producto'] = processed_df['hs_code'].apply(self.map_hs_code_to_product)
                
                # Save as CSV
                output_filename = f"{country}_{base_filename}_{sheet_name}_{idx}.csv"
                output_path = os.path.join(country_output_path, output_filename)
                
                processed_df.to_csv(output_path, index=False)
                logger.info(f"Saved: {output_path} with {len(processed_df.columns)} columns")
                
                # Log the columns that were successfully mapped
                logger.info(f"Columns in output: {', '.join(processed_df.columns)}")
            
            except Exception as e:
                logger.error(f"Error processing sheet {sheet_name} in {file_path}: {e}")
    
    def process_all_files(self) -> None:
        """Process all Excel files in the input directory recursively."""
        # Find all Excel files recursively
        excel_files = glob.glob(os.path.join(self.input_path, '**', '*.xlsx'), recursive=True)
        
        if not excel_files:
            logger.warning(f"No Excel files found in {self.input_path}")
            return
        
        logger.info(f"Found {len(excel_files)} Excel files to process")
        
        # Process each file with progress bar
        for file_path in tqdm(excel_files, desc="Processing files"):
            self.process_excel_file(file_path)
        
        logger.info("ETL process completed successfully")


if __name__ == "__main__":
    # Example usage
    input_path = r"C:\\Temp\\Proyecto materiales\\temp\\PorProducto"
    output_path = "ArchivosCSV"
    
    processor = ETLProcessor(input_path=input_path, output_base_path=output_path)
    processor.process_all_files()