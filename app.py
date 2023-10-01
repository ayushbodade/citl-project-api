import requests
from flask import Flask, jsonify, request, render_template

headers_search_anime = {
    "X-RapidAPI-Key": "yourkey",
    "X-RapidAPI-Host": "myanimelist.p.rapidapi.com"
}

headers_get_translations = {
	"content-type": "application/x-www-form-urlencoded",
	"Accept-Encoding": "application/gzip",
	"X-RapidAPI-Key": "yourkey",
	"X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
}

url_get_translations = "https://google-translate1.p.rapidapi.com/language/translate/v2"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('anime_search.html')

@app.route('/anime-search', methods=['GET'])
def search_anime():
    anime_name = request.args.get('name')
    pref_lang = str(request.args.get('language'))
    print("Payload : ",anime_name, pref_lang)
    url = f"https://myanimelist.p.rapidapi.com/anime/search/{anime_name}"
    response = requests.get(url, headers=headers_search_anime).json()
    print("Anime Search Response : ",response)
    anime_data = response[0]  # Assuming you want the first result
    title = anime_data.get("title", "")
    description = str(anime_data.get("description", ""))
    picture_url = anime_data.get("picture_url", "")
    myanimelist_url = anime_data.get("myanimelist_url", "")

    payload = {
	    "q": description,
	    "target": pref_lang
    }
    response = requests.post(url_get_translations, data=payload, headers=headers_get_translations).json()
    print("Text Translation Response : ",response)
    description = response.get('data',{}).get('translations',[])[0].get('translatedText',"")
    print("Text After processing : ",description)
    return render_template(
        'anime_search.html',
        title=title,
        description=description,
        picture_url=picture_url,
        myanimelist_url=myanimelist_url
    )

if __name__ == '__main__':
    app.run(debug=True)
