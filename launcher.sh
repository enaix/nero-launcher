#!/bin/bash

cd ~

nohup $1 </dev/null &>/dev/null 2>&1 &  
