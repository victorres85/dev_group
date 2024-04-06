
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv('.env')
ENVIRONMENT = 'prod'

NEO4J_PASSWORD = 'password'
NEO4J_USERNAME = 'neo4j'
NEO4J_HOST = 'localhost:7687'
PROTOCOL = 'bolt'

if ENVIRONMENT == 'prod':
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_HOST = os.getenv("NEO4J_HOST")
    NEO4J_PORT = os.getenv("NEO4J_PORT")
    PROTOCOL = 'bolt+s'



MARKDOWN = '''

# Welcome
<div style='display:flex; flex-direction:row; flex-wrap:wrap; margin-bottom:10px;'>
Welcome to TeamNet, feel free to modify any content of your profile by simple clicking on the element you want to modify, it will then change to an input type element, make the changes you like and do not forget to click on the <div style="border:solid 1px #0d6efd; border-radius:4px; width:120px; height:30px; display:flex; flex-direction:row; justify-content:center; align-items:center; margin-right:10px;"> <p style="color:#0d6efd; margin:0; "> Save Changes </p></div> button. </div>


You can use HTML tags or MarkDown to style your text and add links or images to it, please see below some basic MarkDown syntax which will allow you to write rich texts

## Basic Syntax
### Headers:

Use # for the main header (similar to HTML h1), ## for a secondary header (similar to h2), and so on, up to ###### for the smallest header (h6).

# Header 1

## Header 2

### Header 3

---

### Emphasis:

**Italic**: Wrap text with one asterisk or one underscore.
*italic* or _italic_ 

**Bold**: Use two asterisks or underscores.
**bold** or __bold__

**Combined**: bold & italic
**_bold & italic_**

---

### Lists:

**Unordered lists**: Use asterisks, plus signs, or hyphens interchangeably.

* Item 1
* Item 2
* Item 3

**Ordered lists**: Use numbers followed by periods.
1. First Item
2. Second Item
3. Third Item

---

### Links and Images:

**Links**: 
[Link Text](Text URL)

[Google](http://www.google.com)

**Images**: ![Alt text](Image URL)
![Sample Image](https://www.company02.com/resources/assets/images/sections/intro/background.jpg)

---

### Blockquotes:

Use > before the text.
> This is a blockquote.

---

### Code:
Inline code: Use single backticks.
\`Inline code\`

---

### Code blocks: 
Use triple backticks or indent with four spaces.

```
<!DOCTYPE html>
<html>
  <head>
    <title>Page Title</title>
  </head>
<body>
    <p> Body Content</p>
</body>
</html>
```

---

### Horizontal Rules:

Use three or more hyphens, asterisks, or underscores.

---

'''