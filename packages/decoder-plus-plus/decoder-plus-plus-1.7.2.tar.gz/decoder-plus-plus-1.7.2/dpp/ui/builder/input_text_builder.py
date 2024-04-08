from typing import List


class InputTextBuilder:

    def __init__(self, input_text: str, text_selections: List):
        self._input_text = input_text
        self._text_selections = self.addTextSelections(text_selections)

    def addTextSelection(self, start, end, plugin):
        self._text_selections.append((start, end, plugin))

    def addTextSelections(self, text_selections):
        for index_start, index_end, plugin in text_selections:
            self.addTextSelection(index_start, index_end, plugin)


    def build(self) -> str:
        replacements = {}
        selected_text_index_start, selected_text_index_end = frame.getTextSelection()
        for text_index_start, text_index_end, plugin in frame.getTextSelections():
            text_selection = self._input_text[selected_text_index_start:selected_text_index_end]
            if text_index_start == selected_text_index_start and text_index_end == selected_text_index_end:
                # Current selection requires initial plugin configuration.
                self._configure_plugin(frame_id, text_selection, plugin)
                output, status, error = self._run_plugin(frame_id, text_selection, plugin)
            else:
                # Other selections are already configured and can be run without any further ado.
                output, status, error = self._run_plugin(frame_id, text_selection, plugin)
            replacements[text_index_start] = (text_index_start, text_index_end, output)

        return self._replace_input_text(input_text, replacements)