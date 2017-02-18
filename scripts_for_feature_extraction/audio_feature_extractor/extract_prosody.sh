#!/bin/bash
#SBATCH -p standard
#SBATCH -J coopetition
#SBATCH -o /scratch/mtanveer/coopetition/praat_%j_%a
#SBATCH --mem=0gb
#SBATCH -t 23:58:00

# Note: Obtain PRAAT from: http://www.fon.hum.uva.nl/praat/
# Note 2: Obtain FFMPEG from https://ffmpeg.org/

module load praat
module load ffmpeg
for inp in ./videos/*.mp4
do
    echo $inp
    temp=${inp/videos/audio}
    out=${temp/mp4/mp3}
    ffmpeg -i $inp $out
    praat ./prosody-tanveer.praat $out
    mv output.formant ${out/mp3/formant}
    mv output.loud ${out/mp3/loud}
    mv output.pitch ${out/mp3/pitch}
    rm $inp
    rm $out
done

