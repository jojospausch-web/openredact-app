import base64
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from starlette.responses import StreamingResponse, JSONResponse
import io
import json
import os
import logging
from expose_text import BinaryWrapper, UnsupportedFormat
import nerwhal
from anonymizer import AnonymizerConfig, Anonymizer, Pii, ParserError

from app.schemas import (
    Annotation,
    AnnotationsForEvaluation,
    EvaluationResponse,
    FindPiisResponse,
    ErrorMessage,
    AnonymizedPiisResponse,
    AnonymizedPii,
    WhitelistResponse,
    WhitelistEntry,
    WhitelistBulkUpdate,
    TemplateData,
    TemplateResponse,
    TemplatesResponse,
    TemplateImport,
    SuccessResponse,
)
from app.storage import WhitelistStorage, TemplateStorage

logger = logging.getLogger(__name__)

router = APIRouter()

recognizer_name_to_path_lookup = {Path(path).stem: path for path in nerwhal.list_integrated_recognizers()}


@router.post(
    "/anonymize",
    summary="Anonymize PIIs",
    description="Anonymize the given PIIs by replacing their text content according to the provided config.",
    response_model=AnonymizedPiisResponse,
    responses={400: {"model": ErrorMessage}},
)
async def anonymize(piis: List[Pii], config: AnonymizerConfig):
    anonymizer = Anonymizer(config)
    try:
        anonymized_piis = [AnonymizedPii(text=pii.text, id=pii.id) for pii in anonymizer.anonymize(piis) if pii.modified]
    except ParserError:
        raise HTTPException(status_code=400, detail="Error parsing a pii")

    if len(anonymized_piis) != len(piis):
        # one or more piis were not flagged as `modified`
        logger.error(f"Invalid config (anonymized_piis={anonymized_piis}; piis={piis}")
        raise HTTPException(status_code=400, detail="Invalid Config")

    return AnonymizedPiisResponse(anonymized_piis=anonymized_piis)


@router.post(
    "/anonymize-file",
    summary="Anonymize file",
    description="Anonymize the given file by replacing the text passages specified in anonymizations. The character indices "
    "in anonymizations refer to the file's plain text representation.",
    responses={200: {"content": {"application/octet-stream": {}}}, 400: {"model": ErrorMessage}},
)
async def anonymize_file(
    file: UploadFile = File(...),
    anonymizations: str = Form(
        ...,
        description="A json array of objects with fields startChar, endChar and text. E.g. "
        '[{"startChar":0,"endChar":10,"text":"XXX"}].',
    ),
    return_base64: bool = False,
):
    _, extension = os.path.splitext(file.filename)
    content = await file.read()
    await file.close()

    try:
        wrapper = BinaryWrapper(content, extension)
    except UnsupportedFormat as e:
        logger.error(f"Unsupported File Format: {e}")
        raise HTTPException(status_code=400, detail="Unsupported File Format")

    for alteration in json.loads(anonymizations):
        wrapper.add_alter(alteration["startChar"], alteration["endChar"], alteration["text"])
    wrapper.apply_alters()

    if return_base64:
        try:
            # Send anonymized file as base64 encoding
            base64_bytes = base64.b64encode(wrapper.bytes)

            return JSONResponse({"base64": base64_bytes.decode()})
        except Exception as e:
            logger.error(f"base64 encoding failed: {e}")
            raise HTTPException(status_code=400, detail="File Handling Error (base64 encoding failed)")

    else:
        # Regular download
        return StreamingResponse(
            io.BytesIO(wrapper.bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment;{file.filename}"},
        )


@router.post(
    "/find-piis",
    summary="Find PIIs",
    description="Find personally identifiable information in the given file. The character and token indices refer to the "
    "file's plain text representation.",
    response_model=FindPiisResponse,
    responses={400: {"model": ErrorMessage}},
)
async def find_piis(recognizers: str = Form(...), file: UploadFile = File(...)):
    _, extension = os.path.splitext(file.filename)
    content = await file.read()
    await file.close()

    try:
        wrapper = BinaryWrapper(content, extension)
    except UnsupportedFormat as e:
        logger.error(f"Unsupported File Format: {e}")
        raise HTTPException(status_code=400, detail="Unsupported File Format")
    except Exception as e:
        logger.error(f"File Handling Error: {e}")
        raise HTTPException(status_code=400, detail="File Handling Error")

    recognizers = json.loads(recognizers)
    use_statistical_ner = False
    if "statistical_recognizer" in recognizers:
        use_statistical_ner = True
        recognizers.remove("statistical_recognizer")
    recognizer_paths = [recognizer_name_to_path_lookup[name] for name in recognizers]

    nerwhal_config = nerwhal.Config(language="de", recognizer_paths=recognizer_paths, use_statistical_ner=use_statistical_ner)
    res = nerwhal.recognize(wrapper.text, config=nerwhal_config, combination_strategy="smart-fusion")

    # Filter out whitelisted entities
    whitelist = WhitelistStorage.get_all()
    whitelist_lower = [entry.lower() for entry in whitelist]

    filtered_piis = []
    for pii in res["ents"]:
        pii_text_lower = pii.text.lower().strip()
        if pii_text_lower not in whitelist_lower:
            filtered_piis.append(pii)
        else:
            logger.info(f"Filtered whitelisted PII: {pii.text}")

    return FindPiisResponse(
        piis=[asdict(pii) for pii in filtered_piis],
        tokens=[asdict(token) for token in res["tokens"]],
        format=str(wrapper.file.__class__.__name__).lower().replace("format", ""),
    )


@router.post(
    "/score",
    summary="Compute scores",
    description="Compute common scoring metrics for the provided annotations data.",
    response_model=EvaluationResponse,
)
async def score(data: AnnotationsForEvaluation):
    def _create_entity(annot: Annotation):
        # annotation start and end are token based indices; in the context of scoring the actual value is not
        # important though, so we can pretend they are character based
        return nerwhal.NamedEntity(start_char=annot.start, end_char=annot.end, tag=annot.tag)

    gold = [_create_entity(annot) for annot in data.gold_annotations]
    piis = [_create_entity(annot) for annot in data.computed_annotations]
    return nerwhal.evaluate(piis, gold)


@router.get(
    "/tags",
    summary="PII Tags",
    description="Fetch the types of personally identifiable information that the backend is looking for. The result is a "
    "string of tags, e.g. PER or LOC.",
    response_model=List[str],
)
async def tags():
    return sorted(["PER", "LOC", "ORG", "MISC", "MONEY", "EMAIL", "PHONE", "NUMBER", "COUNTRY", "DATE"])


@router.get(
    "/recognizers",
    summary="PII Recognizers",
    description="Fetch the list of recognizers that are supported by the backend.",
    response_model=List[str],
)
async def supported_recognizers():
    return list(recognizer_name_to_path_lookup.keys()) + ["statistical_recognizer"]


# Whitelist endpoints
@router.get(
    "/whitelist",
    summary="Get Whitelist",
    description="Fetch all whitelist entries. Whitelisted terms are excluded from anonymization.",
    response_model=WhitelistResponse,
)
async def get_whitelist():
    """Get all whitelist entries"""
    entries = WhitelistStorage.get_all()
    return WhitelistResponse(entries=entries)


@router.post(
    "/whitelist",
    summary="Add Whitelist Entry",
    description="Add a new entry to the whitelist.",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorMessage}},
)
async def add_whitelist_entry(data: WhitelistEntry):
    """Add entry to whitelist"""
    if not data.entry or not data.entry.strip():
        raise HTTPException(status_code=400, detail="Entry cannot be empty")

    success = WhitelistStorage.add(data.entry.strip())
    if success:
        return SuccessResponse(success=True, message="Entry added successfully")
    raise HTTPException(status_code=500, detail="Failed to add entry")


