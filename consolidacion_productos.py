import os
import pandas as pd
import re
import unicodedata
import logging

# --- Configuración ---
ROOT_DIR = 'C:\Temp\Proyecto materiales\ArchivosCSV' # Directorio raíz que contiene las carpetas por país
# Asegúrate de que estos nombres coincidan EXACTAMENTE con los de tus columnas CSV
COLUMNS_TO_STANDARDIZE_NAMES = ['importador', 'exportador', 'origen_pais', 'transporte', 'marca', 'unidad'] 
# Agrega aquí TODAS las columnas que necesitan limpieza de acentos y caracteres especiales
COLUMNS_TO_REMOVE_ACCENTS = ['importador', 'exportador', 'origen_pais', 'transporte', 'marca', 'unidad']  # ¡AJUSTA ESTOS NOMBRES!

# LISTA DE SUFIJOS SIMPLES A ELIMINAR AL FINAL DEL NOMBRE (AÑADIR/QUITAR SEGÚN NECESIDAD)
# Importante: No incluir sufijos que formen parte de estructuras más complejas que SÍ quieres conservar
# (ej: no pongas 'CV' si quieres mantener 'SA DE CV').
# Los espacios y puntos se manejan en la lógica de eliminación.
SIMPLE_SUFFIXES_TO_REMOVE = [
    'SA', 'S A', 
    'SAC', 'S A C', 
    'SAA', 'S A A', 
    'SRL', 'S R L', 
    'LTDA', 'L T D A', 
    'EIRL', 'E I R L', 
    'CIA', 'COMPANIA', 
    'INC', 'INCORPORATED', 
    'LLC', 
    'SL', 'S L', 
    'CO', 'CORP', 'CORPORATION', 
    'SAS'
]
# Crear un patrón regex para estos sufijos (se usará más adelante)
# Se asegura de que coincida como palabra completa al final, opcionalmente precedido por punto y/o espacios
suffix_pattern = r'\b(?:' + '|'.join(re.escape(s) for s in SIMPLE_SUFFIXES_TO_REMOVE) + r')\.?\s*$'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funciones de Limpieza ---

def remove_accents(input_str):
    if pd.isna(input_str) or not isinstance(input_str, str):
        return input_str 
    try:
        nfkd_form = unicodedata.normalize('NFD', input_str)
        cleaned_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper()
        cleaned_str = cleaned_str.replace('Ñ', 'N')
        # Limpieza adicional de caracteres extraños residuales (ej: comillas tipográficas)
        cleaned_str = re.sub(r'[^\w\s./-]', '', cleaned_str) # Permite letras, números, espacio, punto, slash, guión
        return cleaned_str
    except Exception as e:
        logging.warning(f"Error al quitar acentos de '{input_str}': {e}")
        return input_str

def standardize_company_name(name):
    if pd.isna(name) or not isinstance(name, str):
        return name 
    
    try:
        # 1. Convertir a mayúsculas
        name = str(name).upper() # Asegurar que sea string
        
        # 2. Reemplazar variaciones complejas de tipos de sociedad PRIMERO
        #    Estas reglas tienen prioridad y conservan estas estructuras.
        #    Usamos espacios alrededor para ayudar a separar, se limpiarán luego.
        complex_replacements = {
            r'\bS\s*\.?\s*A\s*\.?\s*P\s*\.?\s*I\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' S A P I DE CV ',
            r'\bS\s*\.?\s*A\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' SA DE CV ',
            r'\bS\s*\.?\s*DE\s*R\s*\.?\s*L\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' S DE RL DE CV ',
            # Añade más reglas complejas si es necesario ANTES de la eliminación de sufijos simples
        }
        for pattern, replacement in complex_replacements.items():
            name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)

        # 3. Eliminar puntuación general (excepto la necesaria para sufijos complejos)
        #    Conservamos letras, números y espacios. Eliminamos puntos, comas, etc. redundantes.
        name = re.sub(r'[.,;:!?"\'`~#&()]', '', name) # Elimina puntuación común
        name = name.replace('-', ' ') # Reemplaza guiones por espacios

        # 4. Normalizar espacios (múltiples a uno solo)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # 5. ELIMINAR SUFIJOS SIMPLES (definidos en SIMPLE_SUFFIXES_TO_REMOVE)
        #    Esto se hace DESPUÉS de normalizar espacios y DESPUÉS de manejar los tipos complejos.
        #    Usamos el patrón regex pre-compilado 'suffix_pattern'.
        #    Se aplica repetidamente en caso de que haya múltiples sufijos (ej: "EMPRESA SA LTDA")
        original_name = name + " " # Placeholder para detectar cambios
        while True:
            # Intentar eliminar un sufijo del final
            name = re.sub(suffix_pattern, '', name, count=1, flags=re.IGNORECASE).strip()
            # Si ya no hubo cambios en esta pasada, salir del bucle
            if name == original_name.strip():
                 break
            original_name = name + " " # Actualizar para la siguiente iteración

        # 6. Normalizar espacios y strip final (por si la eliminación de sufijos dejó espacios)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    except Exception as e:
        logging.warning(f"Error al estandarizar nombre '{name}': {e}")
        return name # Devuelve original en caso de error

