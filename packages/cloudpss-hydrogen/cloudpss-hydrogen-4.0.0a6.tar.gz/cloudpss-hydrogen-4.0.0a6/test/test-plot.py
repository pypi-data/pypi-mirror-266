import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..\\'))

import cloudpss
if __name__ == '__main__':
    job = cloudpss.currentJob()
    
    
    job.plot(traces= [
        { 'name': 'trace1', 'type': 'scatter', 'x': [1, 2, 3], 'y': [1, 2, 3] },
            { 'name': 'trace2', 'type': 'bar', 'x': [1, 2, 3], 'y': [1, 2, 3] },
        ], layout= {
            'xaxis': { 'title': 'x坐标' },
            'yaxis': { 'title': 'y坐标' },
        },title= 'My Plot', key='plot-1')