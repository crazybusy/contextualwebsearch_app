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
        
    def on_text(self, instance, value):
        self.clear_tree(self.values)                 
        if value != "" and not value.isspace() and len(value) > 3:
            url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/AutoComplete"
            params = {'text': value}
            headers = {"X-RapidAPI-Key": "5b7ec33f4dmsh08ea9efedd164b7p1392d6jsn645e17978f7f"}
            response = requests.get(url, params = params, headers = headers)
            if response.status_code == 200:
                data = json.loads(response.text)
                self.add_nkeys(self.values, data , 3)

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
