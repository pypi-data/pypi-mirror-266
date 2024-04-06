To deploy to pip:
$ make build
$ make deploy

---

HashQuery refers to a collection of packages which work together
to provide an expressive language for users to author analytics.

> NOTE:
> Breaking changes to this package can have _source_ compatibility impact.

Framework code should not access private Hashboard packages or resources
directly. This code is designed to run on external customer hardware or
environments without the ability to talk with internal Hashboard services,
provided the `HashboardAPI` is configured to authenticate correctly.

Framework code explicitly relies on Hashboard to provide the backend for
its functionality. As a result, we don't build any SQL here or query any data
sources here, we just build API structures and dispatch them to Hashboard
servers.

---

# Related technologies (separate folders)

Below are some related packages that are located elsewhere but can be helpful
to understand to get a full picture of what's going on.

### Managed Execution

GraphQL endpoint which accepts HashQuery scripts (as source code) and
executes them on behalf of a user. This provides an endpoint that web clients
send raw Hashquery source code to in order to perform work and get a result.

The primary tasks of the managed execution code is to:

1. Provide an endpoint for which clients can send raw HashQuery source code to
   and receive results.
2. Prepare a performant, safe sandbox to run client Python code away from other
   server state.

Note that this may not be the only way to execute Hashquery logic. Users can
run framework code on their own hardware, provided they configure it to make
authorized requests to us.

### Hashboard APIs

`HashboardAPI` can make any requests against the Hashboard servers, including
GraphQL getters, mutations, or the DB aggregation endpoints. These requests
function like any other external network request to our web server, with the
one change being that users are authenticated via a JWT.
