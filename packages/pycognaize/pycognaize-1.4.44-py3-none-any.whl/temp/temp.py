from pycognaize.document import Document
from pycognaize.document.field import TableField

if __name__ == '__main__':
    doc = Document.fetch_document(recipe_id="649a7c0180d898001055a354",
                                  doc_id="65db38f7dc54d400119ae1f3")

    def parse_table(table_field: TableField):
        df = table_field.tags[0].df
        new_header = df.iloc[0]  # grab the first row for the header
        df = df[1:]  # take the data less the header row
        df.columns = new_header  # set the header row as the df header
        df_text = df.to_markdown(index=False)
        return df_text

    def sort_function(field) -> tuple:
        ...


    doc_text = doc.get_layout_text(
        field_type="both",
        field_filter=lambda pname, field: pname != 'table',
        sorting_function=lambda x: (x.tags[0].top, x.tags[0].left),
        table_parser=TableField.parse_table
    )
    print(doc_text)
    for page_number, page_text in enumerate(doc_text, start=1):
        print(f"---------PAGE {page_number}---------------\n")
        print(page_text)
    ...
