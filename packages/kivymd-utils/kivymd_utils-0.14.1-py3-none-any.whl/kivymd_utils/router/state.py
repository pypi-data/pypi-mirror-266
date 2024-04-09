from __future__ import annotations
from kivymd_utils.router.route import RouteBase

class RouteState:
    def __init__(self, path: str) -> None:
        self.unmatched = path
        self.matched = ""

        self.parameters = {}

        self.prev_unmatched = path
        self.prev_matched = ""

    def should_build(self) -> bool:
        return self.unmatched == ""

    def get_route(self, routes: list[RouteBase], *args, reconsume = False):
        if reconsume:
            self.unmatched = self.prev_unmatched
            self.matched = self.prev_matched
        
        route_item = None
        route_match_len = 0
        route_match = None
        for route in routes:
            for match in route.match_path(self.unmatched):
                #print(f"match {route} with \n{match}")
                if match is None:
                    continue
                if match.start() != 0:
                    continue

                len = match.end()
                if len > route_match_len:
                    #print("match succesfull")
                    route_item = route
                    route_match = match
                    route_match_len = len
        
        if route_item is None:
            return None

        self.prev_unmatched = self.unmatched
        self.prev_matched = self.matched

        self.matched += self.unmatched[:route_match_len]
        self.unmatched = self.unmatched[route_match_len:]

        for argument in route_item.arguments:
            data = route_match.group(argument)
            if argument in self.parameters.keys():
                continue
            self.parameters[argument] = data

        return route_item
