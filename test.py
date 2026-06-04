import os
import pandas as pd
import re
import unicodedata
import logging

# --- Configuración ---
ROOT_DIR = r'C:\Temp\Proyecto materiales\ArchivosCSV' # Directorio raíz donde están las carpetas por país con CSVs
COLUMNS_TO_STANDARDIZE_NAMES = ['importador', 'exportador'] # Columnas a las que aplicar estandarización de nombres de empresa
COLUMNS_TO_REMOVE_ACCENTS = ['importador', 'exportador', 'origen_pais', 'transporte', 'marca', 'unidad'] # Columnas a las que aplicar limpieza básica (si no son de nombres)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funciones de Limpieza ---

def basic_clean(input_str):
    """
    Aplica limpieza básica: mayúsculas, elimina acentos, maneja Ñ,
    normaliza espacios. Mantiene puntuación común interna (&, -, /)
    para pasos posteriores.
    Devuelve una cadena vacía para entradas NaN o vacías después de limpiar.
    """
    if pd.isna(input_str):
        return ""
    input_str = str(input_str)
    if not input_str:
        return ""

    try:
        # 1. Mayúsculas
        input_str = input_str.upper()

        # 2. Eliminar acentos (usando normalización NFD)
        nfkd_form = unicodedata.normalize('NFD', input_str)
        cleaned_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

        # 3. Manejar caracteres específicos (Ñ -> N)
        cleaned_str = cleaned_str.replace('Ñ', 'N')

        # 4. Normalizar espacios: reemplazar múltiples espacios, tabs, saltos de línea por un solo espacio
        cleaned_str = re.sub(r'\s+', ' ', cleaned_str).strip()

        # Nota: Esta versión mantiene toda la puntuación original como .,;:'"&-/
        # Pasos posteriores manejarán la eliminación de puntuación específica si es necesario.

        return cleaned_str
    except Exception as e:
        logging.warning(f"Error durante basic_clean en '{input_str}': {e}")
        # Fallback: simple mayúsculas y strip
        try:
             return str(input_str).upper().strip()
        except:
             return str(input_str) # Último recurso


