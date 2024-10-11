#!/usr/bin/env bash

docker_container="act-BuildBinary-build-bot"
docker_build_dir="docker-build"

act -j build_bot
echo "---------------------------------------"
echo "---------------------------------------"
docker_container=$(docker ps --format "{{.Names}}" | grep $docker_container)
echo "Copy firmwares from $docker_container to $(pwd)"

hash=$(git log -1 --format=%h 2>&1)

rm -rf $docker_build_dir 2> /dev/null

docker cp $docker_container:$(pwd)/dist ./$docker_build_dir
docker rm -f $docker_container

cd $docker_build_dir && zip ../jirabot_$hash.zip * && cd ../
rm -rf $docker_build_dir
