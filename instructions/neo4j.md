# Connect and log in to the project's neo4j instance.

## URL

Our neo4j server can be found at: https://neo4j-wft-med.dieterichlab.org:7473/

## Browser configuration

We had problems login with firefox on both Linux and Windows, so we strongly advice to use Chrome/Chromium in the case you experience login issues. Alternatively, you can also setup [neo4j Desktop](https://neo4j.com/download/).

### TLS certificate

Please install our trust certficate  (under [/assets/DieterichLab_CA.crt](/assets/DieterichLab_CA.crt)) to rule out any errors that may occur accessing dieterichlab URLs. Just google for "Certificate Manager" or "Import Certificates" for your corresponding browser. For Firefox it is usually:

```
Preferences --> Certificates --> View Certificates --> Authorities --> Import...
```

## Login

You'll see a login UI, where you only have to switch fom `neo4j+s://` to `bolt+s://` and type in your username and password:

* `username`: _first letter of first name_ + _full last name_ (i.e. _pwiesenbach_)
* `password`: _abcd1234_

You will be prompted to change your password on first login.

![jupyter_lab_with_kernels](../assets/images/neo4j_login.png)