# --- Procesamiento Principal ---
# (El bucle principal de procesamiento de archivos permanece igual que en la versión anterior)
# ... (copia aquí el bloque "Procesamiento Principal" de la respuesta anterior) ...

if not os.path.isdir(ROOT_DIR):
    logging.error(f"El directorio raíz '{ROOT_DIR}' no existe. Por favor, créalo o corrige la ruta.")
else:
    logging.info(f"Iniciando procesamiento en: {ROOT_DIR}")
    processed_files_count = 0
    modified_files_count = 0 # Contador para archivos modificados

    for country_folder in os.listdir(ROOT_DIR):
        country_path = os.path.join(ROOT_DIR, country_folder)
        
        if os.path.isdir(country_path):
            logging.info(f"--- Procesando Carpeta: {country_folder} ---")
            
            for filename in os.listdir(country_path):
                if filename.lower().endswith('.csv'):
                    file_path = os.path.join(country_path, filename)
                    logging.info(f"  Procesando archivo: {filename}")
                    processed_files_count += 1
                    
                    try:
                        try:
                            df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
                            original_encoding = 'utf-8'
                        except UnicodeDecodeError:
                            logging.warning(f"    Archivo '{filename}' no es UTF-8, intentando con Latin-1.")
                            df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
                            original_encoding = 'latin1'
                        except Exception as e:
                             logging.error(f"    No se pudo leer el archivo '{filename}' con UTF-8 ni Latin-1: {e}. Saltando archivo.")
                             continue 

                        df_original = df.copy() 
                        
                        for col in COLUMNS_TO_STANDARDIZE_NAMES:
                            if col in df.columns:
                                logging.info(f"    Estandarizando columna de nombres: '{col}'")
                                df[col] = df[col].apply(standardize_company_name) # No necesita astype(str) aquí, la función lo maneja
                            else:
                                logging.warning(f"    Columna '{col}' para estandarizar nombres no encontrada en '{filename}'.")

                        for col in COLUMNS_TO_REMOVE_ACCENTS:
                            if col in df.columns:
                                logging.info(f"    Quitando acentos de columna: '{col}'")
                                df[col] = df[col].apply(remove_accents) # No necesita astype(str) aquí, la función lo maneja
                            else:
                                logging.warning(f"    Columna '{col}' para quitar acentos no encontrada en '{filename}'.")
                        
                        if not df.equals(df_original):
                            logging.info(f"    Detectados cambios en '{filename}'. Guardando...")
                            try:
                                df.to_csv(file_path, index=False, encoding=original_encoding)
                                logging.info(f"    Archivo '{filename}' actualizado y guardado con encoding '{original_encoding}'.")
                                modified_files_count += 1
                            except Exception as e:
                                logging.error(f"    ¡ERROR al guardar! No se pudo guardar el archivo '{filename}' con encoding '{original_encoding}': {e}")
                                logging.error(f"    Los cambios en '{filename}' podrían haberse perdido.")
                        else:
                            logging.info(f"    No se detectaron cambios necesarios en '{filename}'. No se sobrescribe.")

                    except pd.errors.EmptyDataError:
                         logging.warning(f"    El archivo '{filename}' está vacío. Saltando.")
                    except Exception as e:
                        logging.error(f"    Error inesperado procesando el archivo '{filename}': {e}")
                        
    logging.info(f"--- Procesamiento Completo ---")
    logging.info(f"Se revisaron {processed_files_count} archivos CSV.")
    logging.info(f"Se modificaron y guardaron {modified_files_count} archivos.")