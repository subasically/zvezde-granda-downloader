import requests

def thumbnail(url, filename):
    print(filename)
    # This statement requests the resource at 
    # the given link, extracts its contents 
    # and saves it in a variable 
    data = requests.get(url).content
    
    # Opening a new file named img with extension .png 
    # This file would store the data of the image file 
    f = open(f"downloads/{filename}",'wb')
    
    # Storing the image data inside the data variable to the file 
    f.write(data) 
    f.close()