.SUFFIXES:	.priv .pub .cert .csr .req
.PRECIOUS:	%.priv %.pub %.cert %.csr %.req

DEFAULT:	all

CA_DIR:=	CERTIFICATE_AUTHORITY
CA_NAME:=	$(CA_DIR)/fetch-ca
ROOT_CERT:=	$(CA_NAME).cert

# comment me to make the CA cleanable.
LOCK	:=	lockout

#-----------------------------------------------------------------------------
# How to build parts of the certificate authority.
#

certificates:
	mkdir -p certificates

$(CA_NAME).cert: $(CA_DIR)/serial $(CA_DIR)/index.txt $(CA_NAME).priv $(CA_NAME).req certificates
	mkdir -vp certs $(CA_DIR)/crl newcerts $(CA_DIR)/private
	openssl req \
		-new \
		-config $(CA_NAME).cnf \
		-x509 \
		-days 7305 \
		-extensions rootcert_extensions \
		-key $*.priv \
		-out $*.cert \
		-outform PEM

	@hash=`openssl x509 -hash -in $(ROOT_CERT) | head -1`;\
	hashname="certificates/$$hash.0";\
	cp -v $(ROOT_CERT) $$hashname;

$(CA_DIR)/index.txt:
	@echo "----------------------------------------------------------------"
	@echo "creating index"
	mkdir -vp certs $(CA_DIR)/crl newcerts $(CA_DIR)/private
	cp /dev/null $(CA_DIR)/index.txt

$(CA_DIR)/serial:
	@echo "----------------------------------------------------------------"
	@echo "creating serial number store"
	mkdir -vp certs $(CA_DIR)/crl newcerts $(CA_DIR)/private
	echo "01" > $(CA_DIR)/serial



$(LOCK)clean:
	rm -f $(CA_NAME).priv $(CA_NAME).pub $(CA_NAME).req \
		$(CA_NAME).cert $(CA_NAME).csr
	rm -f client.priv client.pub client.req client.cert client.csr
	rm -f serial index.txt
	rm -rf private

#------------------------------------------------------------------------------


%.priv:
	openssl genrsa -out $*.priv 1024
	openssl rsa -in $*.priv -out $*.pub

%.req:	%.cnf %.priv
	openssl req -new -config $*.cnf -key $*.priv \
	-out $*.req -outform PEM

%.cert:	%.priv %.req $(CA_NAME).cert
	openssl ca -batch -in $*.req -out $*.cert \
	-config $(CA_NAME).cnf -days 3650

%.p12:	%.priv %.cert
	foo=`basename "$*"`;echo "NAME=$$foo";openssl pkcs12 \
	-export -out $*.p12 \
	-in $*.cert \
	-inkey $*.priv \
	-name $$foo

%.pem:	%.priv %.cert
	@cat $*.priv $*.cert > $*.pem
	@openssl x509 -text -in $*.pem
	@openssl rsa -text -in $*.pem

%.show:
	@echo "$* = $($*)"

%.verify:	%.cert	certificates
	openssl verify \
	-verbose \
	-CApath certificates \
	-purpose sslclient \
	\
	$*.cert

%.reqshow:	%.req
	openssl req -in $*.req -text -noout

%.certshow:	%.cert
	openssl x509 -in $*.cert -text -noout

%.fingerprint:	%.cert
	openssl x509 -noout -in $*.cert -fingerprint

%.dershow:	%.der
	openssl x509 -inform DER -in $*.der -text -noout

%.der:	%.cert
	openssl x509 -in $*.cert -outform der -out $*.der

#REQ_INPUTS:=	$(wildcard requests/*.cnf)
#REQ_KEYS:=	$(REQ_INPUTS:.cnf=.priv)
#REQ_REQS:=	$(REQ_INPUTS:.cnf=.req)
#REQ_CERTS:=	$(REQ_INPUTS:.cnf=.cert)
#REQ_DERS:=	$(REQ_INPUTS:.cnf=.der)
#REQ_VERIFIES:=	$(REQ_INPUTS:.cnf=.verify)
#REQ_P12S:=	$(REQ_INPUTS:.cnf=.p12)
#
#all:	$(CA_NAME).req $(CA_NAME).cert $(CA_NAME).der
#signatures:	$(REQ_CERTS) $(REQ_DERS) $(REQ_P12S)
