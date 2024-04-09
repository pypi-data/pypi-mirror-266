from weasyform.FormFinisher import FormFinisher
from weasyprint import HTML
html = """
<style>
table {
    width: 100%;
    
}

table, th, td {
  border: 1px solid;
}

input {
    width: 100%;
    height: 20px;
}

input, textarea, select {
  display: block;
  appearance: auto;
}

</style>
<h1>TEST</h1>
<table>
<tr>
    <th>URL</th><td><a href="https://salamek.cz">This is a URL</a></td>
</tr>
<tr>
    <th>URL</th><td><textarea name="asdasd">dfsfsf</textarea></td>
</tr>
<tr>
    <th>Signature</th><td><input type="signature" name="testSignature" style="width: 100% height: 20px"></td>
</tr>
<tr>
    <th>Input text</th><td><input name="testText" type="text" value="value"/></td>
</tr>
<tr>
    <th>Input number</th><td><input name="testNumber" type="number"></td>
</tr>
<tr>
    <th>Input email</th><td><input name="testEmail" type="email"></td>
</tr>
<tr>
    <th>Select</th><td><select name="testSelect"><option>A</option><option>B</option></select></td>
</tr>
</table>
"""


pdf_html = HTML(string=html).render()


target = 'forms.pdf'
form_finisher = FormFinisher(inject_empty_cryptographic_signature=False, is_signature_visible=False)
pdf_html.write_pdf(finisher=form_finisher, target=target)


