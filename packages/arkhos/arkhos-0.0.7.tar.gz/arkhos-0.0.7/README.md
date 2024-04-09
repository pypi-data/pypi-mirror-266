# The Arkhos Python Client

[Arkhos](https://www.getArkhos.com>) is a Python framework for easily deploying small Python apps.

```python
# main.py
def arkhos_handler(event):
    return arkhos.json({
        "greeting": f"Hello {event.GET.get("name")}!"
    })

```

```bash
$ git add main.py
$ git push arkhos
$ curl "https://my-first-app.arkhosapp.com?name=Wally"
{
  "greeting": "Hello Wally!"
}
```

## Docs
See the full [Arkhos Docs](https://getarkhos.com/docs) and [Getting started guide](https://getarkhos.com/guides/python-hello-world)
|**Arkhos Requests**|**Description**|
|-|-|
|request.method|GET, POST, INTERVAL, EMAIL, ….|
|request.GET<br>request.GET["some_key"]|Request GET parameters, *dictionary*<br> eg. ?favorite_project=arkhos|
|request.body|Request body, *string*|
|request.json|Request POST body parsed as json into *dictionary*|
|request.headers|Request headers, *dictionary*|
|request.path|The url path, *string*, <br>eg. "/about"|
|&nbsp;||
|**Arkhos Responses**<br>All responses also accept headers={} and status=200,404||
|return arkhos.json(<br>&nbsp;&nbsp;&nbsp;&nbsp;{"key":"value"}<br>)|Return JSON|
|return arkhos.http(<br>&lt;h1&gt;some html&lt;/h1&gt;<br>)|Return HTML|
|return arkhos.render(<br>&nbsp;&nbsp;&nbsp;&nbsp;"path/to/file.html",<br>&nbsp;&nbsp;&nbsp;&nbsp;{"name": "Lucille"}<br>)|Return the html with the variables in the dict.<br> Uses [jinja](https://jinja.palletsprojects.com/en/3.1.x/templates/#variables) templating. Eg. in your HTML `{{ name }}`|
|&nbsp;||
|**Static files (.js, .css, .jpg)**||
|Any files in /static folder are available at &lt;my-app&gt;.arkhosapp.com/static/|Not implemented|
|&nbsp;||
|**Key/Value and Storage**||
|arkhos.set(key, value)|Store a key, value. key should be a *string*. value can be *string,int,float,* or *boolean*|
|arkhos.get(key)|Get a key|
|arkhos.event(type, payload, resource)|Not implemented|
|&nbsp;||
|**Communicate**||
|arkhos.email(email_address, subject, message, attachment)|Not implemented|
|arkhos.sms(phone_number, message)|Not implemented|
|&nbsp;||
|**Environment Variables**||
|arkhos.env(environment_variable)|Not implemented|
