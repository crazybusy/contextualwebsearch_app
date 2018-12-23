from kivy.app import App
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from urllib.parse import quote
from urllib.parse import urlencode

import webbrowser
import requests
import json

from threading import Thread
from threading import Lock

MIN_SEARCH = 3
AUTO_LIST = 3

class SafeDataModel:
    
    def __init__(self, loaded_data = None):
        self.data = list()
        self.displayed_view_index = 0
        if loaded_data:
            self.data.extend(loaded_data)  

    def add(self, one_data):
        self.data.append(one_data)

    def get_last_index(self):
        return len(self.data)

    def get_latest(self):
        if len(self.data) == 0:
            return 0, []
        else:
            return len(self.data), self.data[-1]


    def set_displayed(self, displayed_view_index):
        self.displayed_view_index = displayed_view_index

    def get_displayed(self):
        return self.displayed_view_index

class MainScreen(GridLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
        self.cols = 2                    
        self.tfa = TextInput(multiline=False)
        self.tfa.bind(text=self.on_text)
        self.tfa.bind(on_text_validate=self.on_enter)
        self.add_widget(self.tfa)
        button = Button(text='Search', font_size=14)
        button.bind(on_press=self.on_search)
        self.add_widget(button)
        self.values = TreeView(root_options={
            'text': 'Suggestions'})
        self.add_widget(self.values)
        self.lock = Lock()

        self.suggestions_list = SafeDataModel()
        self.recent_list = list()
        
    def on_text(self, instance, value):                   
        if value != "" and not value.isspace() and len(value) > MIN_SEARCH:
            thread = Thread(target = self.get_suggestions_task)
            thread.start()
        else:
            self.refresh_widget_from_list(self.recent_list)
    
    def refresh_widget_from_model(self, model, force = False):
        if (force and model.get_last_index()) or model.get_last_index() > model.get_displayed():
            last_retrieved, data = model.get_latest()
            self.add_nkeys(self.values, data , AUTO_LIST)
            model.set_displayed(model.get_last_index())
            self.values.canvas.ask_update()
    
    def refresh_widget_from_list(self, strings):
        self.add_nkeys(self.values, strings , AUTO_LIST)
        self.values.canvas.ask_update()

    def get_suggestions_task(self):                
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/AutoComplete"
        params = {'text': self.tfa.text}
        headers = {"X-RapidAPI-Key": "5b7ec33f4dmsh08ea9efedd164b7p1392d6jsn645e17978f7f"}
        response = requests.get(url, params = params, headers = headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            self.suggestions_list.add(data)
            self.refresh_widget_from_model(self.suggestions_list)
            

    def suggestion_node_clicked(self, instance, value):
        self.tfa.text = instance.text        
    
    def on_enter(self, instance):
        self.search(self.tfa.text)

    def on_search(self, instance):
        self.search(self.tfa.text)

    def search(self, text):        
        if text != "" and not text.isspace():
            url = "https://contextualwebsearch.com/search/"+quote(text)
            webbrowser.open(url)
            self.recent_list.append(text)

    def add_nkeys(self, tree, data, n):
        self.lock.acquire()
        self.clear_tree(self.values)        
        
        for key in data:            
            node = TreeViewLabel(text=key)
            node.bind(on_touch_down=self.suggestion_node_clicked)
            self.values.add_node(node)           
            count = count + 1
        self.lock.release()

    def clear_tree(self, tree):        
        #for node in tree.iterate_all_nodes():
        #    tree.remove_node(node)
        for node in tree.root.nodes:
            tree.remove_node(node)

class SimpleKivy(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    SimpleKivy().run()
