import xbmcaddon,os,xbmc,xbmcvfs,time
import simplejson as json
from Utils import *
import urllib
from urllib2 import Request, urlopen

moviedb_key = '34142515d9d23817496eeb4ff1d223d0'      
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def HandleTheMovieDBMovieResult(results):
    base_url,size = GetMovieDBConfig()
    movies = []
    log("starting HandleTheMovieDBMovieResult")
    if True:
        for movie in results:
            log(movie)
            newmovie = {'Art(fanart)': base_url + size + str(movie.get('backdrop_path',"")),
                        'Art(poster)': base_url + size + str(movie.get('poster_path',"")),
                        'Title': movie.get('title',""),
                        'OriginalTitle': movie.get('original_title',""),
                        'ID': movie.get('id',""),
                        'Rating': movie.get('vote_average',""),
                        'ReleaseDate':movie.get('release_date',"")  }
            if not str(movie['id']) in str(movies):
                movies.append(newmovie)
    else:
        log("Error when handling TheMovieDB movie results")
    return movies
    
def HandleTheMovieDBListResult(results):
    base_url,size = GetMovieDBConfig()
    lists = []
    if True:
        for list in results["results"]:
            newlist = {'Art(poster)': base_url + size + str(list.get('poster_path',"")),
                        'Title': list['name'],
                        'ID': list['id'],
                        'Description': list['description']}
            lists.append(newlist)
    else:
        pass
    return lists
    
def HandleTheMovieDBPeopleResult(results):
    people = []
    if True:
        for person in results:
            newperson = {'adult': person['adult'],
                        'name': person['name'],
                        'also_known_as': person['also_known_as'],
                        'biography': person['biography'],
                        'birthday': person['birthday'],
                        'id': person['id'],
                        'deathday': person['deathday'],
                        'place_of_birth': person['place_of_birth'],
                        'thumb': person['profile_path']  }
            people.append(newperson)
    else:
        log("Error when handling TheMovieDB people results")
    return people
    
