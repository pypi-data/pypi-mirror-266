# PiFolderOrganizer

PiFolderOrganizer is a Python package that helps organize files into different categories based on their file extensions.

## Installation

You can install PiFolderOrganizer using pip:

```bash
pip install pi-folder-organizer
```
## Usage
To use PiFolderOrganizer in your Python code, import the PiFolderOrganizer class:
```python
from pi_folder_organizer import PiFolderOrganizer
```
Make object of class
```python
pi_organizer=PiFolderOrganizer()
```
To continue with default cleaning:
```python
pi_organizer.pi_folder_organizer("/path/to/source_folder", "/path/to/destination_folder")
```
If you want to see which folders and extentions I use:
```python
pi_organizer.get_counter()
```
This will return you a dictionary of folders and the files list as folder's files.
Same for getting extensions
```python
pi_organizer.get_extensions()
```
This will return you a dictionary of folders and the files tuple of file's extensions.

### Customization Options

You can customize the counter dictionary and extensions dictionary according to your preferences. Here's how:

```python
from pi_folder_organizer import PiFolderOrganizer

# Initialize PiFolderOrganizer
pi_organizer = PiFolderOrganizer()

# Customize the counter dictionary
new_counter = {
    "Images": [],
    "Documents": []
}

# Set the new counter
pi_organizer.set_counter(new_counter)
print("Updated Counter:", pi_organizer.get_counter())

# Customize the extensions dictionary
new_extensions = {
    "Images": (".png", ".jpg"),
    "Documents": (".txt", ".docs")
}

# Set the new extensions
pi_organizer.set_extensions(new_extensions)
print("Updated Extensions:", pi_organizer.get_extensions())

# Run the PiFolderOrganizer method after your setup
pi_organizer.pi_folder_organizer("source_folder", "destination_folder")
```
**Note**
The length of ```new_counter``` and ```new_extensions``` must be same. The remaining files automatically moved to folder ```Others```.

### Contact Information

Feel free to reach out to me on social media:

[![GitHub](https://img.shields.io/badge/GitHub-mrqadeer)](https://github.com/mrqadeer)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Qadeer)](https://www.linkedin.com/in/qadeer-ahmad-3499a4205/)
[![Twitter](https://img.shields.io/badge/Twitter-Twitter)](https://twitter.com/mr_sin_of_me)
[![Facebook](https://img.shields.io/badge/Facebook-Facebook)](https://web.facebook.com/mrqadeerofficial/)




## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