@router.delete(
    "/whitelist",
    summary="Remove Whitelist Entry",
    description="Remove an entry from the whitelist.",
    response_model=SuccessResponse,
)
async def remove_whitelist_entry(data: WhitelistEntry):
    """Remove entry from whitelist"""
    success = WhitelistStorage.remove(data.entry)
    if success:
        return SuccessResponse(success=True, message="Entry removed successfully")
    raise HTTPException(status_code=500, detail="Failed to remove entry")


@router.put(
    "/whitelist",
    summary="Update Whitelist",
    description="Replace the entire whitelist with new entries.",
    response_model=SuccessResponse,
)
async def update_whitelist(data: WhitelistBulkUpdate):
    """Update entire whitelist"""
    success = WhitelistStorage.set_all(data.entries)
    if success:
        return SuccessResponse(success=True, message="Whitelist updated successfully")
    raise HTTPException(status_code=500, detail="Failed to update whitelist")


# Template endpoints
@router.get(
    "/templates",
    summary="Get All Templates",
    description="Fetch all anonymization templates.",
    response_model=TemplatesResponse,
)
async def get_templates():
    """Get all templates"""
    templates = TemplateStorage.get_all()
    return TemplatesResponse(templates=templates)


@router.get(
    "/templates/{template_id}",
    summary="Get Template",
    description="Fetch a specific anonymization template by ID.",
    response_model=TemplateResponse,
    responses={404: {"model": ErrorMessage}},
)
async def get_template(template_id: str):
    """Get specific template"""
    template = TemplateStorage.get(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(template_id=template_id, template=template)


@router.post(
    "/templates/{template_id}",
    summary="Save Template",
    description="Create or update an anonymization template.",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorMessage}},
)
async def save_template(template_id: str, template: TemplateData):
    """Save or update template"""
    if not template_id or not template_id.strip():
        raise HTTPException(status_code=400, detail="Template ID cannot be empty")

    # Add timestamps
    now = datetime.utcnow().isoformat()
    template_dict = template.dict()
    if not template_dict.get("created_at"):
        template_dict["created_at"] = now
    template_dict["updated_at"] = now

    success = TemplateStorage.save(template_id, template_dict)
    if success:
        return SuccessResponse(success=True, message="Template saved successfully")
    raise HTTPException(status_code=500, detail="Failed to save template")


@router.delete(
    "/templates/{template_id}",
    summary="Delete Template",
    description="Delete an anonymization template.",
    response_model=SuccessResponse,
)
async def delete_template(template_id: str):
    """Delete template"""
    success = TemplateStorage.delete(template_id)
    if success:
        return SuccessResponse(success=True, message="Template deleted successfully")
    raise HTTPException(status_code=500, detail="Failed to delete template")


@router.post(
    "/templates/import",
    summary="Import Templates",
    description="Import templates from a JSON file. Existing templates with same IDs will be overwritten.",
    response_model=SuccessResponse,
)
async def import_templates(data: TemplateImport):
    """Import templates"""
    success = TemplateStorage.import_templates(data.templates)
    if success:
        return SuccessResponse(success=True, message=f"Imported {len(data.templates)} template(s)")
    raise HTTPException(status_code=500, detail="Failed to import templates")


@router.get(
    "/templates/export/all",
    summary="Export All Templates",
    description="Export all templates as JSON for backup or sharing.",
    response_model=TemplatesResponse,
)
async def export_templates():
    """Export all templates"""
    templates = TemplateStorage.get_all()
    return TemplatesResponse(templates=templates)
