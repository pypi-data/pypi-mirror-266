# Editor.JS Repackaged for Django

[Editor.JS](https://editorjs.io/) packaged in a Django reusable app.

## Installation

    pip install django-js-lib-editor-js

## Usage

1. Add `"js_lib_editor_js"` to your `INSTALLED_APPS` setting like this::

       INSTALLED_APPS = [
           ...
           "js_lib_editor_js",
           ...
       ]

2. In your template use:
   
       {% load static %}
   
   ...
   
       <script src="{% static "editorjs/editorjs.js">" %}"></script>
