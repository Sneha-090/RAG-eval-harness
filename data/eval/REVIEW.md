# Draft benchmark review sheet

Status: pending author review. Checking a box requires reviewing the question,
reference and evidence in the frozen source; text validation alone is insufficient.
All evidence items are required. Reserved test questions must not guide tuning.

## q001 — direct / dev

- [ ] Author reviewed

**Question:** Which declaration is needed to read a cookie instead of a query parameter?

**Reference:** Use Cookie; without it the parameter is interpreted as a query parameter.

**Evidence:**

- `cookie-params.md`: To declare cookies, you need to use `Cookie`, because otherwise the parameters would be interpreted as query parameters.

## q002 — direct / dev

- [ ] Author reviewed

**Question:** How does Header handle underscores in parameter names by default?

**Reference:** Header converts underscores to hyphens when extracting and documenting headers.

**Evidence:**

- `header-params.md`: So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

## q003 — direct / dev

- [ ] Author reviewed

**Question:** Should HTTPException be returned or raised?

**Reference:** It must be raised because it is a Python exception.

**Evidence:**

- `handling-errors.md`: Because it's a Python exception, you don't `return` it, you `raise` it.

## q004 — direct / dev

- [ ] Author reviewed

**Question:** Where do query parameters appear in a URL and how are they separated?

**Reference:** They follow the question mark and are separated by ampersands.

**Evidence:**

- `query-params.md`: The query is the set of key-value pairs that go after the `?` in a URL, separated by `&` characters.

## q005 — similar_page / dev

- [ ] Author reviewed

**Question:** How do I explicitly read a header versus a cookie, rather than treating either as a query parameter?

**Reference:** Use Header for headers and Cookie for cookies; without those declarations they are interpreted as query parameters.

**Evidence:**

- `header-params.md`: To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

- `cookie-params.md`: To declare cookies, you need to use `Cookie`, because otherwise the parameters would be interpreted as query parameters.

## q006 — multi_part / dev

- [ ] Author reviewed

**Question:** How do I disable header underscore conversion, and what compatibility issue should I consider?

**Reference:** Set convert_underscores to False on Header. Some HTTP proxies and servers disallow headers containing underscores.

**Evidence:**

- `header-params.md`: If for some reason you need to disable automatic conversion of underscores to hyphens, set the parameter `convert_underscores` of `Header` to `False`:

- `header-params.md`: Before setting `convert_underscores` to `False`, bear in mind that some HTTP proxies and servers disallow the usage of headers with underscores.

## q007 — multi_part / dev

- [ ] Author reviewed

**Question:** How can duplicate header values be declared, and what Python type receives their values?

**Reference:** Use a list in the type declaration; the duplicate values are received as a Python list.

**Evidence:**

- `header-params.md`: You can define those cases using a list in the type declaration.

- `header-params.md`: You will receive all the values from the duplicate header as a Python `list`.

## q008 — paraphrase / dev

- [ ] Author reviewed

**Question:** Can the detail of an HTTPException contain structured data rather than just text?

**Reference:** Yes. It accepts JSON-convertible values, including dictionaries and lists.

**Evidence:**

- `handling-errors.md`: When raising an `HTTPException`, you can pass any value that can be converted to JSON as the parameter `detail`, not only `str`.

- `handling-errors.md`: You could pass a `dict`, a `list`, etc.

## q009 — paraphrase / dev

- [ ] Author reviewed

**Question:** How can a query argument be made mandatory without assigning it a default?

**Reference:** Declare it without a default value.

**Evidence:**

- `query-params.md`: But when you want to make a query parameter required, you can just not declare any default value:

## q010 — unanswerable / dev

- [ ] Author reviewed

**Question:** Which Docker base image and Dockerfile instructions should I use to deploy this FastAPI application?

**Reference:** I cannot find this in the provided documentation.

**Evidence:**

No gold evidence: confirm the requested instructions are absent across all 12 pages.

## q011 — direct / dev

- [ ] Author reviewed

**Question:** What class should a request-body data model inherit from?

**Reference:** It should inherit from Pydantic BaseModel.

**Evidence:**

- `body.md`: Then you declare your data model as a class that inherits from `BaseModel`.

