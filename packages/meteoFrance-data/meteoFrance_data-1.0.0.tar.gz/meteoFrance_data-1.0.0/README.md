# Météo-France Python API


====================

# Previsions météo : 

utilisation d'API http://webservice.meteofrance.com fournissant jusqu'a 14 jours de previsions 

source : HACF Communauté francophone pour Home-Assistant

https://github.com/hacf-fr/meteofrance-api

====================

# historique météo : 

utilisation d'API https://public-api.meteofrance.fr fournissant des données par station météo 


![station select](map_pin.jpg)

Etapes :

    1 - Recherche des stations météo les plus proches d'un point GPS et ayants un historique sur la periode demandée

    2 - Passer une commande de données pour chaque année

    3 - Télécharger les données
    
    4 - En cas d'erreur chercher l'historique dans la nième station la plus proche Etc ..

======================


# Exemple d'utilisation:


    test_api_token = 'eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0YmFubm91ckBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InRiYW5ub3VyIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6ODk1OSwidXVpZCI6ImM3OGMwOTkwLWUwMzYtNDUxNi1iMjRmLTg2NmEzN2RlYzc2YiJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9LCI4NTByZXFQZXI1TWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwic3Vic2NyaWJlZEFQSXMiOlt7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiRG9ubmVlc1B1YmxpcXVlc0NsaW1hdG9sb2dpZSIsImNvbnRleHQiOiJcL3B1YmxpY1wvRFBDbGltXC92MSIsInB1Ymxpc2hlciI6ImFkbWluX21mIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNQYXF1ZXRSYWRhciIsImNvbnRleHQiOiJcL3B1YmxpY1wvRFBQYXF1ZXRSYWRhclwvdjEiLCJwdWJsaXNoZXIiOiJsb2ljLm1hcnRpbiIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzUmFkYXIiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQUmFkYXJcL3YxIiwicHVibGlzaGVyIjoiTUVURU8uRlJcL21hcnRpbmwiLCJ2ZXJzaW9uIjoidjEiLCJzdWJzY3JpcHRpb25UaWVyIjoiODUwcmVxUGVyNU1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJBUk9NRS1QSSIsImNvbnRleHQiOiJcL3B1YmxpY1wvYXJvbWVwaVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJ0b2tlbl90eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzA4OTU0MTIxLCJqdGkiOiJkNTc1NDNkMi01MzE0LTQ4ZDItOGY3YS05MzU3MmM3YzcwYTAifQ==.j5kSjg6vBmQlJwtRHORzlkqmGkHM2acudIuMCEHSQMWpbyMObjC12U87SleMVWTRvDJp2kK5SxiQUBubGH1InbQMCKwjwvJx7smJ4PaNtrz-oTBtfucUHze-iSs6qS3l70uk1JDuW9kj45u4kqU8yfzGGzrJ6ix-lIewqX3kaS_rUVKqqc1tzi_N_2OVxgrbagu4oFgeoj2m7jylivH6SLbWgxEhWYci5h1-eak466JHDgsBJw2zffXgfTkjAb-WkZ7Gd7ICM449GD-sl9WrJo8OqzKdR2NAy9TFL33RyWP2S2nAgKmX8iyOawchsr7ECtloNYrk_bdzUtIdci17rg=='

    client = MeteoFranceClient()
    #################################### FORCAST ##############################################################
    forcast = client.get_forecast(latitude=44.84153973276238, longitude=-0.5798359378981625, language='fr')
    dailyForcast = forcast.daily_forecast
    dfResult = pd.DataFrame({})
    dates = []
    Tmin = []
    Tmax = []
    RR = []
    Desc = []
    for dforcast in dailyForcast:
        dates.append(str(datetime.fromtimestamp(dforcast['dt'])))
        Tmin.append(dforcast['T']['min'])
        Tmax.append(dforcast['T']['max'])
        RR.append(dforcast['precipitation']['24h'])
        Desc.append(dforcast['weather12H']['desc'])


    dfResult['date'] = dates
    dfResult['Tmin'] = Tmin
    dfResult['Tmax'] = Tmax
    dfResult['precipitation'] = RR
    dfResult['description'] = Desc

    dfResult.to_csv('export.csv', index=False)


    ####################################### HiSTORY ########################################## 
    
    ################# Commande des données journalières ######################################
    HistoryData = client.getDataOfClosestStation(33 , test_api_token, 44.89710867517252, -0.5004530272595558
                                                , '2019-03-15' , '2021-03-15')

    HistoryData.to_csv('export.csv', index=False)

    ################# Commande des données horaires ######################################
    # il faut ajouter le paramétre fréquence (H)
    HistoryData = client.getDataOfClosestStation(33 , test_api_token, 44.89710867517252, -0.5004530272595558
                                                , '2024-03-15T12:00:00Z' , '2024-03-15T20:00:00Z' , 'H')

    HistoryData.to_csv('export.csv', index=False)

    ################# Commande des données avec une fréquence de 6 minutes ######################################
    # il faut ajouter le paramétre fréquence (M)
    HistoryData = client.getDataOfClosestStation(33 , test_api_token, 44.89710867517252, -0.5004530272595558
                                                , '2024-03-15T12:00:00Z' , '2024-03-15T12:30:00Z' , 'M')

    HistoryData.to_csv('export.csv', index=False)


    ###########################################################################################