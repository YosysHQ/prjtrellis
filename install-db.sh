#!/bin/sh

if [ -d "$MESON_SOURCE_ROOT/../database" ]; then
    mkdir -p "$DESTDIR/$MESON_INSTALL_PREFIX/share/trellis"
    cp -a "$MESON_SOURCE_ROOT/../database" "$DESTDIR/$MESON_INSTALL_PREFIX/share/trellis/"
fi
