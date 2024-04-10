import os
import ast
import time
from typing import Literal, Optional, Union
import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True 
 
if not _RELEASE:
    _st_session_browser_storage = components.declare_component(

        "st_session_browser_storage",

        url="http://localhost:3001",
    )
else:

    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _st_session_browser_storage = components.declare_component("st_session_browser_storage", path=build_dir)


class SessionStorage:
    """
    Component to help manager sessionBrowser storage for streamlit apps
    """

    def __init__(self):
        self.sessionBrowserStorageManager = _st_session_browser_storage
            
    def setItem(self, itemKey:str=None, itemValue:Union[str, int, float, bool]=None, key:str="set", default=None):
        """
        Set individual items to sessionBrowser storage with a given name (itemKey) and value (itemValue)

        Args:
            itemKey: Name of the item to set
            itemValue: The value to save. Can be string, int, float, bool, dict, json but will be stored as a string
        """

        if (itemKey is None or itemKey == "") or (itemValue is None or itemValue == ""):
            return
        
        try:
            self.sessionBrowserStorageManager(method="setItem", itemKey=itemKey, itemValue=itemValue, key=key, default=default)
            return True
        except:
            return False   
        
    def deleteItem(self, itemKey:str, key:str="delete", default=None): 
        """
        Delete individual item from sessionBrowser storage

        Args:
            itemKey: item key to delete from sessionBrowser storage
            key: unique identifier for the function/method in case you wish to execute it again somewhere else in the app.
        """

        if itemKey is None or itemKey == "":
            return
        
        self.sessionBrowserStorageManager(method="deleteItem", itemKey=itemKey, key=key, default=default) 
        
        return True
    
    def eraseItem(self, itemKey:str, key:str="eraseItem", default=None):
        """
        Erase item from sessionBrowser storage. deleteItem does not remove it from storage, merely changes its default value. This will do so.

        Args:
            itemKey: item key to remove from sessionBrowser storage 
            key: unique identifier for the function/method in case you wish to execute it again somewhere else in the app.
        """
        if itemKey is None or itemKey == "":
            return
        
        self.sessionBrowserStorageManager(method="eraseItem", itemKey=itemKey, key=key, default=default) 

    
    def getItem(self, pause:int=None, itemKey:str=None, key:str="get"):
        """
        Get individual items stored in sessionBrowser storage.

        Args:
            itemKey: name of item to get from sessionBrowser storage
        """

        if itemKey is None or itemKey == "":
            return
        
        saved_key = self.sessionBrowserStorageManager(method="getItem", itemKey=itemKey, key=key, default={}) 
        print(saved_key)
        if pause != None:
            time.sleep(pause) 
            
        return saved_key
        
    def getAll(self, pause:int=None, in_built_formating:bool=True, key:str="get_all"):
        """
        Get all items saved on sessionBrowser storage.

        Args:
            key: unique identifier for the function/method in case you wish to execute it again somewhere else in the app.
        """

        saved_keys = self.sessionBrowserStorageManager(method="getAll", key=key)
        if pause != None:
            time.sleep(pause) 
        
        if in_built_formating: 

            all_storage_items = []
            for k,v in saved_keys.items():
                all_storage_items.append(ast.literal_eval(saved_keys[k].replace('"',"'").replace('null', "None")))
            
            return all_storage_items
        return saved_keys
        
    def deleteAll(self, key:str="delete_all"):
        """
        Delete all items you saved on sessionBrowser storage

        Args:
            key: unique identifier for the function/method in case you wish to execute it again somewhere else in the app.
        """

        self.sessionBrowserStorageManager(method="deleteAll", key=key) 

       
        
    
   
    
    