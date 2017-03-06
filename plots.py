from bokeh.plotting import figure, show, output_file
from bokeh.charts.utils import df_from_json
from bokeh.models import HoverTool, ranges
from bokeh.charts import Donut, Bar
import random



def hbarLength(right):
    p = figure(width=800, height=100, y_range=['AvarageSentenceLength(Chars)', 'AvarageSentenceLength(Tokens)', 'AvarageTokenLength(Chars)'], title="AvarageStatistics")
    p.hbar(y=[1, 2, 3], height=0.3, left=0, right=right, color="green")
    return p

def hbarMCT(y_range, right):
    #print(y_range)
    p = figure(width=400, height=350, y_range=y_range, title="MostCommonTypes")
    p.hbar(y=[i + 1 for i in range(len(y_range))], height=0.1, left=0, right=right, color="navy")
    return p

def donutLsi(data):
    TOOLS = 'box_zoom,hover,crosshair,resize,reset'
    dat = {'object': 'list'}  # {'type': 'old', 'contr': -3.5}, {'type': 'cold', 'contr': -4.45}
    dat['data'] = data
    df = df_from_json(dat)
    TITLE = "LSI Topic #"+ str(data[0]['nr'])
    d = Donut(df, label='type', text_font_size='10pt', hover_text='Test', values='contr', toolbar_location="right", tools=TOOLS, title=TITLE)
    return d

def barDocLsi(data): 
    data = {
    'doc': [i for i in range(len(data))],
    'contr': data
    }
    # x-axis labels pulled from the interpreter column, stacking labels from sample column
    bar = Bar(data, values='contr', label='doc',
           agg='mean', title="Document contribution", plot_width=200, color="olive")
    return bar

def barSim(data):
    data = {
    'doc': data[0],
    'similarity': data[1]
    }
    bar = Bar(data, values='similarity', label='doc',
            agg='mean',
            title="Similarity between given document and corpus documents",
            plot_width=500, plot_height=900, color="SteelBlue", legend=None, bar_width=0.6)
    return bar

def lineHistory(data):
    x = data[0]
    y = data[1]
    word = data[2]
    TITLE = "History of '" + word + "' in documents"
    p = figure(plot_width=800, plot_height=400, title=TITLE)
    colors=['Cyan', 'Aqua', 'Brown', 'Chartreuse', 'Crimson', 'DarkOrange', 'DarkGreen', 'DarkMagenta', 'HotPink', 'Yellow']
    for i in range(len(x)):
        p.line(x[i], y[i], line_width=2, legend="doc"+str(i), color=random.choice(colors))
    return p

if __name__ == '__main__':
    main()


"""
d = donutLsi(5)
output_file("do.html")
show(d)
"""