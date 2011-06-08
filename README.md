# oreilly_downloader #

## Description ##

This script downloads your e-books from the O'Reilly website

## Usage ##

List available books/formats for download

    python oreilly_downloader.py list
    
Download a specified book in a specified format

    python oreilly_downloader.py download -t "Cooking for Geeks" pdf
    
Download all books in a specified format

    python oreilly_downloader.py download --all pdf
    
## Password File ##

If you don't care about storing your password in plaintext on the file system, you can avoid needing to be prompted for your username and password by creating a file:

    # ~/.scriptconfig
    
    [oreilly]
    email = john.doe@domain.com
    password = p@ssw0rd
    