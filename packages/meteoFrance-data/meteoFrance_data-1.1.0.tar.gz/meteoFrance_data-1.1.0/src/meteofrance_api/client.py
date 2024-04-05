# -*- coding: utf-8 -*-
"""Client for the Météo-France REST API."""
from typing import List
from typing import Optional

from .const import COASTAL_DEPARTMENT_LIST
from .const import METEOFRANCE_API_TOKEN
from .const import METEOFRANCE_API_HISTORY_URL
from .const import METEOFRANCE_API_URL
from .model import CurrentPhenomenons
from .model import Forecast
from .model import Full
from .model import Observation
from .model import PictureOfTheDay
from .model import Place
from .model import Rain
from .model import WarningDictionary
from .session import MeteoFranceSession


import requests
import json
import geopy.distance
import pandas as pd
from io import StringIO
from datetime import datetime
import time


# TODO: investigate bulletincote, montagne, etc...
#       http://ws.meteofrance.com/ws//getDetail/france/330630.json
# TODO: add protection for warning if domain not valid
# TODO: strategy for HTTP errors
# TODO: next rain in minute. Necessary ?
# TODO: forecast/metadata from ID to get gps ?


class MeteoFranceClient:
    """Proxy to the Météo-France REST API.

    You will find methods and helpers to request weather forecast, rain forecast and
    weather alert bulletin.
    """

    def __init__(self, access_token: Optional[str] = None) -> None:
        """Initialize the API and store the auth so we can make requests.

        Args:
            access_token: a string containing the authentication token for the REST API.
        """
        self.session = MeteoFranceSession(access_token)

    #
    # Place
    #
    def search_places(
        self,
        search_query: str,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
    ) -> List[Place]:
        """Search the places (cities) linked to a query by name.

        You can add GPS coordinates in parameter to search places arround a given
        location.

        Args:
            search_query: A complete name, only a part of a name or a postal code (for
                France only) corresponding to a city in the world.
            latitude: Optional; Latitude in degree of a reference point to order
                results. The nearest places first.
            longitude: Optional; Longitude in degree of a reference point to order
                results. The nearest places first.

        Returns:
            A list of places (Place instance) corresponding to the query.
        """
        # Construct the list of the GET parameters
        params = {"q": search_query}
        if latitude is not None:
            params["lat"] = latitude
        if longitude is not None:
            params["lon"] = longitude

        # Send the API resuest
        resp = self.session.request("get", "places", params=params)
        return [Place(place_data) for place_data in resp.json()]


    #
    # History DATA
    #
    def annees_entre_deux_dates(self, date_debut, date_fin):
        """Get years between two dates
                
        Args:
            date_debut: history data begin date 
            date_fin: history data end date 

        Returns:
            A list of years between two dates
            
        """
    
        try:
            debut = datetime.strptime(date_debut, '%Y-%m-%d')
            fin = datetime.strptime(date_fin, '%Y-%m-%d')
            if fin < debut:
                return "La date de fin doit être postérieure à la date de début."
            
            annees = []
            for annee in range(debut.year, fin.year + 1):
                annees.append(annee)
            
            return annees
        except ValueError:
            return "Format de date incorrect. Utilisez le format YYYY-MM-DD."   
    
    
    def getDataOfClosestStation(self , departement , api_token , lat , lon , fromDate , toDate , frequence = 'D'):
        
        """search the closest meteo station from GPS point   
        Args:
            departement: departement number : example : 33 Gironde
            api_token: generated api token from meteo-france site 
            lat : latitude
            lon : longitude
            fromDate: history data begin date 
            toDate: history data end date 
            frequence : data history frequence ( D : Daily , H : evry hour , M : evry 6 minutes )
            

        Returns:
            A dataframe of history data 
            
        """
    
        orderedStations = self.listStations(departement , api_token , lat, lon , frequence)
        idList = orderedStations['stationData']['id'].unique().tolist()
        for id in idList:
            info = self.getStationInformation(api_token , id)
            if(info and info['dateDebut'] <= fromDate and info['dateFin'] >= toDate):
                try:
                    print('Essayer une commande de données de la station avec la reference : ' + id)
                    D = self.getHistoryData(api_token , id , fromDate , toDate , frequence)
                except  Exception as error:
                    print(error)    
                    continue
                if(len(D) != 0):
                    return D
            else:
                continue



    def getStationInformation(self , api_token ,idStation ):
        """Get station informations  
        Args:
            api_token: generated api token from meteo-france site 
            idStation : station id
            

        Returns:
            data dates intrval ( from to ..)
            
        """
        requestUrl = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/information-station?id-station={idStation}'
        headers = {'accept': '*/*' , 'apikey' : f'{api_token}' }
        response = requests.get(requestUrl, headers=headers )
        if(response.status_code == 200 or response.status_code == 201):
            res = response.text
            responseObject = json.loads(res)
            if(len(responseObject) > 0 and 'dateDebut' in responseObject[0] and 'dateFin' in responseObject[0] ):
                endDate = responseObject[0]['dateFin']
                if(responseObject[0]['dateFin'] == ''):
                    endDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                return ({'dateDebut' : responseObject[0]['dateDebut'] , 'dateFin' : endDate})
            else:
                return None
        else:
            return None
    
    

    def getHistoryData(self, api_token ,idStation , fromDate , toDate , frequence = 'D'):
        """Get history data from API
            
        Args:
            api_token: generated api token from meteo-france site 
            idStation : station id
            fromDate: history data begin date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            toDate: history data end date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            frequence : data history frequence ( D : Daily , H : evry hour , M : evry 6 minutes )
            

        Returns:
            pandas dataframe of history data
            
        """
        if(frequence == 'D'):
            fromDate_object = datetime.strptime(fromDate, '%Y-%m-%d')
            toDate_object = datetime.strptime(toDate, '%Y-%m-%d')
            
            daysDiff = abs((toDate_object - fromDate_object).days)
            #if history period < 1 year
            if(daysDiff <= 365):
                apiData = self.getYearHistoryData(api_token , idStation , fromDate , toDate)['stationData']
                csvStringIO = StringIO(apiData)
                return pd.read_csv(csvStringIO, sep=";")
            else:
                # une requéte par année
                years = self.annees_entre_deux_dates(fromDate , toDate)
                response = []
                for y in years :
                    FD = f'{y}-01-01'
                    TD = f'{y}-12-31'
                    DD = self.getYearHistoryData(api_token , idStation , FD , TD)
                    if(int(DD['status']) == 200 or int(DD['status']) == 201):
                        csvStringIO = StringIO(DD['stationData'])
                        response.append(pd.read_csv(csvStringIO, sep=";"))
                    else:
                        df_concat = pd.concat(response)
                        return df_concat
                
                df_concat = pd.concat(response)
                return df_concat
            
        if(frequence == 'H' or frequence == 'M'):
            fromDate_object = datetime.strptime(fromDate, '%Y-%m-%dT%H:%M:%SZ')
            toDate_object = datetime.strptime(toDate, '%Y-%m-%dT%H:%M:%SZ')
            
            apiData = self.getHourMinutesHistoryData(api_token , idStation , fromDate , toDate , frequence)['stationData']
            csvStringIO = StringIO(apiData)
            return pd.read_csv(csvStringIO, sep=";")
            
 
    

    def getHourMinutesHistoryData(self, api_token , idStation , fromDate , toDate , frequence):
        """Get history data from API with frequence of one hour or 6 minutes
            
        Args:
            api_token: generated api token from meteo-france site 
            idStation : station id
            fromDate: history data begin date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            toDate: history data end date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            frequence : data history frequence ( D : Daily , H : evry hour , M : evry 6 minutes )
            

        Returns:
            pandas dataframe of history data
            
        """
        strFromDate = fromDate + ''
        strToDate = toDate + ''
        if(frequence == 'M'):
            requestUrl = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/commande-station/infrahoraire-6m?id-station={idStation}&date-deb-periode={strFromDate}&date-fin-periode={strToDate}'
        else:
            requestUrl = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/commande-station/horaire?id-station={idStation}&date-deb-periode={strFromDate}&date-fin-periode={strToDate}'
        headers = {'accept': '*/*' , 'apikey' : f'{api_token}' }
        response = requests.get(requestUrl, headers=headers )
        res = response.text
        print('generation ID commande ..')
        print(res)
        data  = json.loads(res)
        commandData =  self.passDataCommand(api_token , data['elaboreProduitAvecDemandeResponse']['return'])
        return({ 'status' : commandData['status'] , 'stationData' : commandData['data'] })
    
    
       
    def getYearHistoryData(self, api_token , idStation , fromDate , toDate):
        """Get history data of one YEAR
            
        Args:
            api_token: generated api token from meteo-france site 
            idStation : station id
            fromDate: history data begin date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            toDate: history data end date ( format : AAAA-MM-JJThh:00:00Z  if frequence is H or M / AAAA-MM-JJ if frequence is D) 
            

        Returns:
            pandas dataframe of history data
            
        """ 
        strFromDate = fromDate + 'T00:00:00Z'
        strToDate = toDate + 'T00:00:00Z'
        requestUrl = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/commande-station/quotidienne?id-station={idStation}&date-deb-periode={strFromDate}&date-fin-periode={strToDate}'
        headers = {'accept': '*/*' , 'apikey' : f'{api_token}' }
        response = requests.get(requestUrl, headers=headers )
        res = response.text
        print('generation ID commande ..')
        print(res)
        data  = json.loads(res)
        commandData =  self.passDataCommand(api_token , data['elaboreProduitAvecDemandeResponse']['return'])
        return({ 'status' : commandData['status'] , 'stationData' : commandData['data'] })
    
    
           


    def passDataCommand(self, api_token , idCommande):
        """Get command result CSV file    
        Args:
            api_token: generated api token from meteo-france site 
            idCommande : returned request data command id
        Returns:
            CSV data text
            
        """ 
        requestUrl = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/commande/fichier?id-cmde={idCommande}'
        headers = {'accept': '*/*' , 'apikey' : f'{api_token}' }
        response = requests.get(requestUrl, headers=headers )
        if(response.status_code == 204): # Si les données sont en cours de preparation  
            for i in range(10):
                waitTime = 10*i
                print('Attente de  :' + str(waitTime) + ' secondes ...')
                time.sleep(waitTime)
                newResponse = requests.get(requestUrl, headers=headers )
                print(newResponse.text)
                if(newResponse.status_code == 200 or newResponse.status_code == 201):
                    R = newResponse.text
                    print('reponse de commande de données :')
                    print(R)
                    return({ 'status' : newResponse.status_code , 'data' : R })
        else:
            res = response.text
            print('reponse de commande de données :')
            print(res)
            return({ 'status' : response.status_code , 'data' : res })

    
    def listStations(self , departement : int , api_token : str , lat : float , lon : float , frequence : str ):
        """Get list stations of departement
            
        Args:
            api_token: generated api token from meteo-france site 
            lat :  latitude
            lon : longitude
            frequence : data history frequence ( D : Daily , H : evry hour , M : evry 6 minutes )
            
        Returns:
            list of stations from nearest to the farthest from indicated GPS point
            
        """
        headers = {'accept': '*/*' , 'apikey' : f'{api_token}' }
        api_url = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/liste-stations/quotidienne?id-departement={departement}'
        if(frequence == 'M'):
            api_url = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/liste-stations/infrahoraire-6m?id-departement={departement}'
        if(frequence == 'H'):
            api_url = f'{METEOFRANCE_API_HISTORY_URL}/public/DPClim/v1/liste-stations/horaire?id-departement={departement}'
        response = requests.get(api_url, headers=headers )
        res = response.text
        data  = json.loads(res)    
        stationData = {}
        # get closest station if GPS location is specified
        stationData = self.closestStation(data , lat , lon)

        return({ 'status' : response.status_code , 'stationData' : stationData })




    def closestStation(self ,Data , lat , lon):
        """order stations by distance
            
        Args:
            Data: list of stations Data
            lat :  latitude
            lon : longitude
            
        Returns:
            dataframe of stations ordered by distance
        """ 
        distances = []
        for station in Data:
            coords_1 = (station['lat'], station['lon'])
            coords_2 = (lat, lon)
            D = geopy.distance.geodesic(coords_1, coords_2)
            distances.append(D)
        df = pd.DataFrame(Data)
        df['distance'] = distances
        df = df.sort_values(by=['distance'], ascending=True)

        return df
                
        
    #
    # Observation
    #
    def get_observation(
        self,
        latitude: float,
        longitude: float,
        language: str = "fr",
    ) -> Observation:
        """Retrieve the weather observation for a given GPS location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the weather
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the weather
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            An Observation instance.
        """
        resp = self.session.request(
            "get",
            "v2/observation",
            params={"lat": latitude, "lon": longitude, "lang": language},
        )
        return Observation(resp.json())

    def get_observation_for_place(
        self,
        place: Place,
        language: str = "fr",
    ) -> Observation:
        """Retrieve the weather observation for a given Place instance.

        Results can be fetched in french or english according to the language parameter.

        Args:
            place: Place class instance corresponding to a location.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            An Observation intance.
        """
        return self.get_observation(place.latitude, place.longitude, language)

    #
    # Forecast
    #
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        language: str = "fr",
    ) -> Forecast:
        """Retrieve the weather forecast for a given GPS location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the weather
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the weather
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Forecast intance representing the hourly and daily weather forecast.
        """
        # TODO: add possibility to request forecast from id

        # Send the API request
        resp = self.session.request(
            "get",
            "forecast",
            params={"lat": latitude, "lon": longitude, "lang": language},
        )
        return Forecast(resp.json())

    def get_forecast_for_place(
        self,
        place: Place,
        language: str = "fr",
    ) -> Forecast:
        """Retrieve the weather forecast for a given Place instance.

        Results can be fetched in french or english according to the language parameter.

        Args:
            place: Place class instance corresponding to a location.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Forecast intance representing the hourly and daily weather forecast.
        """
        return self.get_forecast(place.latitude, place.longitude, language)

    #
    # Rain
    #
    def get_rain(self, latitude: float, longitude: float, language: str = "fr") -> Rain:
        """Retrieve the next 1 hour rain forecast for a given GPS the location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the rain
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the rain
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Rain instance representing the next hour rain forecast.
        """
        # TODO: add protection if no rain forecast for this position

        # Send the API request
        resp = self.session.request(
            "get", "rain", params={"lat": latitude, "lon": longitude, "lang": language}
        )
        return Rain(resp.json())

    #
    # Warning
    #
    def get_warning_current_phenomenoms(
        self, domain: str, depth: int = 0, with_coastal_bulletin: bool = False
    ) -> CurrentPhenomenons:
        """Return the current weather phenomenoms (or alerts) for a given domain.

        Args:
            domain: could be `france` or any metropolitan France department numbers on
                two digits. For some departments you can access an additional bulletin
                for coastal phenomenoms. To access it add `10` after the domain id
                (example: `1310`).
            depth: Optional; To be used with domain = 'france'. With depth = 0 the
                results will show only natinal sum up of the weather alerts. If
                depth = 1, you will have in addition, the bulletin for all metropolitan
                France department and Andorre
            with_coastal_bulletin: Optional; If set to True (default is False), you can
                get the basic bulletin and coastal bulletin merged.

        Returns:
            A warning.CurrentPhenomenons instance representing the weather alert
            bulletin.
        """
        # Send the API request
        resp = self.session.request(
            "get",
            "v3/warning/currentphenomenons",
            params={"domain": domain, "depth": depth},
        )

        # Create object with API response
        phenomenoms = CurrentPhenomenons(resp.json())
        # if user ask to have the coastal bulletin merged
        if with_coastal_bulletin:
            if domain in COASTAL_DEPARTMENT_LIST:
                resp = self.session.request(
                    "get",
                    "v3/warning/currentphenomenons",
                    params={"domain": domain + "10"},
                )
                phenomenoms.merge_with_coastal_phenomenons(
                    CurrentPhenomenons(resp.json())
                )

        return phenomenoms

    def get_warning_full(
        self, domain: str, with_coastal_bulletin: bool = False
    ) -> Full:
        """Retrieve a complete bulletin of the weather phenomenons for a given domain.

        For a given domain we can access the maximum alert, a timelaps of the alert
        evolution for the next 24 hours, a list of alerts and other metadatas.

        Args:
            domain: could be `france` or any metropolitan France department numbers on
                two digits. For some departments you can access an additional bulletin
                for coastal phenomenoms. To access it add `10` after the domain id
                (example: `1310`).
            with_coastal_bulletin: Optional; If set to True (default is False), you can
                get the basic bulletin and coastal bulletin merged.

        Returns:
            A warning.Full instance representing the complete weather alert bulletin.
        """
        # TODO: add formatDate parameter

        # Send the API request
        resp = self.session.request(
            "get", "/v3/warning/full", params={"domain": domain}
        )

        # Create object with API response
        full_phenomenoms = Full(resp.json())

        # if user ask to have the coastal bulletin merged
        if with_coastal_bulletin:
            if domain in COASTAL_DEPARTMENT_LIST:
                resp = self.session.request(
                    "get",
                    "v3/warning/full",
                    params={"domain": domain + "10"},
                )
                full_phenomenoms.merge_with_coastal_phenomenons(Full(resp.json()))

        return full_phenomenoms

    def get_warning_thumbnail(self, domain: str = "france") -> str:
        """Retrieve the thumbnail URL of the weather phenomenoms or alerts map.

        Args:
            domain: could be `france` or any metropolitan France department numbers on
                two digits.

        Returns:
            The URL of the thumbnail representing the weather alert status.
        """
        # Return directly the URL of the gif image
        return (
            f"{METEOFRANCE_API_URL}/v3/warning/thumbnail?&token={METEOFRANCE_API_TOKEN}"
            f"&domain={domain}"
        )

    def get_warning_dictionary(self, language: str = "fr") -> WarningDictionary:
        """Retrieves the meteorological dictionary from the Météo-France API.

        This dictionary includes information about various meteorological
        phenomena and color codes used for weather warnings.

        Args:
            language (str): The language in which to retrieve the
                dictionary data. Default is 'fr' for French. Other language codes
                can be used if supported by the API.

        Returns:
            WarningDictionary: An object containing structured data about
                meteorological phenomena and warning color codes. It has two main
                attributes: 'phenomenons' (list of PhenomenonDictionaryEntry) and
                'colors' (list of ColorDictionaryEntry).
        """
        resp = self.session.request(
            "get", "v3/warning/dictionary", params={"lang": language}
        )
        dictionary = WarningDictionary(resp.json())
        return dictionary

    #
    # Picture of the day
    #
    def get_picture_of_the_day(self, domain: str = "france") -> PictureOfTheDay:
        """Retrieve the picture of the day image URL & description.

        Args:
            domain: could be `france`

        Returns:
            PictureOfTheDay instance with the URL and the description of the picture of
            the day.
        """
        # Send the API request
        # TODO: check if other value of domain are usable

        resp = self.session.request(
            "get",
            "v2/report",
            params={
                "domain": domain,
                "report_type": "observation",
                "report_subtype": "image du jour",
                "format": "txt",
            },
        )

        image_url = (
            f"{METEOFRANCE_API_URL}/v2/report"
            f"?domain={domain}"
            f"&report_type=observation&report_subtype=image%20du%20jour&format=jpg"
            f"&token={METEOFRANCE_API_TOKEN}"
        )

        return PictureOfTheDay({"image_url": image_url, "description": resp.text})
