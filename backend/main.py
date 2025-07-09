# main.py - The complete and corrected FastAPI application file.

import os
import shutil
import base64
from fastapi import FastAPI, HTTPException
from uuid import uuid4

# Import Pydantic components for data validation and schema definition
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
    ValidationInfo,
)
from typing import Optional, Dict
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your core pipeline function from your pipeline.py file
# Make sure pipeline.py is in the same directory.
from pipeline import create_podcast_pipeline


# --- Pydantic Models for Request and Response ---

class PodcastLength(str, Enum):
    """Enum to ensure podcast_length is one of the allowed values."""
    short = "short"
    moderate = "moderate"
    long = "long"

class SpeakerModel(BaseModel):
    """
    A specific model for speakers. This ensures the API documentation (Swagger UI)
    shows the correct field names (speaker1, speaker2, etc.) instead of generic names.
    """
    speaker1: Optional[str] = None
    speaker2: Optional[str] = None
    speaker3: Optional[str] = None
    speaker4: Optional[str] = None
    speaker5: Optional[str] = None

class PodcastRequest(BaseModel):
    """Defines the structure and validation rules for an incoming API request."""
    file: Optional[str] = Field(None, description="The content of the PDF file, Base64 encoded.")
    url: Optional[HttpUrl] = Field(None, description="The URL of the article to process.")
    no_of_speaker: int = Field(..., gt=0, le=5, description="The total number of speakers (1-5).")
    speaker: SpeakerModel = Field(..., description="An object containing the names for each speaker.")
    podcast_length: PodcastLength = Field(..., description="The desired length of the podcast.")

    @model_validator(mode='before')
    @classmethod
    def check_file_or_url(cls, data: Dict) -> Dict:
        """Validates that either 'file' or 'url' is provided, but not both."""
        if ('file' in data and data.get('file')) and ('url' in data and data.get('url')):
            raise ValueError("Provide either 'file' or 'url', not both.")
        if not ('file' in data and data.get('file')) and not ('url' in data and data.get('url')):
            raise ValueError("Either 'file' or 'url' must be provided.")
        return data

    @field_validator('speaker')
    @classmethod
    def check_speaker_consistency(cls, speaker_model: SpeakerModel, info: ValidationInfo) -> SpeakerModel:
        """
        Validates that the number of provided speakers with actual names (not empty strings)
        matches the 'no_of_speaker' field.
        """
        if 'no_of_speaker' in info.data:
            # Count only the speakers that have a non-empty name.
            active_speakers = [
                name for name in speaker_model.model_dump().values() if name
            ]
            
            if len(active_speakers) != info.data['no_of_speaker']:
                raise ValueError(
                    f"The number of active speakers provided ({len(active_speakers)}) "
                    f"does not match 'no_of_speaker' ({info.data['no_of_speaker']})."
                )
        return speaker_model

class PodcastResponseData(BaseModel):
    """Defines the structure for the 'data' part of a successful API response."""
    title: str
    podcast_script: str
    audio_data: str = Field(..., description="The generated MP3 audio file, Base64 encoded.")

class PodcastApiResponse(BaseModel):
    """Defines the top-level structure for a successful API response."""
    message: str
    data: PodcastResponseData


# --- FastAPI Application Initialization ---
# This 'app' object is the main entry point for the Uvicorn server.
app = FastAPI(
    title="Podcast Generation API",
    description="API to create podcasts from URLs or Base64 PDF files."
)

# Define the origins that are allowed to connect.
# For development, allowing all origins ("*") is easiest.
origins = ["*"]

# Add the CORS middleware to your application.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoint ---
@app.post(
    "/podcasts/",
    response_model=PodcastApiResponse, # Ensures the response matches our defined model
    tags=["Podcast Generation"]
)
async def create_podcast_endpoint(request: PodcastRequest):
    """
    This single endpoint handles podcast creation from either a URL or a PDF file.
    It validates the incoming request, calls the processing pipeline, and
    returns the generated podcast title, script, and audio data.
    """
    file_path = None
    temp_dir = "temp_files"
    try:
        # Convert the SpeakerModel to the simple dictionary format that the pipeline expects.
        pipeline_speakers = request.speaker.model_dump()

        # Determine the input source based on the request payload.
        if request.file:
            input_type = 'pdf'
            try:
                # Decode the Base64 string to binary data.
                file_content = base64.b64decode(request.file)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid Base64 string for file.")
            
            # Save the binary data to a temporary file for processing.
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, f"{uuid4()}.pdf")
            with open(file_path, "wb") as f:
                f.write(file_content)
            input_source = file_path
        else: # A URL must be present if a file is not, due to our validator.
            input_type = 'url'
            input_source = str(request.url)

        # Call the main processing pipeline with the prepared inputs.
        result = create_podcast_pipeline(
            input_type=input_type,
            input_source=input_source,
            speaker_names=pipeline_speakers,
            podcast_length=request.podcast_length.value
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate podcast. Check pipeline logs for errors.")

        # Format the successful response according to our PodcastApiResponse model.
        return {
            "message": f"Podcast created successfully from {input_type}!",
            "data": result
        }

    except ValueError as e:
        # Catches Pydantic validation errors and returns them as a 400 Bad Request.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catches any other unexpected errors during processing.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # This block always runs, ensuring we clean up the temporary PDF file if it was created.
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
