#!/bin/sh
# Render the generated SVG into launcher-mask previews: preview.sh <gen_out_dir>
set -e
D="$1"; cd "$D"
magick -background none shima-icon-full.svg full.png                       # 432x432 = 108 units * 4
magick full.png -crop 288x288+72+72 +repage visible.png                   # 72dp visible viewport
mask() { magick visible.png \( -size 288x288 xc:none -fill white -draw "$1" \) -compose DstIn -composite "$2"; }
mask "circle 144,144 144,0" m_circle.png
mask "roundrectangle 0,0 287,287 92,92" m_squircle.png
mask "roundrectangle 0,0 287,287 40,40" m_rounded.png
magick -background none -density 384 shima-icon-monochrome.svg -resize 432x432 mono.png
magick mono.png -crop 288x288+72+72 +repage -fill "#3b2b31" -colorize 100 \
  \( -size 288x288 xc:"#f6dfe6" -fill white -draw "circle 144,144 144,0" \) +swap -compose Over -composite m_mono.png
magick m_circle.png m_squircle.png m_rounded.png m_mono.png -background none -gravity east -splice 24x0 -gravity center +append +repage row_big.png
for s in 48 72 96; do magick m_circle.png -resize ${s}x${s} s_$s.png; done
magick s_48.png s_72.png s_96.png -background none -gravity east -splice 24x0 -gravity south +append +repage row_small.png
magick row_big.png row_small.png -background none -gravity west -append +repage -bordercolor "#ECEFF1" -border 24 -background "#ECEFF1" -flatten sheet_light.png
magick row_big.png row_small.png -background none -gravity west -append +repage -bordercolor "#1F1B1D" -border 24 -background "#1F1B1D" -flatten sheet_dark.png
magick sheet_light.png sheet_dark.png -append preview.png
echo "$D/preview.png"
