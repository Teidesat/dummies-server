from requests import post as post_request

#ENDPOINT = "http://receiver-server:5001/receive_binary"
ENDPOINT = "http://127.0.0.1:5001/receive_binary"

class Package:
  PACKAGE_SIZE = 4096
  STR_LENGTH = 80

  def __init__(self):
    self.bytes = b""
    self.percentage_package_tag = [] # To add tags when printing

  def send(self):
    diff = self.get_empty_space()
    bytes_to_send = self.bytes if diff == 0 else self.bytes + b"0" * diff
    post_request(ENDPOINT, data=bytes_to_send, headers={"Content-Type": "application/octet-stream"})

  def add_bytes(self, bytes_to_add: bytes, tag: str):
    """
    Adds the given bytes to the package. Give a tag to be displayed when printing these bytes.
    Returns the bytes that could not be added due to the size of the package,
    empty bytes object if all bytes were added succesfully.
    """
    empty_space = self.get_empty_space()
    next_bytes = bytes_to_add[0:empty_space]
    percentage_of_package = round(len(next_bytes) / Package.PACKAGE_SIZE * 100)
    if len(tag) == 0:
      tag = "B" # Default, B (Bytes)
    self.percentage_package_tag.append((percentage_of_package, tag[0]))
    self.bytes += next_bytes
    return bytes_to_add[empty_space + 1:]

  def get_empty_space(self):
    """
    Gets the empty space in the package.
    """
    return Package.PACKAGE_SIZE - len(self.bytes)

  def __str__(self):
    delimiter = " " + "-" * (Package.STR_LENGTH - 2) + " "
    content = "|"
    content_length = Package.STR_LENGTH - 2
    for (percentage, tag) in self.percentage_package_tag:
      package_length = round(percentage / 100 * content_length)
      package_content = " " * package_length
      if package_length >= 3:
        middle = package_length // 2
        package_content = package_content[:middle] + tag + package_content[middle + 1:] 
      package_content = package_content[0:len(package_content) - 1] + "|"
      content += package_content
    if len(content) == content_length + 1:
      content = content[:len(content) - 1] + " "
    else: # Fill with spaces
      content += " " * (content_length - len(content) + 1)
    content += "|"
    
    return "\n".join((delimiter, content, delimiter))