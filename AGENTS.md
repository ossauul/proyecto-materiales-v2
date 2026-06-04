# Project Overview
Proyecto que recopila informacion sobre importaciones por pais, para generarlo para un dashboard.

## Tech stack
Python.

## Plataformas para obtener datos
- Mexico - Panjiva.
- Colombia, Costa Rica, Ecuador, Peru, Paraguay, Chile - Data Sur.

## Security rules
- No hardcodear secrets.
- No loggear tokens, passwords ni datos personales.
- Validar input externo.
- Revisar permisos antes de tocar auth/billing.
- No tocar, modificar, sobrescribir ni depurar datos reales sin contar antes con un backup verificable y recuperable.
- No loggear nombres completos ni identificadores tributarios completos como RUT, NIT o RUC; usar mascaramiento, hashing irreversible o identificadores sintéticos cuando sea necesario para diagnostico.
- No hardcodear rutas locales o de sistema como `C:\Temp\...`, rutas absolutas de usuario o paths especificos de una maquina.
- Preferir configuracion por variables de entorno (`.env`) o por archivos YAML versionables sin secretos; documentar las claves esperadas y sus valores por defecto seguros.

## Definition of done
Antes de terminar:
- El codigo compila con `python -m py_compile` sobre los modulos Python modificados o relevantes.
- Tests unitarios relevantes pasan.
- Lint/typecheck relevantes pasan cuando existan herramientas configuradas en el repo.
- La validacion de esquema de salida pasa para datasets normalizados o consolidados afectados.
- Los logs generados o modificados fueron revisados para confirmar que no contienen PII ni identificadores RUT/NIT/RUC completos.
- Cambios documentados si afectan API, contrato de datos o comportamiento.
