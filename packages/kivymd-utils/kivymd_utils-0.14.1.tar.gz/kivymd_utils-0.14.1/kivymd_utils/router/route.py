from __future__ import annotations
from kivymd_utils.router.path_utils import patternToRe

class RouteBase:
    def __init__(
            self,
            routes: list[RouteBase],
            builder = None,
            widget = None,
        ) -> None:
        self.widget = widget
        self.routes = routes
        self.builder = builder
        self.arguments = []
        

    def __repr__(self) -> str:
        return f"""
RouteBase:
    routes: {self.routes}
"""
        
    def match_path(self, path: str):
        raise NotImplementedError()
    
    def build(self, state, *args, **kwargs):
        if state.should_build():
            #TODO: make it so a page should not be rebuild if not needed
            #if self.widget is not None:
            #    return self.widget
            if self.builder is not None:
                self.widget = self.builder(state, *args, **kwargs)
            return self.widget

        route = state.get_route(self.routes)
        if route is None:
            return None
        return route.build(state, *args, **kwargs)
    

class Route(RouteBase):
    def __init__(self, 
                 *args,
                 path: str, 
                 name: str = None, 
                 redirect: str = None, 
                 widget = None,
                 routes: list[RouteBase] = [],
                 builder = None
                ) -> None:
        """create a new Route for the path specified
        
        # Parameters
        name: Optional but non empty
        redirect: Optional path to new page,
        widget: widget to display 
        builder: builder to create widget, gets passed a state
        routes: subroutes for the path

        either redirect, widget or builder must be set
        
        To utilize a widget directly the Router object cant be a global

        """
        assert builder != None or redirect != None or widget != None
        super().__init__(routes=routes, builder=builder, widget=widget)
        assert name == None or len(name) != 0 
        self.path = path
        self.name = name
        self.redirect = redirect

        (self.pattern, self.arguments) = patternToRe(path)

    def match_path(self, path: str):
        return [self.pattern.match(path)]

    def build(self, state, *args, **kwargs):
        if self.redirect is not None:
            return kwargs["router"].build(self.redirect)

        return super().build(state, *args, **kwargs)
    
    def __repr__(self) -> str:
        return f"""
Route:
    path: {self.path}
"""

class ShellRoute(RouteBase):
    def __init__(self, 
                routes: list[RouteBase], 
                builder,
                ) -> None:
        assert builder is not None
        super().__init__(routes, builder)

    def match_path(self, path: str):
        # a shellroute is invisible for the match so just match the children
        matches = []
        for item in self.routes:
            matches.extend(item.match_path(path))
        return matches
    
    def build(self, state, *args, **kwargs):
        route = state.get_route(self.routes, reconsume=True)
        if route is None:
            return None
        child = route.build(state, *args, **kwargs)
        print(f"building shellroute {child}")
        return self.builder(state, child, *args, **kwargs)
    
from kivymd_utils.router.error_page import ErrorPage
class ErrorRoute(RouteBase):
    def __init__(self, path: str = "", builder = lambda state, path, *args, **kwargs: ErrorPage(path, *args, **kwargs) ) -> None:
        super().__init__([], builder)
        self.path = path

    def set_path(self, path):
        self.path = path

    def match_path(self, path: str):
        return [False]
    
    def build(self, state, *args, **kwargs):
        print("showing error route")
        return self.builder(state, self.path, *args, **kwargs)
    
    def __repr__(self) -> str:
        return f"""
ErrorRoute:
    path: {self.path}
"""