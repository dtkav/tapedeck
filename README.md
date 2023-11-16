# Proxy Service                                                                                                                                                                           
                                                                                                                                                                                          
This repository contains a simple proxy service that can record HTTP requests and replay them. It consists of two main components: `tapedeck.py`, which is a Flask application that acts  
the proxy server, and `cassette.py`, which is a command-line interface (CLI) for interacting with the proxy server.                                                                       
                                                                                                                                                                                          
## Getting Started                                                                                                                                                                        
                                                                                                                                                                                          
To get started with this proxy service, follow these steps:                                                                                                                               
                                                                                                                                                                                          
1. Ensure you have Python installed on your system.                                                                                                                                       
2. Install the required dependencies by running `pip install flask requests click`.                                                                                                       
3. Start the proxy server by running `python tapedeck.py`.                                                                                                                                
4. In a separate terminal, start the CLI by running `python cassette.py`.                                                                                                                 
                                                                                                                                                                                          
## Using the CLI                                                                                                                                                                          
                                                                                                                                                                                          
The CLI provides the following commands:                                                                                                                                                  
                                                                                                                                                                                          
- `history`: Fetches and displays the history of the last 10 proxied requests.                                                                                                            
- `replay <index>`: Replays a request by its index in the history.                                                                                                                        
- `exit`: Exits the CLI.                                                                                                                                                                  
                                                                                                                                                                                          
## Proxy Server Endpoints                                                                                                                                                                 
                                                                                                                                                                                          
The proxy server provides the following endpoints:                                                                                                                                        
                                                                                                                                                                                          
- `/<path:path>`: Proxies requests to the specified path to the upstream URL.                                                                                                             
- `/history`: Returns the history of proxied requests.                                                                                                                                    
- `/replay`: Replays a request based on the provided index in the request history.                                                                                                        
                                                                                                                                                                                          
## Configuration                                                                                                                                                                          
                                                                                                                                                                                          
You can configure the upstream URL by modifying the `UPSTREAM_URL` variable in `tapedeck.py`.                                                                                             
                                                                                                                                                                                          
## License                                                                                                                                                                                
                                                                                                                                                                                          
This project is licensed under the MIT License - see the LICENSE file for details.  
