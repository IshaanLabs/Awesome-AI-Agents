import os
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))


def load_resume(pdf_path: str) -> list[str]:
    print(f"[1/5] Loading resume from: {pdf_path}")
    loader = UnstructuredPDFLoader(pdf_path)
    docs = loader.load()
    full_text = "\n".join([doc.page_content for doc in docs])
    print(f"[1/5] Resume loaded — {len(full_text)} characters")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(full_text)
    print(f"[1/5] Resume split into {len(chunks)} chunks")
    return chunks


def get_available_models() -> list[str]:
    print(f"[*] Fetching available models from: {OLLAMA_BASE_URL}")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        print(f"[*] Found models: {model_names}")
        return model_names
    except Exception as e:
        print(f"[!] Failed to fetch models: {e}")
        return []


def generate_cover_letter(chunks: list[str], job_description: str, model: str) -> str:
    llm = OllamaLLM(model=model, base_url=OLLAMA_BASE_URL)
    parser = StrOutputParser()

    # Map chain: extract relevant info from each chunk against the job description
    map_prompt = PromptTemplate(
        input_variables=["chunk", "job_description"],
        template="""From the resume excerpt below, extract only the information that is relevant 
                    to the job description. If nothing is relevant, respond with "Nothing relevant".

                    Resume Excerpt:
                    {chunk}

                    Job Description:
                    {job_description}

                    Relevant Information:"""
                        )
    map_chain = map_prompt | llm | parser

    # Run map chain over all chunks
    print(f"[2/5] Running map chain over {len(chunks)} chunks...")
    mapped_results = []
    for i, chunk in enumerate(chunks):
        print(f"[2/5] Processing chunk {i + 1}/{len(chunks)}")
        result = map_chain.invoke({"chunk": chunk, "job_description": job_description})
        mapped_results.append(result)

    # Filter out non-relevant chunks
    relevant_chunks = [r for r in mapped_results if "nothing relevant" not in r.lower()]
    print(f"[3/5] {len(relevant_chunks)}/{len(chunks)} chunks had relevant info")
    relevant_info = "\n\n".join(relevant_chunks)

    # Reduce chain: condense all relevant info into a clean summary
    reduce_prompt = PromptTemplate(
        input_variables=["relevant_info"],
        template="""Below are relevant excerpts extracted from a resume. Combine and deduplicate 
                    them into a single concise professional summary without losing any important details.

                    Relevant Excerpts:
                    {relevant_info}

                    Condensed Summary:"""
                        )
    reduce_chain = reduce_prompt | llm | parser
    print("[4/5] Running reduce chain to condense relevant info...")
    condensed_resume = reduce_chain.invoke({"relevant_info": relevant_info})
    print(f"[4/5] Condensed summary — {len(condensed_resume)} characters")

    # Final chain: generate the cover letter
    cover_letter_prompt = PromptTemplate(
        input_variables=["condensed_resume", "job_description"],
        template="""You are an expert career coach. Using the candidate summary and job description 
                    below, write a professional, compelling, and personalized cover letter.

                    Candidate Summary:
                    {condensed_resume}

                    Job Description:
                    {job_description}

                    Cover Letter:"""
                        )
    cover_letter_chain = cover_letter_prompt | llm | parser
    print("[5/5] Generating cover letter...")
    cover_letter = cover_letter_chain.invoke({
        "condensed_resume": condensed_resume,
        "job_description": job_description
    })
    print("[5/5] Cover letter generated successfully!")
    return cover_letter
