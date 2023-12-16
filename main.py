# main.py

from fastapi import FastAPI, File, UploadFile , Form ,HTTPException
from fastapi.responses import JSONResponse
import requests
import time
import json
import json
import re
import pickle
app = FastAPI()

global_cf_tunnel = ""
global_bearer_token = ""
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/loadenv")
def setenv(cf_tunnel: str, bearer_token: str ):
    global global_cf_tunnel, global_bearer_token
    global_cf_tunnel = cf_tunnel
    global_bearer_token = bearer_token

    return {"item_id": global_cf_tunnel, "query_param": global_bearer_token}


@app.post("/geturl")
def geturl(input_url:str):
    url = f"{global_cf_tunnel}/tasks/create/submit"
    headers = {"Authorization": f"Bearer {global_bearer_token}"}
    response = requests.post(url, headers=headers,data={"strings":f"{input_url}"})
    data = response.json()
    task_id = data["task_ids"][0]
    # task_id = response.json()["task_id"]
    family = get_tasksummary(task_id)
    return {"ransom_family": family}


@app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile = File(...), item_id: int = Form(...), query_param: str = Form(...)):
def create_upload_file(file: UploadFile = File(...)):
    # Global list to store filenames
    uploaded_filenames = []
    print("filename is " ,file.filename )
    uploaded_filenames.append(file.filename)

    # Send to cuckoo
    
    files = {"files": (file.filename, file.file)}
    headers = {"Authorization": f"Bearer {global_bearer_token}"}
    url = f"{global_cf_tunnel}/tasks/create/submit"
    try:
        response = requests.post(url, headers=headers, files=files)
        # response.raise_for_status()
        data = response.json()
        task_id = data["task_ids"][0]
        family = get_tasksummary(task_id)
        print(family[0])
        # return JSONResponse(content=family, status_code=200)
        return {"predicted_family": family[0]}


        # return {"ransom_family": family}

        # Return the response from the external endpoint
        # return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to external endpoint failed: {str(e)}")
    # return {"filename": file.filename}


def get_tasksummary(task_id):
    start_time = time.time()  # Record the start time

    url = f"{global_cf_tunnel}/tasks/view/{task_id}"
    headers = {"Authorization": f"Bearer {global_bearer_token}"}
    response = requests.get(url, headers=headers)
    parsed_data = response.json()

    # content = response.content
    # with open("data.json", "wb") as outfile:
    #     outfile.write(content)
    # print("Data saved successfully!")

    status = parsed_data['task']['status']
    # print(f"Initial status: {status}")

    while status != 'reported':
        elapsed_time = time.time() - start_time
        if elapsed_time > 900:  # Check if 10 minutes (600 seconds) have passed
            print("Task status not reported within 10 minutes. Returning unable to complete.")
            return "Unable to complete"

        print(f"Task not reported yet. Waiting for a minute...")
        time.sleep(60)  # Wait for one minute (60 seconds)

        # Send the cURL request again
        response = requests.get(url, headers=headers)

        # parsed_data = json.loads(response.stdout)
        parsed_data =  response.json()
        # print(parsed_data)
        status = parsed_data['task']['status']
        print(f"Updated status: {status}")

        if status == 'reported':
            print("Task status has changed to reported.")
            savereport(task_id)
            api_list = ["CreateToolhelp32Snapshot", "DeviceIoControl", "EnumWindows", "GetAdaptersAddresses", "GetComputerNameA", "GetComputerNameW", "GetDiskFreeSpaceExW", "GetSystemInfo", "GetSystemMetrics", "GetUserNameA", "GetUserNameW", "LdrGetProcedureAddress", "NtClose", "NtCreateFile", "NtEnumerateKey", "NtOpenDirectoryObject", "NtOpenKey", "NtQuerySystemInformation", "NtQueryValueKey", "ReadProcessMemory", "RegCloseKey", "SetWindowsHookExA", "SetWindowsHookExW"]
            with open('report.json', 'r') as json_file:
                parsed_data = json.load(json_file)
            # Convert the JSON data to a string for regex matching
            json_string = json.dumps(parsed_data, indent=2)

            result_list = [1 if re.search(fr'\b{api}\b', json_string) else 0 for api in api_list]
            print(result_list)

            filename = 'random_forest_model.pkl'
            pkl_classifier = pickle.load(open(filename, 'rb'))
            y_pred = pkl_classifier.predict([result_list])
            print(y_pred)
            return y_pred
            # response_data = {"predicted_family": y_pred}
            # return response_data


            
            
            # family = predict_family(task_id)
            # # return "reported "
            # print("Return Family is",family)

            # return family

            break  # Exit the loop once the status is reported

    return print("Task status is now reported.")

def predict_family(task_id):

    # Define the URL and headers
    url = f"{global_cf_tunnel}/tasks/summary/{task_id}"
    headers = {"Authorization": f"Bearer {global_bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # response = response.json()
        # content = response.json()
        content = response.content

        with open("report.json", "wb") as outfile:
            outfile.write(content)
        print("Data saved successfully!")
    else:
        # Handle error
        print(f"Error hai pranjal : {response.status_code}")
        print(response.text)


    # List of APIs to check
    api_list = [
        "CreateToolhelp32Snapshot",
        "DeviceIoControl",
        "EnumWindows",
        "GetAdaptersAddresses",
        "GetComputerNameA",
        "GetComputerNameW",
        "GetDiskFreeSpaceExW",
        "GetSystemInfo",
        "GetSystemMetrics",
        "GetUserNameA",
        "GetUserNameW",
        "LdrGetProcedureAddress",
        "NtClose",
        "NtCreateFile",
        "NtEnumerateKey",
        "NtOpenDirectoryObject",
        "NtOpenKey",
        "NtQuerySystemInformation",
        "NtQueryValueKey",
        "ReadProcessMemory",
        "RegCloseKey",
        "SetWindowsHookExA",
        "SetWindowsHookExW"
    ]

    with open('report.json', 'r') as json_file:
        parsed_data = json.load(json_file)
    # Convert the JSON data to a string for regex matching
    json_string = json.dumps(parsed_data, indent=2)
    # json_string = json.dumps(content, indent=2)


    # Search for APIs using regular expressions
    result_list = [1 if re.search(fr'\b{api}\b', json_string) else 0 for api in api_list]
    print(result_list)

    filename = 'random_forest_model.pkl'
    pkl_classifier = pickle.load(open(filename, 'rb'))
    y_pred = pkl_classifier.predict([result_list])
    print(y_pred)
    response_data = {"predicted_family": y_pred}
    return response_data
    # return y_pred


def savereport(task_id):
   # Define the URL and headers
    url = f"{global_cf_tunnel}/tasks/summary/{task_id}"
    headers = {"Authorization": f"Bearer {global_bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # response = response.json()
        # content = response.json()
        content = response.content

        with open("report.json", "wb") as outfile:
            outfile.write(content)
        print("Data saved successfully!")
    else:
        # Handle error
        print(f"Error hai pranjal : {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
