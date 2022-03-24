# LSB_Steganography
Python Program allowing the user to hide an image inside the Least Sig. Bit (LSB) of a second image (cover image). Requires that the cover image be slightly greater than 8x the size of the secret image (in bytes) as each byte of the hidden image will be hidden within a single bit of the cover image + metadata of the hidden image will also be embedded within the cover image. Tested with .bmp files only currently.

There is error checking in place to ensure that the cover image and secret image are the appropriate sizes and the program will not start unless there is sufficient room in the cover image to hide the secret image + metadata. 

The Program uses the Least Sig. Bit methodology. The program will first open both the cover and secret image, and iterate through each RGB pixel of the secret image, paired with 8 RGB pixels of the cover image. Each pixel is separated into their respective channels, and the least significant bit of each channel (byte) is replaces with the most significant bit of the secret image to create a resultant stego image. 

The Secret Image is also encrypted using a simple Caesar Cipher prior to the LSB Transformation of the cover image

i.e.
Cover Image:  00001111, 11110000, 11110000, 00001111, 11110000, 00001111, 00001111, 11110000

Secret Image: 01100101

Stego Image:  00001110, 11110001, 11110001, 00001110, 11110000, 00001111, 00001110, 11110001

The decoding process is simply the reverse. The cover image is processed 24 bytes at a time via a generator. The least significant bit of each byte is pulled out and combined into a Red, Green and Blue value to create 1 pixel of the Secret Image per 24 bytes of the Cover image. The metadata is also pulled out, including the filename, extension, and size of the hidden image, using delimiter characters to tell the program when the Image Data stops and when the Metadata starts.

Once all the pixels are re-created for the Secret Image, they are combined with the information regarding the dimensions (pulled out from the metadata) to rewrite the image pixel by pixel using the PIL library.


## Compatability
* Runs on Python 3.9
* Currently only tested for .bmp files
* Tested on Windows 10 Version 10.0.19044 Build 19044
* Secret and Cover images are converted to RGB Files if not already in RGB channel format 


# How To
## Usage:
  If Encoding:
  LSB_Main.py -c <coverfile> -s <secretfile> -o <outputfile>
  
  If Decoding:
  LSB_Main.py -f <stegofile> -o <hidden output file>
  
## Options:
  -h, --help                Show this help
  
  If Encoding:
*  -c,--cover=<file>         Cover Image that will hide the file ( Only required for encoding )
*  -s,--secret=<file>        Secret Image that will be hidden ( Only required for encoding ) 
*  -o,--output=<file>        Resultant output file ( Only required for encoding ) 
  
  If Decoding:
*  -f, --stegofile=<file>    File with the hidden data that will be extracted ( Only required for decoding )
*  -o, --output=<file>       File that the extracted hidden data will be written to ( Only required for decoding )


## Quickstart
1) Download .ZIP File and extract to a directory of your choice
2) ```sudo python3 SSH_Auth_Monitor.py -t [Timelimit] -f [logfile] -l [Threshold]```
3) i.e. ``` sudo python3 SSH_Auth_Monitor.py -t 5 -l 5 ```

### Example Output
![image](https://user-images.githubusercontent.com/77559638/151867534-33fc3318-df21-4297-8a7a-df7a83e98b74.png)

![image](https://user-images.githubusercontent.com/77559638/151867617-4409faf3-0614-4f7e-bd8c-b092345b847c.png)

![image](https://user-images.githubusercontent.com/77559638/151867645-a87869fd-7458-4da8-9532-41bb13fda312.png)

![image](https://user-images.githubusercontent.com/77559638/151871927-9a8b0749-5aab-43ca-8db6-3dad96e68fe5.png)


