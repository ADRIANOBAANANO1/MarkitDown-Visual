#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$HOME/.local/share/applications/markitdown-visual.desktop"

mkdir -p "$(dirname "$DESTINO")"

cat > "$DESTINO" <<EOF
[Desktop Entry]
Type=Application
Name=MarkItDown Visual
Comment=Convierte PDF y otros documentos a Markdown
Exec="$DIR/venv/bin/python" "$DIR/src/gui.py"
Path=$DIR
Terminal=false
Categories=Utility;
Icon=accessories-text-editor
EOF

chmod +x "$DESTINO"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo "Lanzador instalado: $DESTINO"
echo "Buscá 'MarkItDown Visual' en el menú de aplicaciones."
