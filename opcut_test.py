import subprocess
import json


panels = [4000,4000]
items = [400,500]

pOut = {}
pIndex = 1
for p in panels:
    pOut["p"+str(pIndex)] = {
        'width':p,
        'height':4
    }
    pIndex += 1

iOut = {}
iIndex = 1
for i in items:
    iOut["i"+str(iIndex)] = {
        'width':i,
        'height':1,
        'can_rotate':False
    }
    iIndex += 1

    
jsonOut = {
    "cut_width":2.5,
    'min_initial_usage':True,
}

jsonOut['panels'] = pOut
jsonOut['items'] = iOut

'''
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
'''


with open('params2.json', 'w') as fp:
    json.dump(jsonOut, fp)

result = subprocess.run('opcut calculate --method forward_greedy_native --output result.json params2.json', shell=True)

f = open('result.json')
resultData = json.load(f)
print("Predlog odreza:")
for i in resultData['used']:
    print(i['item']+" dolzina: "+str(iOut[i['item']]['width'])+"mm "+i['panel']+" rez: "+str(i['x'])+"mm")
print()
print("Ostanek:")
for i in resultData['unused']:
    if i['height'] == 4.0:
        print(i['panel']+" "+str(i['width']))