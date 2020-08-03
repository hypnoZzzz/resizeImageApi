#README
*Good day! 
Sorry for my google- english*

**This is a small API service for changing the width and height of images. 
It works with jpg and png files.**

1. ###To work with the application, download the repository to your device and go to the console in the project folder;
2. ###Create a virtual environment:
	- for Windows:
     python -m venv venv;
	- for linux-types of systems:
     python3 -m venv venv;
3. ###Activate venv:
	- for Windows:
     cd venv/Scripts $activate;
	- for linux-types of systems:
     source venv/bin/activate;
4. ###Install dependency packages:
	- for Windows:
     pip install -r requirements.txt;
	- for linux-types of systems:
     pip install -r requirements.txt;
5. ###Run the app.py file:
	- for Windows:
     python app.py;
	- for linux-types of systems:
     python3 app.py;

> *The application will run at (http://localhost: 85/)*

6. ###The server responds to comments using the curl utility. 
	- ######An example of receiving a request correctly:
		curl -i http://localhost:85/
	- ######An example of a valid post request:
		for Windows:
		curl -i -H "Content-Type: application/json" -X POST -d "{"""file""": """<PATH_TO_FILE>/<FILE_NAME>"""}" http://localhost: 85/image_change_service/api/v1.0/add_image;
		for linux-like systems:
		curl -i -H "Content-Type: application/json" -X POST -d '{"file": "<PATH_TO_FILE>/<FILE_NAME>"}' http://localhost: 85/image_change_service/api/v1.0/add_image;

7. ###Application routes:
			####GET REQUESTS
		- Checking server status: '/';
		- Getting information about a file by its id: '/image_change_service/api/v1.0/images/<int:id>';
		- Getting information about existing tasks: '/image_change_service/api/v1.0/images/tasks_counter';
		- Saving the modified file to the path specified by the client: 'start SERVER_URL/image_change_service/api/v1.0/download_file/<int:id>';
			####POST REQUESTS
		- Send the file for processing: '/image_change_service/api/v1.0/add_image';
		> for Windows: curl -i -H "Content-Type: application/json" -X POST -d "{"""file""": """<PATH_TO_FILE>/<FILENAME>"""}" http://localhost:85/image_change_service/api/v1.0/add_image;
		> for linux-like systems: curl -i -H "Content-Type: application/json" -X POST -d '{"file": "<PATH_TO_FILE>/<FILENAME>"}' http://localhost:85/image_change_service/api/v1.0/add_image;
		- Create a task: '/image_change_service/api/v1.0/add_task';
			>example for Windows: curl -i -H "Content-Type: application / json" -X POST -d "{"""id""": <FILE ID>, """required_height""": 50, """required_width""": 50}" http://localhost: 85/image_change_service/api/v1.0/add_task;
			>for linux-like systems: curl -i -H "Content-Type: application / json" -X POST -d '{"id": <FILE ID>, "required_height": 50, "required_width": 50}' http://localhost: 85/image_change_service/api/v1.0/add_task;