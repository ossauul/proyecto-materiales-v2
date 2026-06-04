# Tests Instructions

## Datos de prueba
- Usar fixtures sinteticas; no incluir nombres, RUT, NIT, RUC, direcciones, telefonos, emails ni datos personales reales.
- Los identificadores de empresas o personas deben ser ficticios, enmascarados o generados especificamente para pruebas.
- No usar extractos de archivos reales salvo que esten anonimizados y aprobados para versionarse.

## Cobertura esperada
- Cubrir extractores y normalizadores de Panjiva Mexico.
- Cubrir extractores y normalizadores de Data Sur para Colombia, Costa Rica, Ecuador, Peru, Paraguay y Chile.
- Incluir pruebas de columnas requeridas, tipos, fechas, valores numericos, encoding y manejo de filas invalidas.
- Incluir pruebas de idempotencia cuando un proceso escriba salidas o genere claves deterministicas.

## Buenas practicas
- Preferir fixtures pequenas y legibles.
- Separar pruebas unitarias de pruebas de integracion con red, archivos grandes o dependencias externas.
- Los logs capturados durante pruebas no deben contener PII ni identificadores tributarios completos.
