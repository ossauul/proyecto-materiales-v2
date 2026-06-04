# ETL Instructions

## Alcance
Aplica a extractores, transformaciones y cargas ubicadas bajo `etl/`, incluyendo logica por pais y plataforma.

## Extractores por pais/plataforma
- Mantener extractores separados por plataforma y pais cuando las reglas de descarga, layout o normalizacion difieran.
- Panjiva Mexico debe tratarse como fuente independiente de Data Sur.
- Data Sur debe cubrir Colombia, Costa Rica, Ecuador, Peru, Paraguay y Chile con configuracion explicita por pais.
- Evitar duplicar logica comun: centralizar lectura de archivos, normalizacion de nombres de columnas, conversion de tipos y validaciones compartidas.
- Validar todo input externo antes de procesarlo, incluyendo extension, tamano esperado, columnas presentes y tipos inferidos.

## Contrato de entrada/salida
El flujo esperado es:
1. Excel/CSV crudo de la fuente.
2. DataFrame normalizado con columnas canonicas y tipos consistentes.
3. Dataset consolidado listo para dashboard o consumo aguas abajo.

Reglas del contrato:
- Preservar una referencia trazable al archivo crudo, fuente, pais y fecha de extraccion.
- No mezclar datos crudos con datos normalizados en el mismo artefacto de salida.
- Documentar cualquier columna derivada, conversion monetaria, limpieza de texto o regla de homologacion.

## Idempotencia y trazabilidad
- Los jobs deben ser idempotentes: reejecutar con el mismo input debe producir el mismo output o reemplazarlo de forma controlada.
- Usar claves deterministicas para registros cuando sea posible.
- Registrar metadata tecnica sin PII: fuente, pais, nombre de archivo enmascarado si aplica, hash/checksum, timestamp de proceso, version de esquema y conteos de filas.
- Nunca sobrescribir datos reales sin backup verificable.

## Reintentos y errores
- Implementar reintentos acotados para operaciones transitorias de red, IO o descarga.
- Diferenciar errores recuperables de errores de contrato/esquema.
- Los mensajes de error no deben incluir nombres completos, RUT, NIT, RUC ni otros datos personales completos.

## Encoding y formatos
- Declarar encoding esperado para CSV y manejar BOM cuando corresponda.
- Detectar o configurar separador decimal, separador de miles, delimitador CSV y formato de fecha por fuente/pais.
- Normalizar texto a Unicode consistente y documentar reglas de limpieza de acentos, espacios y mayusculas/minusculas.