# --- Definiciones para la Consolidación Específica Proporcionada por el Usuario ---
# Define explícitamente los grupos de nombres que deben consolidarse y su forma canónica deseada.
# Esto garantiza que las variaciones proporcionadas por el usuario terminen en el mismo nombre.
# El campo 'canonical' es el nombre final deseado (se le aplicará basic_clean).
# El campo 'variations' contiene las diferentes formas (se les aplicará basic_clean para usarlas como claves).
USER_CONSOLIDATION_DEFINITIONS = [
    {"canonical": "ACI AUTOMOTIVE COMPOUNDING", "variations": ["ACI AUTOMOTIVE COMPOUNDING INDUSTRY S DE RL DE CV", "ACI AUTOMOTIVE COMPOUNDING"]},
    {"canonical": "ASCEND PERFORMANCE MATERIALS", "variations": ["ASCEND PERFORMANCE MATERIALS DISTRIBUTION S DE RL DE CV", "ASCEND PERFORMANCE MATERIALS S DE RL DE CV"]},
    {"canonical": "AVIENT", "variations": ["AVIENT COLORANTS SA DE CV", "AVIENT DE SA DE CV"]},
    {"canonical": "BELDEN DE SONORA", "variations": ["BELDEN DE SONORA S DE RL DE CV", "BELDEN DE SONORA SA DE CV"]},
    {"canonical": "CONCORD PACKAGING", "variations": ["CONCORD PACKAGING DE MEXICOSA DE CV", "CONCORD PACKAGING DE SA DE CV"]},
    {"canonical": "ENTECRESINS MEXICOSA", "variations": ["ENTECRESINS MEXICOSA DE CV"]},
    {"canonical": "EXCEL NOBLEZA", "variations": ["EXCEL NOBLEZA SA DE CV", "EXCEL NOBLEZA SAPI DE CV"]},
    {"canonical": "GLOBAL PLASTIC", "variations": ["GLOBAL PLASTIC SA DE CV", "GLOBAL PLASTIC SOLUTIONS S DE RL DE CV"]},
    {"canonical": "HEXPOL COMPOUNDING", "variations": ["HEXPOL COMPOUNDING QUERETARO SA DE CV", "HEXPOL COMPOUNDING SA DE CV"]},
    {"canonical": "JOHNSON CONTROLS", "variations": ["JOHNSON CONTROLS ENTERPRISES S DE RL DE CV", "JOHNSON CONTROLS"]},
    {"canonical": "KIMBERLY CLARK DE", "variations": ["KIMBERLY CLARK DE SA DE C", "KIMBERLY CLARK DE SAB DE CV"]},
    {"canonical": "MONT BAG", "variations": ["MONT BAG SA DE CV", "MONT BAGSA DE CV"]},
    {"canonical": "MUEHLSTEIN DE", "variations": ["MUEHLSTEIN DE S DE RL DE CV", "MUEHLSTEIN DE SA DE CV"]},
    {"canonical": "POLIMEROS NACIONALES", "variations": ["POLIMEROS NACIONALES", "POLIMEROS NACIONALES SA DE CV"]},
    {"canonical": "STARPLAST", "variations": ["STARPLAST MEXICOSA DE CV", "STARPLAST SA DE CV"]},
    {"canonical": "VISCOFAN DE", "variations": ["VISCOFAN DE S DE RL DE C", "VISCOFAN DE S DE RL DE CV"]},

    {"canonical": "ALICO", "variations": ["ALICO", "ALICO SAS BIC"]},
    {"canonical": "BAVARIA", "variations": ["BAVARIA SC A", "BAVARIA SCA"]},
    {"canonical": "CABLES DE ENERGIA Y DE TELECOMUNICACIONES", "variations": ["CABLES DE ENERGIA Y DE TELECOMUNICACIONES", "CABLES DE ENERGIA Y DE TELECOMUNICACIONES SAS", "CABLES DE ENERGIA Y TELECOMUNICACIONES"]},
    {"canonical": "COLGATE PALMOLIVE", "variations": ["COLGATE PALMOLIVE", "COLGATE PALMOLIVE COMPAIA"]},
    {"canonical": "COM S Y E Y", "variations": ["COM S Y E Y"]},
    {"canonical": "DISENOS Y SISTEMAS", "variations": ["DISENOS Y SISTEMAS", "DISEOS Y SISTEMAS"]},
    {"canonical": "EMPRESARIAL DE", "variations": ["EMPRESARIAL D E", "EMPRESARIAL DE"]},
    {"canonical": "ENKA DE COLOMBIA", "variations": ["ENKA DE COLOMBIA", "ENKA DE COLOMBIA SA EN ACUERDO DE RESTRUCTURACION"]},
    {"canonical": "EQUIPOS DE PROTECCION INDIVIDUAL", "variations": ["EQUIPOS DE PROTECCION INDIVIDUAL", "EQUIPOS DE PROTECCION INDIVIDUAL SAS BIC"]},
    {"canonical": "ESENTTIA", "variations": ["ESENTTIA MASTERBATCH", "ESENTTIA"]},
    {"canonical": "FABRICATO", "variations": ["FABRICATO SA EN ACUERDO DE RESTRUCTURACION", "FABRICATO"]},
    {"canonical": "FILMTEX", "variations": ["FILMTEX SAS", "FILMTEX SAS EN LIQUIDACION"]},
    {"canonical": "FLEX PACK", "variations": ["FLEX PACK", "FLEX PACKS"]},
    {"canonical": "FLEXO SPRING", "variations": ["FLEXO SPRING", "FLEXO SPRING SAS"]},
    {"canonical": "GILPA IMPRESORES", "variations": ["GILPA IMPRESORES", "GILPA IMPRESORES ZONA FRANCA"]},
    {"canonical": "ITALCOL", "variations": ["ITALCOL", "ITALCOL DE OCCIDENTE"]},
    {"canonical": "PLASTICOS MONACO", "variations": ["PLASTICOS MONACO", "PLASTICOS MONACO SAS"]},
    {"canonical": "PLASTICOS MAFRA COLEY", "variations": ["PLASTICOS MAFRA COLEY Y S EN C", "PLASTICOS MAFRA COLEY Y COMPAIA S EN C"]},
    {"canonical": "PLASTICOS RIMAX", "variations": ["PLASTICOS RIMAX SAS", "PLASTICOS RIMAX"]},
    {"canonical": "PREBEL", "variations": ["PREBEL", "PREBEL SA BIC"]},
    {"canonical": "PROD NATURALES DE LA SABANA", "variations": ["PROD NATURALES DE LA SABANA SAS", "PROD NATURALES DE LA SABANA SAS BIC"]},
    {"canonical": "PROD VARIOS PRODUVARIOS", "variations": ["PROD VARIOS PRODUVARIOS", "PROD VARIOS PRODUVARIOS SA EN REORGANIZACION"]},
    {"canonical": "PRODUCTORA DE CABLES PROCABLES", "variations": ["PRODUCTORA DE CABLES PROCABLES SAS", "PRODUCTORA DE CABLES PROCABLES"]},
    {"canonical": "RAMBAL", "variations": ["RAMBAL", "RAMBAL SAS BIC"]},
    {"canonical": "SOCIEDAD NARIENSE DE PLASTICOS", "variations": ["SOCIEDAD NARIENSE DE PLASTICOS", "SOCIEDAD NARINENSE DE PLASTICOS"]},
    {"canonical": "STANTON", "variations": ["STANTON", "STANTON SAS"]},
    {"canonical": "TEAM FOODS COLOMBIA ACEGRASA", "variations": ["TEAM FOODS COLOMBIA S A Y PODRA UTILIZAR LAS SIGLAS ACEGRASA"]},
    {"canonical": "TUBULARES Y BOLSAS PLASTICAS TUBOPLAST", "variations": ["TUBULARES Y BOLSAS PLASTICAS SAS TUBOPLAST", "TUBULARES Y BOLSAS PLASTICAS SASTUBOPLAST SASBIC"]},
    {"canonical": "UNIFORMES INDUSTRIALES ROPA Y CALZADO QUINLOP", "variations": ["UNIFORMES INDUSTRIALES ROPA Y CALZADO QUIN LOP", "UNIFORMES INDUSTRIALES ROPA Y CALZADO QUINLOP"]},

    {"canonical": "3 102 844388", "variations": ["3 102 844388", "3 102 844388 SOCIEDAD DE RESPONSABILIDAD"]},
    {"canonical": "3 102 866716", "variations": ["3 102 866716", "3 102 866716 SOCIEDAD DE RESPONSABILIDAD"]},
    {"canonical": "AGROINDUSTRIAL NUMAR", "variations": ["AGROINDUSTRIAL NUMAR SOCIEDAD ANON"]},
    {"canonical": "ALPLA", "variations": ["ALPLA COSTA RICA SA DE CV", "ALPLA CR SA DE CV"]},
    {"canonical": "ARTHROCARE COSTA RICA", "variations": ["ARTHROCARE COSTA RICA S DE RL DE CV", "ARTHROCARE COSTA RICA SOCIEDAD DE RESPON"]},
    {"canonical": "ATL TECHNOLOGY CR", "variations": ["ATL TECHNOLOGY CR", "ATL TECHNOLOGY CR S DE RL DE CV"]},
    {"canonical": "AZZAM SHADEN", "variations": ["AZZAM SHADEN", "AZZAM SHADEN SOCIEDAD DE RESPONSABILIDAD"]},
    {"canonical": "BOSTON SCIENTIFIC DE COSTA RICA", "variations": ["BOSTON SCIENTIFIC DE COSTA RICA S DE RL DE CV", "BOSTON SCIENTIFIC DE COSTA RICA SOCIEDAD"]},
    {"canonical": "BRETANO COSTA RICA", "variations": ["BRETANO COSTA RICA", "BRETANO COSTA RICA SA DE CV", "BRETANO CR"]},
    {"canonical": "CALIDAD SOLUQUIM", "variations": ["CALIDAD SOLUQUIM", "CALIDAD SOLUQUIM SA DE CV"]},
    {"canonical": "CARUTI SANTA ANA", "variations": ["CARUTI DE SANTA ANA SA DE CV", "CARUTI SANTA ANA"]},
    {"canonical": "CHAJINO", "variations": ["CHAJINO", "CHAJINO SOCIEDAD DE RESPONSABILIDAD LIMI"]},
    {"canonical": "COANSA SNETOR COSTA RICA", "variations": ["COANSA SNETOR COSTA RICA SA DE CV"]},
    {"canonical": "COCA COLA FEMSA DE COSTA RICA", "variations": ["COCA COLA FEMSA DE COSTA RICA", "COCA COLA FEMSA DE COSTA RICA SA DE CV", "COCA COLA FEMSA DE COSTA RICA SOCIEDAD A"]},
    {"canonical": "COM LEON MEJIA", "variations": ["COM LEON MEJIA SOCIED", "COM LEON MEJIA"]},
    {"canonical": "COMERCIO E INDUSTRIAS PIMASA", "variations": ["COMERCIO E INDUSTRIAS PIMASA SA DE CV", "COMERCIO E INDUSTRIAS PIMASA SOCIEDAD AN"]},
    {"canonical": "COMPANIA PANAMENA DE AVIACION", "variations": ["COMPAAAIA PANAMEAAA DE AVIACION", "COMPAAIA PANAMEAA DE AVIACION"]},
    {"canonical": "COMPANIA FLEXTECH", "variations": ["COMPAAAIA FLEXTECH SA DE CV", "COMPAAIA FLEXTECH SA DE CV", "COMPAIÂ¾IA FLEXTECH SA DE CV"]},
    {"canonical": "COOPERATIVA DE PRODUCTORES DE LECHE DOS PINOS R L", "variations": ["COOPERATIVA DE PRODUCTORES DE LECHE DOS", "COOPERATIVA DE PRODUCTORES DE LECHE DOS PINOS R L"]},
    {"canonical": "COOPERMEDICAL", "variations": ["COOPERMEDICAL S DE RL DE CV", "COOPERMEDICAL SOCIEDAD DE RESPONSABILIDA"]},
    {"canonical": "COOPERVISION MANUFACTURING COSTA RICA", "variations": ["COOPERVISION MANUFACTURING COSTA RICA S DE RL DE CV", "COOPERVISION MANUFACTURING COSTA RICA SO", "COOPERVISION MANUFACTURING COSTA RICA SOCIEDAD DE RESPONSABIL"]},
    {"canonical": "CORP CEK DE COSTA RICA", "variations": ["CORP CEK DE COSTA RICA", "CORP CEK DE COSTA RICA SA DE CV", "CORP CEK DE COSTA RICA SOCIEDAD A"]},
    {"canonical": "CORP DEL VALLE METROPOLITANO", "variations": ["CORP DEL VALLE METROPOLITANO SA DE CV", "CORP DEL VALLE METROPOLITANO SOCI"]},
    {"canonical": "CORP KUPP AMERICA", "variations": ["CORP KUPP DE AMERICA SOCIEDAD ANO", "CORPORACON KUPP AMERICA"]},
    {"canonical": "COVIDIEN MANUFACTURING SOLUTIONS", "variations": ["COVIDIEN MANUFACTURING SOLUTIONS SA DE CV", "COVIDIEN MANUFACTURING SOLUTIONS SOCIEDA"]},
    {"canonical": "CREATIVE MODA", "variations": ["CREATIVE MODA", "CREATIVE MODA SA DE CV"]},
    {"canonical": "CRI IND DE TERMOFORMADOS", "variations": ["CRI IND DE TERMOFORMADORES SOCIED", "CRI IND DE TERMOFORMADOS SA DE CV"]},
    {"canonical": "CSI CLOSURE SYSTEMS MANUFACTURING DE CENTRO AMERICA", "variations": ["CSI CLOSURE SYSTEMS MANUFACTURING DE CENTRO AMERICA S DE RL DE CV", "CSI CLOSURE SYSTEMS MANUFACTURING DE CENTRO AMERICA SOCIEDAD"]},
    {"canonical": "CURRIPLAST", "variations": ["CURRIPLAST", "CURRIPLAST SA DE CV"]},
    {"canonical": "DEROYAL CIENTIFICA DE LATAM", "variations": ["DEROYAL CIENTIFICA DE LATAM S DE RL DE CV", "DEROYAL CIENTIFICA DE LATAM SOCIEDAD DE RESPONSABILID"]},
    {"canonical": "DIST CHANTO", "variations": ["DIST CHANTO", "DIST CHANTO SA DE CV"]},
    {"canonical": "DIST EL CARMEN DE SANTA ANA", "variations": ["DIST EL CARMEN DE SANTA ANA", "DIST EL CARMEN DE SANTA ANA SOC"]},
    {"canonical": "DIST LA FLORIDA", "variations": ["DIST LA FLORIDA", "DIST LA FLORIDA SOCIEDAD ANONIM"]},
    {"canonical": "DIST MATERIAS PRIMAS BELEN", "variations": ["DIST MATERIAS PRIMAS BELEN SA DE CV", "DIST MATERIAS PRIMAS BELEN SOCI"]},
    {"canonical": "DIST PLASTIMEX DE COSTA RICA", "variations": ["DIST PLASTIMEX DE COSTA RICA SA DE CV", "DIST PLASTIMEX DE COSTA RICA SO"]},
    {"canonical": "DURALAC", "variations": ["DURALAC", "DURALAC SA DE CV"]},
    {"canonical": "E R A ECOTANK ROTOMOULDING", "variations": ["E R A ECOTANK ROTOMOULDING SA DE CV", "E R A ECOTANK ROTOMOULDING SOCIEDAD ANON"]},
    {"canonical": "EAGLE ELECTRIC CENTROAMERICAN", "variations": ["EAGLE ELECTRIC CENTROAMERICAN", "EAGLE ELECTRIC CENTROAMERICAN SA DE CV", "EAGLE ELECTRIC CENTROAMERICAN SOCIEDAD A"]},
    {"canonical": "ECOPLAST", "variations": ["ECOPLAST", "ECOPLAST SA DE CV"]},
    {"canonical": "EL SOMBRERO AZUL DEL MARIACHI", "variations": ["EL SOMBRERO AZUL DEL MARIACHI S DE RL DE CV", "EL SOMBRERO AZUL DEL MARIACHI SOCIEDAD DE RESPONSABILIDAD LI"]},
    {"canonical": "ENVASES COMERCIALES ENVASA", "variations": ["ENVASES COMERCIALES ENVASA", "ENVASES COMERCIALES ENVASA SA DE CV"]},
    {"canonical": "ETIQUETAS PLASTICAS ETIPLAST", "variations": ["ETIQUETAS PLASTICAS ETIPLAST", "ETIQUETAS PLASTICAS ETIPLAST SA DE CV", "ETIQUETAS PLASTICAS ETIPLAST SOCIEDAD AN"]},
    {"canonical": "FIBRAS DE CENTROAMERICA", "variations": ["FIBRAS DE CENTROAMERICA", "FIBRAS DE CENTROAMERICA SA DE CV"]},

    {"canonical": "AGRICOMINSA AGRICOLA", "variations": ["AGRICOMINSA AGRICOLA", "AGRICOMINSA AGRICOLA COM IND SA AGRICOMINSA"]},
    {"canonical": "APLICACIONES EN PLASTICO APLIPLAST", "variations": ["APLICACIONES EN PASTICO APLIPLAST", "APLICACIONES EN PLASTICO APLIPLAST"]},
    {"canonical": "ARBELAEZ OCHOA", "variations": ["ARBELAEZ OCHOA", "ARBELAEZ OCHOA IVAN"]},
    {"canonical": "BOPP ECUADOR", "variations": ["BOPP DEL ECUADOR", "BOPP ECUADOR"]},
    {"canonical": "CA ECUATORIANA DE CERAMICA", "variations": ["C A ECUATORIANA DE CERAMICA", "CA ECUATORIANA DE CERAMICA"]},
    {"canonical": "CODIEMPAQUES DEL ECUADOR", "variations": ["CODI EMPAQUES DEL ECUADOR", "CODIEMPAQUES DEL ECUADOR"]},
    {"canonical": "TRUE INNOVATION", "variations": ["TRUE INNOVATION", "TRUE INNOVATION A"]},
    {"canonical": "SUNCHODESA REPRESENTACIONES", "variations": ["SUNCHODESA REPRESENTACIONES", "SUNCHODESA C", "SUNCHODESA REPRESENTACIONES C"]},
    {"canonical": "SIGMAPLAST", "variations": ["SIGMAPLAST", "SIGMAPLAST SA SIGMAPLAST"]},
    {"canonical": "SECURITY DEPOT", "variations": ["SECURITY DEPOT", "SECURITY DEPOT CIALTDA"]}
]


