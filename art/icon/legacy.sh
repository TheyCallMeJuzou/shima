#!/bin/sh
# Legacy (pre-API 26) launcher PNGs + 512px store icon from the generated SVG: legacy.sh <gen_out_dir>
set -e
D="$1"; cd "$D"; mkdir -p legacy
magick -background none -density 384 shima-icon-full.svg -resize 1728x1728 hi.png          # 108 units * 16
magick hi.png -crop 1152x1152+288+288 +repage hi_visible.png                                # 72-unit visible area
magick hi_visible.png -resize 512x512 legacy/shima-icon-512.png
for pair in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
  dpi=${pair%%:*}; s=${pair##*:}; mkdir -p legacy/mipmap-$dpi
  inner=$((s * 44 / 48)); off=$(( (s - inner) / 2 )); r=$((inner * 12 / 100)); sh=$((s / 48 + 1))
  for shape in square round; do
    if [ $shape = square ]; then draw="roundrectangle 0,0 $((inner-1)),$((inner-1)) $r,$r"; name=ic_launcher
    else draw="circle $((inner/2)),$((inner/2)) $((inner/2)),0"; name=ic_launcher_round; fi
    magick hi_visible.png -resize ${inner}x${inner} \( -size ${inner}x${inner} xc:none -fill white -draw "$draw" \) \
      -compose DstIn -composite art.png
    magick art.png \( +clone -background black -shadow 30x${sh}+0+${sh} \) +swap -background none -layers merge +repage shadowed.png
    magick -size ${s}x${s} xc:none shadowed.png -gravity center -geometry +0+$((sh/2)) -composite legacy/mipmap-$dpi/$name.png
  done
done
rm -f art.png shadowed.png
ls -R legacy | head -30
