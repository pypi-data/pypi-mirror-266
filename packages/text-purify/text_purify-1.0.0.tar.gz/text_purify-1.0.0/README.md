# Text purify

## Remove special characters
```python
import text_purify

text = "Jakiś! tekst? z #różnymi$ znakami& specjalnymi*."

cleanText = text_purify.remove_special_characters(text)
print(cleanText) # Jakiś tekst z różnymi znakami specjalnymi
```

## Remove html tags
```python
import text_purify

text_with_html = "To jest <strong>ważny</strong> tekst z <a href='link' target = '_blank'>linkiem</a>."
clean_text = text_purify.remove_html_tags(text_with_html)
print(clean_text) # To jest ważny tekst z linkiem.
```

## Remove double spaces
```python
import text_purify

text = 'this   is test  text :)'
clean_text = text_purify.remove_double_spaces(text)
print(clean_text) # this is test text :)
```