import mainV2 as tv

obj = tv.TextVisualizer('corpus\\')
obj.main()
sims = obj.similarityReq('compare\\')
hist = obj.wordHistory('old', 500)
obj.showSimPlot(sims)
obj.showHistPlot(hist)