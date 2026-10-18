from pydantic import BaseModel, Field

from stakagents.core.agent import Agent
from stakagents.core.llm import get_chat_model
from stakagents.core.registry import register

_SYSTEM_PROMPT = (
    "You are a careful video analyst. You are given the transcript of a single "
    "YouTube video. Each line is prefixed with an [MM:SS] timestamp marking when "
    "it was said. Work ONLY from this transcript — do not add facts, opinions, "
    "context, or claims that are not supported by it. If the transcript is thin "
    "or cuts off, say only what it supports; never invent detail to fill gaps.\n"
    "\n"
    "Produce three things:\n"
    "- summary: a concise, faithful summary of what the video actually covers, "
    "in the speaker's own framing. A few sentences to a short paragraph.\n"
    '- timestamps: the key moments, each as "[MM:SS] short label", reusing the '
    "timestamps that appear in the transcript. Order them chronologically and "
    "keep them to the genuinely notable turns, not every line.\n"
    "- themes: a short list of the main topics or recurring ideas, each a few "
    "words.\n"
    "\n"
    "Base every timestamp and theme on text that is present in the transcript."
)


class YoutubeInput(BaseModel):
    video_url: str = Field(description="URL of video to be transcribed")
    transcript: str | None = Field(
        default=None,
        description="Pre-fetched transcript. When set, run() uses it verbatim "
        "and skips the live fetch. This is the eval/test seam.",
    )


class YoutubeOutput(BaseModel):
    summary: str = Field(description="Plain text summary of the video content")
    timestamps: list[str] = Field(description="Timestamps of key moments")
    themes: list[str] = Field(description="Themes found in the video content")


@register
class YouTube(Agent[YoutubeInput, YoutubeOutput]):
    name = "youtube"
    input_model = YoutubeInput
    output_model = YoutubeOutput