## q012 — direct / dev

- [ ] Author reviewed

**Question:** When both response_model and a return type annotation are declared, which does FastAPI use?

**Reference:** FastAPI gives response_model priority.

**Evidence:**

- `response-model.md`: If you declare both a return type and a `response_model`, the `response_model` will take priority and be used by FastAPI.

## q013 — direct / dev

- [ ] Author reviewed

**Question:** Should a dependency function be called when it is passed to Depends?

**Reference:** No. Pass the function itself without calling it.

**Evidence:**

- `dependencies__index.md`: You **don't call it** directly (don't add the parenthesis at the end), you just pass it as a parameter to `Depends()`.

## q014 — direct / dev

- [ ] Author reviewed

**Question:** What status code does OAuth2PasswordBearer return when the Authorization header has no Bearer token?

**Reference:** It returns HTTP 401 Unauthorized.

**Evidence:**

- `security__first-steps.md`: If it doesn't see an `Authorization` header, or the value doesn't have a `Bearer ` token, it will respond with a 401 status code error (`UNAUTHORIZED`) directly.

## q015 — direct / dev

- [ ] Author reviewed

**Question:** Can a path parameter become optional by setting its default to None?

**Reference:** No. Path parameters are always required, even when a default or None is declared.

**Evidence:**

- `path-params-numeric-validations.md`: A path parameter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

## q016 — direct / dev

- [ ] Author reviewed

**Question:** Why must /users/me be declared before /users/{user_id}?

**Reference:** Routes are evaluated in order; otherwise the variable route can match me as user_id.

**Evidence:**

- `path-params.md`: Because *path operations* are evaluated in order, you need to make sure that the path for `/users/me` is declared before the one for `/users/{user_id}`:

- `path-params.md`: Otherwise, the path for `/users/{user_id}` would match also for `/users/me`, "thinking" that it's receiving a parameter `user_id` with a value of `"me"`.

## q017 — direct / dev

- [ ] Author reviewed

**Question:** Which query declaration option hides a parameter from OpenAPI documentation?

**Reference:** Set Query include_in_schema to False.

**Evidence:**

- `query-params-str-validations.md`: To exclude a query parameter from the generated OpenAPI schema (and thus, from the automatic documentation systems), set the parameter `include_in_schema` of `Query` to `False`:

## q018 — direct / dev

- [ ] Author reviewed

**Question:** Where is the raw OpenAPI schema available in the tutorial application?

**Reference:** At /openapi.json.

**Evidence:**

- `first-steps.md`: You can see it directly at: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json).

## q019 — direct / test

- [ ] Author reviewed

**Question:** Which decorator installs a handler for a custom exception?

**Reference:** Use @app.exception_handler().

**Evidence:**

- `handling-errors.md`: You could add a custom exception handler with `@app.exception_handler()`:

## q020 — direct / test

- [ ] Author reviewed

**Question:** Which response model setting omits fields that were not explicitly set?

**Reference:** Set response_model_exclude_unset=True.

**Evidence:**

- `response-model.md`: You can set the *path operation decorator* parameter `response_model_exclude_unset=True`:

- `response-model.md`: and those default values won't be included in the response, only the values actually set.

## q021 — direct / test

- [ ] Author reviewed

**Question:** Which dependency is required to parse the form data used by the OAuth2 password flow?

**Reference:** The python-multipart package is needed because OAuth2 sends the username and password as form data.

**Evidence:**

- `security__first-steps.md`: However, if you use the `uv add fastapi` command, the `python-multipart` package is not included by default.

- `security__first-steps.md`: To install it manually, add it to your project with:

- `security__first-steps.md`: $ uv add python-multipart

- `security__first-steps.md`: This is because **OAuth2** uses "form data" for sending the `username` and `password`.

## q022 — similar_page / dev

- [ ] Author reviewed

**Question:** Which helpers add validation metadata to query parameters and path parameters respectively?

**Reference:** Use Query for query parameters and Path for path parameters.

**Evidence:**

- `path-params-numeric-validations.md`: In the same way that you can declare more validations and metadata for query parameters with `Query`, you can declare the same type of validations and metadata for path parameters with `Path`.

