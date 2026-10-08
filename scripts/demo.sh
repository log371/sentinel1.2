#!/usr/bin/env sh
set -eu

API_URL="${API_URL:-http://localhost:8000}"
curl --fail --silent --show-error -F "file=@examples/documents/pv-assemblee-generale.md;type=text/markdown" "$API_URL/v1/documents"
printf '\n'
curl --fail --silent --show-error -H 'Content-Type: application/json' -d '{"question":"Quels travaux ont ete votes, pour quel montant et avec quel prestataire ?"}' "$API_URL/v1/query"
printf '\n'

