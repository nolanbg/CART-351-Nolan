from flask import Flask,render_template,request,redirect,url_for
import requests
app = Flask(__name__)


# the default route
@app.route("/")
def index():
      return render_template("index.html")

#*************************************************
#Task-1: GET REQUEST
@app.route("/t1")
def t1():
    return render_template("t1.html",have_results=False)
#*************************************************
@app.route("/getSearchCriteria")
def getSearchCriteria():
    #fill me in :
    # 1. Take the user input from the client
    userInput = request.args.get("search", "").strip()
    # 2. Formulate the URL for the NASA Image API
    url = "https://images-api.nasa.gov/search"
    params = {"q": userInput, "media_type": "image"}
    # 3. Perform the request and retrieve the JSON result
    response = requests.get(url, params=params)
    data = response.json()
    # 4. Access the list of items
    items = data['collection']['items']
    # 5. First element -> first image href and first description
    first = items[0]
    imgFromNasa = first['links'][0]['href']
    description = first['data'][0]['description']

    #replace the empty space to be url encoded
    imgFromNasa = imgFromNasa.replace(' ', '%20')
    return render_template("t1.html",
                               have_results = True,
                               description=description,
                               imgPath = imgFromNasa
                                           
                            )
    pass

#*************************************************
# Task-2: GET REQUEST
@app.route("/t2")
def t2():
    return render_template("t2.html")
#*************************************************
@app.route("/getSearchCriteria_adv")
def getSearchCriteria_adv():
    # 1. Take the user input from the client
    userInput = request.args.get("search", "").strip()

    # 2. Formulate the URL and perform the request
    url = "https://images-api.nasa.gov/search"
    params = {"q": userInput, "media_type": "image"}
    response = requests.get(url, params=params)
    data = response.json()

    # 3. Iterate through the items and collect every image link
    encodedImageLinks = []
    for item in data['collection']['items'][:4]:  # limit to first 4 items
        links = item.get('links')
        if not links:
            continue  # skip items without an image link
        singleImage = links[0]['href']
        encodedImageLinks.append(singleImage.replace(' ', '%20'))

    return render_template("t2.html", images=encodedImageLinks)
#*************************************************

#run
app.run(debug=True)