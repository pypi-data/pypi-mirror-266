from __future__ import annotations

from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import NumericProperty
from kivymd_utils.router.route import RouteBase, ErrorRoute
from kivymd_utils.router.state import RouteState

from kivymd.uix.screen import MDScreen

class Router:
    def __init__(self, *args, 
                initial_route: str, 
                routes: list[RouteBase], 
                error_route = ErrorRoute(),
                **kwargs):
        self.routes = routes 
        self.path = initial_route
        self.error_route = error_route
        # page stack to allow pushing
        self.page_stack = []

    def go(self, path: str):
        """go to a path by url"""
        print(f"going to {path}")
        self._switch_to_path(path)

    def goData(self, path: str, attributes: dict):
        """allows redirecting to a path and passing more complex objects
        
        Router.goData("/item", {"id": 5})

        is identical to 
        
        Router.goData("/item/5")

        where both match "/item/:id"
        """
        self._switch_to_path(path, initial_dict=attributes)

    
    def push(self, path: str):
        """
        push a new page to the page stack,

        the page stack is cleared when utilising Router.go()
        """
        self._push_to_path(path)

    def pushData(self, path:str, initial_attributes: dict):
        """
        push a new page to the stack with custom objects in the dict"""
        self._push_to_path(path, initial_dict=initial_attributes)

    def pop(self):
        self._pop()
    
        

    def build(self, path: str = None, is_push= False, initial_dict: dict = None):
        if path is None:
            path = self.path
            
        self.path = path
        state = RouteState(path)
        if initial_dict is not None:
            state.parameters = initial_dict
        
        route = state.get_route(self.routes)
        
        print(f"displaying {route}")
        print(state.parameters)
        item = route.build(state, router=self)

        if item is None:
            self.page_stack.append(path)
            self.error_route.set_path(path)
            #print(f"page stack is {self.page_stack}")
            return MDScreen(
                self.error_route.build(state, router=self)
            )
        if is_push == False:
            self.page_stack.clear()
            self.page_stack.append(path)
        screen = MDScreen(
            item
        )
        return screen
    


    def _switch_to_path(self, path: str, initial_dict: dict = None):
        self._switch_to(self.build(path, initial_dict=initial_dict))

    def _push_to_path(self, path: str, initial_dict: dict = None):
        self.page_stack.append(self.path)
        self._switch_to(self.build(path, is_push=True, initial_dict=initial_dict))

    def _pop(self):
        #print("trying pop")
        if len(self.page_stack) == 1:
            return
        #print(f"got pop to {self.page_stack}")
        _ = self.page_stack.pop()
        self._switch_to(self.build(self.page_stack[-1], is_push=True))

    def _add_switch_manager(self, switch_manager):
        self._switch_to = switch_manager


    

class RouterWidget(ScreenManager):
    reloader = NumericProperty(0)
    def __init__(self, *args, router: Router, **kwargs):
        from kivy.uix.screenmanager import NoTransition
        super().__init__(*args, transition=NoTransition(),**kwargs)
        self.router = router
        self.switch_to(router.build())
        router._add_switch_manager(self.switch_to)