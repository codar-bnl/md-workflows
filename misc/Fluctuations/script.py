import extractData as ed

#ed.collectData("prova","exp-clean","info")
data = ed.readFileAndGroupBy("prova",[0,4],6)
#print(data['3468773'])
