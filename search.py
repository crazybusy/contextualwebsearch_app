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

class SafeDataModel:    
    def __init__(self):
        self.data = list()        
        self.displayed_view_index = 0

    def add(self, one_data):
        self.data.append(one_data)

    def last_retrieved(self):
        return len(self.data)

    def get_latest(self):
        return self.data[-1]

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

        self.suggestions_list = SafeDataModel()
        
    def on_text(self, instance, value):                   
        if value != "" and not value.isspace() and len(value) > 3:
            thread = Thread(target = self.get_suggestions_task)
            thread.start()
    
    def refresh_widget_data(self):
        if self.suggestions_list.last_retrieved() > self.suggestions_list.get_displayed():
            data = self.suggestions_list.get_latest()
            self.add_nkeys(self.values, data , 3)
            self.suggestions_list.set_displayed(self.suggestions_list.last_retrieved())
            self.values.canvas.ask_update()

    def get_suggestions_task(self):                
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/AutoComplete"
        params = {'text': self.tfa.text}
        headers = {"X-RapidAPI-Key": "5b7ec33f4dmsh08ea9efedd164b7p1392d6jsn645e17978f7f"}
        response = requests.get(url, params = params, headers = headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            self.suggestions_list.add(data)
            self.refresh_widget_data()
            

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
    
    def add_nkeys(self, tree, data, n):
        self.clear_tree(self.values)
        count = 0 
        for key in data:            
            node = TreeViewLabel(text=key)
            node.bind(on_touch_down=self.suggestion_node_clicked)
            self.values.add_node(node)           
            count = count + 1
            if count > n:
                break

    def clear_tree(self, tree):
        for node in tree.iterate_all_nodes():
            tree.remove_node(node)

class SimpleKivy(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    SimpleKivy().run()
