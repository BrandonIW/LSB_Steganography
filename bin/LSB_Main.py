import pyfiglet
import termcolor

from LSB_Args import check_args
from LSB_Image import encoder, decoder
from time import sleep

"""
LSB_Main.py

Usage:
  If Encoding:
  LSB_Main.py -c <coverfile> -s <secretfile> -o <outputfile>
  
  If Decoding:
  LSB_Main.py -f <stegofile> -h <hidden output file>
  
Options:
  -h, --help                Show this help
  
  If Encoding:
  -c,--cover=<file>         Cover Image that will hide the file ( Only required for encoding )
  -s,--secret=<file>        Secret Image that will be hidden ( Only required for encoding ) 
  -o,--output=<file>        Resultant output file ( Only required for encoding ) 
  
  If Decoding:
  -f, --stegofile=<file>    File with the hidden data that will be extracted ( Only required for decoding )
  -o, --output=<file>       File that the extracted hidden data will be written to ( Only required for decoding )
"""


# TODO - Test only of BMP files first. Edit the Help/Parser with whatever file formats we end up doing
# TODO - Edit the option #3 (print help stuff) if we find out that what we put so far is wrong lol
# TODO - Depending on if we use png and jpg etc. then we might need to do some checks for the --output option?
# TODO - Encryption of hidden file before stego creation

class Bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    ascii_title = pyfiglet.figlet_format("LSB Steganography", font="slant")
    print(termcolor.colored(ascii_title, color='cyan'))

    steg_options = {
        1: _encode_image,
        2: _decode_image,
        3: _print_help
    }

    print(f"{Bcolours.OKBLUE}Please choose an option below")
    while True:
        _print_main_menu()
        option = input("Enter your choice: ")
        if option not in ["1", "2", "3", "4"]:
            print(f"{Bcolours.OKBLUE}Invalid option. Choose 1, 2, 3, or 4\n")
            sleep(1)
            continue
        elif option == "4":
            print(f"{Bcolours.FAIL}Exiting Program...")
            sleep(1)
            quit(0)

        steg_options[int(option)]()


def _encode_image():
    print(f"Running verification checks on files...")
    sleep(1)
    args = check_args(True)

    if not args:
        print(f"{Bcolours.FAIL}The cover image must be slightly larger than 8x the size (in bytes) than the secret "
              f"image. (Must accommodate entirety of secret image in LSB + Metadata) Please "
              f"input different images for the arguments or check file size")
        quit(1)

    print(f"{Bcolours.OKGREEN}Success. Starting program...")
    sleep(1)
    print(f"{Bcolours.OKGREEN}Parameters Inputted: Cover Image: {args.cover} | Secret Image: {args.secret} | "
          f"Output File: {args.output}")

    encoder(args.cover, args.secret, args.output)
    print(f"{Bcolours.OKGREEN}Completed. Output/Stego File: {args.output}")


def _decode_image():
    print(f"Running verification checks on files...")
    sleep(1)
    args = check_args()

    print(f"{Bcolours.OKGREEN}Success. Starting program...")
    sleep(1)
    print(f"{Bcolours.OKGREEN}Parameters Inputted: Stego File: {args.stegofile} | "
          f"Output File: {args.output}")

    decoder(args.stegofile, args.output)
    print(f"{Bcolours.OKGREEN}Completed. Output Hidden File: {args.output}")


#####________Menu Printing Functions________######

def _print_main_menu():
    menu_options = {
        1: 'Encode Image',
        2: 'Decode Image',
        3: 'Help/How-To',
        4: 'Exit Application'
    }
    print("\n")
    for key in menu_options.keys():
        print(f"{Bcolours.OKBLUE}{key} - {menu_options[key]}")
    print("\n")


def _print_help():
    print(f"\n{Bcolours.OKBLUE}This program functions by taking in 2 or 3 required cmd-line parameters depending on "
          f"what the user wants to accomplish, either encoding or deocoding. These options are selected in the main "
          f"menu when you return back to the app{Bcolours.ENDC}")
    print(f"{Bcolours.OKBLUE}For Example:\n{Bcolours.OKGREEN}Cover Image: 00001111, 11110000, 11110000, 00001111, "
          f"11110000, 00001111, "
          f"00001111, 11110000\n{Bcolours.OKCYAN}Secret Image: 01100101\n{Bcolours.WARNING}Stego Image: 00001110, "
          f"11110001, 11110001, 00001110, 11110000, 00001111, 00001110, 11110001\n")
    print(f"{Bcolours.OKBLUE}The above example places each bit of the Secret Image into the LSB of each byte of the "
          f"cover image, resulting in our final Stego Image. This process is repeated until the entire Secret Image "
          f"is hidden\n{Bcolours.ENDC}")

    print(f"\n{Bcolours.UNDERLINE}{Bcolours.BOLD}Encoding{Bcolours.ENDC}")
    print(f"\n{Bcolours.UNDERLINE}{Bcolours.OKBLUE}Description{Bcolours.ENDC}")
    print(f"{Bcolours.OKBLUE}Takes in required parameters of -c/--cover, -o/--output and -s/--secret. -c refers to "
          f"the image that will be used to hide the secret image. Must be slightly larger than 8x the size of the "
          f"secret image, in bytes. -s refers to the secret image that will be hidden within the cover image. -o "
          f"refers to the resultant stego file that contains the hidden information{Bcolours.ENDC}")
    print(f"\n{Bcolours.UNDERLINE}{Bcolours.OKBLUE}Usage{Bcolours.ENDC}")
    print(f"{Bcolours.OKBLUE}LSB_Main.py -c Coverfile.bmp -s Hiddenfile.bmp -o stegofile.bmp{Bcolours.ENDC}")

    print(f"\n{Bcolours.UNDERLINE}{Bcolours.BOLD}Decoding{Bcolours.ENDC}")
    print(f"\n{Bcolours.UNDERLINE}{Bcolours.OKBLUE}Description{Bcolours.ENDC}")
    print(
        f"{Bcolours.OKBLUE}Takes in required parameters of -f/--stegofile and -o/--output. -f refers to the "
        f"resultant stego file created during the encoding process. -h refers to the resultant output file that will "
        f"be created after the decoding process, that will contain the hidden image{Bcolours.ENDC}")
    print(f"\n{Bcolours.UNDERLINE}{Bcolours.OKBLUE}Usage{Bcolours.ENDC}")
    print(f"{Bcolours.OKBLUE}LSB_Main.py -f Stegofile.bmp -h HiddenImageExtracted.bmp{Bcolours.ENDC}")

    sleep(2)
    input("Type anything to return to App: ")
    return


if __name__ == "__main__":
    main()
