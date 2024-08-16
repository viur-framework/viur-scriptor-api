WebRequest
==========
The ``WebRequest``-Class handles HTTP(S)-Request. It supports GET, POST, PUT and DELETE operations.
The main functionality is in the ``request``-method, to which you have to pass the method-parameter.
For convenience there are the explicit methods ``get``, ``post``, ``put`` and ``delete``.

In the Browser, some requests might not succeed because of CORS-policies (Cross Origin Resource Sharing:
see `the wikipedia article for CORS <https://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_). This
will raise an exception.

The return value of all methods of ``WebRequest`` is a ``WebResponse``. ``WebResponse`` inherits all functionality from
``File``, so you can use all methods of it (i.e. as_text, as_list_table etc.).
Additionaly there is ``get_url``, ``get_status_code`` and ``get_content``.
The ``get_status_code`` method returns the HTTP-Status code. This should be a value between (incl.) 200 and 299 if the
request was successful. Otherwise the code will indicate what went wrong
(see `the wikipedia article for HTTP-Status-Codes <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_).
