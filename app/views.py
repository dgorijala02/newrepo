import json
import os
import requests
from flask import render_template, redirect, request,send_file
from werkzeug.utils import secure_filename
from app import app

# Stores all the post transaction in the node
request_tx = []
#store filename
files = [0]
#destiantion for upload files
UPLOAD_FOLDER = "/E:/Fall 2023/4300/Project/Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# store  address
ADDR = "http://127.0.0.1:8800"


#create a list of requests that peers has send to upload files
def get_tx_req():
    global request_tx
    chain_addr = "{0}/chain".format(ADDR)
    resp = requests.get(chain_addr)
    if resp.status_code == 200:
        content = []
        chain = json.loads(resp.content.decode())
        for block in chain["chain"]:
            for trans in block["transactions"]:
                trans["index"] = block["index"]
                trans["hash"] = block["prev_hash"]
                content.append(trans)
        request_tx = sorted(content,key=lambda k: k["hash"],reverse=True)


# Loads and runs the home page
@app.route("/")
def index():
    get_tx_req()
    return render_template("index.html",title="FileStorage",subtitle = "A Decentralized Network for File Storage/Sharing",node_address = ADDR,request_tx = request_tx)


@app.route("/submit", methods=["POST"])
# When new transaction is created it is processed and added to transaction
def submit():
    user = request.form["user"]
    up_file = request.files["v_file"]
    #save the uploaded file in destination
    up_file.save(os.path.join("E:/Fall 2023/4300/Project/Uploads/",secure_filename(up_file.filename)))
    #create a transaction object
    post_object = {
        "user": user,
        "v_file" : up_file.filename
    }
    #add the file to the list to create a download link
    files[0] = "E:/Fall 2023/4300/Project/Uploads/"+up_file.filename
    # Submit a new transaction
    address = "{0}/new_transaction".format(ADDR)
    requests.post(address, json=post_object)
    return redirect("/")

#creates a download link for the file
@app.route("/submit")
def download_file():
    p = files[0]
    return send_file(p,as_attachment=True)

