

import pygame


def runapp():
    try:
        import argparse
        parser = argparse.ArgumentParser(description="Run SightTraining game.")
        parser.add_argument("-D", "--debug", action="store_true", help="Run game in debug mode.")
        parser.add_argument("-f", "--fullscreen", action="store_true", help="Run game in fullscreen mode.")
        parser.add_argument("-r", "--resolution", choices=["1080", "900", "720"], default="720", help="Set game resolution.")

        args = parser.parse_args()

        
        from spacedefense.config import configmap
        
        if args.fullscreen:
            configmap["fullscreen"] = True
            
        if args.resolution == "1080":
            configmap["display_width"] = 1920
            configmap["display_height"] = 1080
        elif args.resolution == "900":
            configmap["display_width"] = 1600
            configmap["display_height"] = 900
        elif args.resolution == "720":
            configmap["display_width"] = 1280
            configmap["display_height"] = 720

        from spacedefense.game import main
        main()
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

