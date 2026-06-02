#!/bin/sh
set -eu

# Executa o pg_restore usando as variáveis de ambiente nativas do container
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v /docker-entrypoint-initdb.d/dump-ecommerce.dump

# Marca que a restauração terminou; o healthcheck usa este arquivo para só liberar dependências quando o banco estiver realmente pronto.
touch /var/lib/postgresql/data/.restore-complete
