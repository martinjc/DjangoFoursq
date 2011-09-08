import urllib
import urllib2
import json

from django.http import *
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import logout

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

request_token_url = 'https://foursquare.com/oauth2/authenticate'
access_token_url = 'https://foursquare.com/oauth2/access_token'
redirect_url = 'http://127.0.0.1:8000/foursq_auth/callback'

def main( request ):
    return render_to_response( 'foursq_auth/login.html' )

def callback( request ):
    # get the code returned from foursquare
    code = request.GET.get('code')

    # build the url to request the access_token
    params = { 'client_id' : CLIENT_ID,
               'client_secret' : CLIENT_SECRET,
               'grant_type' : 'authorization_code',
               'redirect_uri' : redirect_url,
               'code' : code}
    data = urllib.urlencode( params )
    req = urllib2.Request( access_token_url, data )

    # request the access_token
    response = urllib2.urlopen( req )
    access_token = json.loads( response.read( ) )
    access_token = access_token['access_token']

    # store the access_token for later use
    request.session['access_token'] = access_token

    # redirect the user to show we're done
    return HttpResponseRedirect(reverse( 'oauth_done' ) )

def unauth( request ):
    # clear any tokens and logout
    request.session.clear( )
    logout( request )
    return HttpResponseRedirect( reverse( 'main' ) )  

def auth( request ):
    # build the url to request
    params = {'client_id' : CLIENT_ID,
            'response_type' : 'code',
            'redirect_uri' : redirect_url }
    data = urllib.urlencode( params )
    # redirect the user to the url to confirm access for the app
    return HttpResponseRedirect( '%s?%s' % ( request_token_url, data  ) )

def done( request ):
    # get the access_token
    access_token = request.session.get('access_token')

    # request user details from foursquare
    params = { 'oauth_token' : access_token }
    data = urllib.urlencode( params )
    url = 'https://api.foursquare.com/v2/users/self'
    full_url = url + '?' + data
    print full_url
    response = urllib2.urlopen( full_url )
    response = response.read( )
    user = json.loads( response )['response']['user']
    name = user['firstName']

    # show the page with the user's name to show they've logged in
    return render_to_response( 'foursq_auth/done.html', { 'name' : name } )


