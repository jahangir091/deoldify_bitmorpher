#!/usr/bin/env bash
#################################################
# Please do not make any changes to this file,  #
# change the variables in webui-user.sh instead #
#################################################


prepare_installation(){
  apt update -y
  apt upgrade -y
  apt install htop -y
  apt install git -y
  apt install libgl1 libglib2.0-0 -y
  git clone https://github.com/jahangir091/deoldify_custom.git
  cd
  cd /deoldify_custom
  wget https://huggingface.co/spensercai/DeOldify/resolve/main/ColorizeStable_gen.pth
  wget https://huggingface.co/spensercai/DeOldify/resolve/main/ColorizeArtistic_gen.pth
  wget https://huggingface.co/spensercai/DeOldify/resolve/main/ColorizeVideo_gen.pth
  python3 -m venv env_deoldify
  source env_deoldify/bin/activate
  pip install -r requirements.txt

  rm -rf /var/log/deoldify
  mkdir /var/log/deoldify
  touch /var/log/deoldify/access.log
  touch /var/log/deoldify/error.log
  chmod 777 -R /var/log/deoldify

  rm -rf /etc/systemd/system/deoldify.service
  cp deoldify.service /etc/systemd/system/
  systemctl daemon-reload
  systemctl start deoldify
  systemctl enable deoldify
  systemctl restart deoldify

  service deoldify restart
}

start_rembg(){
  cd
  cd deoldify_custom
  service deoldify restart
}

update_rembg(){
  cd
  cd /deoldify_custom
  git fetch
  git reset --hard origin/master
}


install="install"
start="start"
update="update"


if [ "$1" == "$start" ]
then
  start_rembg
elif [ "$1" == "$install" ]
then
  prepare_installation
  start_rembg
elif [ "$1" == "$update" ]
then
  update_rembg
else
  printf "\n\n expected flags 'install' or 'start' or 'update'\n\n"
fi
#uvicorn main:app --host 0.0.0.0 --port 8001 --reload
#gunicorn main:app --workers "$1" --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:"$2"