# --- Construir el Mapa de Consolidación del Usuario ---
# Esto depende de basic_clean, así que debe definirse después de basic_clean.
USER_PROVIDED_CONSOLIDATION_MAP = {}
for group in USER_CONSOLIDATION_DEFINITIONS:
    # Aplicar basic_clean a la forma canónica deseada
    canonical_cleaned = basic_clean(group.get("canonical", "")) # Usar get con valor por defecto por seguridad
    if not canonical_cleaned:
        logging.warning(f"Forma canónica '{group.get('canonical', '')}' resultó vacía después de basic_clean. Saltando este grupo.")
        continue

    # Obtener la lista de variaciones, asegurándose de que sea una lista
    variations_list = group.get("variations", [])
    if not isinstance(variations_list, list):
        logging.warning(f"Variaciones para la canónica '{group.get('canonical', '')}' no es una lista. Saltando este grupo.")
        continue

    # Mapear cada variación limpiada a la forma canónica limpiada
    for variation_raw in variations_list:
        variation_cleaned = basic_clean(variation_raw)
        if variation_cleaned: # Solo mapear variaciones no vacías después de limpiar
            # Evitar mapear la canónica a sí misma si está en la lista de variaciones (opcional pero limpio)
            if variation_cleaned == canonical_cleaned:
                 # logging.debug(f"Saltando mapeo de canónica a sí misma: '{canonical_cleaned}'")
                 continue

            # Verificar si ya existe un mapeo para esta variación
            if variation_cleaned in USER_PROVIDED_CONSOLIDATION_MAP:
                 # Si ya existe y mapea a una canónica diferente, registrar conflicto
                 if USER_PROVIDED_CONSOLIDATION_MAP[variation_cleaned] != canonical_cleaned:
                    logging.warning(f"Conflicto en mapa de consolidación del usuario: '{variation_cleaned}' ya mapeado a '{USER_PROVIDED_CONSOLIDATION_MAP[variation_cleaned]}', intentando mapear a '{canonical_cleaned}'. Se mantiene el mapeo existente.")
                    # Mantener el primer mapeo encontrado para asegurar determinismo
                    pass
            else:
                # Añadir el nuevo mapeo
                USER_PROVIDED_CONSOLIDATION_MAP[variation_cleaned] = canonical_cleaned

