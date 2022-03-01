# API Reference
## APIRequest

*class* **piwebasync.APIRequest**(*root, method, protocol, controller, scheme, host, *, port=None, action=None, webid=None, add_path=None, ****kwargs*)

Base model for Pi Web API requests. An API request is passed to a client instance to handle the request. You will not typically create APIRequest objects yourself. Generally, you should use the *Controller* object instead. However, for non supported controllers and controller methods you may want to create your own APIRequest directly

**Parameters**
- root (str): root path to PI Web API
- method (str): the HTTP method for the request
- protocol (str): request protocol to use; either *"HTTP"* or *"Websockets"*
- controller (str): the controller being accessed on the PI Web API
- scheme (str): URL scheme; *"http"*, *"https"*, *"ws"*, *"wss"*
- host (str): PI Web API host address
- port (Optional(str)): the port to connect to
- action (Optional(str)): the PI Web API controller method, is a path parameter
- webid (Optional(str)): the WebId of a resource as path parameter
- add_path (Optional(str))
- kwargs (Optional(Any)): query params for controller method

`APIRequest.absolute_url`: Returns full URL path as str

`APIRequest.params`: Returns normalized query params as dict

`APIRequest.path`: Returns URL path

`APIRequest.query`: Returns normalized query params as str

`APIRequest.raw_path`: Returns URL target as str

## APIResponse