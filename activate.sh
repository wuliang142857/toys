#!/usr/bin/env bash


SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  TARGET=$(readlink "$SOURCE")
  if [[ $TARGET == /* ]]; then
    echo "SOURCE '$SOURCE' is an absolute symlink to '$TARGET'"
    SOURCE=$TARGET
  else
    DIR=$( dirname "$SOURCE" )
    echo "SOURCE '$SOURCE' is a relative symlink to '$TARGET' (relative to '$DIR')"
    SOURCE=$DIR/$TARGET # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  fi
done
current_dir=$(dirname $(readlink -f $SOURCE))
export PATH=${current_dir}/noarch:$PATH

# 得到的事Linux、Darwin之类
os_name=$(uname -s)
# 得到是x86_64之类
arch_name=$(uname -m)

if [[ "$os_name" == 'Linux' &&  "$arch_name" == 'x86_64' ]]; then
   export PATH=${current_dir}/linux-amd64:$PATH
elif [[ "$os_name" == 'Linux' &&  "$arch_name" == 'x86' ]]; then
   export PATH=${current_dir}/linux-x86:$PATH
elif [[ "$os_name" == 'Linux' &&  "$arch_name" == 'arm64' ]]; then
   export PATH=${current_dir}/linux-arm64:$PATH
elif [[ "$os_name" == 'Linux' &&  "$arch_name" == 'armv7l' ]]; then
   export PATH=${current_dir}/linux-armv7:$PATH
elif [[ "$os_name" == 'Darwin' && "$arch_name" == 'x86_64' ]]; then
   export PATH=${current_dir}/darwin-amd64:$PATH
elif [[ "$os_name" == 'Darwin' && "$arch_name" == 'x86' ]]; then
   export PATH=${current_dir}/darwin-x86:$PATH
elif [[ "$os_name" == 'Darwin' && "$arch_name" == 'arm64' ]]; then
   export PATH=${current_dir}/darwin-arm64:$PATH
fi
