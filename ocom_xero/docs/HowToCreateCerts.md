## On Windows
1. Install openssl from here : http://slproweb.com/products/Win32OpenSSL.html
2. Reboot
3. Run these. From (http://developer.xero.com/documentation/advanced-docs/public-private-keypair/)

## Generate .crt

Run the following on the command line (Works in linux and windows (as above)

> openssl genrsa -out privatekey.pem 1024
> openssl req -new -x509 -key privatekey.pem -out publickey.cer -days 1825

Enter some values.. Anything that makes sense

> openssl pkcs12 -export -out public_privatekey.pfx -inkey privatekey.pem -in publickey.cer

Leave the password blank

>openssl pkcs8 -topk8 -nocrypt -in privatekey.pem -out privatekey.pcks8
# From http://developer.xero.com/code-samples/libraries/java/
wAnd https://developer.xero.com/documentation/api-guides/create-publicprivate-key