logging.info(f"Construido USER_PROVIDED_CONSOLIDATION_MAP con {len(USER_PROVIDED_CONSOLIDATION_MAP)} entradas.")
# print("Vista previa del Mapa de Usuario:", list(USER_PROVIDED_CONSOLIDATION_MAP.items())[:10]) # Debugging

# 1. MAPEOS CANÓNICOS PRIORITARIOS / CORRECCIONES MANUALES GENERALES
# Aplicar basic_clean a las claves aquí, después de basic_clean está definido
MANUAL_CANONICAL_MAP = {
    "COCACOLA": "COCA COLA COMPANY",
    "COCA COLA": "COCA COLA COMPANY",
    "COCA COLA FEMSA": "COCA COLA COMPANY",
    "AVON COSMETICS DE MEXICO": "AVON",
    "HEWLETT PACKARD COMPANY": "HP INC",
    "H P MEXICO": "HP INC",
    "CORPORACON KUPP AMERICA": "CORP KUPP AMERICA",
    # Añade aquí tus mapeos específicos. Las claves deben estar en formato original o como aparecen en tus datos.
    # Se les aplicará basic_clean antes de añadirlas al mapa real usado.
}
# Aplicar basic_clean a las claves del mapa manual para que coincidan con el formato de comparación
MANUAL_CANONICAL_MAP_CLEANED = {basic_clean(key): value for key, value in MANUAL_CANONICAL_MAP.items() if basic_clean(key)}


