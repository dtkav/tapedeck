import json                                                                                                                                                                               
import pytest                                                                                                                                                                             
from tapedeck import app                                                                                                                                                                  
                                                                                                                                                                                          
@pytest.fixture                                                                                                                                                                           
def client():                                                                                                                                                                             
    with app.test_client() as client:                                                                                                                                                     
        yield client                                                                                                                                                                      
                                                                                                                                                                                          
def test_proxy_get_request(client):                                                                                                                                                       
    response = client.get('/test')                                                                                                                                                        
    assert response.status_code == 200                                                                                                                                                    
                                                                                                                                                                                          
def test_proxy_post_request(client):                                                                                                                                                      
    headers = {'Content-Type': 'application/json'}                                                                                                                                        
    data = {'key': 'value'}                                                                                                                                                               
    response = client.post('/test', headers=headers, data=json.dumps(data))                                                                                                               
    assert response.status_code == 200                                                                                                                                                    
    assert response.json == data                                                                                                                                                          
                                                                                                                                                                                          
def test_history_endpoint(client):                                                                                                                                                        
    client.get('/test')  # Make a request to add to history                                                                                                                               
    response = client.get('/history')                                                                                                                                                     
    assert response.status_code == 200                                                                                                                                                    
    history = response.json                                                                                                                                                               
    assert len(history) > 0                                                                                                                                                               
    assert history[-1]['path'] == 'test'                                                                                                                                                  
                                                                                                                                                                                          
def test_replay_endpoint(client):                                                                                                                                                         
    client.get('/test')  # Make a request to add to history                                                                                                                               
    history_response = client.get('/history')                                                                                                                                             
    history = history_response.json                                                                                                                                                       
    last_index = len(history) - 1                                                                                                                                                         
    replay_response = client.post('/replay', json={'index': last_index})                                                                                                                  
    assert replay_response.status_code == 200
