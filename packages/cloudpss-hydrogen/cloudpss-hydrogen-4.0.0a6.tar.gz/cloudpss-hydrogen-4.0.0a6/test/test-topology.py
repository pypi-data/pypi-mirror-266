import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..\\'))
import cloudpss
import time
import numpy as np
import pandas as pd
import json

if __name__ == '__main__':
    os.environ['CLOUDPSS_API_URL'] = 'http://10.101.10.45/'
    print('CLOUDPSS connected')
    cloudpss.setToken(
        'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInNjb3BlcyI6WyJtb2RlbDo5ODMzNSIsImZ1bmN0aW9uOjk4MzM1IiwiYXBwbGljYXRpb246OTgzMzUiXSwicm9sZXMiOlsiYWRtaW4iXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzI0NTU3MDIzLCJub3RlIjoiYSIsImlhdCI6MTY5MzQ1MzAyM30._Xuyo62ESKLcIAFeNdnfBM44yPiiXli9OPKvXDzL2rPV4J1_qsGZP--bsS1tXAVy-x8ooUIIAAG1yhwmZuk7-Q')
    print('Token done')
    # project = cloudpss.Model.fetch('model/admin/7744b02b-0636-5a39-8c16-eca939259ee1')
    t = time.time()
    topology = cloudpss.ModelTopology.fetch("24sne1BQ_lLCRLBnVl7_9QdhR70HxKIWsmIpKMF4iBw6tTt-h6ZkB-vUgm-nfDp2","emtp",{'args':{}})
    # topology = cloudpss.ModelTopology.fetch("JwHbZdjco9eC0nZw3fY7Iz9rqsQ4HFGJObiBW3bFuYLPCd0Vqb2vb8zNY28D1AXV","emtp",{'args':{}})
    print(time.time()-t)
    
    
    
    # topology= project.fetchTopology(config={'args':{}})

    # topology.dump(topology,'test.json')
    
    
    