# 2. NORMALIZACIÓN DE PALABRAS CLAVE INTERNAS
# Regex patterns. Aplicado después de limpieza, estandarización de sufijos complejos y eliminación de puntuación.
INTERNAL_KEYWORD_NORMALIZATION = {
    r'\b(?:INTERNACIONAL|INTERNATIONAL|INTERCONTINENTAL|INTL|INT\'L)\b': 'INTL',
    r'\b(?:CORPORACION|CORPORATION|CORP)\b': 'CORP',
    r'\b(?:DISTRIBUIDORA|DISTRIBUIDORES|DIST)\b': 'DIST',
    r'\b(?:FABRICA|FABRICACION|FAB)\b': 'FAB',
    r'\b(?:PRODUCTOS|PRODUCTO)\b': 'PROD',
    r'\b(?:SERVICIOS|SERVICIO|SERV)\b': 'SERV',
    r'\b(?:TECNOLOGIA|TECNOLOGIAS|TECH)\b': 'TECH',
    r'\b(?:COMERCIALIZADORA|COMERCIAL)\b': 'COM',
    r'\b(?:IMPORTADORA|IMPORTACIONES|IMP)\b': 'IMP',
    r'\b(?:EXPORTADORA|EXPORTACIONES|EXP)\b': 'EXP',
    r'\b(?:INDUSTRIA|INDUSTRIAL|IND)\b': 'IND',
    r'\b(?:COMPANIA|COMPAÑIA|CIA)\b': '',
    r'\b(?:GRUPO|GROUP|HOLDING|HOLDINGS)\b': '',
    r'\b(?:LATINOAMERICA|LATAM)\b': 'LATAM',
}


# 3. REEMPLAZOS COMPLEJOS DE TIPOS DE SOCIEDAD
# Regex patterns que esperan puntuación/espacios de basic_clean.
# Aplicado DESPUÉS de basic_clean, pero ANTES de eliminar puntuación general.
COMPLEX_REPLACEMENTS = {
    r'\bS\s*\.?\s*A\s*\.?\s*P\s*\.?\s*I\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' SAPI DE CV ',
    r'\bS\s*\.?\s*A\s*\.?\s*B\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' SAB DE CV ',
    r'\bS\s*\.?\s*A\s*\.?\s*P\s*\.?\s*I\s*\.?\b': ' SAPI ',
    r'\bS\s*\.?\s*A\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' SA DE CV ',
    r'\bS\s*\.?\s*DE\s*R\s*\.?\s*L\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' S DE RL DE CV ',
    r'\bS\s*\.?\s*DE\s*R\s*\.?\s*L\s*\.?\b': ' S DE RL ',
    r'\bS\s*\.?\s*C\s*\.?\s*(?:DE)?\s*R\s*\.?\s*L\s*\.?\s*(?:DE)?\s*C\s*\.?\s*V\s*\.?\b': ' SC DE RL DE CV ',
    r'\bS\s*\.?\s*EN\s*N\s*\.?\s*C\s*\.?\b': ' S EN NC ',
    r'\bS\s*\.?\s*EN\s*C\s*\.?\s*POR\s*A\s*\.?\s*(?:CCIONES)?\b': ' S EN C POR A ',
    r'\bS\s*\.?\s*EN\s*C\s*\.?\s*(?:SIMPLE)?\b': ' S EN C ',
    r'\bS\s*\.?\s*C\s*\.?\s*L\s*\.?\b': ' SCL ',
    r'\bS\s*\.?\s*C\s*\.?\s*S\s*\.?\b': ' SCS ',
    r'\bA\s*\.?\s*C\s*\.?\b': ' AC ',
    r'\bS\s*\.?\s*C\s*\.?\b': ' SC ',
    r'\bS\s*\.?\s*A\s*\.?\s*S\s*\.?\b': ' SAS ',
    r'\bSOCIEDAD\s*ANONIMA\s*PROMOTORA\s*DE\s*INVERSION\s*(?:DE\s*CAPITAL\s*VARIABLE)?\b': ' SAPI DE CV ',
    r'\bSOCIEDAD\s*ANONIMA\s*BURSATIL\s*(?:DE\s*CAPITAL\s*VARIABLE)?\b': ' SAB DE CV ',
    r'\bSOCIEDAD\s*ANONIMA\s*(?:DE\s*CAPITAL\s*VARIABLE)?\b': ' SA DE CV ',
    r'\bSOCIEDAD\s*DE\s*RESPONSABILIDAD\s*LIMITADA\s*(?:DE\s*CAPITAL\s*VARIABLE)?\b': ' S DE RL DE CV ',
    r'\bSOCIEDAD\s*DE\s*RESPONSABILIDAD\s*LIMITADA\b': ' S DE RL ',
    r'\bSOCIEDAD\s*COOPERATIVA\s*(?:DE\s*RESPONSABILIDAD\s*LIMITADA)?\s*(?:DE\s*CAPITAL\s*VARIABLE)?\b': ' SC DE RL DE CV ',
    r'\bSOCIEDAD\s*POR\s*ACCIONES\s*SIMPLIFICADA\b': ' SAS ',
    r'\bASOCIACION\s*CIVIL\b': ' AC ',
    r'\bSOCIEDAD\s*CIVIL\b': ' SC ',
    r'\bSOCIEDAD\s*EN\s*COMANDITA\s*SIMPLE\b': ' S EN C ',
    r'\bSOCIEDAD\s*EN\s*COMANDITA\s*POR\s*ACCIONES\b': ' S EN C POR A ',
    r'\bSOCIEDAD\s*EN\s*NOMBRE\s*COLECTIVO\b': ' S EN NC ',
}

