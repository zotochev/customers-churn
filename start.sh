#!/bin/sh

docker build -t zotochev_prolong_image .
docker run -p 5001:5001 -d --rm --name zotochev_prolong_container zotochev_prolong_image