## q023 — similar_page / dev

- [ ] Author reviewed

**Question:** Does a Pydantic model parameter represent a query parameter or a request body?

**Reference:** A parameter typed as a Pydantic model is interpreted as the request body.

**Evidence:**

- `body.md`: * If the parameter is declared to be of the type of a **Pydantic model**, it will be interpreted as a request **body**.

## q024 — similar_page / dev

- [ ] Author reviewed

**Question:** How do I receive a list from repeated query parameters rather than from the request body?

**Reference:** Explicitly use Query for the list-typed parameter; otherwise a list parameter is interpreted as a request body.

**Evidence:**

- `query-params-str-validations.md`: To declare a query parameter with a type of `list`, like in the example above, you need to explicitly use `Query`, otherwise it would be interpreted as a request body.

## q025 — similar_page / dev

- [ ] Author reviewed

**Question:** Is Depends used to specify an HTTP header value or to supply the result of a dependency function?

**Reference:** Depends supplies the dependency function result to a path-operation parameter; Header declares a header parameter.

**Evidence:**

- `dependencies__index.md`: * Assign that result to the parameter in your *path operation function*.

- `header-params.md`: To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

## q026 — similar_page / dev

- [ ] Author reviewed

**Question:** How do request-body models and response models differ in which direction they handle data?

**Reference:** A request body is client-to-API data; a response body is API-to-client data. A Pydantic request model declares input, while response_model converts and filters output.

**Evidence:**

- `body.md`: A **request** body is data sent by the client to your API. A **response** body is the data your API sends to the client.

- `body.md`: Then you declare your data model as a class that inherits from `BaseModel`.

- `response-model.md`: FastAPI will use this `response_model` to do all the data documentation, validation, etc. and also to **convert and filter the output data** to its type declaration.

## q027 — similar_page / dev

- [ ] Author reviewed

**Question:** Can query parameters have optional defaults in the same way as path parameters?

**Reference:** Query parameters can be optional and have defaults; path parameters are always required.

**Evidence:**

- `query-params.md`: As query parameters are not a fixed part of a path, they can be optional and can have default values.

- `path-params-numeric-validations.md`: A path parameter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

## q028 — similar_page / dev

- [ ] Author reviewed

**Question:** What differs between FastAPI HTTPException and Starlette HTTPException in the accepted detail value?

**Reference:** FastAPI accepts any JSON-able detail value, whereas Starlette accepts only strings.

**Evidence:**

- `handling-errors.md`: The only difference is that **FastAPI**'s `HTTPException` accepts any JSON-able data for the `detail` field, while Starlette's `HTTPException` only accepts strings for it.

## q029 — similar_page / test

- [ ] Author reviewed

**Question:** Does declaring tokenUrl on OAuth2PasswordBearer create a token endpoint, or only document one?

**Reference:** It declares the URL clients should use and documents it in OpenAPI; it does not create the endpoint.

**Evidence:**

- `security__first-steps.md`: This parameter doesn't create that endpoint / *path operation*, but declares that the URL `/token` will be the one that the client should use to get the token. That information is used in OpenAPI, and then in the interactive API documentation systems.

## q030 — similar_page / test

- [ ] Author reviewed

**Question:** What are the default URLs for the Swagger UI and ReDoc documentation?

**Reference:** Swagger UI is at /docs, and ReDoc is at /redoc.

**Evidence:**

- `first-steps.md`: Now go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

