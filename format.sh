#!/usr/bin/env bash

for i in data/users/*.json; do
	cat $i | jq . > tmp.json
	mv tmp.json $i
done
