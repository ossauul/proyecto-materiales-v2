# Data Contracts Instructions

## Versionado de esquemas
- Todo esquema debe tener version explicita y documentada.
- Usar versionado semantico cuando sea posible: cambios compatibles incrementan version menor; cambios incompatibles incrementan version mayor.
- Registrar fecha, motivo y alcance de cada cambio de contrato.

## Columnas canonicas
Los contratos para datasets normalizados o consolidados deben documentar al menos estas columnas canonicas:
- `hs_code`: codigo arancelario o partida homologada.
- `cantidad`: cantidad importada en unidad normalizada o documentada.
- `valor_cif`: valor CIF en moneda y escala documentadas.
- `fecha`: fecha de operacion, importacion o registro segun fuente.
- `importador`: entidad importadora; no usar datos personales reales en fixtures o logs.
- `exportador`: entidad exportadora; no usar datos personales reales en fixtures o logs.
- `origen_pais`: pais de origen normalizado.
- `transporte`: via o modo de transporte normalizado.
- `producto`: descripcion de producto normalizada o descripcion fuente preservada segun contrato.

Para cada columna documentar tipo, obligatoriedad, valores nulos permitidos, reglas de normalizacion y ejemplos sinteticos.

## Cambios incompatibles
Antes de aceptar un cambio incompatible:
- Identificar consumidores aguas abajo y dashboards afectados.
- Agregar una nueva version mayor del esquema o una migracion explicita.
- Ejecutar validaciones contra fixtures sinteticas y, si aplica, muestras anonimizadas.
- Documentar estrategia de migracion, periodo de convivencia y criterio de rollback.
- Confirmar que los validadores rechazan datasets con el esquema anterior cuando el cambio sea intencionalmente incompatible.