def HandleTheMovieDBCompanyResult(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    if True:
        for company in results:
            newcompany = {'parent_company': company['parent_company'],
                        'name': company['name'],
                        'description': company['description'],
                        'headquarters': company['headquarters'],
                        'homepage': company['homepage'],
                        'id': company['id'],
                        'logo_path': company['logo_path'] }
            companies.append(newcompany)
    else:
        log("Error when handling TheMovieDB companies results")
    return companies
    
def SearchforCompany(Company):
    response = GetMovieDBData("http://api.themoviedb.org/3/search/company?query=%s&api_key=%s" % (urllib.quote_plus(Company),moviedb_key))
    if len(response["results"]) > 0:
        return response["results"][0]["id"]
    else:
        return ""
        
def GetPersonID(person):
    response = GetMovieDBData("http://api.themoviedb.org/3/search/person?query=%s&api_key=%s" % (urllib.quote_plus(person),moviedb_key))
    if len(response["results"]) > 0:
        return response["results"][0]["id"]
    else:
        return ""

def GetMovieDBData(url):
    log("Downloading MovieDB Data: " + url)
    headers = {"Accept": "application/json"}
    request = Request(url, headers = headers)
    response = urlopen(request).read()
    return json.loads(response)
        
def GetMovieDBConfig():
    filename = Addon_Data_Path + "/MovieDBConfig.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return (results["images"]["base_url"],results["images"]["poster_sizes"][-1])
    else:
        headers = {"Accept": "application/json"}
        request = Request("http://api.themoviedb.org/3/configuration?api_key=%s" % (moviedb_key), headers=headers)
        response = urlopen(request).read()
        save_to_file(response,"MovieDBConfig",Addon_Data_Path)
        results = json.loads(response)
        return (results["images"]["base_url"],results["images"]["poster_sizes"][-1])
    
def GetCompanyInfo(Id):
    response = GetMovieDBData("http://api.themoviedb.org/3/company/%s/movies?append_to_response=movies&api_key=%s" % (Id,moviedb_key))
    return HandleTheMovieDBMovieResult(response["results"])
    
def GetExtendedMovieInfo(Id):
    base_url,size = GetMovieDBConfig()
    response = GetMovieDBData("http://api.themoviedb.org/3/movie/%s?append_to_response=trailers,casts&api_key=%s" % (Id,moviedb_key))
    if 1 == 1:
        authors = []
        directors = []
        genres = []
        for item in response['genres']:
            genres.append(item["name"])
        for item in response['casts']['crew']:
            if item["job"] == "Author":
                authors.append(item["name"])
            if item["job"] == "Director":
                directors.append(item["name"])
        Writer = " / ".join(authors)
        Director = " / ".join(directors)
        Genre = " / ".join(genres)
        if len(response['trailers']['youtube']) > 0:
            Trailer = response['trailers']['youtube'][0]['source']
        else:
            Trailer = ""
        if len(response['production_countries']) > 0:
            Country = response['production_countries'][0]["name"]
        else:
            Country = ""
        if len(response['production_companies']) > 0:
            Studio = response['production_companies'][0]["name"]
        else:
            Studio = ""
        Set = response.get("belongs_to_collection","")
        if Set:
            SetName = Set.get("name","")
            SetID = Set.get("id","")         
        else:
            SetName = ""
            SetID = ""
        newmovie = {'Art(fanart)': base_url + size + str(response.get('backdrop_path',"")),
                    'Fanart': base_url + size + str(response.get('backdrop_path',"")),
                    'Art(poster)': base_url + size + str(response.get('poster_path',"")),
                    'Poster': base_url + size + str(response.get('poster_path',"")),
                    'Title': response.get('title',""),
                    'Label': response.get('title',""),
                    'Tagline': response.get('tagline',""),
                    'RunningTime': response.get('runtime',""),
                    'Budget': response.get('budget',""),
                    'Director': Director,
                    'Writer': Writer,
                    'Budget': response.get('budget',""),
                    'Homepage': response.get('homepage',""),
                    'Set': SetName,
                    'SetID': SetID,
                    'ID': response.get('id',""),
                    'Plot': response.get('overview',""),
                    'OriginalTitle': response.get('original_title',""),
                    'Genre': Genre,
                    'Rating': response.get('vote_average',""),
                    'Play': 'PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid=%s)' %Trailer,
                    'Trailer': 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' %Trailer,
                    'ReleaseDate':response.get('release_date',""),
                    'Country':Country,
                    'Studio':Studio,
                    'DiscArt':"",
                    'VideoResolution':"",
                    'AudioChannels':"",
                    'VideoCodec':"",
                    'Logo': "",
                    'DBID': "",
                    'Studio':Studio,
                    'Year':response.get('release_date',"")[:4]  }
    else:
        return False
    return newmovie
     
def GetMovieLists(Id):
    response = GetMovieDBData("http://api.themoviedb.org/3/movie/%s/lists?append_to_response=movies&api_key=%s" % (Id,moviedb_key))
    return HandleTheMovieDBListResult(response)
    
def GetSimilarMovies(Id):
    response = GetMovieDBData("http://api.themoviedb.org/3/movie/%s/similar_movies?&api_key=%s" % (Id,moviedb_key))
    return HandleTheMovieDBMovieResult(response["results"])
    
def GetSetMovies(Id):
    response = GetMovieDBData("http://api.themoviedb.org/3/collection/%s?&api_key=%s" % (Id,moviedb_key))
    return HandleTheMovieDBMovieResult(response["parts"])

def GetDirectorMovies(Id):
    response = GetMovieDBData("http://api.themoviedb.org/3/person/%s/credits?api_key=%s" % (Id,moviedb_key))
    # return HandleTheMovieDBMovieResult(response["crew"]) + HandleTheMovieDBMovieResult(response["cast"])
    return HandleTheMovieDBMovieResult(response["crew"])
              
def search_movie(medianame,year = ''):
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame, year) )
    medianame = urllib.quote_plus(medianame.encode('utf8','ignore'))
    response = GetMovieDBData("http://api.themoviedb.org/3/search/movie?query=%s+%s&api_key=%s" % (medianame, year, moviedb_key))
    tmdb_id = ''
    try:
        if response == "Empty":
            tmdb_id = ''
        else:
            for item in response['results']:
                if item['id']:
                    tmdb_id = item['id']
                    log(tmdb_id)
                    break
    except Exception, e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found ID: %s' %tmdb_id)
    return tmdb_id
        