# --- Mapa para Expandir Abreviaciones de Países a Nombre Completo ---
# Se aplicará basic_clean a las claves y valores al construir los patrones.
COUNTRY_ABBREVIATION_MAP_RAW = {
    "MX": "MEXICO",
    "CR": "COSTA RICA",
    "CO": "COLOMBIA",
    "EC": "ECUADOR",
    "PY": "PARAGUAY",
    "PE": "PERU"
    # Añade más abreviaciones de 2 o 3 letras según sea necesario
    # Ej: USA, GBR, FRA, DEU, ESP, CAN, etc.
}

# Compilar patrones regex para las abreviaciones y mapearlos a sus nombres completos (limpiados)
# Usar \b para asegurar que se coincida la palabra completa (ej: evitar que CR en ACRILICO coincida)
COUNTRY_ABBREVIATION_EXPANSION_COMPILED = []
for abbr, full_name in COUNTRY_ABBREVIATION_MAP_RAW.items():
    cleaned_abbr = basic_clean(abbr)
    cleaned_full_name = basic_clean(full_name)
    if cleaned_abbr and cleaned_full_name:
         # Crear un patrón regex compilado para la abreviación como palabra completa
         # Flags re.IGNORECASE ya incluidas en compile
         pattern = re.compile(r'\b' + re.escape(cleaned_abbr) + r'\b', flags=re.IGNORECASE)
         COUNTRY_ABBREVIATION_EXPANSION_COMPILED.append((pattern, cleaned_full_name))

# Ordenar los patrones compilados por la longitud de la abreviación original (descendente)
# Esto es útil si hay abreviaciones que son subcadenas de otras (ej: US vs USA) y para procesar más largas primero.
COUNTRY_ABBREVIATION_EXPANSION_ORDERED = sorted(
    COUNTRY_ABBREVIATION_EXPANSION_COMPILED,
    key=lambda item: len(item[0].pattern), # Ordenar por la longitud del patrón (basado en la abreviación)
    reverse=True
)


# 4. SUFIJOS SIMPLES A ELIMINAR LIST
# Lista de términos/frases que deben eliminarse si aparecen al final del nombre.
# **Importante: Se han eliminado los nombres y abreviaciones de países de esta lista.**
SIMPLE_SUFFIXES_TO_REMOVE_LIST = [
    'SAPI DE CV', 'SA DE CV', 'S DE RL DE CV', 'SAB DE CV', 'SAPI', 'SA', 'S DE RL', 'SC DE RL DE CV',
    'S EN NC', 'S EN C POR A', 'S EN C', 'SCL', 'SCS', 'AC', 'SC', 'SAS',
    'SAC', 'SAA', 'SRL', 'LTDA', 'LIMITADA', 'LDA', 'EIRL',
    'INC', 'INCORPORATED', 'LLC', 'PLC', 'LTD', 'LIMITED',
    'GMBH', 'AG', 'AB', 'AS', 'PT', 'OY', 'SPA',
    'UNIPERSONAL', 'PROPRIETARY', 'PTY',
    'EN ACUERDO DE RESTRUCTURACION', 'EN LIQUIDACION', 'EN REORGANIZACION', 'BIC',
    'COMPANY', 'ENTERPRISE', 'VENTURES', 'SOLUTIONS', 'SYSTEMS', 'TECHNOLOGIES',
    'INDUSTRIES', 'MANUFACTURING', 'TRADING', 'SUPPLY', 'LOGISTICS',
    # **NOMBRES Y ABREVIACIONES DE PAISES SE ELIMINARON DE AQUI**
    'SOCIEDAD ANONIMA', 'SOCIEDAD DE RESPONSABILIDAD', 'SOCIEDAD AN', 'SOCIEDAD ANONIM', 'SOCIEDAD ANON',
    'SOCIEDAD DE RESPON', 'SOCIEDAD DE RESPONSABILIDA', 'SOCIEDAD DE RESPONSABILID',
    'SOCI', 'SOC', 'RESPONSABILIDAD', 'ANONIMA',
    'COM IND SA', 'CIALTDA', 'SASBIC', 'SASTUBOPLAST SASBIC',
    'SA EN ACUERDO DE RESTRUCTURACION', 'SAS EN LIQUIDACION', 'SA EN REORGANIZACION', 'SA EN REORGANIZACION', 'SAS BIC', 'SA BIC',
    'Y COMPAIA S EN C', 'S EN C', 'ZONA FRANCA', 'DE OCCIDENTE', 'SAS', 'SCA',
    'DISTRIBUTION', 'COLORANTS', 'ENTERPRISES', 'SOLUTIONS', 'QUERETARO',
    'MASTERBATCH', 'INDIVIDUAL', 'PACKS', 'IMPRESORES', 'ZONA FRANCA', 'DE OCCIDENTE',
    'SOCIED', 'RESPONSABILIDA', 'RESPONSABILID', 'ANONIM', 'ANON', 'SOCI',
    'DE SANTA ANA', 'SANTA ANA', 'LIMI', 'SNETOR', 'DEL VALLE METROPOLITANO', 'METROPOLITANO', 'CIENTIFICA',
    'DE LATAM', 'CHANTO', 'LA FLORIDA', 'MATERIAS PRIMAS', 'BELEN', 'PLASTIMEX', 'ECOTANK', 'ROTOMOULDING',
    'ELECTRICA', 'CENTROAMERICAN', 'DEL MARIACHI', 'COMERCIALES', 'ENVASA', 'PLASTICAS', 'ETIPLAST', 'FIBRAS',
    'AGRICOLA', 'COM IND SA', 'APLIPLAST', 'IVAN', 'CERAMICA', 'EMPAQUES', 'CODIEMPAQUES',
    'A', 'C', # Cuidado con estos, muy genéricos
    'SIGMAPLAST SA', 'CIALTDA',
]

