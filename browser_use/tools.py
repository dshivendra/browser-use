"""Tool specifications for controller actions."""

from pydantic import BaseModel, create_model

from agentic_os import ToolSpec, register_spec
from browser_use.agent.views import ActionResult
from browser_use.controller.views import (
    ClickElementAction,
    CloseTabAction,
    DoneAction,
    DragDropAction,
    GoToUrlAction,
    InputTextAction,
    NoParamsAction,
    OpenTabAction,
    ScrollAction,
    SearchGoogleAction,
    SendKeysAction,
    SwitchTabAction,
)


class WaitParams(BaseModel):
    """Parameters for the wait action."""

    seconds: int = 3


# Actions without explicit parameters use this empty model
class EmptyParams(NoParamsAction):
    pass


# Register tool specs ---------------------------------------------------------
register_spec(
    ToolSpec(
        id="done",
        description=(
            "Complete task - provide a summary of results for the user. "
            "Set success=True if task completed successfully, false otherwise. "
            "Text should be your response to the user summarizing results. "
            "Include files you would like to display to the user in files_to_display."
        ),
        input_model=DoneAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="search_google",
        description=(
            "Search the query in Google, the query should be a search query "
            "like humans search in Google, concrete and not vague or super long."
        ),
        input_model=SearchGoogleAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="go_to_url",
        description="Navigate to URL in the current tab",
        input_model=GoToUrlAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="go_back",
        description="Go back",
        input_model=NoParamsAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="wait",
        description="Wait for x seconds default 3",
        input_model=WaitParams,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="click_element_by_index",
        description="Click element by index",
        input_model=ClickElementAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="input_text",
        description="Click and input text into a input interactive element",
        input_model=InputTextAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="save_pdf",
        description="Save the current page as a PDF file",
        input_model=EmptyParams,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="switch_tab",
        description="Switch tab",
        input_model=SwitchTabAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="open_tab",
        description="Open a specific url in new tab",
        input_model=OpenTabAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="close_tab",
        description="Close an existing tab",
        input_model=CloseTabAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="extract_structured_data",
        description=(
            "Extract structured, semantic data (e.g. product description, price, "
            "all information about XYZ) from the current webpage based on a textual "
            "query. Only use this for extracting info from a single product/article "
            "page, not for entire listings or search results pages."
        ),
        input_model=create_model("ExtractStructuredDataParams", query=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="get_ax_tree",
        description=(
            "Get the accessibility tree of the page in the format 'role name' with "
            "the number_of_elements to return"
        ),
        input_model=create_model("GetAxTreeParams", number_of_elements=(int, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="scroll_down",
        description="Scroll down the page by pixel amount - if none is given, scroll one page",
        input_model=ScrollAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="scroll_up",
        description="Scroll up the page by pixel amount - if none is given, scroll one page",
        input_model=ScrollAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="send_keys",
        description=(
            "Send strings of special keys like Escape,Backspace, Insert, PageDown, "
            "Delete, Enter, shortcuts such as Control+o, Control+Shift+T are supported."
        ),
        input_model=SendKeysAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="scroll_to_text",
        description="If you dont find something which you want to interact with, scroll to it",
        input_model=create_model("ScrollToTextParams", text=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="write_file",
        description="Write content to file_name in file system, use only .md or .txt extensions.",
        input_model=create_model(
            "WriteFileParams", file_name=(str, ...), content=(str, ...)
        ),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="append_file",
        description="Append content to file_name in file system",
        input_model=create_model(
            "AppendFileParams", file_name=(str, ...), content=(str, ...)
        ),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="read_file",
        description="Read file_name from file system",
        input_model=create_model("ReadFileParams", file_name=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="get_dropdown_options",
        description="Get all options from a native dropdown",
        input_model=create_model("GetDropdownOptionsParams", index=(int, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="select_dropdown_option",
        description="Select dropdown option for interactive element index by the text of the option you want to select",
        input_model=create_model(
            "SelectDropdownOptionParams", index=(int, ...), text=(str, ...)
        ),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="drag_drop",
        description="Drag and drop elements or between coordinates on the page - useful for canvas drawing, sortable lists, sliders, file uploads, and UI rearrangement",
        input_model=DragDropAction,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="read_sheet_contents",
        description="Google Sheets: Get the contents of the entire sheet",
        input_model=EmptyParams,
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="read_cell_contents",
        description="Google Sheets: Get the contents of a cell or range of cells",
        input_model=create_model("ReadCellContentsParams", cell_or_range=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="update_cell_contents",
        description="Google Sheets: Update the content of a cell or range of cells",
        input_model=create_model(
            "UpdateCellContentsParams",
            cell_or_range=(str, ...),
            new_contents_tsv=(str, ...),
        ),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="clear_cell_contents",
        description="Google Sheets: Clear whatever cells are currently selected",
        input_model=create_model("ClearCellContentsParams", cell_or_range=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="select_cell_or_range",
        description="Google Sheets: Select a specific cell or range of cells",
        input_model=create_model("SelectCellOrRangeParams", cell_or_range=(str, ...)),
        output_model=ActionResult,
    )
)

register_spec(
    ToolSpec(
        id="fallback_input_into_single_selected_cell",
        description="Google Sheets: Fallback method to type text into (only one) currently selected cell",
        input_model=create_model("FallbackInputParams", text=(str, ...)),
        output_model=ActionResult,
    )
)
