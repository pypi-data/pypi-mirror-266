"""
Helper functions to generate/manage excels
"""
import io
import pandas as pd

__all__ = [
    'generate_xlsx'
]

def generate_xlsx(spec):
    """
    Generate an excel sheet according to specification

    Args:
        spec (dict): Specification of the excel

    Returns:
        bytes: content of an excel file


    Example of spec::

        [
            {
                "name": "Variables",
                "tables": [
                    {
                        "name": "variables",
                        "position": [0,0],
                        "data": vdf
                    }
                ]
            },        
            {
                "name": "Metrics",
                "tables": [
                    {
                        "name": "metrics",
                        "position": [0,0],
                        "data": mdf
                    }
                ]
            },
        ]
    """

    # Sanity check
    if not isinstance(spec, list) or len(spec) == 0:
        raise Exception("Invalid excel generation specification")

    for sheetspec in spec:
        if not isinstance(sheetspec, dict) or len(sheetspec) == 0:
            raise Exception("Invalid sheet specification. Invalid dictionary")

        if (("name" not in sheetspec) or ("tables" not in sheetspec)):
            raise Exception("Sheet specification should include name of sheet and the tables")

    
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    for sheetspec in spec:
        sheetname = sheetspec['name']
        for t in sheetspec['tables']:
            name = t['name']
            df= t['data']
            position = t['position']
            extra = t.get('extra', {})
            if len(df) > 0: 
                df.to_excel(writer,
                            sheet_name=sheetname,
                            index=False,
                            encoding='utf-8',
                            startrow=position[0],
                            startcol=position[1],
                            **extra)
                        

    writer.save()
    output.seek(0)
    
    return output.read()

if __name__ == "__main__":

    vdf = pd.DataFrame([
        { 'a': 2, 'b': 2},
        { 'a': 3, 'b': 4}
    ])

    mdf = pd.DataFrame([
        { 'c': 2, 'd': 2},
        { 'c': 3, 'd': 4}
    ])    
    
    excelspec = [
        {
            "name": "Variables",
            "tables": [
                {
                    "name": "variables",
                    "position": [0,0],
                    "data": vdf
                }
            ]
        },        
        {
            "name": "Metrics",
            "tables": [
                {
                    "name": "metrics",
                    "position": [0,0],
                    "data": mdf
                }
            ]
        },
    ]
    content = generate_xlsx(excelspec)
    with open('excelspectest.xlsx', 'wb') as fd:
        fd.write(content)
