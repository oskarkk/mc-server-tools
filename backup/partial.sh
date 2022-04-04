#!/bin/bash


dir="/home/oskark/backup/spigot"
spigot="/home/mc/spigot"
world=$spigot"/worlds/world/region"
bkpdate=$(date +"%Y-%m-%d--%H-%M")
mca="/home/oskark/software/mca-selector/mca.sh"
linkdest="../../../../latest/worlds/world/region"

info="-hh --info=progress2 --no-i-r --stats"
filter='xPos < 150 AND xPos > -150 AND zPos > -600 AND zPos < 300 OR InhabitedTime > 60'


shopt -s expand_aliases
source /home/oskark/various/bash/mc.sh

spigsay PELNA KOPIA ZAPASOWA SERWERA START

# sprawdzanie miejsca na dysku
free=`df --output=avail / | tail -1`
if [ $free -lt 15000000 ]; then
  spigsay MAŁO MIEJSCA NA DYSKU, POWIADOM NIEZWŁOCZNIE PREZESA
  exit
fi

sudo ~mc/permfix.sh



# PHASE 1 - copy everything except regions
cd $dir
mkdir full/"$bkpdate"
rsync $info -a --link-dest=../latest/ --exclude-from=ignore-partial $spigot/ full/"$bkpdate"
if [ $? -ne 0 ]; then
  spigsay BŁĄD KOPII, POWIADOM NIEZWŁOCZNIE PREZESA
  exit
fi


# PHASE 2 - copy filtered regions to temp dir
rm tempbkp/*
nice -n 15 $mca --mode export --region $world --query "$filter" --output-region tempbkp


# PHASE 3 - change modifiction times back to original times
cd $dir/tempbkp
chgrp mc *
chmod g+w *

for file in *; do
    touch -r $world/$file $file
done

cd ..


# PHASE 4 - place files in the backup dir and try to hardlink them to the previous backup
rsync $info -a --link-dest=$linkdest tempbkp/ full/"$bkpdate"/worlds/world/region



cd full
rm -f latest			# usuniecie poprzedniego linku
ln -s "$bkpdate" latest	# nowy link do nowego backupa

# delete backups older than 12 days and not taken on days that end with 0 or 5
find -depth -maxdepth 1 -ctime +9 -regextype egrep -regex "^.{11}[^05].*" -print -exec rm -rf {} + >> ../delete.log
# delete backups older than a month and a half and not taken on days that end with 0
find -depth -maxdepth 1 -ctime +45 -regextype egrep -regex "^.{11}[^0].*" -print -exec rm -rf {} + >> ../delete.log

spigsay PELNA KOPIA ZAPASOWA SERWERA STOP
