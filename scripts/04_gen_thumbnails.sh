set -e

mkdir -p thumbs

echo "Generating thumbnails..."

for f in $@; do
  convert -thumbnail 120x120 +dither -depth 8 -colors 256 $f PNG8:`dirname $f`/thumbs/`basename $f`
done;

echo "Generating JPG copies..."

mogrify -format jpg -quality 85 *.png