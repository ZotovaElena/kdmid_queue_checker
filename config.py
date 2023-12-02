# -*- coding: utf-8 -*-

with open('token.key', 'r') as fh:
    data = fh.read()
    
TOKEN = data.strip()
EVERY_HOURS=2