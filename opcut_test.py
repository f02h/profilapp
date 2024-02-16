import subprocess
import json


data = {
    "cut_width":2.5,
    'min_initial_usage':True,
    'panels':{
        'p1':{
            'width':4000,
            'height':4
        }
    },
    'items':{
         'i1':{
            'width':400,
            'height':1,
            'can_rotate':False
         },
        'i2':{
            'width':500,
            'height':1,
            'can_rotate':False
         }
      }  
}

with open('params2.json', 'w') as fp:
    json.dump(data, fp)

result = subprocess.run('opcut calculate --method forward_greedy_native --output result.json params2.json', shell=True)