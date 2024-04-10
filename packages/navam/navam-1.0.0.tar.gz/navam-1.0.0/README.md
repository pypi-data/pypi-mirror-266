# Navam's Encryption Technique (NET)

## Encrypting

```python
from navam import encrypt
encrypt('path_to_file')
```

The encrypted file is stored as `encrypted.nvm`

## Decrypting

```python
from navam import decrypt
decrypt('encrypted.nvm')
```

> [!NOTE]
> NET encrypts a single file. So, consider zipping a folder you want to encrypt.  
> The encrypted file can be many times larger than the original file.
