from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel,Field
from mcp.server.fastmcp.prompts import base
mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool("read_doc_contents",
        description="Read the contents of a document and return it as a string."
        )
def read_document(doc_id:str=Field(description="Id of the document to read.")):
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found.")
    
    return docs[doc_id]


@mcp.tool("edit_document",
        description="Edit a document by replacing a string in the document content with new contents and return it as a string."
        )
def edit_document(
    doc_id:str=Field(description="Id of the document to edit."),
    old_string:str=Field(description="String to replace in the document."),
    new_string:str=Field(description="New string to replace the old string with."),
    )->str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found.")

    if old_string not in docs[doc_id]:
        raise ValueError(f"String '{old_string}' not found in document {doc_id}.")

    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
    return docs[doc_id]

@mcp.resource("docs://documents",
               mime_type="application/json")
            
def list_docs()->list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}",
              mime_type="text/plain")

def fetch_doc(doc_id:str)->str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found.")
    
    return docs[doc_id]


@mcp.prompt(name="format",
            description="Rewrite a document in markdown format.")

def format_document(doc_id:str=Field(description="Id of the document to format."))->list[base.Message]:
    prompt=f"""
        Your goal is to reformat a document to be written with markdown syntax.
        The id of the document you need to reformat is :
        <document_id>
        {doc_id}
        </document_id>

        Add in headers,bullet points, tables, etc as necessary. Feel free to add in extra content as necessary.
        Use the 'edit_document' tool to edit the document. After the document has been formatted, return the document.
    """
    return [base.UserMessage(content=prompt)]

if __name__ == "__main__":
    mcp.run(transport="stdio")
