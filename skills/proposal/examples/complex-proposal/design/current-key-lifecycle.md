# Current key lifecycle

The authentication service signs tokens with one private key and verifiers cache its
public key. Regional cache propagation is asynchronous. Tokens identify a signing key
in the `kid` header and remain valid for ten minutes.
