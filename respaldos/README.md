# Respaldos locales

Los respaldos PostgreSQL se guardan con el formato:

```text
tesismcp_respaldo_YYYY-MM-DD_HHMMSS.dump
```

Para crear uno con fecha y hora automáticas:

```bash
python3 scripts/respaldar_base.py
```

Los archivos `.dump` y sus sumas `.sha256` están excluidos de Git porque pueden contener información sensible. Deben copiarse además a un almacenamiento externo protegido.
