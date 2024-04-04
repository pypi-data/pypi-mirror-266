import os
import sys
import json
import trp
import boto3
from datetime import datetime
import tempfile


from pdf2image import convert_from_path

class ExtractorBase():
    """
    Base class for extractors
    """
    pass

class AWSTextactor(ExtractorBase):
    """
    Class to use Textractor to process images...

    There are two implementations:
    (1) Low-level - get_text etc
    (2) TRP-library-based - doc_to_tabletext, doc_to_linetext

    https://github.com/mludvig/amazon-textract-parser
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract/client/analyze_document.html
    https://docs.aws.amazon.com/textract/latest/dg/examples-export-table-csv.html
    """

    def __init__(self, cred=None):
        self.cred = cred

    def get_text(self, result, blocks_map):
        """

        """
        text = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] =='SELECTED':
                                text +=  'X '
        return text

    def get_table_rows(self, table_block, blocks_map):
        """
        Get text from the cells
        """

        rows = {}
        for relationship in table_block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    cell = blocks_map[child_id]
                    if cell['BlockType'] == 'CELL':
                        row_index = cell['RowIndex']
                        col_index = cell['ColumnIndex']

                        if row_index not in rows:
                            # create new row
                            rows[row_index] = {}

                        # get the text value
                        rows[row_index][col_index] = self.get_text(cell, blocks_map)
        return rows

    def get_one_table(self, table_block, blocks_map):
        """
        Get one table's content by looking at the children
        """
        rows = self.get_table_rows(table_block, blocks_map)

        result = []
        for row_index, cols in rows.items():
            row = []
            for col_index, text in cols.items():
                row.append(text)
            result.append(row)

        return result

    def get_all_tables(self, blocks):

        tables = {}

        # => Which blocks have tables?
        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "TABLE":
                table_blocks.append(block)

        if len(table_blocks) <= 0:
            return tables

        for index, table_block in enumerate(table_blocks):
            tableid = f"table_{index+1}"
            tables[tableid] = self.get_one_table(table_block, blocks_map)

        return tables


    def get_all_signatures(self, blocks):

        signatures = {}

        # => Which blocks have tables?
        blocks_map = {}
        signature_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "SIGNATURE":
                signature_blocks.append(block)

        if len(signature_blocks) <= 0:
            print("NO signatures found")
            return signatures

        for index, sig_block in enumerate(signature_blocks):
            sigid = f"sig_{index+1}"
            print(json.dumps(sig_block, indent=4))
            signatures[sigid] = {
                'confidence': sig_block['Confidence']
            }
            if 'Text' in sig_block:
                signatures[sigid].update({
                    'text': sig_block['Text'],
                    'type': sig_block['TextType'],
                })

        return signatures

    def get_blocks(self, content):

        # Get the text blocks
        blocks = content['Blocks']

        return blocks

    def get_all_content(self, content):

        featuretypes=['TABLES', 'SIGNATURES']

        if isinstance(content, str):
            img_test = open(content, 'rb').read()
            bytes_test = bytearray(img_test)
        elif isinstance(content, bytes):
            bytes_test = bytearray(content)
        else:
            raise Exception("Content should be filename or byte array")

        # process using image bytes
        # get the results
        session = boto3.Session()
        client = session.client('textract')
        response = client.analyze_document(Document={'Bytes': bytes_test},
                                           FeatureTypes=featuretypes)

        return response

    def doc_to_signatures(self, textract_data):
        """
        Take a textract response and extract all signatures
        """
        content = textract_data['content']
        filename = textract_data['filename']
        pageno = textract_data['page']

        # check for signatures
        signatures = []
        signo = 0
        for item in content["Blocks"]:
            if item["BlockType"] == "SIGNATURE":
                one_sig = {
                    "id": f"{filename}-p{pageno}-s{signo}",
                    "page": pageno,
                    "confidence": item["Confidence"],
                    "location": item["Geometry"]
                }
                signatures.append(one_sig)
                signo += 1

        return signatures

    def doc_to_tabletext(self, textract_data):
        """
        Take a textract response and extract all tables
        """
        content = textract_data['content']
        filename = textract_data['filename']
        pageno = textract_data['page']

        # convert to Document format
        doc = trp.Document(content)

        # extract all tables
        tables = []
        tableno = 0
        for page in doc.pages:
            # for each table
            for table in page.tables:
                table_rows = []
                # for each row
                for row in table.rows:
                    table_rows.append("\t".join([cell.text for cell in row.cells]))

                # we now have all the text for one table
                table_text = "\n".join(table_rows)

                # construct one table
                one_table = {
                    "id": f"{filename}-p{pageno}-t{tableno}",
                    "text": table_text
                }
                tables.append(one_table)

                tableno += 1

        return tables

    def doc_to_linetext(self, textract_data):
        """
        Take a textract response and extract all tables
        """
        content = textract_data['content']
        filename = textract_data['filename']
        pageno = textract_data['page']

        blocks = content['Blocks']
        text = ""
        for item in blocks:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"
        text = {
            "id": f"{filename}-p{pageno}-text",
            "text": text.strip()
        }

        return text

    def extract_and_organize(self, content):

        # First get the structure of the document
        response = self.get_all_content(content)

        # Incorporate the blocks..
        blocks = self.get_blocks(response)
        tables = self.get_all_tables(blocks)
        signatures = self.get_all_signatures(blocks)

        return {
            "timestamp": datetime.now().isoformat(),
            'metadata': {
                'blocks': blocks
            },
            'tables': tables,
            'signatures': signatures
        }

    def extract(self, content):
        # Get the full structured content of the document
        response = self.get_all_content(content)
        return response


def extract_text_from_file(filename, provider="aws"):

    if provider == "aws":
        handler = AWSTextactor()
    else:
        raise Exception("Only aws is supported as a provider for now")

    allresults = []
    if filename.lower().endswith("pdf"):
        with tempfile.TemporaryDirectory() as path:
            images_from_path = convert_from_path(filename,
                                                 output_folder=path,
                                                 fmt='png',
                                                 poppler_path="")
            print (f"Extracting text from: {filename}")
            for idx, img in enumerate(sorted(os.listdir(path))):
                print (f"..page {idx}")
                response = handler.extract(os.path.join(path, img))
                result = {
                    "content": response,
                    "filename": filename,
                    "page": idx,
                }
                result['signatures'] = handler.doc_to_signatures(result)
                result['tables'] = handler.doc_to_tabletext(result)
                result['text'] = handler.doc_to_linetext(result)
                allresults.append(result)

    else:
        result = handler.extract(filename)
        result['page'] = 1
        allresults.append(result)

    return allresults
