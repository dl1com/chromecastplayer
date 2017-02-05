"""
chromecastplayer.py

Very simple script to control a chromecast, based on the examples
of pychromecast.

Just call
pychromecast play_media url
to start playback of a file/stream on the chromecast.
"""

from __future__ import print_function
import time
import select
import sys
import logging
import argparse

import pychromecast

"""
Check for cast.socket_client.get_socket() and
handle it with cast.socket_client.run_once()
"""
def main_loop():
    """Handle parameter"""
    timer = 1
    cast = None
    def callback(chromecast):
        """Callback for asynchronous chromecast discovery"""
        nonlocal cast
        cast = chromecast
        stop_discovery()

    stop_discovery = pychromecast.get_chromecasts(blocking=False,
                                                  callback=callback)

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['play_media',
                                           'play',
                                           'pause',
                                           'stop',
                                           'stop_app'])
    parser.add_argument('url')

    args = parser.parse_args()

    while True:
        if cast:
            polltime = 0.1
            can_read, _, _ = select.select([cast.socket_client.get_socket()],
                                           [], [], polltime)
            if can_read:
                #received something on the socket, handle it with run_once()
                cast.socket_client.run_once()

            if timer == 5:
                do_actions(cast, args.action, args.url)

            print()
            print("Media status", cast.media_controller.status)

            timer += 1
            if timer > 20:
                break
        else:
            print("=> Waiting for cast discovery...")
        time.sleep(1)

def do_actions(cast, action, url):
    """Parse actions from commandline"""
    if action == 'play_media':
        print()
        print("=> Sending non-blocking play_media command")
        cast.play_media((str(url)), "video/mp4")
    elif action == 'pause':
        print()
        print("=> Sending non-blocking pause command")
        cast.media_controller.pause()
    elif action == 'play':
        print()
        print("=> Sending non-blocking play command")
        cast.media_controller.play()
    elif action == 'stop':
        print()
        print("=> Sending non-blocking stop command")
        cast.media_controller.stop()
    elif action == 'quit_app':
        print()
        print("=> Sending non-blocking quit_app command")
        cast.quit_app()

if '--show-debug' in sys.argv:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

main_loop()
