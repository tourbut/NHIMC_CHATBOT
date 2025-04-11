from unstructured.partition import pdf,xlsx,docx
from pathlib import Path
from bs4 import BeautifulSoup
from markitdown import MarkItDown
import re

def html_table_to_markdown(html_content):
    """HTML 테이블을 Markdown 테이블로 변환하는 함수"""
    
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')
    
    markdown_tables = []
    
    # 모든 테이블 처리
    for table in soup.find_all('table'):
        markdown_rows = []
        
        # 모든 행 처리
        rows = table.find_all(['tr'])
        for row_index, row in enumerate(rows):
            # 셀 데이터 추출 (th와 td 모두 처리)
            cells = row.find_all(['th', 'td'])
            row_data = []
            
            for cell in cells:
                # 셀 내용 정리 (줄바꿈을 <br>로 변환)
                content = cell.get_text().strip()
                content = re.sub(r'\s+', ' ', content)
                content = content.replace('\n', '<br>')
                row_data.append(content)
            
            # Markdown 행 생성
            markdown_row = f"| {' | '.join(row_data)} |"
            markdown_rows.append(markdown_row)
            
            # 헤더 행 다음에 구분선 추가
            if row_index == 0:
                separator = f"|{'|'.join(['---' for _ in cells])}|"
                markdown_rows.append(separator)
        
        # 테이블 완성
        markdown_table = '\n'.join(markdown_rows)
        markdown_tables.append(markdown_table)
    
    # 모든 테이블을 줄바꿈으로 구분하여 반환
    return '\n\n'.join(markdown_tables)

async def pdf_to_markdown(input_path: str,output_path: str=None):
    # PDF 파일 파싱
    elements = pdf.partition_pdf(
        input_path,
        strategy="fast",
        extract_images_in_pdf=False,
        extract_tables=True,
    )
    
    markdown_content = []
    
    for element in elements:
        if element.category == "Title":
            markdown_content.append(f"# {element.text}\n\n")
        elif element.category == "NarrativeText":
            markdown_content.append(f"{element.text}\n\n")
        elif element.category == "ListItem":
            markdown_content.append(f"- {element.text}\n")
        elif element.category == "Table":
            markdown_content.append(f"{html_table_to_markdown(element.metadata.text_as_html)}\n\n")
        else :
            markdown_content.append(f"{element.text}\n\n")
    
    if output_path:
        Path(output_path).write_text(''.join(markdown_content), encoding='utf-8')
    else:
        return "".join(markdown_content)

async def xlsx_to_markdown(input_path: str,output_path: str=None):
    # PDF 파일 파싱
    elements = xlsx.partition_xlsx(
        filename=input_path,
    )
    
    markdown_content = []
    
    for element in elements:
        if element.category == "Title":
            markdown_content.append(f"# {element.text}\n\n")
        elif element.category == "NarrativeText":
            markdown_content.append(f"{element.text}\n\n")
        elif element.category == "ListItem":
            markdown_content.append(f"- {element.text}\n")
        elif element.category == "Table":
            markdown_content.append(f"{html_table_to_markdown(element.metadata.text_as_html)}\n\n")
        else :
            markdown_content.append(f"{element.text}\n\n")
    
    if output_path:
        Path(output_path).write_text(''.join(markdown_content), encoding='utf-8')
    else:
        return "".join(markdown_content)    

async def docx_to_markdown(input_path: str,output_path: str=None):
    # PDF 파일 파싱
    elements = docx.partition_docx(
        filename=input_path,
    )
    
    markdown_content = []
    
    for element in elements:
        if element.category == "Title":
            markdown_content.append(f"# {element.text}\n\n")
        elif element.category == "NarrativeText":
            markdown_content.append(f"{element.text}\n\n")
        elif element.category == "ListItem":
            markdown_content.append(f"- {element.text}\n")
        elif element.category == "Table":
            markdown_content.append(f"{html_table_to_markdown(element.metadata.text_as_html)}\n\n")
        else :
            markdown_content.append(f"{element.text}\n\n")
    
    if output_path:
        Path(output_path).write_text(''.join(markdown_content), encoding='utf-8')
    else:
        return "".join(markdown_content)      

async def use_markitdown(input_path: str,output_path: str=None):
    """
    pip install 'markitdown[all]'
        PDF
        PowerPoint
        Word
        Excel
        Images (EXIF metadata and OCR)
        Audio (EXIF metadata and speech transcription)
        HTML
        Text-based formats (CSV, JSON, XML)
        ZIP files (iterates over contents)
        Youtube URLs
        EPubs
    """
    md = MarkItDown(enable_plugins=False)
    result = md.convert(input_path)
    markdown_content = result.text_content
    if output_path:
        Path(output_path).write_text(markdown_content, encoding='utf-8')
    else:
        return markdown_content

    
def convert_encoding(in_text:str,encoding:str):
    
    out_text = in_text.encode(encoding, errors='ignore').decode(encoding)

    return out_text