- `first-steps.md`: You will see the automatic interactive API documentation (provided by [Swagger UI](https://github.com/swagger-api/swagger-ui)):

- `first-steps.md`: And now, go to [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

- `first-steps.md`: You will see the alternative automatic documentation (provided by [ReDoc](https://github.com/Redocly/redoc)):

## q031 — multi_part / dev

- [ ] Author reviewed

**Question:** Can normal def and async def dependencies be mixed with either type of path-operation function?

**Reference:** Yes. Dependencies may use normal def or async def, and can be mixed with either kind of path-operation function.

**Evidence:**

- `dependencies__index.md`: You can use `async def` or normal `def`.

- `dependencies__index.md`: And you can declare dependencies with `async def` inside of normal `def` *path operation functions*, or `def` dependencies inside of `async def` *path operation functions*, etc.

## q032 — multi_part / dev

- [ ] Author reviewed

**Question:** What happens if HTTPException is raised inside a utility called by a path operation, and does the remaining path-operation code execute?

**Reference:** The request terminates immediately, the HTTP error is sent to the client, and the remaining path-operation code does not execute.

**Evidence:**

- `handling-errors.md`: This also means that if you are inside a utility function that you are calling inside of your *path operation function*, and you raise the `HTTPException` from inside of that utility function, it won't run the rest of the code in the *path operation function*, it will terminate that request right away and send the HTTP error from the `HTTPException` to the client.

## q033 — multi_part / dev

- [ ] Author reviewed

**Question:** Which comparisons do the numeric validation options gt and ge represent, and can numeric validation apply to floats?

**Reference:** gt means greater than, ge means greater than or equal, and numeric validation also supports floats.

**Evidence:**

- `path-params-numeric-validations.md`: * `gt`: `g`reater `t`han

- `path-params-numeric-validations.md`: * `ge`: `g`reater than or `e`qual

- `path-params-numeric-validations.md`: Number validations also work for `float` values.

## q034 — multi_part / dev

- [ ] Author reviewed

**Question:** What does FastAPI do when a Pydantic request body has invalid data, and how are model schemas exposed?

**Reference:** It returns an error indicating the invalid data; model JSON Schemas are included in OpenAPI and used by automatic documentation.

**Evidence:**

- `body.md`: * If the data is invalid, it will return a nice and clear error, indicating exactly where and what was the incorrect data.

- `body.md`: * Those schemas will be part of the generated OpenAPI schema, and used by the automatic documentation <abbr title="User Interfaces">UIs</abbr>.

## q035 — multi_part / test

- [ ] Author reviewed

**Question:** How can a response omit a password even if the returned object contains one, and why is filtering useful?

**Reference:** Declare an output model without the password and use it as response_model. FastAPI filters undeclared data, preventing the password from being exposed.

**Evidence:**

- `response-model.md`: We can instead create an input model with the plaintext password and an output model without it:

- `response-model.md`: ...we declared the `response_model` to be our model `UserOut`, that doesn't include the password:

- `response-model.md`: So, **FastAPI** will take care of filtering out all the data that is not declared in the output model (using Pydantic).

## q036 — multi_part / test

- [ ] Author reviewed

**Question:** What does OAuth2PasswordBearer extract from the Authorization header, and does this tutorial already verify the token validity?

**Reference:** It extracts the Bearer token and returns it as a string. This tutorial does not yet verify token validity.

**Evidence:**

- `security__first-steps.md`: It will go and look in the request for that `Authorization` header, check if the value is `Bearer ` plus some token, and will return the token as a `str`.

- `security__first-steps.md`: We are not verifying the validity of the token yet, but that's a start already.

## q037 — paraphrase / dev

- [ ] Author reviewed

**Question:** My Python argument name cannot contain a dash, but the URL must use item-query. What feature maps those names?

**Reference:** Declare an alias for the query parameter; the alias is used to find its value.

**Evidence:**

- `query-params-str-validations.md`: Then you can declare an `alias`, and that alias is what will be used to find the parameter value:

## q038 — paraphrase / dev

- [ ] Author reviewed

**Question:** I want older clients to keep using a query argument while the docs mark it obsolete. What should I set?

**Reference:** Set deprecated=True on Query.

**Evidence:**

- `query-params-str-validations.md`: Then pass the parameter `deprecated=True` to `Query`:

## q039 — paraphrase / dev

- [ ] Author reviewed

**Question:** Can a request argument allow null yet still require the caller to supply a value?

**Reference:** Yes. Allow None in its type but do not declare a default value.

**Evidence:**

- `query-params-str-validations.md`: You can declare that a parameter can accept `None`, but that it's still required. This would force clients to send a value, even if the value is `None`.

- `query-params-str-validations.md`: To do that, you can declare that `None` is a valid type but simply do not declare a default value:

## q040 — paraphrase / dev

- [ ] Author reviewed

**Question:** Must I manually register a class before FastAPI can execute a shared dependency?

**Reference:** No. Pass the dependency to Depends; no special registration class is required.

**Evidence:**

- `dependencies__index.md`: Notice that you don't have to create a special class and pass it somewhere to **FastAPI** to "register" it or anything similar.

- `dependencies__index.md`: You just pass it to `Depends` and **FastAPI** knows how to do the rest.

## q041 — paraphrase / dev

- [ ] Author reviewed

**Question:** Why do my typed query inputs arrive as integers even though a URL carries text?

**Reference:** FastAPI converts the query strings to their declared Python types and validates them.

**Evidence:**

- `query-params.md`: As they are part of the URL, they are "naturally" strings.

- `query-params.md`: But when you declare them with Python types (in the example above, as `int`), they are converted to that type and validated against it.

## q042 — paraphrase / dev

- [ ] Author reviewed

**Question:** Can I constrain a URL path variable to a fixed set of named choices?

**Reference:** Yes. Use a standard Python Enum for predefined path parameter values.

**Evidence:**

- `path-params.md`: If you have a *path operation* that receives a *path parameter*, but you want the possible valid *path parameter* values to be predefined, you can use a standard Python <abbr title="Enumeration">`Enum`</abbr>.

## q043 — paraphrase / dev

- [ ] Author reviewed

**Question:** I filled in a cookie in the interactive docs, but Execute behaves as though no cookie was supplied. Why?

**Reference:** The docs UI uses JavaScript, and browser cookie handling prevents those entered cookies from being sent by that UI.

**Evidence:**

- `cookie-params.md`: But even if you **fill the data** and click "Execute", because the docs UI works with **JavaScript**, the cookies won't be sent, and you will see an **error** message as if you didn't write any values.

## q044 — paraphrase / dev

- [ ] Author reviewed

**Question:** Can the schema produced by FastAPI help generate clients for other applications?

**Reference:** Yes. The OpenAPI schema can be used to automatically generate client code for applications communicating with the API.

**Evidence:**

- `first-steps.md`: You could also use it to generate code automatically, for clients that communicate with your API. For example, frontend, mobile or IoT applications.

## q045 — paraphrase / test

- [ ] Author reviewed

**Question:** Does the order of header-name capitalization matter when declaring a Header parameter?

**Reference:** No. HTTP headers are case-insensitive, so standard Python snake_case names can be used.

**Evidence:**

- `header-params.md`: Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

## q046 — paraphrase / test

- [ ] Author reviewed

**Question:** Will a dependency be able to require another dependency of its own?

**Reference:** Yes. Dependencies may define their own dependencies; FastAPI resolves the hierarchy and injects results.

**Evidence:**

- `dependencies__index.md`: You can define dependencies that in turn can define dependencies themselves.

- `dependencies__index.md`: In the end, a hierarchical tree of dependencies is built, and the **Dependency Injection** system takes care of solving all these dependencies for you (and their sub-dependencies) and providing (injecting) the results at each step.

## q047 — unanswerable / dev

- [ ] Author reviewed

**Question:** What Alembic commands create and apply a PostgreSQL database migration for this application?

**Reference:** I cannot find this in the provided documentation.

**Evidence:**

No gold evidence: confirm the requested instructions are absent across all 12 pages.

## q048 — unanswerable / dev

- [ ] Author reviewed

**Question:** How should a Redis connection be configured to cache API responses with a time-to-live?

**Reference:** I cannot find this in the provided documentation.

**Evidence:**

No gold evidence: confirm the requested instructions are absent across all 12 pages.

## q049 — unanswerable / dev

- [ ] Author reviewed

**Question:** What Kubernetes deployment and service YAML should expose this application?

**Reference:** I cannot find this in the provided documentation.

**Evidence:**

No gold evidence: confirm the requested instructions are absent across all 12 pages.

## q050 — unanswerable / test

- [ ] Author reviewed

**Question:** What code implements a WebSocket endpoint that broadcasts messages to all connected clients?

**Reference:** I cannot find this in the provided documentation.

**Evidence:**

No gold evidence: confirm the requested instructions are absent across all 12 pages.
