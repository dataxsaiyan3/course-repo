import os
import comtypes.client

# Directory containing the Word files
word_dir = r"path_to_where_word_files_are"

# Directory to save the PDF files
pdf_dir = r"path_to_where_you_want_converted_files_be_stored\name_of_folder"

try:
    os.mkdir(pdf_dir)
except FileExistsError:
    pass

# Convert Word to PDF
for file_name in os.listdir(word_dir):
    if file_name.endswith('.docx'):
        word_path = os.path.join(word_dir, file_name)
        pdf_path = os.path.join(pdf_dir, file_name[:-5] + '.pdf')
        
        word = comtypes.client.CreateObject('Word.Application')
        doc = word.Documents.Open(word_path)
        
        doc.SaveAs(pdf_path, FileFormat=17)
        
        # Close the document and Word
        doc.Close()
        word.Quit()