# Crear patrón regex para sufijos simples, limpiados usando basic_clean.
# Depende de basic_clean y SIMPLE_SUFFIXES_TO_REMOVE_LIST.
# Ordenar por longitud descendente para mejor coincidencia.
# Filtrar cadenas que queden vacías después de basic_clean.
cleaned_suffixes = sorted([basic_clean(s) for s in SIMPLE_SUFFIXES_TO_REMOVE_LIST if basic_clean(s)], key=len, reverse=True)
# El patrón busca límites de palabra, el sufijo, opcionalmente un punto, y el fin de la cadena (más espacios opcionales al final).
suffix_pattern_str = r'\b(?:' + '|'.join(re.escape(s) for s in cleaned_suffixes) + r')\.?\s*$'
suffix_pattern = re.compile(suffix_pattern_str, flags=re.IGNORECASE)


# --- Función principal de estandarización de nombres de empresa ---
# Depende de basic_clean, USER_PROVIDED_CONSOLIDATION_MAP, MANUAL_CANONICAL_MAP_CLEANED,
# COMPLEX_REPLACEMENTS, INTERNAL_KEYWORD_NORMALIZATION, COUNTRY_ABBREVIATION_EXPANSION_ORDERED,
# y suffix_pattern.
def standardize_company_name(name_input):
    """
    Estandariza nombres de empresa aplicando reglas de limpieza:
    1. Limpieza básica inicial (caso, acentos, espacios).
    2. Mapa de consolidación específico del usuario (prioridad alta).
    3. Mapa de correcciones/canónicos generales (prioridad media).
    4. Estandarización de sufijos legales complejos.
    5. Eliminación de puntuación residual y normalización de separadores.
    6. Normalización/eliminación de palabras clave internas.
    7. Eliminación iterativa de sufijos simples.
    8. Expansión de abreviaciones de países. <--- PASO MOVIDO AQUÍ
    9. Limpieza final.
    """
    if pd.isna(name_input):
        return name_input # Devolver NaN si la entrada es NaN

    try:
        # 1. Limpieza Básica Inicial (mayúsculas, acentos, Ñ, normalización de espacios)
        # Mantiene puntuación original como .,;:'"&-/ para el paso de regex de sufijos complejos.
        partially_cleaned_name = basic_clean(name_input)

        # Si la limpieza básica resulta en una cadena vacía, devolver cadena vacía.
        if not partially_cleaned_name:
            # logging.debug(f"basic_clean de '{name_input}' resultó en cadena vacía.")
            return ""

        # 2. Aplicar Mapa de Consolidación Específico del Usuario (Máxima Prioridad)
        # Las claves en este mapa son las variaciones después de basic_clean.
        if partially_cleaned_name in USER_PROVIDED_CONSOLIDATION_MAP:
            # logging.debug(f"'{name_input}' ('{partially_cleaned_name}') mapeado por mapa de usuario a '{USER_PROVIDED_CONSOLIDATION_MAP[partially_cleaned_name]}'")
            # La forma canónica del mapa de usuario ya está basic_cleaneada.
            return USER_PROVIDED_CONSOLIDATION_MAP[partially_cleaned_name]

        # 3. Aplicar Mapa de Correcciones/Canónicos Generales (Prioridad Media)
        # Las claves en este mapa también están basic_cleaneada.
        if partially_cleaned_name in MANUAL_CANONICAL_MAP_CLEANED:
            # logging.debug(f"'{name_input}' ('{partially_cleaned_name}') mapeado por mapa manual a '{MANUAL_CANONICAL_MAP_CLEANED[partially_cleaned_name]}'")
            return MANUAL_CANONICAL_MAP_CLEANED[partially_cleaned_name]

        # --- Reglas de Estandarización General (aplicadas si no se mapeó manualmente) ---

        processed_name = partially_cleaned_name # Empezar con el resultado de basic_clean

        # 4. Estandarizar Sufijos Legales Complejos
        # Este paso opera sobre la cadena que contiene la puntuación y espaciado de basic_clean.
        for pattern, replacement in COMPLEX_REPLACEMENTS.items():
             processed_name = re.sub(pattern, replacement, processed_name, flags=re.IGNORECASE)
        # Limpiar espacios que pudieron haberse introducido por los reemplazos.
        processed_name = re.sub(r'\s+', ' ', processed_name).strip()

        # 5. Eliminar puntuación no deseada restante y normalizar separadores (mantener alfanuméricos, espacio, &, -, /)
        # Aplicar DESPUÉS de estandarizar sufijos complejos.
        processed_name = re.sub(r'[^A-Z0-9\s&\-/]', '', processed_name)
        # Normalizar secuencias de separadores permitidos (&, -, /, espacio) a un solo espacio.
        processed_name = re.sub(r'[\s&\-/]+', ' ', processed_name).strip()

        # 6. Normalizar o Eliminar Palabras Clave Internas
        # Aplicar DESPUÉS de estandarizar sufijos y eliminar puntuación.
        for pattern, replacement in INTERNAL_KEYWORD_NORMALIZATION.items():
            processed_name = re.sub(pattern, replacement, processed_name, flags=re.IGNORECASE)
        # Limpiar espacios después de normalización.
        processed_name = re.sub(r'\s+', ' ', processed_name).strip()

        # 7. Eliminar Sufijos Simples (Eliminación iterativa)
        # Este patrón no incluye ahora nombres/abreviaciones de países.
        previous_name = "INITIAL_STATE_DUMMY_DIFFERENT_FROM_NAME"
        while processed_name != previous_name :
            previous_name = processed_name
            processed_name = suffix_pattern.sub('', processed_name).strip()
            processed_name = re.sub(r'\s+', ' ', processed_name).strip()

        # 8. Expandir Abreviaciones de Países (PASO MOVIDO AQUÍ)
        # Aplicar DESPUÉS de eliminar sufijos, para evitar expandir dentro de sufijos legales.
        for pattern, replacement in COUNTRY_ABBREVIATION_EXPANSION_ORDERED:
             processed_name = pattern.sub(replacement, processed_name)
        # Limpiar espacios después de la expansión.
        processed_name = re.sub(r'\s+', ' ', processed_name).strip()


        # 9. Limpieza Final: Asegurar que no queden espacios al inicio/final o múltiples espacios.
        final_name = re.sub(r'\s+', ' ', processed_name).strip()

        # 10. Manejar casos donde el nombre queda vacío después de todas las reglas.
        if not final_name:
             # Si el resultado final está vacío, pero la entrada original no lo estaba,
             # devolver la versión basic_cleaneada de la entrada original como fallback.
             # Si basic_clean ya resultó en vacío, la comprobación en el paso 1 lo manejaría.
             # Devolver "" si incluso el fallback está vacío. basic_clean maneja esto.
             # logging.warning(f"Reglas de estandarización resultaron en cadena vacía para '{name_input}'. Devolviendo basic_clean del original como fallback.")
             return basic_clean(name_input)

        return final_name

    except Exception as e:
        logging.error(f"Error durante la estandarización de '{name_input}': {e}")
        # En caso de cualquier error inesperado durante la estandarización,
        # devolver la versión basic_cleaneada para minimizar la pérdida de datos.
        return basic_clean(name_input)


