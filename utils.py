#!/usr/bin/env python3

import time
import random
import requests
import textwrap


def _request_content(url, **kwargs):
    """
    Description:
        Given a url, we will perform a request using the requests library.
        This handles error catching and sleeps to avoid spamming, in hopes
        of avoiding being blocked from future request.
        
    Arguement:
        url: url to perform a request on
        
    Keyword argument:
        kwargs: keyword arguments passed to request.get()
        
    Notes:
        ^Sleep [0.5, 1) seconds after a request to avoid spamming server
        
    Returns:
        A response's content
    """
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise SystemExit(error)
    except requests.exceptions.RequestException as error:
        raise SystemExit(error)
    print('[HTTP STATUS:{}] {} (elapsed={})'
          .format(response.status_code, url, response.elapsed))
    time.sleep(0.5*(1+random.random()))
    return response.content


def wraprint(*args, width=72, indent='  '):
    wrapper = textwrap.TextWrapper(width=width, subsequent_indent=indent)
    text = ''
    for arg in args:
        text += str(arg)+' '
    text = text[:-1]
    paragraph = wrapper.wrap(text=text)
    print(paragraph[0])
    for line in paragraph[1:]:
        print(line)