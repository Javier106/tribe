from langchain.pydantic_v1 import BaseModel
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.utilities import WikipediaAPIWrapper

# Importar el tool de mercury.py
from mercury import mercury_search

# from vulcano import vulcano_search
# from minerva import minerva_tool


class SkillInfo(BaseModel):
    description: str
    tool: BaseTool


managed_skills: dict[str, SkillInfo] = {
    "duckduckgo-search": SkillInfo(description="Searches the web using DuckDuckGo", tool=DuckDuckGoSearchRun()),
    "wikipedia": SkillInfo(
        description="Searches Wikipedia",
        tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
    ),
    "yahoo-finance": SkillInfo(
        description="Get information from Yahoo Finance News.",
        tool=YahooFinanceNewsTool(),
    ),
    # "mercury-search": SkillInfo(
    #   description="Useful for listing objects in an S3 bucket",
    #    tool=mercury_search,
    # ),
    # "vulcano_search": SkillInfo(
    #    description="key_words_search.description",
    #    tool=vulcano_search,
    # ),
    # "minerva-tool": SkillInfo(
    #    description=minerva_tool.description,
    #    tool=minerva_tool,
    # ),
}


# To add more custom tools, follow these steps:
# 1. Create a new Python file in the `skills` folder (e.g., `calculator.py`).
# 2. Define your tool. Refer to `calculator.py` or see https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/
# 3. Import your new tool here and add it to the `managed_skills` dictionary above.
