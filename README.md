## Usage
### Text
Embed text data into text.
```
python stealth_text.py x
```
Extract embedded data.
```
python stealth_text.py x󠅘󠅕󠅜󠅜󠅟󠄐󠅧󠅟󠅢󠅜󠅔 --decode
```
### Image
Embed image data into text.
```
python stealth_text.py 🐈 -i cat.jpg -o out.txt
```
Extract embedded data.
```
python stealth_text.py -i out.txt -o cat.jpg --decode
```
### Large data
Embed large data into text.
```
python stealth_text.py BIG -i bigcat.mp4 -o out.txt -c
```
Extract embedded data.
```
python stealth_text.py -i out.txt -o bigcat.mp4 -d --decode
```