# --- Procesamiento Principal (Mantiene la estructura de bucle existente) ---
if not os.path.isdir(ROOT_DIR):
    logging.error(f"El directorio raíz '{ROOT_DIR}' no existe. Por favor, créalo o corrige la ruta.")
else:
    logging.info(f"Iniciando procesamiento en: {ROOT_DIR}")
    processed_files_count = 0
    modified_files_count = 0

    # Recorrer la estructura de directorios
    for subdir, dirs, files in os.walk(ROOT_DIR):
         logging.info(f"--- Procesando Carpeta: {subdir} ---")

         for filename in files:
             if filename.lower().endswith('.csv'):
                 file_path = os.path.join(subdir, filename)
                 logging.info(f"  Procesando archivo: {filename}")
                 processed_files_count += 1

                 try:
                     # Intentar leer primero con UTF-8, luego con Latin-1 si es necesario
                     try:
                         df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
                         original_encoding = 'utf-8'
                     except UnicodeDecodeError:
                         logging.warning(f"  Archivo '{filename}' no es UTF-8, intentando con Latin-1.")
                         df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
                         original_encoding = 'latin1'
                     except Exception as e:
                          logging.error(f"  No se pudo leer el archivo '{filename}' con UTF-8 ni Latin-1: {e}. Saltando archivo.")
                          continue

                     df_original = df.copy() # Mantener una copia para verificar cambios

                     # Aplicar estandarización de nombres de empresa a las columnas especificadas
                     for col in COLUMNS_TO_STANDARDIZE_NAMES:
                         if col in df.columns:
                             logging.info(f"    Estandarizando columna de nombres: '{col}'")
                             # Aplicar la función principal de estandarización
                             df[col] = df[col].astype(str).apply(standardize_company_name)
                         else:
                             logging.warning(f"    Columna '{col}' para estandarizar nombres no encontrada en '{filename}'.")

                     # Aplicar limpieza básica a otras columnas especificadas que no son nombres
                     other_cols_to_clean = [col for col in COLUMNS_TO_REMOVE_ACCENTS if col not in COLUMNS_TO_STANDARDIZE_NAMES]
                     for col in other_cols_to_clean:
                         if col in df.columns:
                             logging.info(f"    Aplicando basic_clean a columna: '{col}'")
                             # Usar basic_clean para limpieza de texto genérica
                             df[col] = df[col].astype(str).apply(basic_clean)
                         else:
                             logging.warning(f"    Columna '{col}' para basic_clean no encontrada en '{filename}'.")

                     # Verificar si se realizaron cambios en el DataFrame
                     cols_to_compare = COLUMNS_TO_STANDARDIZE_NAMES + other_cols_to_clean
                     cols_to_compare = [col for col in cols_to_compare if col in df.columns]

                     changed = False
                     if cols_to_compare:
                         for col in cols_to_compare:
                             if col in df_original.columns:
                                 # Convertir las columnas relevantes a string para una comparación fiable después de limpiar
                                 if not df[col].astype(str).equals(df_original[col].astype(str)):
                                     changed = True
                                     break # Se encontró un cambio, no es necesario verificar otras columnas
                             # Si una columna existe en df pero no en df_original (no debería ocurrir con df.copy()),
                             # indicaría un cambio, pero el bucle asegura que col está en df.columns

                     if changed:
                         logging.info(f"  Detectados cambios en '{filename}'. Guardando...")
                         try:
                             # Guardar el DataFrame modificado de vuelta en la ruta del archivo original
                             # Usar la codificación original si es posible
                             df.to_csv(file_path, index=False, encoding=original_encoding)
                             logging.info(f"  Archivo '{filename}' actualizado y guardado con encoding '{original_encoding}'.")
                             modified_files_count += 1
                         except Exception as e:
                             logging.error(f"  ¡ERROR al guardar! No se pudo guardar el archivo '{filename}' con encoding '{original_encoding}': {e}")

                     else:
                         logging.info(f"  No se detectaron cambios necesarios en '{filename}'. No se sobrescribe.")

                 except pd.errors.EmptyDataError:
                     logging.warning(f"  El archivo '{filename}' está vacío. Saltando.")
                 except Exception as e:
                     logging.error(f"  Error inesperado procesando el archivo '{filename}': {e}")

    logging.info(f"--- Procesamiento Completo ---")
    logging.info(f"Se revisaron {processed_files_count} archivos CSV.")
    logging.info(f"Se modificaron y guardaron {modified_files_count} archivos.")